import typing
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_args, get_origin

from pydantic import BaseModel, create_model


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


def get_subtype_of_optional_or_list(anno: typing._UnionGenericAlias, debug=False) -> Any:
    args = typing.get_args(anno)
    if debug:
        for a in args:
            print(f"getting subtype {a}, is it NoneType?={a is type(None)}")
    args = [a for a in args if not a is type(None)]
    # if len(args) > 1:
    #     raise ValueError(f"Too many sub types: {args}")
    for arg in args:
        if hasattr(arg, "annotation") and is_dict_annotation(arg.annotation):
            raise NotImplementedError("DICTS not yet implemented")
    for arg in args:
        if hasattr(arg, "annotation") and is_list_annotation(arg.annotation):
            return get_subtype_of_optional_or_list(arg.annotation)
    if len(args) == 1:
        return args[0]
    else:
        raise NotImplementedError("Only optional lists optional builtin types implemented")


def _annotation_contains_generic(
    anno: typing._UnionGenericAlias, checker: Callable[[typing._UnionGenericAlias], bool]
) -> bool:
    if checker(anno):
        return True
    elif is_union_annotation(anno):
        args = typing.get_args(anno)
        args = [a for a in args if not a is type(None)]
        for a in args:
            if checker(a):
                return True
    elif is_optional_annotation(anno) or is_list_annotation(anno):
        subtype = get_subtype_of_optional_or_list(anno)
        return checker(subtype)
    return False


def annotation_contains_list(anno: typing._UnionGenericAlias) -> bool:
    return _annotation_contains_generic(anno, is_list_annotation)


def annotation_contains_dict(anno: typing._UnionGenericAlias) -> bool:
    return _annotation_contains_generic(anno, is_dict_annotation)


def annotation_contains_pydantic(anno: typing._UnionGenericAlias) -> bool:
    return _annotation_contains_generic(anno, lambda x: isinstance(x, type(BaseModel)))


def assert_dict_annotation_is_strings_or_any(anno):
    if is_dict_annotation(anno):
        args = typing.get_args(anno)
        for a in args:
            if not (a is str or a is typing.Any):
                raise AssertionError(f"exepcted dictionaries of strings to strings or Any but got {anno}")
    elif is_optional_annotation(anno):
        assert_dict_annotation_is_strings_or_any(get_subtype_of_optional_or_list(anno))
    else:
        raise ValueError(f"Expected dictionary or optional dictionary annotation but got {anno}")


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


def subset_pydantic_model_type(
    model_type: Type[BaseModel], feature_names: List[str], name: Optional[str] = None
) -> Type[BaseModel]:
    """
    Create a new Pydantic model type with only the specified subset of features.

    :param model: The original Pydantic model object.
    :param feature_names: List of feature names to include in the new model.
    :return: A new Pydantic model type with the specified features from the original model
    """
    # Filter the fields of the original model based on the feature names
    fields = {
        name: (model_type.model_fields[name].annotation, model_type.model_fields[name].default)
        for name in feature_names
        if name in model_type.model_fields
    }

    # Create a new Pydantic model with the filtered fields
    if name is None:
        name = "SubsetModel"
    SubModel = create_model(name, **fields)
    return SubModel


def subset_pydantic_model(model: BaseModel, feature_names: List[str], name: Optional[str] = None) -> BaseModel:
    SubModel = subset_pydantic_model_type(type(model), feature_names, name=name)
    return SubModel(**{k: v for k, v in model.model_dump().items() if k in feature_names})
