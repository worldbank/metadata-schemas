import warnings
from typing import Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, Field, create_model

from .utils import get_subtype_of_optional_or_list, is_list_annotation, is_optional_annotation, standardize_keys_in_dict


def get_child_field_info_from_dot_annotated_name(name, parent_schema):
    name_split = name.split(".")
    for key in name_split[:-1]:
        parent_schema = parent_schema.model_fields[key].annotation
        if is_optional_annotation(parent_schema) or is_list_annotation(parent_schema):
            parent_schema = get_subtype_of_optional_or_list(parent_schema)
    try:
        child_field_info = parent_schema.model_fields[name_split[-1]]
    except KeyError as e:
        raise KeyError(name)
    return child_field_info


def define_simple_element(item, parent_schema, type=str):
    assert (
        isinstance(item, dict) and "type" in item and item["type"] in ["string", "integer"]
    ), f"expected string item, got {item}"
    try:
        child_field_info = get_child_field_info_from_dot_annotated_name(item["key"], parent_schema)
        if "title" in item:
            child_field_info.title = item["title"]
        if "description" in item:
            child_field_info.description = item["description"]
    except KeyError as e:
        warnings.warn(f"KeyError: {e}. Proceeding since {item['key']} is a string type.", UserWarning)
        child_field_info = Field(..., title=item["title"], description=item["help_text"])
    if "required" in item and item["required"]:
        field_type = type, child_field_info
    else:
        child_field_info.default = None
        field_type = Optional[type], child_field_info
    return {item["key"]: field_type}


def get_children_of_props(props, parent_schema) -> Dict[str, Tuple["type_annotation", "field_info"]]:
    children = {}
    for prop in props:
        name = prop["prop_key"]
        try:
            child_field_info = get_child_field_info_from_dot_annotated_name(name, parent_schema)
            if "title" in prop:
                child_field_info.title = prop["title"]
            if "help_text" in prop:
                child_field_info.description = prop["help_text"]
            child_field = child_field_info.annotation, child_field_info
            children[prop["key"]] = child_field
        except KeyError as e:
            if prop["type"] == "string":
                warnings.warn(f"KeyError: {e}. Proceeding since {name} is a string type.", UserWarning)
                children.update(define_simple_element(prop, parent_schema=parent_schema))
            elif prop["type"] == "integer":
                warnings.warn(f"KeyError: {e}. Proceeding since {name} is an int type.", UserWarning)
                children.update(define_simple_element(prop, parent_schema=parent_schema, type=int))
            else:
                raise KeyError(e) from e
    children = standardize_keys_in_dict(children, snake_to_pascal=True)
    return children


def define_array_element(item, parent_schema):
    assert "type" in item and (
        item["type"] == "array" or item["type"] == "nested_array"
    ), f"expected array item but got {item}"
    assert "props" in item, f"expected props in item but got {item.keys()}"
    assert "key" in item, f"expected key in item but got {item.keys()}"
    children = get_children_of_props(item["props"], parent_schema)
    item_element = create_model(f"{item['key']}_item", **children)
    return {item["key"]: (List[item_element], item_element)}


def define_simple_array_element(item, parent_schema):
    assert (
        isinstance(item, dict) and "type" in item and item["type"] == "simple_array"
    ), f"expected simple_array item, got {item}"
    try:
        child_field_info = get_child_field_info_from_dot_annotated_name(item["key"], parent_schema)
        if "title" in item:
            child_field_info.title = item["title"]
        if "description" in item:
            child_field_info.description = item["description"]
    except KeyError as e:
        warnings.warn(f"KeyError: {e}. Proceeding since {item['key']} is a simple_array type.", UserWarning)
        child_field_info = Field(..., title=item["title"], description=item["help_text"])
    if "required" in item and item["required"]:
        field_type = List[str], child_field_info
    else:
        child_field_info.default = None
        field_type = Optional[List[str]], child_field_info
    return {item["key"]: field_type}


def define_from_section_container(item, parent_schema):
    assert (
        isinstance(item, dict) and "type" in item and item["type"] == "section_container"
    ), f"expected section_container got {item}"
    name = item["key"]
    sub_model = create_model(name, **define_group_of_elements(item["items"], parent_schema))
    sub_field = Field(...)
    if "title" in item:
        sub_field.title = item["title"]
    if "required" not in item or not item["required"]:
        sub_field.default = None
    return {name: (sub_model, sub_field)}


def define_group_of_elements(items, parent_schema):
    elements = {}
    for i, item in enumerate(items):
        if item["type"] == "section_container":
            elements.update(define_from_section_container(item, parent_schema=parent_schema))
        elif item["type"] == "string":
            elements.update(define_simple_element(item, parent_schema, str))
        elif item["type"] == "integer":
            elements.update(define_simple_element(item, parent_schema, int))
        elif item["type"] in ["array", "nested_array"]:
            elements.update(define_array_element(item, parent_schema))
        elif item["type"] == "simple_array":
            elements.update(define_simple_array_element(item, parent_schema))
        elif item["type"] == "section":
            print(f"encountered section {item['key']}, {item['title']}, ignoring this heirarchy and appending")
            assert "items" in item, f"section does not contain items, found only {item}"
            elements.update(define_group_of_elements(item["items"], parent_schema))
        else:
            raise NotImplementedError(f"item {i} has type {item['type']}, {item}")
    elements = standardize_keys_in_dict(elements, snake_to_pascal=True)
    return elements


def pydantic_from_template(template: Dict, parent_schema: Type[BaseModel], name: Optional[str] = None) -> BaseModel:
    assert "items" in template, f"expected 'items' in template but got {list(template.keys())}"
    m = define_group_of_elements(template["items"], parent_schema)
    m = standardize_keys_in_dict(m, snake_to_pascal=True)
    if name is None:
        if "title" in template:
            name = template["title"]
        else:
            name = "new_model"
    name = name.replace(" ", "_").rstrip("_").split(".")[-1]
    return create_model(name, **m)
