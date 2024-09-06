import pytest

from pydantic_schemas.metadata_manager import MetadataManager


@pytest.mark.parametrize(
    "metadata_name", ["document", "script", "survey", "table", "timeseries_db", "timeseries", "video"]
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
    mm.create_metadata_outline(metadata_name_or_class=metadata_name)


@pytest.mark.parametrize(
    "metadata_name", ["document", "script", "survey", "table", "timeseries_db", "timeseries", "video"]
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
        "timeseries-db",
        "timeseries-db",
        "TimeSeries",
        "VIdeo",
    ]

    expecteds = [
        "document",
        "script",
        "survey",
        "survey",
        "survey",
        "survey",
        "table",
        "timeseries_db",
        "timeseries_db",
        "timeseries",
        "video",
    ]

    for inp, expected in zip(inputs, expecteds):
        actual = mm.standardize_metadata_name(inp)
        assert actual == expected, f"expected {expected} but got {actual}"

    with pytest.raises(NotImplementedError):
        mm.standardize_metadata_name("Image")

    with pytest.raises(ValueError):
        mm.standardize_metadata_name("Bad-name")
