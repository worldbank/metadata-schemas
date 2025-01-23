import inspect
import typing
from enum import Enum
from typing import Any, Callable, List, Type

from pydantic import AnyUrl, BaseModel

from .utils import standardize_keys_in_dict

DEFAULT_URL = "https://www.example.com"
MAX_DEPTH = 12


def _is_typing_annotation(annotation):
    if isinstance(annotation, str):
        return False  # Skip forward references which are in string form

    # Check if the annotation is directly from typing
    if getattr(annotation, "__module__", None) == "typing":
        return True

    # Handle special cases for generic types like List[int], Dict[str, int], etc.
    origin = getattr(annotation, "__origin__", None)
    return origin and getattr(origin, "__module__", None) == "typing"


def _is_builtin_type(tp):
    return tp in (str, int, float, bool, bytes, complex)


def _is_enum_type(tp):
    return inspect.isclass(tp) and issubclass(tp, Enum)


def _is_pydantic_subclass(cl):
    return inspect.isclass(cl) and issubclass(cl, BaseModel)


def _filter_list_for_condition(args: List[Any], condition: Callable[[Any], bool]) -> List[Any]:
    return [a for a in args if condition(a)]


def _is_pydantic_annotated_string(p, debug=False, recursion_level=0):
    if typing.get_origin(p) is typing.Annotated:
        args = typing.get_args(p)
        if args[0] is str:
            if debug:
                print("  " * recursion_level, "Is Annotated String")
            return True
        if debug:
            print("  " * recursion_level, f"Is Annotated but not a string {p}")
    return False


def _is_pydantic_annotated_float(p, debug=False, recursion_level=0):
    if typing.get_origin(p) is typing.Annotated:
        args = typing.get_args(p)
        if args[0] is float:
            if debug:
                print("  " * recursion_level, "Is Annotated float")
            return True
        if debug:
            print("  " * recursion_level, f"Is Annotated but not a float {p}")
    return False


def _create_default_class_from_annotation(
    p: Any, is_optional: bool = False, debug: bool = False, recursion_level: int = 0
):
    if p is str:
        if debug:
            print("  " * recursion_level, "STR")
        if is_optional:
            return None
        return ""
    if p is float:
        if debug:
            print("  " * recursion_level, "STR")
        if is_optional:
            return None
        raise ValueError("Cannot create default float as it's not optional")
    if _is_enum_type(p):
        if debug:
            print("  " * recursion_level, "ENUM")
        if is_optional:
            return None
        return list(p)[0].value  # get first value of the enum
    if _is_pydantic_subclass(p) and recursion_level < MAX_DEPTH:
        if debug:
            print("  " * recursion_level, "pydantic CLASS")
        return make_skeleton(p, debug=debug, recursion_level=recursion_level + 1)
    if _is_pydantic_subclass(p) and is_optional:
        return None
    if isinstance(p, type(AnyUrl)):
        return DEFAULT_URL
    raise ValueError(f"Unknown annotation: {p}")


def _create_default_from_list_of_args(args: List[Any], is_optional=True, debug=False, recursion_level=0):
    """
    return None for built in types and enums, but create skeletons of pydantic or typed parameters
    """
    if is_optional and recursion_level >= MAX_DEPTH:
        return None
    args = _filter_list_for_condition(args, lambda a: a is not type(None))
    typed_args = _filter_list_for_condition(args, _is_typing_annotation)  # _filter_list_for_typing_args(args)
    pydantic_args = _filter_list_for_condition(args, _is_pydantic_subclass)  #  _filter_for_pydantic_args(args)
    if debug:
        print(
            "  " * recursion_level,
            f"LIST OF ARGS: {args}, LIST OF TYPED ARGS: {typed_args}, LIST_OF_PYDANTIC_ARGS: {pydantic_args}",
        )
    if len(typed_args):
        if debug:
            print("  " * recursion_level, "moving to _create_default_from_typing_annotation")
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
            chosen_type, is_optional=is_optional, debug=debug, recursion_level=recursion_level
        )
    if len(pydantic_args):
        return make_skeleton(pydantic_args[0], debug=debug, recursion_level=recursion_level + 1)
    if len(_filter_list_for_condition(args, lambda a: _is_builtin_type(a) or _is_enum_type(a))):
        if debug:
            print("  " * recursion_level, "all builtins or enums")
        if is_optional:
            return None
        if len(_filter_list_for_condition(args, lambda a: a is str)):
            return ""
        raise ValueError(f"Can't create a default of {args}")
    if len(args) == 1 and _is_pydantic_annotated_string(args[0], debug=debug, recursion_level=recursion_level):
        if is_optional:
            return None
        return ""
    if len(args) == 1 and _is_pydantic_annotated_float(args[0], debug=debug, recursion_level=recursion_level):
        if is_optional:
            return None
        raise ValueError(f"Can't create a default of {args}")
    if len(args) == 1 and isinstance(args[0], type(AnyUrl)):
        if is_optional:
            return None
        return DEFAULT_URL
    raise ValueError(f"Can't create a default of {args}")


