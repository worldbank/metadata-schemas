import json
from typing import Annotated, Any, List, Optional, Type, Union, get_args, get_origin

import numpy as np
import pandas as pd
from pydantic import BaseModel, create_model

from ..utils.pydantic_to_excel import pydantic_to_dataframe
from .quick_start import make_skeleton
from .utils import (
    annotation_contains_pydantic,
    get_subtype_of_optional_or_list,
    is_dict_annotation,
    is_list_annotation,
    is_optional_annotation,
    seperate_simple_from_pydantic,
    standardize_keys_in_dict,
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


def get_relevant_sub_frame(m: Type[BaseModel], df: pd.DataFrame, name_of_field: Optional[str] = None, debug=False):
    """
    THe dataframe likely contains lots and lots of information about other models.

    THis function obtains only that information that pertains to this model
    """
    names = df.iloc[:, 0].to_numpy()
    if debug:
        print(f"getting subframe for {m} or {name_of_field} given {names}")
    try:
        json_schema = m.model_json_schema()
        if debug:
            print(f"get relevant sub frame using json schema: {json_schema}")
        name_of_class = json_schema["title"]
        idx, sze = find_string_and_count_nans(names, name_of_class)
    except (AttributeError, KeyError):
        idx = -1
        sze = 0
    if idx < 0:
        if name_of_field is not None:
            idx, sze = find_string_and_count_nans(names, name_of_field)
        if idx < 0:
            error_message = f"'{m}' "
            if name_of_field is not None:
                error_message += f"and '{name_of_field}' "
            error_message += f"not found in {names}"
            raise IndexError(error_message)
        if debug:
            print(f"get relevant sub frame sze={sze}, idx={idx}")

    sub = df.iloc[idx : idx + sze + 1, 1:]
    if debug:
        print(sub)
    sub = sub.dropna(how="all", axis=0)  # drop all null rows
    sub = sub.dropna(how="all", axis=1)  # drop all null columns
    if debug:
        print("SubFrame = \n", sub)
    return sub


def handle_optional(name, annotation, df, from_within_list: bool = False, debug=False):
    args = [a for a in get_args(annotation) if a is not type(None)]
    if len(args) > 1:
        list_args = [a for a in args if is_list_annotation(a)]
        if len(list_args):
            arg = list_args[0]
        elif str in args:
            arg = str
        elif float in args:
            arg = float
        else:
            arg = args[0]
    else:
        arg = args[0]
    ret = annotation_switch(name, arg, df, from_within_list=from_within_list, debug=debug)
    if debug:
        print(f"optional ret: {ret}")
        print(f"isinstance(ret, list): {isinstance(ret, list)}")
    if isinstance(ret, (list, dict)) and len(ret) == 0:
        return None
    if isinstance(ret, str) and ret == "":
        return None
    return ret


def handle_list(name, anno, df, debug=False):
    subtype = get_subtype_of_optional_or_list(anno)
    if debug:
        print(f"handle_list found subtype: {subtype} from {anno} with name {name}\n{df}")
    if isinstance(subtype, type(BaseModel)):
        try:
            subframe = get_relevant_sub_frame(subtype, df, name_of_field=name, debug=debug)
            if debug:
                print(f"subframe\n{subframe}")
        except IndexError:
            return []
        list_of_subs = []
        if debug:
            print("handle list df received")
            print(subframe)
            print("handle list df expected except for the specific values")
            print(pydantic_to_dataframe([make_skeleton(subtype)])[0])
        index_size = max(
            [len(x) if isinstance(x, tuple) else 1 for x in pydantic_to_dataframe([make_skeleton(subtype)])[0].index]
        )
        if debug:
            print(f"measured index to have depth={index_size}")
        ## need to figure out the index columns and the data columns rather than assuming that the zeroth column is the *only* index column
        for c in list(range(len(subframe.columns)))[index_size:]:
            subsubframe = subframe.iloc[
                :, list(range(index_size)) + [c]
            ]  #  subframe.loc[:, [subframe.columns[:index_size], c]]
            if debug:
                print("subsubframe")
                print(subsubframe)
                print()
            sub = instantiate_pydantic_object(model_type=subtype, df=subsubframe, from_within_list=True, debug=debug)
            if debug:
                print(f"instantiated: {sub}")
            list_of_subs.append(sub)
        return list_of_subs
    values = df.set_index(df.columns[0]).loc[name]
    if debug:
        print(f"handle_list anno:{anno}, value: {values}")
    return [v for v in values if v is not None]


def handle_list_within_list(name, anno, df, debug=False):
    if debug:
        print(f"handle_list_within_list {name}, {anno}")
        print(df)
        print(df.set_index(df.columns[0]).loc[name])
        print(df.columns)

    df = df.dropna(axis=1, how="all")
    if debug:
        print("dropna")
        print(df)
    df = df.set_index(df.columns[0])
    if debug:
        print("setting index")
        print(df)
    values = df.loc[name]
    if debug:
        print(f"getting entry for '{name}'")
        print(values)
    values = values.to_numpy()[-1]  # , df.columns[1]
    if debug:
        print(f"values: {values}, {type(values)}")
    if values is None:
        return []
    try:
        values = json.loads(values.replace("'", '"').replace("None", "null"))
    except json.JSONDecodeError:
        try:
            values = json.loads(values.replace("None", "null"))
        except json.JSONDecodeError:
            try:
                appostrophe_string = "__APOSTROPHE__"
                values = json.loads(
                    values.replace("'", appostrophe_string)
                    .replace("'", '"')
                    .replace(appostrophe_string, "'")
                    .replace("None", "null")
                )
            except json.JSONDecodeError as e:
                raise ValueError(f"cannot decode {name}:{anno} with values {values}") from e
    if debug:
        print("decoded values:", values)
    if len(values) == 0:
        return []
    sub_type = get_subtype_of_optional_or_list(anno)
    is_dicts = any(isinstance(v, dict) for v in values)
    if is_dicts and annotation_contains_pydantic(sub_type):
        return [sub_type(**standardize_keys_in_dict(v)) for v in values]
    if not is_dicts and not annotation_contains_pydantic(sub_type):
        return values
    raise NotImplementedError(f"handle_list_within_list unexpected values - {name}, {anno}, {values}, {df}")


def handle_builtin_or_enum(name, anno, df, debug=False):
    if debug:
        print(df)
    if len(df) == 0:
        return ""
    df_indexed = df.set_index(df.columns[0])
    if debug:
        print("handle_builtin_or_enum", df_indexed)
    if name not in df_indexed.index:
        return ""
    values = df_indexed.loc[name]
    if len(values) == 0:
        return ""
    values = [v for v in values if v is not None]
    if len(values) == 0:
        return ""
    if len(values) >= 2:
        raise ValueError(f"Expected only a single value but got {values}")
    return values[0]


def handle_dict(name, anno, df):
    dictionary_type = create_model(name, key=(Optional[List[str]], None), value=(Optional[List[Any]], None))
    dict_results = annotation_switch(name, dictionary_type, df)
    if (
        dict_results.key is None
        or len(dict_results.key) == 0
        or dict_results.value is None
        or len(dict_results.value) == 0
    ):
        return {}
    return {k: v for k, v in zip(dict_results.key, dict_results.value) if k is not None}


def annotation_switch(name: str, anno, df: pd.DataFrame, from_within_list=False, debug=False) -> Any:
    if debug:
        print(f"annotation_to_value name: {name}")
    if is_optional_annotation(anno):
        if debug:
            print("optional")
        return handle_optional(name, anno, df, from_within_list=from_within_list, debug=debug)
    if is_dict_annotation(anno):
        return handle_dict(name, anno, df)
    if is_list_annotation(anno):
        if from_within_list:
            if debug:
                print("list within a list")
            return handle_list_within_list(name, anno, df, debug=debug)
        if debug:
            print("list")
        return handle_list(name, anno, df, debug=debug)
    if isinstance(anno, type(BaseModel)):
        if debug:
            print("pydantic")
            print(anno)
            print(name)
            print(df)
        try:
            sub = get_relevant_sub_frame(anno, df, name_of_field=name, debug=debug)
            if debug:
                print("pydantic sub:")
                print(sub)
        except IndexError:
            return make_skeleton(anno)
        return instantiate_pydantic_object(anno, sub, from_within_list=from_within_list, debug=debug)
    if len(get_args(anno)) == 0:
        if debug:
            print("builtin or enum")
        return handle_builtin_or_enum(name, anno, df)
    if get_origin(anno) is Annotated:
        if debug:
            print(f"got Annotated type: {anno}, treating as builtin or enum")
        datatype = getattr(anno, "__origin__", None)
        return handle_builtin_or_enum(name, datatype, df)
    raise NotImplementedError(anno)


def instantiate_pydantic_object(
    model_type: Type[BaseModel], df: pd.DataFrame, from_within_list=False, debug=False
) -> BaseModel:
    ret = {}
    if debug:
        print(f"instantiate_pydantic_object df = {df}")
    for field_name, field_info in model_type.model_fields.items():
        anno = field_info.annotation
        if debug:
            print(f"Instantiating field {field_name}, anno {anno} and args {get_args(anno)}")
        ret[field_name] = annotation_switch(field_name, anno, df, from_within_list=from_within_list, debug=debug)
        if debug:
            print(ret[field_name])
            print()
    return model_type(**standardize_keys_in_dict(ret))


def excel_sheet_to_pydantic(
    filename: str, sheetname: str, model_type: Union[Type[BaseModel], Type[List[BaseModel]]], debug=False
):
    if debug:
        print(f"excel_sheet_to_pydantic, sheetname={sheetname}, model_type={model_type}")
    df = pd.read_excel(filename, sheet_name=sheetname, header=None)
    df = df.where(df.notna(), None)
    if debug:
        print("line 304", model_type)
        print(df)

    if is_optional_annotation(model_type):
        if not annotation_contains_pydantic(model_type):
            return handle_optional(df.iloc[0, 0], model_type, df, debug=debug)
        model_type = [x for x in get_args(model_type) if x is not type(None)][0]

    if is_list_annotation(model_type):
        return handle_list(df.iloc[0, 0], model_type, df, debug=debug)

    if debug:
        print("getting children for", model_type)
    children = seperate_simple_from_pydantic(model_type)
    if debug:
        print(f"children: {children}")
    ret = {}
    if "simple" in children and len(children["simple"]):
        if set(children["simple"]) != set(df.iloc[:, 0].values):
            if debug:
                print(f"simple children: {set(children['simple'])}")
                print(f"df columns: {set(df.iloc[:, 0].values)}")
            sub = get_relevant_sub_frame(model_type, df, name_of_field=df.iloc[0, 0])
        else:
            sub = df
        simple_child_field_type = subset_pydantic_model_type(model_type, children["simple"])
        fields = instantiate_pydantic_object(simple_child_field_type, sub, from_within_list=False, debug=debug)
        for child in children["simple"]:
            ret[child] = getattr(fields, child)
    for name in children["pydantic"]:
        if debug:
            print(f"sheet Looking to get {name}")
        anno = model_type.model_fields[name].annotation
        ret[name] = annotation_switch(name, anno, df, from_within_list=False, debug=debug)
    for k, v in ret.items():
        if isinstance(v, (list, np.ndarray)):
            ret[k] = [elem for elem in v if elem is not None]
    if debug:
        print(ret)

    return model_type(**ret)


def excel_single_sheet_to_pydantic(filename: str, model_type: Type[BaseModel], verbose=False) -> BaseModel:
    return excel_sheet_to_pydantic(filename, "metadata", model_type, debug=verbose)


def excel_doc_to_pydantic(filename: str, model_type: Type[BaseModel], verbose=False) -> BaseModel:
    children = seperate_simple_from_pydantic(model_type)
    annotations = {k: v.annotation for k, v in model_type.model_fields.items()}
    ret = {}

    if len(children["simple"]) > 0:
        field_type = subset_pydantic_model_type(model_type, children["simple"])
        fields = excel_sheet_to_pydantic(filename, sheetname="metadata", model_type=field_type, debug=verbose)
        for child in children["simple"]:
            ret[child] = getattr(fields, child)
    for fieldname in children["pydantic"]:
        if verbose:
            print(f"Looking to get {fieldname}")
        field_type = annotations[fieldname]
        ret[fieldname] = excel_sheet_to_pydantic(filename, sheetname=fieldname, model_type=field_type, debug=verbose)
    return model_type(**ret)
