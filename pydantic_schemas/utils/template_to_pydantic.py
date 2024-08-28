import warnings
from typing import Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, Field, create_model

from .utils import get_subtype_of_optional_or_list, is_list_annotation, is_optional_annotation, standardize_keys_in_dict


def get_child_field_info_from_dot_annotated_name(name, parent_schema):
    assert isinstance(parent_schema, type(BaseModel)), "get_child_field_info_from_dot_annotated_name"
    name_split = name.split(".")
    for key in name_split[:-1]:
        parent_schema = parent_schema.model_fields[key].annotation
        if is_optional_annotation(parent_schema) or is_list_annotation(parent_schema):
            parent_schema = get_subtype_of_optional_or_list(parent_schema)
        if not isinstance(parent_schema, type(BaseModel)):
            raise KeyError(name)
    try:
        child_field_info = parent_schema.model_fields[name_split[-1]]
    except KeyError as e:
        raise KeyError(name) from e
    except:
        raise ValueError(f"name={name}, parent_schema={parent_schema}")
    return child_field_info


def define_simple_element(item, parent_schema, element_type=str):
    assert isinstance(parent_schema, type(BaseModel)), "define_simple_element"
    assert (
        isinstance(item, dict) and "type" in item and item["type"] in ["string", "text", "integer", "number", "boolean"]
    ), f"expected string, integer or boolean item, got {item}"
    try:
        child_field_info = get_child_field_info_from_dot_annotated_name(item["key"], parent_schema)
        if "title" in item:
            child_field_info.title = item["title"]
        if "description" in item:
            child_field_info.description = item["description"]
    except KeyError as e:
        warnings.warn(f"KeyError: {e}. Proceeding since {item['key']} is a string type.", UserWarning)
        child_field_info = Field(..., title=item["title"])
        if "help_text" in item:
            child_field_info.description = item["help_text"]
    if "required" in item and item["required"]:
        field_type = element_type, child_field_info
    else:
        child_field_info.default = None
        field_type = Optional[element_type], child_field_info
    return {item["key"]: field_type}


def get_children_of_props(props, parent_schema) -> Dict[str, Tuple["type_annotation", "field_info"]]:
    assert isinstance(parent_schema, type(BaseModel)), "get_children_of_props"
    children = {}
    for prop in props:
        if "prop_key" not in prop:
            children.update(template_type_handler(prop, parent_schema))
        else:
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
                children.update(template_type_handler(prop, parent_schema))
    return children


def define_array_element(item, parent_schema):
    assert isinstance(parent_schema, type(BaseModel)), "define_array_element"
    assert "type" in item and (
        item["type"] == "array" or item["type"] == "nested_array"
    ), f"expected array item but got {item}"
    assert "key" in item, f"expected key in item but got {item.keys()}"
    if "props" not in item:
        warnings.warn(f"array without type found, assuming array of str: {item}")
        field_info = Field(..., title=item["title"])
        if "help_text" in item:
            field_info.description = item["help_text"]
        return {item["key"]: (List[str], field_info)}
    else:
        children = get_children_of_props(item["props"], parent_schema)
        item_element = create_model(f"{item['key']}_item", **children)
        return {item["key"]: (List[item_element], item_element)}


def define_simple_array_element(item, parent_schema):
    assert isinstance(parent_schema, type(BaseModel)), "define_simple_array_element"
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
        child_field_info = Field(..., title=item["title"])
        if "help_test" in item:
            child_field_info.description = item["help_text"]
    if "required" in item and item["required"]:
        field_type = List[str], child_field_info
    else:
        child_field_info.default = None
        field_type = Optional[List[str]], child_field_info
    return {item["key"]: field_type}


def define_from_section_container(item, parent_schema):
    assert isinstance(parent_schema, type(BaseModel)), "define_from_section_container"
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
    assert isinstance(parent_schema, type(BaseModel)), "define_group_of_elements"
    elements = {}
    for i, item in enumerate(items):
        if "is_custom" in item and item["is_custom"] == True:
            if "additional" not in elements:
                elements["additional"] = {}
            elements["additional"].update(template_type_handler(item, parent_schema))
            elements["additional"] = standardize_keys_in_dict(elements["additional"], pascal_to_snake=True)
        else:
            elements.update(template_type_handler(item, parent_schema))
    elements = standardize_keys_in_dict(elements, pascal_to_snake=True)
    if "additional" in elements:
        additional = elements.pop("additional")
        additional = create_model("additional", **additional)
        sub_field = Field(...)
        sub_field.title = "additional"
        elements["additional"] = additional, sub_field
    return elements


def template_type_handler(item, parent_schema):
    assert isinstance(parent_schema, type(BaseModel)), "template_type_handler"
    if item["type"] == "section_container":
        return define_from_section_container(item, parent_schema)
    elif item["type"] in ["string", "text"]:
        return define_simple_element(item, parent_schema, str)
    elif item["type"] in ["integer", "number"]:
        return define_simple_element(item, parent_schema, int)
    elif item["type"] == "boolean":
        return define_simple_element(item, parent_schema, bool)
    elif item["type"] in ["array", "nested_array"]:
        return define_array_element(item, parent_schema)
    elif item["type"] == "simple_array":
        return define_simple_array_element(item, parent_schema)
    elif item["type"] == "section":
        warnings.warn(f"encountered section {item['key']}, {item['title']}, ignoring this heirarchy and appending")
        if "items" in item:
            return define_group_of_elements(item["items"], parent_schema)
        elif "props" in item:
            return define_group_of_elements(item["props"], parent_schema)
        else:
            raise ValueError(f"section does not contain items or props, found only {item}")
    else:
        raise NotImplementedError(f"type {item['type']}, {item}")


def pydantic_from_template(
    template: Dict, parent_schema: Type[BaseModel], name: Optional[str] = None
) -> Type[BaseModel]:
    assert isinstance(parent_schema, type(BaseModel)), "pydantic_from_template"
    assert "items" in template, f"expected 'items' in template but got {list(template.keys())}"
    m = define_group_of_elements(template["items"], parent_schema)
    m = standardize_keys_in_dict(m, pascal_to_snake=True)
    if name is None:
        if "title" in template:
            name = template["title"]
        else:
            name = "new_model"
    name = name.replace(" ", "_").rstrip("_").split(".")[-1]
    return create_model(name, **m)
