import importlib
import inspect
import typing
from enum import Enum
from typing import Any, Callable, Dict, List, Type

from pydantic import AnyUrl, BaseModel

from .utils import standardize_keys_in_dict

METADATA_TYPES_FILE_MAP = {
    "document_schema": "ScriptSchemaDraft",
    "geospatial_schema": "GeospatialSchema",
    "image_schema": "ImageDataTypeSchema",
    "microdata_schema": "MicrodataSchema",
    "script_schema": "ResearchProjectSchemaDraft",
    "series_schema": "Series",
    "table_schema": "Model",
    "timeseries_db_schema": "TimeseriesDatabaseSchema",
    "timeseries_schema": "TimeseriesSchema",
    "video_schema": "Model",
}

DEFAULT_URL = "http://www.example.com"


def _is_typing_annotation(annotation):
    if isinstance(annotation, str):
        return False  # Skip forward references which are in string form

    # Check if the annotation is directly from typing
    if getattr(annotation, "__module__", None) == "typing":
        return True

    # Handle special cases for generic types like List[int], Dict[str, int], etc.
    origin = getattr(annotation, "__origin__", None)
    if origin and getattr(origin, "__module__", None) == "typing":
        return True

    return False


def _is_builtin_type(tp):
    return tp in (str, int, float, bool, bytes, complex)


def _is_enum_type(tp):
    return inspect.isclass(tp) and issubclass(tp, Enum)


def _is_pydantic_subclass(cl):
    return inspect.isclass(cl) and issubclass(cl, BaseModel)


def _filter_list_for_condition(args: List[Any], condition: Callable[[Any], bool]) -> List[Any]:
    return [a for a in args if condition(a)]


def _is_pydantic_annotated_string(p, debug=False, indentation=""):
    if typing.get_origin(p) is typing.Annotated:
        args = typing.get_args(p)
        if args[0] is str:
            if debug:
                print(indentation, "Is Annotated String")
            return True
        if debug:
            print(indentation, f"Is Annotated but not a string {p}")
    return False


def _is_pydantic_annotated_float(p, debug=False, indentation=""):
    if typing.get_origin(p) is typing.Annotated:
        args = typing.get_args(p)
        if args[0] is float:
            if debug:
                print(indentation, "Is Annotated float")
            return True
        if debug:
            print(indentation, f"Is Annotated but not a float {p}")
    return False


def _create_default_class_from_annotation(
    p: Any, is_optional: bool = False, debug: bool = False, indentation: str = ""
):
    if p is str:
        if debug:
            print(indentation, "STR")
        if is_optional:
            return None
        else:
            return ""
    elif p is float:
        if debug:
            print(indentation, "STR")
        if is_optional:
            return None
        else:
            raise ValueError("Cannot create default float as it's not optional")
    elif _is_enum_type(p):
        if debug:
            print(indentation, "ENUM")
        if is_optional:
            return None
        else:
            return list(p)[0].value  # get first value of the enum
    elif _is_pydantic_subclass(p):
        if debug:
            print(indentation, "pydantic CLASS")
        return make_skeleton(p, debug=debug, indentation=indentation + "  ")
    elif isinstance(p, type(AnyUrl)):
        return DEFAULT_URL
    else:
        raise ValueError(f"Unknown annotation: {p}")


