from typing import Dict, Optional, Type

import numpy as np
import pandas as pd
from pydantic import BaseModel


def find_string_and_count_nans(arr, search_str):
    """
    Finds the index of the first occurrence of a string in a NumPy array,
    and counts the number of NaNs immediately following that string.

    Args:
    - arr (np.ndarray): The NumPy array to search in.
    - search_str (str): The string to search for.

    Returns:
    - tuple: (index, nan_count)
        - index (int): Index of the first occurrence of the string, or -1 if not found.
        - nan_count (int): Number of NaNs immediately following the string.
    """
    index = np.where(arr == search_str)[0]  # Find index of the first occurrence
    if len(index) == 0:
        return -1, 0  # Return -1 if string not found, nan_count is 0
    index = index[0]  # Take the first occurrence index
    nan_count = 0
    for i in range(index + 1, len(arr)):
        if pd.isna(arr[i]):
            nan_count += 1
        else:
            break
    return int(index), nan_count


def is_horizontally_organized(m: Type[BaseModel], df: pd.DataFrame):
    """True if the index is along the top with the values below. False if the index is on the left side with the values to the right"""
    rows, cols = df.shape
    if rows == 1:
        return True
    elif cols == 1:
        return False

    expected_fields = m.schema()["properties"].keys()
    fields_if_horizontally_arranged = df.iloc[0, :].values
    fields_if_vertically_arranged = df.iloc[:, 0].values

    horizontal_intersection = len(set(expected_fields).intersection(fields_if_horizontally_arranged))
    vertical_intersection = len(set(expected_fields).intersection(fields_if_vertically_arranged))
    return horizontal_intersection > vertical_intersection


def get_relevant_sub_frame(m: Type[BaseModel], df: pd.DataFrame, name_of_field: Optional[str] = None):
    """
    THe dataframe likely contains lots and lots of information about other models.

    THis function obtains only that information that pertains to this model
    """
    name_of_class = m.schema()["title"]
    names = df.iloc[:, 0].values
    idx, sze = find_string_and_count_nans(df.iloc[:, 0].values, name_of_class)
    if idx < 0:
        if name_of_field is not None:
            idx, sze = find_string_and_count_nans(df.iloc[:, 0].values, name_of_field)
        if idx < 0:
            error_message = f"'{name_of_class}' "
            if name_of_field is not None:
                error_message += f"and '{name_of_field}' "
            error_message += "not found in {names}"
            raise IndexError(error_message)

    sub = df.iloc[idx : idx + sze + 1, 1:]

    sub = sub.dropna(how="all", axis=0)  # drop all null rows
    sub = sub.dropna(how="all", axis=1)  # drop all null columns
    if is_horizontally_organized(m, sub):
        sub = sub.T
    # sub.iloc[:, 0] = sub.iloc[:, 0].ffill()
    return sub


# def instantiate_from_df(m: Type[BaseModel], df: pd.DataFrame):
#     name = m.schema()["title"]
#     names = df.iloc[:, 0].values
#     idx, sze = find_string_and_count_nans(df.iloc[:, 0].values, name)
#     if idx < 0:
#         raise IndexError(f"'{name}' not found in {names}")
#     sub = df.iloc[idx + 1 : idx + 1 + sze, 1:]
#     if is_horizontally_organized(m, sub):
#         sub = sub.T
#     sub = sub.dropna(how='all')
#     return m(**sub.set_index(sub.columns[0]).to_dict(orient="dict")[sub.columns[1]])


def get_instance(model_type, df):
    objects = {k: v.annotation for k, v in model_type.model_fields.items()}
    fields = objects.values()
    ret = {}
    for name, field in objects.items():
        if isinstance(field, type(BaseModel)):
            print(f"BASE: {field}")
            sub = get_relevant_sub_frame(field, df, name)
            print(sub)
            ret[name] = get_instance(field, sub)
            print(ret[name])
        else:
            print(f"builtin: {name}")
            ret[name] = df.set_index(df.columns[0]).loc[name].values[0]
            print(ret[name])
        print()
    return model_type(**ret)


def excel_sheet_to_pydantic(filename: str, sheetname: str, model_type: Type[BaseModel]):
    df = pd.read_excel(filename, sheet_name=sheetname)
    try:
        df = get_relevant_sub_frame(model_type, df)
    except (KeyError, IndexError):
        pass
    return get_instance(model_type, df)
    # objects = {k: v.annotation for k, v in model_type.model_fields.items()}
    # fields = objects.values()
    # ret = {}
    # for k, v in objects.items():
    #     ret[k] = instantiate_from_df(v, df)
    # return model_type(**ret)
