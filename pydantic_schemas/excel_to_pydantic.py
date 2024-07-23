import json
import warnings
from collections.abc import Iterable
from typing import Dict, Optional, Type, Union, get_args, get_origin

import numpy as np
import pandas as pd
from pydantic import BaseModel

from .utils import (
    annotation_contains_list,
    get_subtype_of_optional_or_list,
    is_list_annotation,
    seperate_simple_from_pydantic,
    subset_pydantic_model_type,
)


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

    print("is_horizontally_organized is looking at ", m)
    if is_list_annotation(m):
        m = get_subtype_of_optional_or_list(m)
    expected_fields = m.model_json_schema()["properties"].keys()
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
    names = df.iloc[:, 0].values
    try:
        name_of_class = m.model_json_schema()["title"]

        idx, sze = find_string_and_count_nans(names, name_of_class)
    except AttributeError:
        idx = -1
        sze = 0
    if idx < 0:
        if name_of_field is not None:
            idx, sze = find_string_and_count_nans(names, name_of_field)
        if idx < 0:
            error_message = f"'{name_of_class}' "
            if name_of_field is not None:
                error_message += f"and '{name_of_field}' "
            error_message += f"not found in {names}"
            raise IndexError(error_message)

    sub = df.iloc[idx : idx + sze + 1, 1:]

    sub = sub.dropna(how="all", axis=0)  # drop all null rows
    sub = sub.dropna(how="all", axis=1)  # drop all null columns
    print("SubFrame = \n", sub)
    if is_horizontally_organized(m, sub):
        sub = sub.T
    return sub


def get_value(name, field_annotation, df, is_list=False):
    if isinstance(field_annotation, type(BaseModel)):
        print(f"BASE: {field_annotation}")
        sub = get_relevant_sub_frame(field_annotation, df, name)
        print(sub)
        base_instance = get_instance_of_pydantic(field_annotation, sub, is_list=is_list)
        print("BASE INSTANCE: ", base_instance)
        return base_instance
    elif annotation_contains_list(field_annotation):
        print("LIST", name, field_annotation)
        sub_type = get_subtype_of_optional_or_list(field_annotation)
        vals = get_value(name, sub_type, df, is_list=True)
        print(f"vals in get_value of list: {vals}")
        if is_list:
            # we had a list of lists!
            vals = [json.loads(v.replace("'", '"')) if isinstance(v, str) else v for v in vals]

        return vals
    else:
        print(f"builtin: {name}")
        sub = df.set_index(df.columns[0])
        if name in sub.index:
            values = sub.loc[name].values
            if is_list:
                print(values)
                return values
            if len(values) > 0:
                return values[0]
        print(f"No values found for name = {name}, field annotation = {field_annotation}")
        if isinstance(field_annotation, type(str)):
            warnings.warn(
                f"Required string field '{name}' not found, setting to an empty string",
                UserWarning,
            )
            return ""
    return None


def get_instance_of_pydantic(model_type: Type[BaseModel], df, is_list=False):
    objects = {k: v.annotation for k, v in model_type.model_fields.items()}
    ret = {}
    for name, field in objects.items():
        ret[name] = get_value(name, field, df, is_list=is_list)
        print(f"for {name} got {ret[name]}")
    if is_list:
        print(f"Making a list of pydantic objects from {ret}")
        num_list_elements = set([len(v) for _, v in ret.items()])
        assert len(num_list_elements) == 1, ret
        num_list_elements = num_list_elements.pop()
        elements = []
        for i in range(num_list_elements):
            sub = {k: v[i] for k, v in ret.items()}
            if all([v is None for _, v in sub.items()]):
                continue
            elements.append(model_type(**sub))
        return elements
    else:
        for k, v in ret.items():
            if isinstance(v, list) or isinstance(v, np.ndarray):
                ret[k] = [elem for elem in v if elem is not None]
        print(ret)
        return model_type(**ret)


def excel_sheet_to_pydantic(filename: str, sheetname: str, model_type: Type[BaseModel]):
    df = pd.read_excel(filename, sheet_name=sheetname, header=None)
    df = df.where(df.notnull(), None)
    try:
        df = get_relevant_sub_frame(model_type, df)
    except (KeyError, IndexError):
        pass
    children = seperate_simple_from_pydantic(model_type)
    ret = {}
    if len(children["simple"]):
        sub = get_relevant_sub_frame(model_type, df, name_of_field=df.iloc[0, 0])
        for name in children["simple"]:
            print(f"Looking to get {name}")
            field = model_type.model_fields[name]
            ret[name] = get_value(name, field.annotation, sub)
            print()
    for name in children["pydantic"]:
        print(f"Looking to get {name}")
        ret[name] = get_value(name, model_type.model_fields[name].annotation, df)
        print()
    for k, v in ret.items():
        if isinstance(v, list) or isinstance(v, np.ndarray):
            ret[k] = [elem for elem in v if elem is not None]
    print(ret)

    return model_type(**ret)


def excel_doc_to_pydantic(filename, model_type):
    children = seperate_simple_from_pydantic(model_type)
    annotations = {k: v.annotation for k, v in model_type.model_fields.items()}
    ret = {}

    if len(children["simple"]) > 0:
        field_type = subset_pydantic_model_type(model_type, children["simple"])
        toplevel = excel_sheet_to_pydantic(filename, sheetname="metadata", model_type=field_type)
        ret.update(toplevel.model_dump())
    for fieldname in children["pydantic"]:
        print(f"Looking to get {fieldname}")
        field_type = annotations[fieldname]
        if isinstance(field_type, type(BaseModel)):
            ret[fieldname] = excel_sheet_to_pydantic(filename, sheetname=fieldname, model_type=field_type)
        else:
            field_type = subset_pydantic_model_type(model_type, [fieldname])
            sublevel = excel_sheet_to_pydantic(filename, sheetname=fieldname, model_type=field_type)
            ret.update(sublevel.model_dump())
    return model_type(**ret)
