import pytest

from pydantic_schemas.metadata_manager import MetadataManager


@pytest.mark.parametrize(
    "metadata_name", ["document", "script", "survey", "table", "timeseries_db", "timeseries", "video"]
)
def test_metadata(tmpdir, metadata_name):
    ei = MetadataManager()

    # Write empty metadata
    filename = ei.write_metadata_outline_to_excel(
        metadata_name_or_class=metadata_name, filename=tmpdir.join(f"test_{metadata_name}.xlsx"), title=metadata_name
    )

    # Read the metadata back
    tmp = ei.read_metadata_from_excel(filename=filename)

    # Save the read metadata to a new file
    filename2 = tmpdir.join(f"test_{metadata_name}_2.xlsx")
    ei.save_metadata_to_excel(metadata_name_or_class=metadata_name, object=tmp, filename=filename2, title=metadata_name)

    # make an outline object
    ei.create_metadata_outline(metadata_name_or_class=metadata_name)
