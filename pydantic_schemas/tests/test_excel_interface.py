import pytest

from pydantic_schemas.excel_interface import ExcelInterface


@pytest.mark.parametrize(
    "name", ["document", "script", "series", "survey_microdata", "table", "timeseries_db", "timeseries", "video"]
)
def test_metadata(tmpdir, name):
    ei = ExcelInterface()
    filename = tmpdir.join(f"test_{name}.xlsx")

    # Write empty metadata
    write_method = getattr(ei, f"write_empty_metadata_to_excel_for_{name}")
    write_method(filename=filename)

    # Read the metadata back
    read_method = getattr(ei, f"read_metadata_excel_of_{name}")
    tmp = read_method(filename)

    # Save the read metadata to a new file
    filename2 = tmpdir.join(f"test_{name}_2.xlsx")
    save_method = getattr(ei, f"save_metadata_to_excel_for_{name}")
    save_method(object=tmp, filename=filename2)


# def test_document(tmpdir):
#     ei = ExcelInterface()
#     filename = tmpdir.join(f"test_document.xlsx")
#     # filename = "test_document.xlsx"
#     ei.write_empty_metadata_to_excel_for_document(filename=filename)
#     tmp = ei.read_metadata_excel_of_document(filename)
#     filename2 = tmpdir.join(f"test_document2")
#     # filename2 = "test_document2.xlsx"
#     ei.save_metadata_to_excel_for_document(filename=filename2, object=tmp)


# # ei.write_empty_metadata_to_excel_for_script()
# # ei.read_metadata_excel_of_script("Script_metadata.xlsx")
# # ei.write_empty_metadata_to_excel_for_series()
# # ei.read_metadata_excel_of_series("Series_metadata.xlsx")
# # ei.write_empty_metadata_to_excel_for_survey_microdata()
# # ei.read_metadata_excel_of_survey_microdata("Survey_microdata_metadata.xlsx")
# # ei.write_empty_metadata_to_excel_for_table()
# # ei.read_metadata_excel_of_table("Table_metadata.xlsx")
# # ei.write_empty_metadata_to_excel_for_timeseries_db()
# # ei.read_metadata_excel_of_timeseries_db("Timeseries_DB_metadata.xlsx")
# # ei.write_empty_metadata_to_excel_for_timeseries()
# # ei.read_metadata_excel_of_timeseries("Timeseries_metadata.xlsx")
# # ei.write_empty_metadata_to_excel_for_video()
# # ei.read_metadata_excel_of_video("Video_metadata.xlsx")
