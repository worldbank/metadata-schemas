import copy
import re
import typing
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel, create_model


def is_optional_annotation(anno: typing._UnionGenericAlias) -> bool:
    return type(None) in typing.get_args(anno)


def is_union_annotation(anno: typing._UnionGenericAlias) -> bool:
    origin = typing.get_origin(anno)
    return origin in [Optional, Union]


def is_dict_annotation(anno: typing._UnionGenericAlias) -> bool:
    return typing.get_origin(anno) is dict


def is_list_annotation(anno: typing._UnionGenericAlias) -> bool:
    return typing.get_origin(anno) is list


def is_optional_list(anno: typing._UnionGenericAlias) -> bool:
    if is_optional_annotation(anno):
        args = typing.get_args(anno)
        if len(args) == 2 and is_list_annotation(args[0]):
            return True
    return False


def get_subtype_of_optional_or_list(anno: typing._UnionGenericAlias, debug=False) -> Any:
    if debug:
        print(f"getting subtype of {anno}")
    args = typing.get_args(anno)
    if debug:
        for a in args:
            print(f"getting subtype {a}, is it NoneType?={a is type(None)}")
    args = [a for a in args if not a is type(None)]
    for arg in args:
        if hasattr(arg, "annotation") and is_dict_annotation(arg.annotation):
            raise NotImplementedError("DICTS not yet implemented")
    for arg in args:
        if debug:
            print(f"checking arg {arg} -- {hasattr(arg, 'annotation')} -- {is_list_annotation(arg)}")
        if hasattr(arg, "annotation") and is_list_annotation(arg.annotation):
            return get_subtype_of_optional_or_list(arg.annotation, debug=debug)
        if is_list_annotation(arg):
            return get_subtype_of_optional_or_list(arg, debug=debug)
    if len(args) == 1:
        return args[0]
    if len(args) > 1:
        if str in args:
            return str
        return args[0]
    raise NotImplementedError("Only optional lists optional builtin types implemented")


def _annotation_contains_generic(
    anno: typing._UnionGenericAlias, checker: Callable[[typing._UnionGenericAlias], bool]
) -> bool:
    if checker(anno):
        return True
    if is_union_annotation(anno):
        args = typing.get_args(anno)
        args = [a for a in args if not a is type(None)]
        for a in args:
            if checker(a):
                return True
    if is_optional_annotation(anno) or is_list_annotation(anno):  # optional check is pointless given union check above
        subtype = get_subtype_of_optional_or_list(anno)
        return _annotation_contains_generic(subtype, checker=checker)
    return False


def annotation_contains_list(anno: typing._UnionGenericAlias) -> bool:
    return _annotation_contains_generic(anno, is_list_annotation)


def annotation_contains_dict(anno: typing._UnionGenericAlias) -> bool:
    return _annotation_contains_generic(anno, is_dict_annotation)


def annotation_contains_pydantic(anno: typing._UnionGenericAlias) -> bool:
    return _annotation_contains_generic(anno, lambda x: isinstance(x, type(BaseModel)))


def assert_dict_annotation_is_strings_or_any(anno):
    if is_union_annotation(anno):
        args = [a for a in typing.get_args(anno) if a is not type(None)]
        args = [a for a in args if is_dict_annotation(a)]
        anno = args[0]
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


