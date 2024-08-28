import pytest

from pydantic_schemas.schema_interface import SchemaInterface


@pytest.mark.parametrize(
    "metadata_type", ["document", "script", "series", "survey", "table", "timeseries_db", "timeseries", "video"]
)
def test_metadata(tmpdir, metadata_type):
    ei = SchemaInterface()

    # Write empty metadata
    filename = ei.write_outline_metadata_to_excel(
        metadata_type=metadata_type, filename=tmpdir.join(f"test_{metadata_type}.xlsx"), title=metadata_type
    )

    # Read the metadata back
    tmp = ei.read_metadata_from_excel(filename=filename)

    # Save the read metadata to a new file
    filename2 = tmpdir.join(f"test_{metadata_type}_2.xlsx")
    ei.save_metadata_to_excel(metadata_type=metadata_type, object=tmp, filename=filename2, title=metadata_type)

    # make an outline object
    ei.type_to_outline(metadata_type=metadata_type)