def _create_default_from_typing_annotation(p: Any, is_optional: bool = False, debug: bool = False, recursion_level=0):
    if debug:
        print("  " * recursion_level, "_create_default_from_typing_annotation")
    if p is typing.Any:
        return ""
    args = typing.get_args(p)
    if len(args) == 0:
        raise ValueError(p)
    isOptional = type(None) in args
    if isOptional:
        if debug:
            print("  " * recursion_level, "isOPTIONAL")
        if recursion_level >= MAX_DEPTH:
            return None
        return _create_default_from_list_of_args(args, is_optional=True, debug=debug, recursion_level=recursion_level)
    if getattr(p, "__origin__", None) is list:
        if debug:
            print("  " * recursion_level, "isLIST")
        if _is_pydantic_subclass(args[0]):
            return [make_skeleton(args[0], debug=debug, recursion_level=recursion_level + 1)]
        if is_optional:
            return []
        return [_create_default(args[0], is_optional=False, debug=debug, recursion_level=recursion_level + 1)]
    if getattr(p, "__origin__", None) is dict:
        if debug:
            print("  " * recursion_level, "isDICT")
        k = _create_default(args[0], debug=debug, recursion_level=recursion_level + 1)
        v = _create_default(args[1], debug=debug, recursion_level=recursion_level + 1)
        return {k: v}
    if len(args) > 1:
        if debug:
            print("  " * recursion_level, "isUNION")
        return _create_default_from_list_of_args(
            args, is_optional=is_optional, debug=debug, recursion_level=recursion_level
        )
    raise ValueError(f"Unknown typing {p}")


def _create_default(p: inspect.Parameter, is_optional: bool = False, debug: bool = False, recursion_level: int = 0):
    if hasattr(p, "annotation"):
        p = p.annotation
    if inspect.isclass(p) and not _is_typing_annotation(p):
        if debug:
            print("  " * recursion_level, "CLASS")
        return _create_default_class_from_annotation(
            p, is_optional=is_optional, debug=debug, recursion_level=recursion_level
        )
    if _is_typing_annotation(p):
        if debug:
            print("  " * recursion_level, "TYPED")
        return _create_default_from_typing_annotation(
            p, is_optional=is_optional, debug=debug, recursion_level=recursion_level
        )
    if _is_pydantic_annotated_string(p, debug=debug, recursion_level=recursion_level):
        if debug:
            print("  " * recursion_level, "ANNOTATED STRING")
        if is_optional:
            return None
        return ""
    raise ValueError(f"Unknown parameter {p}")


def make_skeleton(cl: Type[BaseModel], debug=False, recursion_level=0):
    parameter_map = inspect.signature(cl).parameters  # {'name': <Paramater "name: type">}
    param_values = {}
    for name, param in parameter_map.items():
        if debug:
            print("  " * recursion_level, f"{param.name}: {param.annotation}")
        param_values[name] = _create_default(param, debug=debug, recursion_level=recursion_level + 1)
        if debug:
            print("  " * recursion_level, f"Parameter: {name}, value: {param_values[name]}")
    param_values = standardize_keys_in_dict(param_values)
    return cl(**param_values)
