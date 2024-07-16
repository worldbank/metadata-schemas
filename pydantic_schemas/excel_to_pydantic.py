from typing import Dict, Type

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
    expected_fields = m.schema()["properties"].keys()
    fields_if_horizontally_arranged = df.iloc[0, :].values
    fields_if_vertically_arranged = df.iloc[:, 0].values

    horizontal_intersection = len(set(expected_fields).intersection(fields_if_horizontally_arranged))
    vertical_intersection = len(set(expected_fields).intersection(fields_if_vertically_arranged))
    return horizontal_intersection > vertical_intersection


def instantiate_from_df(m: Type[BaseModel], df: pd.DataFrame):
    name = m.schema()["title"]
    names = df.iloc[:, 0].values
    idx, sze = find_string_and_count_nans(df.iloc[:, 0].values, "Simple")
    if idx < 0:
        raise IndexError(f"{name} not found in {names}")
    sub = df.iloc[idx + 1 : idx + 1 + sze, 1:]
    if is_horizontally_organized(m, sub):
        sub = sub.T
    return m(**sub.set_index(sub.columns[0]).to_dict(orient="dict")[sub.columns[1]])


def excel_to_pydantic(filename: str, sheetname: str, objects: Dict[str, Type[BaseModel]]):
    fields = objects.values()
    df = pd.read_excel(filename, sheet_name=sheetname)
    ret = {}
    for k, v in objects.items():
        ret[k] = instantiate_from_df(v, df)
    return ret