def merge_dicts(base, update, skeleton_mode=False):
    """merge a pair of dicitonaries in which the values are themselves either dictionaries to be merged or lists of
    dictionaries to be merged.

    If skeleton_mode is True, then the base dictionary is assumed to be a skeleton where all lists of dictionaries have
    only one skeleton element. So then the skeleton element is duplicated and merged with each of the elements of the
    update elements.

    """
    if len(update) == 0:
        return base
    if len(base) == 0:
        return update
    new_dict = {}
    for key, base_value in base.items():
        if key in update:
            update_value = update[key]
            if isinstance(base_value, dict):
                if isinstance(update_value, dict):
                    new_dict[key] = merge_dicts(base_value, update_value)
                else:
                    new_dict[key] = base_value
            elif isinstance(base_value, list):
                if isinstance(update_value, list) and len(update_value) > 0:
                    new_list = []
                    if not skeleton_mode:
                        min_length = min(len(base_value), len(update_value))
                        for i in range(min_length):
                            if isinstance(base_value[i], dict):
                                if isinstance(update_value[i], dict):
                                    new_list.append(merge_dicts(base_value[i], update_value[i]))
                                else:
                                    new_list.append(base_value[i])
                            else:
                                new_list.append(update_value[i])
                        if len(base_value) > len(update_value):
                            new_list.extend(base_value[min_length:])
                        elif len(update_value) > len(base_value):
                            new_list.extend(update_value[min_length:])
                    else:
                        for i in range(len(update_value)):
                            skeleton = copy.deepcopy(base_value[0])
                            if isinstance(skeleton, dict):
                                if isinstance(update_value[i], dict):
                                    new_list.append(merge_dicts(skeleton, update_value[i]))
                                else:
                                    new_list.append(skeleton)
                            else:
                                raise ValueError(
                                    f"skeleton mode only works when passed base dictionaries: base_value = {base_value}, update_value = {update_value}"
                                )

                    new_dict[key] = new_list
                else:
                    new_dict[key] = base_value
            else:
                if skeleton_mode:
                    if update_value is not None:
                        new_dict[key] = update_value
                    else:
                        new_dict[key] = base_value
                else:
                    if base_value is None or base_value == "":
                        new_dict[key] = update_value
                    else:
                        new_dict[key] = base_value
        else:
            new_dict[key] = base_value
    for key, update_value in update.items():
        if key not in base:
            new_dict[key] = update_value
    return new_dict


def capitalize_first_letter(s):
    if s:
        return s[0].upper() + s[1:]
    return s


def split_on_capitals(s):
    # Use regular expression to split on capitalized letters
    return re.findall(r"[a-z]+|[A-Z][a-z]*", s)


def _standardize_keys_in_list_of_possible_dicts(lst: List[any], snake_to_pascal, pascal_to_snake) -> List[Any]:
    new_value = []
    for item in lst:
        if isinstance(item, dict):
            new_value.append(
                standardize_keys_in_dict(item, snake_to_pascal=snake_to_pascal, pascal_to_snake=pascal_to_snake)
            )
        elif isinstance(item, list):
            new_value.append(
                _standardize_keys_in_list_of_possible_dicts(
                    item, snake_to_pascal=snake_to_pascal, pascal_to_snake=pascal_to_snake
                )
            )
        else:
            new_value.append(item)
    return new_value


def standardize_keys_in_dict(
    d: Dict[str, Any], snake_to_pascal: bool = False, pascal_to_snake: bool = False
) -> Dict[str, Any]:
    """
    sometimes when field names are also python protected names like 'from' and 'import'
    then we append an underscore to the field name to avoide clashes.

    But pydantic doesn't expect that underscore to be there when instantiating, so we must remove it.
    """
    new_dict = {}
    for key, value in d.items():
        new_key = key.replace(" ", "_").rstrip("_")
        new_key = new_key.split(".")[-1]
        if snake_to_pascal:
            new_key = "".join([capitalize_first_letter(x) for x in new_key.split("_")])
        elif pascal_to_snake:
            new_key = "_".join([x.lower() for x in split_on_capitals(new_key)])
        if isinstance(value, dict):
            new_value = standardize_keys_in_dict(
                value, snake_to_pascal=snake_to_pascal, pascal_to_snake=pascal_to_snake
            )
        elif isinstance(value, list):
            new_value = _standardize_keys_in_list_of_possible_dicts(
                value, snake_to_pascal, pascal_to_snake=pascal_to_snake
            )
        else:
            new_value = value
        new_dict[new_key] = new_value
    return new_dict


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
    return create_model(name, **fields)


def subset_pydantic_model(model: BaseModel, feature_names: List[str], name: Optional[str] = None) -> BaseModel:
    SubModel = subset_pydantic_model_type(type(model), feature_names, name=name)
    input_dict = {k: v for k, v in model.model_dump(mode="json").items() if k in feature_names}
    input_dict_standardized = standardize_keys_in_dict(input_dict)
    try:
        return SubModel.model_validate(input_dict_standardized)
    except Exception as e:
        raise ValueError(input_dict_standardized) from e
