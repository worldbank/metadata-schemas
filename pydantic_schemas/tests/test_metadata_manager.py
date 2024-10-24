import random
import string
from copy import copy

import pytest
from pydantic import BaseModel, ValidationError

from pydantic_schemas.metadata_manager import MetadataManager


# Function to generate a random 4-character string
def random_string(length=4):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Recursive function to traverse and replace Nones or empty strings
def replace_nones_with_random(model: BaseModel):
    for field_name, field_value in model.__dict__.items():
        # If the field is None or an empty string, replace it with a random string
        if field_value is None or field_value == "":
            try:
                setattr(model, field_name, random_string())
            except ValidationError:
                continue
        # If the field is another Pydantic model, recursively apply the function
        elif isinstance(field_value, BaseModel):
            replace_nones_with_random(field_value)
        # If the field is a list of models, apply the function to each item
        elif isinstance(field_value, list):
            n_elements = random.choices([1, 2, 3])[0]
            non_null_values = [random.random() < 0.7 for _ in range(n_elements)]
            if len(field_value) == 0:
                try:
                    setattr(
                        model, field_name, [random_string() if non_null_values[i] else None for i in range(n_elements)]
                    )
                except ValidationError:
                    continue
            elif isinstance(field_value[0], BaseModel):
                try:
                    setattr(
                        model,
                        field_name,
                        [
                            replace_nones_with_random(copy(field_value[0])) if non_null_values[i] else None
                            for i in range(n_elements)
                        ],
                    )
                except ValidationError:
                    continue
            else:
                continue
            # for item in field_value:
            #     if isinstance(item, BaseModel):
            #         replace_nones_with_random(item)
        # If the field is a dict, apply the function to each value
        elif isinstance(field_value, dict):
            for key, item in field_value.items():
                if isinstance(item, BaseModel):
                    replace_nones_with_random(item)


# Recursive function to compare two Pydantic models
def compare_pydantic_models(model1: BaseModel, model2: BaseModel) -> bool:
    # First, check if the two models are of the same type
    if type(model1) is not type(model2):
        assert False

    if not hasattr(model1, "model_fields"):
        assert model1 == model2

    # Traverse through the fields of the model
    for field_name in model1.model_fields:
        value1 = getattr(model1, field_name)
        value2 = getattr(model2, field_name)

        # If values are different, return False
        if value1 != value2:
            # If both are BaseModel instances, compare recursively
            if isinstance(value1, BaseModel) and isinstance(value2, BaseModel):
                if not compare_pydantic_models(value1, value2):
                    assert False, field_name
            # If both are lists, compare their elements
            elif isinstance(value1, list) and isinstance(value2, list):
                assert len(value1) == len(value2)
                for v1, v2 in zip(value1, value2):
                    if isinstance(v1, BaseModel) and isinstance(v2, BaseModel):
                        if not compare_pydantic_models(v1, v2):
                            assert False, field_name
                    elif v1 != v2:
                        assert False, field_name
            # If both are dicts, compare their items
            elif isinstance(value1, dict) and isinstance(value2, dict):
                assert value1.keys() == value2.keys()
                for key in value1:
                    if isinstance(value1[key], BaseModel) and isinstance(value2[key], BaseModel):
                        if not compare_pydantic_models(value1[key], value2[key]):
                            assert False, field_name
                    else:
                        assert value1[key] == value2[key], field_name
            else:
                assert value1 == value2, field_name  # For other types, if they are not equal, return False

    return True  # All fields are equal


@pytest.mark.parametrize(
    "metadata_name", ["document", "script", "microdata", "table", "indicators_db", "indicator", "video", "geospatial"]
)
def test_metadata_by_name(tmpdir, metadata_name):
    mm = MetadataManager()
    assert metadata_name in mm.metadata_type_names

    for debug in [True, False]:
        mm.create_metadata_outline(metadata_name_or_class=metadata_name, debug=debug)

    # Write empty metadata
    filename = mm.write_metadata_outline_to_excel(
        metadata_name_or_class=metadata_name, filename=tmpdir.join(f"test_{metadata_name}.xlsx"), title=metadata_name
    )

    # Read the metadata back
    tmp = mm.read_metadata_from_excel(filename=filename)

    # Save the read metadata to a new file
    filename2 = tmpdir.join(f"test_{metadata_name}_2.xlsx")
    mm.save_metadata_to_excel(metadata_name_or_class=metadata_name, object=tmp, filename=filename2, title=metadata_name)

    # make an outline object
    modl = mm.create_metadata_outline(metadata_name_or_class=metadata_name)
    replace_nones_with_random(modl)

    # Write filled in metadata
    filename3 = tmpdir.join(f"test_{metadata_name}_3.xlsx")
    # filename3 = f"test_{metadata_name}_3.xlsx"
    mm.save_metadata_to_excel(
        metadata_name_or_class=metadata_name, object=modl, filename=filename3, title=metadata_name
    )

    # Read the metadata back
    actual = mm.read_metadata_from_excel(filename=filename3)
    compare_pydantic_models(modl, actual)
    # assert modl == actual, actual


@pytest.mark.parametrize(
    "metadata_name", ["document", "script", "microdata", "table", "timeseries_db", "indicator", "video", "geospatial"]
)
def test_metadata_by_class(tmpdir, metadata_name):
    mm = MetadataManager()

    metadata_class = mm.metadata_class_from_name(metadata_name=metadata_name)

    # outline from class
    mm.create_metadata_outline(metadata_name_or_class=metadata_class)

    # write and read from class
    filename_class = mm.write_metadata_outline_to_excel(
        metadata_name_or_class=metadata_class,
        filename=tmpdir.join(f"test_class_{metadata_name}.xlsx"),
        title=metadata_name,
    )
    mm.read_metadata_from_excel(filename=filename_class, metadata_class=metadata_class)


def test_standardize_metadata_name():
    mm = MetadataManager()
    inputs = [
        "Document",
        "SCRIPT",
        "survey",
        "survey-microdata",
        "survey microdata",
        "microdata",
        "table",
        "indicators-db",
        "timeseries-db",
        "INdicator",
        "timeseries",
        "VIdeo",
    ]

    expecteds = [
        "document",
        "script",
        "microdata",
        "microdata",
        "microdata",
        "microdata",
        "table",
        "indicators_db",
        "indicators_db",
        "indicator",
        "indicator",
        "video",
    ]

    for inp, expected in zip(inputs, expecteds):
        actual = mm.standardize_metadata_name(inp)
        assert actual == expected, f"expected {expected} but got {actual}"

    with pytest.raises(NotImplementedError):
        mm.standardize_metadata_name("Image")

    with pytest.raises(ValueError):
        mm.standardize_metadata_name("Bad-name")
