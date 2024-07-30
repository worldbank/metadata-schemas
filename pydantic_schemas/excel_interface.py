from pydantic import BaseModel

from pydantic_schemas.definitions.document_schema import ScriptSchemaDraft
from pydantic_schemas.definitions.microdata_schema import MicrodataSchema
from pydantic_schemas.definitions.script_schema import ResearchProjectSchemaDraft
from pydantic_schemas.definitions.series_schema import Series
from pydantic_schemas.definitions.table_schema import Model as TableModel
from pydantic_schemas.definitions.timeseries_db_schema import TimeseriesDatabaseSchema
from pydantic_schemas.definitions.timeseries_schema import TimeseriesSchema
from pydantic_schemas.definitions.video_schema import Model as VideoModel
from pydantic_schemas.utils.excel_to_pydantic import excel_doc_to_pydantic, excel_single_sheet_to_pydantic
from pydantic_schemas.utils.pydantic_to_excel import write_across_many_sheets, write_to_single_sheet
from pydantic_schemas.utils.quick_start import make_skeleton
from pydantic_schemas.utils.utils import standardize_keys_in_dict


class ExcelInterface:
    """
    An Excel interface creating, saving and updating metadata for various types:
      documents, scripts, series, survey_microdata, table, timeseries, timeseries_db, video

    For each of these types there are three functions:

      write_empty_metadata_to_excel_for_<type>
      save_metadata_to_excel_for_<type>
      read_metadata_excel_of_<type>

    write_empty_metadata_to_excel_for_<type>:
        Args:
            filename (str): The path to the Excel file.
            title (str): The title for the Excel sheet.

        Outputs:
            An Excel file into which metadata can be entered

    save_metadata_to_excel_for_<type>:
        Args:
            filename (str): The path to the Excel file.
            title (str): The title for the Excel sheet.
            object (BaseModel): The pydantic object to save to the Excel file.

        Outputs:
            An Excel file containing the metadata from the pydantic object. The file can be updated as needed.

    read_metadata_excel_of_<type>:
        Args:
            filename (str): The path to the Excel file.

        Returns:
            BaseModel: a pydantic object containing the metadata from the file
    """

    _NAME_TO_TYPE_WRITER_READER = {
        "Document": (ScriptSchemaDraft, write_across_many_sheets, excel_doc_to_pydantic),
        # "Geospatial":GeospatialSchema,
        # "Image":ImageDataTypeSchema,
        "Script": (ResearchProjectSchemaDraft, write_across_many_sheets, excel_doc_to_pydantic),
        "Series": (Series, write_to_single_sheet, excel_single_sheet_to_pydantic),  # should be one sheet
        "Survey_microdata": (MicrodataSchema, write_across_many_sheets, excel_doc_to_pydantic),
        "Table": (TableModel, write_across_many_sheets, excel_doc_to_pydantic),
        "Timeseries": (TimeseriesSchema, write_across_many_sheets, excel_doc_to_pydantic),
        "Timeseries_DB": (
            TimeseriesDatabaseSchema,
            write_to_single_sheet,
            excel_single_sheet_to_pydantic,
        ),  # could be one sheet
        "Video": (VideoModel, write_to_single_sheet, excel_single_sheet_to_pydantic),  # could be one sheet
    }

    @staticmethod
    def _merge_dicts(base, update):
        if len(update) == 0:
            return base
        new_dict = {}
        for key, base_value in base.items():
            if key in update:
                update_value = update[key]
                if isinstance(base_value, dict):
                    if isinstance(update_value, dict) and len(update_value) > 0:
                        new_dict[key] = ExcelInterface._merge_dicts(base_value, update_value)
                    else:
                        new_dict[key] = base_value
                elif isinstance(base_value, list):
                    if isinstance(update_value, list) and len(update_value) > 0:
                        new_list = []
                        min_length = min(len(base_value), len(update_value))
                        for i in range(min_length):
                            if isinstance(base_value[i], dict):
                                if isinstance(update_value[i], dict):
                                    new_list.append(ExcelInterface._merge_dicts(base_value[i], update_value[i]))
                                else:
                                    new_list.append(base_value[i])
                            else:
                                new_list.append(update_value[i])
                        new_list.extend(update_value[min_length:])
                        new_dict[key] = new_list
                    else:
                        new_dict[key] = base_value
                else:
                    if update_value is not None:
                        new_dict[key] = update_value
                    else:
                        new_dict[key] = base_value
            else:
                new_dict[key] = base_value
        return new_dict

    def _write_empty_excel(self, name: str, filename: str, title: str):
        assert (
            name in self._NAME_TO_TYPE_WRITER_READER
        ), f"{name} not found in {list(self._NAME_TO_TYPE_WRITER_READER.keys())}"
        schema = self._NAME_TO_TYPE_WRITER_READER[name][0]
        writer = self._NAME_TO_TYPE_WRITER_READER[name][1]
        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        ob = make_skeleton(schema, debug=False)
        writer(filename, ob, title)

    def _save_to_excel(self, name: str, filename: str, title: str, object: BaseModel):
        assert (
            name in self._NAME_TO_TYPE_WRITER_READER
        ), f"{name} not found in {list(self._NAME_TO_TYPE_WRITER_READER.keys())}"
        schema = self._NAME_TO_TYPE_WRITER_READER[name][0]
        writer = self._NAME_TO_TYPE_WRITER_READER[name][1]
        skeleton_object = make_skeleton(schema, debug=False)

        combined_dict = self._merge_dicts(
            skeleton_object.model_dump(),
            object.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True),
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        new_ob = schema(**combined_dict)
        writer(filename, new_ob, title)

    def _read_excel(self, name: str, filename: str) -> BaseModel:
        assert (
            name in self._NAME_TO_TYPE_WRITER_READER
        ), f"{name} not found in {list(self._NAME_TO_TYPE_WRITER_READER.keys())}"
        schema = self._NAME_TO_TYPE_WRITER_READER[name][0]
        reader = self._NAME_TO_TYPE_WRITER_READER[name][2]
        read_object = reader(filename, schema)
        skeleton_object = make_skeleton(schema, debug=False)

        combined_dict = self._merge_dicts(
            skeleton_object.model_dump(),
            read_object.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True),
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        new_ob = schema(**combined_dict)
        return new_ob

    # Method to generate write and read methods for all types
    def __init__(self):
        for name in self._NAME_TO_TYPE_WRITER_READER.keys():
            self._generate_methods(name)

    def _generate_methods(self, name):
        def write_skeleton_method(filename=f"{name}_metadata.xlsx", title=f"{name} Metadata"):
            self._write_empty_excel(name, filename=filename, title=title)

        write_skeleton_method.__name__ = f"write_empty_metadata_to_excel_for_{name.lower()}"
        write_skeleton_doc_template = """
        Create an Excel document formatted for writing {name} metadata.

        Args:
            filename (str): The path to the Excel file.
            title (str): The title for the Excel sheet.

        Outputs:
            An Excel file into which metadata can be entered
        """
        write_skeleton_method.__doc__ = write_skeleton_doc_template.format(name=name)
        setattr(self, write_skeleton_method.__name__, write_skeleton_method)

        def save_to_excel_method(object, filename=f"{name}_metadata.xlsx", title=f"{name} Metadata"):
            self._save_to_excel(name, filename=filename, title=title, object=object)

        save_to_excel_method.__name__ = f"save_metadata_to_excel_for_{name.lower()}"
        save_doc_template = """
        Save an Excel document of the given {name} metadata.

        Args:
            filename (str): The path to the Excel file.
            title (str): The title for the Excel sheet.
            object (BaseModel): The pydantic object to save to the Excel file.

        Outputs:
            An Excel file containing the metadata from the pydantic object. This file can be updated as needed.
        """
        save_to_excel_method.__doc__ = save_doc_template.format(name=name)
        setattr(self, save_to_excel_method.__name__, save_to_excel_method)

        def read_method(filename):
            return self._read_excel(name, filename=filename)

        read_method.__name__ = f"read_metadata_excel_of_{name.lower()}"
        read_doc_template = """
        Read in {name} metadata from an appropriately formatted Excel file as a pydantic object.

        Args:
            filename (str): The path to the Excel file.
        
        Returns:
            BaseModel: a pydantic object containing the metadata from the file
        """
        read_method.__doc__ = read_doc_template.format(name=name)
        setattr(self, read_method.__name__, read_method)