def _create_default_from_list_of_args(args: List[Any], is_optional=True, debug=False, indentation=""):
    """
    return None for built in types and enums, but create skeletons of pydantic or typed parameters
    """
    args = _filter_list_for_condition(args, lambda a: a is not type(None))
    typed_args = _filter_list_for_condition(args, _is_typing_annotation)  # _filter_list_for_typing_args(args)
    pydantic_args = _filter_list_for_condition(args, _is_pydantic_subclass)  #  _filter_for_pydantic_args(args)
    if debug:
        print(
            indentation,
            f"LIST OF ARGS: {args}, LIST OF TYPED ARGS: {typed_args}, LIST_OF_PYDANTIC_ARGS: {pydantic_args}",
        )
    if len(typed_args):
        if debug:
            print(indentation, "moving to _create_default_from_typing_annotation")
        # because dicts are more complicated than lists, we should default to dicts
        typed_dicts = _filter_list_for_condition(typed_args, lambda p: getattr(p, "__origin__", None) is dict)
        typed_lists = _filter_list_for_condition(typed_args, lambda p: getattr(p, "__origin__", None) is list)
        if len(typed_dicts):
            chosen_type = typed_dicts[0]
        elif len(typed_lists):
            chosen_type = typed_lists[0]
        else:
            chosen_type = typed_args[0]
        return _create_default_from_typing_annotation(
            chosen_type, is_optional=is_optional, debug=debug, indentation=indentation
        )
    elif len(pydantic_args):
        return make_skeleton(pydantic_args[0], debug=debug, indentation=indentation + "  ")
    elif len(_filter_list_for_condition(args, lambda a: _is_builtin_type(a) or _is_enum_type(a))):
        if debug:
            print(indentation, "all builtins or enums")
        if is_optional:
            return None
        elif len(_filter_list_for_condition(args, lambda a: a is str)):
            return ""
        else:
            raise ValueError(f"Can't create a default of {args}")
    elif len(args) == 1 and _is_pydantic_annotated_string(args[0], debug=debug, indentation=indentation):
        if is_optional:
            return None
        else:
            return ""
    elif len(args) == 1 and _is_pydantic_annotated_float(args[0], debug=debug, indentation=indentation):
        if is_optional:
            return None
        else:
            raise ValueError(f"Can't create a default of {args}")
    elif len(args) == 1 and isinstance(args[0], type(AnyUrl)):
        if is_optional:
            return None
        else:
            return DEFAULT_URL
    else:
        raise ValueError(f"Can't create a default of {args}")


def _create_default_from_typing_annotation(p: Any, is_optional: bool = False, debug: bool = False, indentation=""):
    if debug:
        print(indentation, "_create_default_from_typing_annotation")
    if p is typing.Any:
        return ""
    args = typing.get_args(p)
    if len(args) == 0:
        raise ValueError(p)
    isOptional = type(None) in args
    if isOptional:
        if debug:
            print(indentation, "isOPTIONAL")
        return _create_default_from_list_of_args(args, is_optional=True, debug=debug, indentation=indentation)
    elif getattr(p, "__origin__", None) is list:
        if debug:
            print(indentation, "isLIST")
        if _is_pydantic_subclass(args[0]):
            return [make_skeleton(args[0], debug=debug, indentation=indentation + "  ")]
        else:
            if is_optional:
                return []
            else:
                return [_create_default(args[0], is_optional=False, debug=debug, indentation=indentation + "  ")]
    elif getattr(p, "__origin__", None) is dict:
        if debug:
            print(indentation, "isDICT")
        k = _create_default(args[0], debug=debug, indentation=indentation + "  ")
        v = _create_default(args[1], debug=debug, indentation=indentation + "  ")
        return {k: v}
    elif len(args) > 1:
        if debug:
            print(indentation, "isUNION")
        return _create_default_from_list_of_args(args, is_optional=is_optional, debug=debug, indentation=indentation)
    else:
        raise ValueError(f"Unknown typing {p}")


def _create_default(p: inspect.Parameter, is_optional: bool = False, debug: bool = False, indentation: str = ""):
    if hasattr(p, "annotation"):
        p = p.annotation
    if inspect.isclass(p) and not _is_typing_annotation(p):
        if debug:
            print(indentation, "CLASS")
        return _create_default_class_from_annotation(p, is_optional=is_optional, debug=debug, indentation=indentation)
    elif _is_typing_annotation(p):
        if debug:
            print(indentation, "TYPED")
        return _create_default_from_typing_annotation(p, is_optional=is_optional, debug=debug, indentation=indentation)
    elif _is_pydantic_annotated_string(p, debug=debug, indentation=indentation):
        if debug:
            print(indentation, "ANNOTATED STRING")
        if is_optional:
            return None
        else:
            return ""
    else:
        raise ValueError(f"Unknown parameter {p}")


def make_skeleton(cl: Type[BaseModel], debug=False, indentation=""):
    parameter_map = inspect.signature(cl).parameters  # {'name': <Paramater "name: type">}
    param_values = {}
    for name, param in parameter_map.items():
        if debug:
            print(indentation, f"{param.name}: {param.annotation}")
        param_values[name] = _create_default(param, debug=debug, indentation=indentation + "  ")
        if debug:
            print(indentation, f"Parameter: {name}, value: {param_values[name]}")
    param_values = standardize_keys_in_dict(param_values)
    return cl(**param_values)


def create_empty_schema_from_path(module_name, class_name, debug=False):
    MyClass = getattr(importlib.import_module(module_name), class_name)
    return make_skeleton(MyClass, debug=debug)
