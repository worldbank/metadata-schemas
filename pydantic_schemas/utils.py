import typing
from typing import Any, Dict, Optional, Union, get_args, get_origin

from pydantic import BaseModel


def is_optional_annotation(anno: typing._UnionGenericAlias) -> bool:
    return type(None) in typing.get_args(anno)


def is_union_annotation(anno: typing._UnionGenericAlias) -> bool:
    # return len(typing.get_args(anno))>=2
    origin = get_origin(anno)
    return origin in [Optional, Union]


def is_dict_annotation(anno: typing._UnionGenericAlias) -> bool:
    return typing.get_origin(anno) is dict


def is_list_annotation(anno: typing._UnionGenericAlias) -> bool:
    return typing.get_origin(anno) is list


def get_subtype_of_optional_or_list(anno: typing._UnionGenericAlias) -> Any:
    args = typing.get_args(anno)
    for a in args:
        print(f"getting subtype {a}, is it None?={isinstance(a, type(None))}")
    args = [a for a in args if not a is type(None)]
    if len(args) > 1:
        raise ValueError(f"Too many sub types: {args}")
    arg = args[0]
    if hasattr(arg, "annotation"):
        if is_list_annotation(arg.annotation):
            return get_subtype_of_optional_or_list(arg.annotation)
        else:
            raise NotYetImplementedError("Only optional lists and optional builtin types implemented")
    return arg


def annotation_contains_pydantic(anno: typing._UnionGenericAlias) -> bool:
    if isinstance(anno, type(BaseModel)):
        return True
    elif is_optional_annotation(anno) or is_list_annotation(anno):
        subtype = get_subtype_of_optional_or_list(anno)
        return isinstance(subtype, type(BaseModel))
    else:
        return False


def annotation_contains_list(anno: typing._UnionGenericAlias) -> bool:
    if is_list_annotation(anno):
        return True
    elif is_union_annotation(anno):
        args = typing.get_args(anno)
        args = [a for a in args if not a is type(None)]
        for a in args:
            if is_list_annotation(a):
                return True
    return False


def seperate_simple_from_pydantic(ob: BaseModel) -> Dict[str, Dict]:
    """
    Returns a dictionary of lists of field names that are either of other pydantic types or of other types
    """
    simple_children = []
    pydantic_children = []
    for mfield, field_info in ob.model_fields.items():
        if annotation_contains_pydantic(field_info.annotation):
            pydantic_children.append(mfield)
        else:
            simple_children.append(mfield)
    return {"simple": simple_children, "pydantic": pydantic_children}
