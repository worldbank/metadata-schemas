from copy import copy
from typing import List, Optional

import pytest
from pydantic import BaseModel, ValidationError
from utils.utils import compare_pydantic_models, fill_in_pydantic_outline

from pydantic_schemas.metadata_manager import MetadataManager


@pytest.mark.parametrize(
    "metadata_name",
    ["document", "script", "microdata", "table", "indicators_db", "indicator", "video", "geospatial", "image"],
)
def test_metadata_by_name(tmpdir, metadata_name):
    mm = MetadataManager()
    assert metadata_name in mm.metadata_type_names

    for debug in [True, False]:
        mm.create_metadata_outline(metadata_name_or_class=metadata_name, debug=debug)

    # Write empty metadata
    filename = mm.write_metadata_outline_to_excel(
        metadata_name_or_class=metadata_name,
        filename=tmpdir.join(f"test_{metadata_name}_outline.xlsx"),
        title=metadata_name,
    )

    # Read the metadata back
    tmp = mm.read_metadata_from_excel(filename=filename)

    # Save the read metadata to a new file
    filename2 = tmpdir.join(f"test_{metadata_name}_save.xlsx")
    mm.save_metadata_to_excel(object=tmp, filename=filename2, title=metadata_name)

    for i in range(10):
        modl = mm.create_metadata_outline(metadata_name_or_class=metadata_name)
        fill_in_pydantic_outline(modl)

        # Write filled in metadata
        filename3 = tmpdir.join(f"test_{metadata_name}_{i}.xlsx")
        # filename3 = f"test_{metadata_name}_{i}.xlsx"
        mm.save_metadata_to_excel(object=modl, filename=filename3, title=metadata_name)

        # Read the metadata back
        actual = mm.read_metadata_from_excel(filename=filename3)
        compare_pydantic_models(modl, actual)
        # assert modl == actual, actual


@pytest.mark.parametrize(
    "metadata_name",
    ["document", "script", "microdata", "table", "timeseries_db", "indicator", "video", "geospatial", "image"],
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
    mm.read_metadata_from_excel(filename=filename_class)


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
        "image",
        "IMaGe",
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
        "image",
        "image",
    ]

    for inp, expected in zip(inputs, expecteds):
        actual = mm.standardize_metadata_name(inp)
        assert actual == expected, f"expected {expected} but got {actual}"

    with pytest.raises(ValueError):
        mm.standardize_metadata_name("Bad-name")


def test_write_read_and_save_for_templates(tmpdir):
    class Simple(BaseModel):
        a: str
        b: List[str]

    class Midlevel(BaseModel):
        c: Optional[str] = None
        d: Optional[List[Simple]]

    class TopLevel(BaseModel):
        e: Optional[Midlevel]
        f: Optional[int]

    mm = MetadataManager()
    filename1 = tmpdir.join(f"test_templates_1.xlsx")

    mm.write_metadata_outline_to_excel(TopLevel, filename=filename1, title="Outline Test")

    assert mm._get_metadata_name_from_excel_file(filename1) == "TopLevel"

    example = TopLevel(
        e=Midlevel(
            c="c_value",
            d=[
                Simple(a="a_value", b=["the", "quick", "brown", "fox"]),
                Simple(a="a_value_2", b=["jumped", "over", "the", "lazy", "dog"]),
            ],
        ),
        f=99,
    )

    filename2 = tmpdir.join(f"test_templates_2.xlsx")
    mm.save_metadata_to_excel(example, filename2)

    assert mm._get_metadata_name_from_excel_file(filename2) == "TopLevel"

    actual = mm.read_metadata_from_excel(filename2, TopLevel)
    assert actual == example
