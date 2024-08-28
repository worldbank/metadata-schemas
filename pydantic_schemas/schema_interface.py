from typing import Dict, Optional, Type

from openpyxl import load_workbook
from pydantic import BaseModel

from . import (  # image_schema,
    document_schema,
    geospatial_schema,
    microdata_schema,
    script_schema,
    table_schema,
    timeseries_db_schema,
    timeseries_schema,
    video_schema,
)
from .utils.excel_to_pydantic import excel_doc_to_pydantic, excel_single_sheet_to_pydantic
from .utils.pydantic_to_excel import write_across_many_sheets, write_to_single_sheet
from .utils.quick_start import make_skeleton
from .utils.template_to_pydantic import pydantic_from_template
from .utils.utils import standardize_keys_in_dict


class SchemaInterface:
    """
    Interface with Excel for creating, saving and updating metadata for various types:
      documents, scripts, survey, table, timeseries, timeseries_db, video

    Retrieve pydantic model definitions for each metadata type
    """

    _TYPE_TO_SCHEMA = {
        "document": document_schema.ScriptSchemaDraft,
        "geospatial": geospatial_schema.GeospatialSchema,
        # "image":image_schema.ImageDataTypeSchema,
        "script": script_schema.ResearchProjectSchemaDraft,
        "survey": microdata_schema.MicrodataSchema,
        "table": table_schema.Model,
        "timeseries": timeseries_schema.TimeseriesSchema,
        "timeseries_db": timeseries_db_schema.TimeseriesDatabaseSchema,
        "video": video_schema.Model,
    }

    _TYPE_TO_WRITER = {
        "document": write_across_many_sheets,
        # "geospatial":,
        # "image":,
        "script": write_across_many_sheets,
        "survey": write_across_many_sheets,
        "table": write_across_many_sheets,
        "timeseries": write_across_many_sheets,
        "timeseries_db": write_to_single_sheet,  # one sheet
        "video": write_to_single_sheet,  # one sheet
    }

    _TYPE_TO_READER = {
        "document": excel_doc_to_pydantic,
        # "geospatial":,
        # "image":,
        "script": excel_doc_to_pydantic,
        "survey": excel_doc_to_pydantic,
        "table": excel_doc_to_pydantic,
        "timeseries": excel_doc_to_pydantic,
        "timeseries_db": excel_single_sheet_to_pydantic,  # one sheet
        "video": excel_single_sheet_to_pydantic,  # one sheet
    }

    def get_metadata_class(self, metadata_type: str):
        metadata_type = self.standardize_metadata_type_name(metadata_type)
        schema = self._TYPE_TO_SCHEMA[metadata_type]
        return schema

    def template_to_pydantic(
        self, template: Dict, parent_schema_type: str, name: Optional[str] = None
    ) -> Type[BaseModel]:
        schema = self.get_metadata_class(parent_schema_type)

        return pydantic_from_template(template, schema, name)

    def list_metadata_types(self):
        return list(self._TYPE_TO_SCHEMA.keys())

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
                        new_dict[key] = SchemaInterface._merge_dicts(base_value, update_value)
                    else:
                        new_dict[key] = base_value
                elif isinstance(base_value, list):
                    if isinstance(update_value, list) and len(update_value) > 0:
                        new_list = []
                        min_length = min(len(base_value), len(update_value))
                        for i in range(min_length):
                            if isinstance(base_value[i], dict):
                                if isinstance(update_value[i], dict):
                                    new_list.append(SchemaInterface._merge_dicts(base_value[i], update_value[i]))
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

    def standardize_metadata_type_name(self, metadata_type: str) -> str:
        metadata_type = metadata_type.lower()
        metadata_type = metadata_type.replace("-", "_")
        if metadata_type == "microdata" or metadata_type == "survey_microdata":
            metadata_type = "survey"
        self._raise_if_unsupported_metadata_type(metadata_type=metadata_type)
        return metadata_type

    def type_to_outline(self, metadata_type: str, debug: bool = False) -> BaseModel:
        schema = self.get_metadata_class(metadata_type)
        skeleton_object = make_skeleton(schema, debug=debug)
        return skeleton_object

    def write_outline_metadata_to_excel(
        self, metadata_type: str, filename: Optional[str] = None, title: Optional[str] = None
    ) -> str:
        """
        Create an Excel file formatted for writing the given metadata_type metadata.

        Args:
            metadata_type (str): the name of a supported metadata type, currently:
                    document, script, series, survey, table, timeseries, timeseries_DB, video
                Currently not supported:
                    geospatial, image
            filename (Optional[str]): The path to the Excel file. If None, defaults to {metadata_type}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. If None, defaults to '{metadata_type} Metadata'

        Returns:
            str: filename of metadata file

        Outputs:
            An Excel file into which metadata can be entered
        """
        metadata_type = self.standardize_metadata_type_name(metadata_type)
        if metadata_type == "geospatial":
            raise NotImplementedError("Geospatial schema contains an infinite loop so cannot be written to excel")

        if filename is None:
            filename = f"{metadata_type}_metadata.xlsx"
        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        if title is None:
            title = f"{metadata_type.capitalize()} Metadata"
        skeleton_object = self.type_to_outline(metadata_type, debug=False)
        writer = self._TYPE_TO_WRITER[metadata_type]
        writer(filename, skeleton_object, metadata_type, title)
        return filename

    def save_metadata_to_excel(
        self, metadata_type: str, object: BaseModel, filename: Optional[str] = None, title: Optional[str] = None
    ) -> str:
        """
        Save an Excel document of the given metadata_type metadata.

        Args:
            metadata_type (str): the name of a supported metadata type, currently:
                    document, script, series, survey, table, timeseries, timeseries_db, video
                Currently not supported:
                    geospatial, image
            object (BaseModel): The pydantic object to save to the Excel file.
            filename (Optional[str]): The path to the Excel file. Defaults to {name}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. Defaults to '{name} Metadata'

        Returns:
            str: filename of metadata file

        Outputs:
            An Excel file containing the metadata from the pydantic object. This file can be updated as needed.
        """
        metadata_type = self.standardize_metadata_type_name(metadata_type)
        if metadata_type == "geospatial":
            raise NotImplementedError("Geospatial schema contains an infinite loop so cannot be written to excel")

        if filename is None:
            filename = f"{metadata_type}_metadata.xlsx"
        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        if title is None:
            title = f"{metadata_type.capitalize()} Metadata"

        skeleton_object = self.type_to_outline(metadata_type=metadata_type, debug=False)
        combined_dict = self._merge_dicts(
            skeleton_object.model_dump(),
            object.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True),
        )
        combined_dict = standardize_keys_in_dict(combined_dict)

        schema = self._TYPE_TO_SCHEMA[metadata_type]
        new_ob = schema(**combined_dict)

        writer = self._TYPE_TO_WRITER[metadata_type]
        writer(filename, new_ob, metadata_type, title)
        return filename

    @staticmethod
    def _get_metadata_type_from_excel_file(filename: str) -> str:
        error_message = "Improperly formatted Excel file for metadata"
        workbook = load_workbook(filename)
        # Select the 'metadata' sheet
        try:
            sheet = workbook["metadata"]
            # Get the value of cell C1
            type_info = sheet["C1"].value
        except KeyError:
            raise ValueError(f"Sheet 'metadata' not found. {error_message}")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}")
        finally:
            # Close the workbook
            workbook.close()

        if not type_info or not isinstance(type_info, str):
            raise ValueError(f"Cell C3 is empty or not a string. {error_message}")

        cell_values = type_info.split(" ")

        if len(cell_values) < 3 or cell_values[1] != "type" or cell_values[2] != "metadata":
            raise ValueError(f"Cell C3 is improperly formatted. {error_message}")

        return cell_values[0]

    def read_metadata_from_excel(self, filename: str) -> BaseModel:
        """
        Read in metadata_type metadata from an appropriately formatted Excel file as a pydantic object.

        Args:
            filename (str): The path to the Excel file.

        Returns:
            BaseModel: a pydantic object containing the metadata from the file
        """
        metadata_type = self._get_metadata_type_from_excel_file(filename)
        metadata_type = self.standardize_metadata_type_name(metadata_type)
        schema = self._TYPE_TO_SCHEMA[metadata_type]
        reader = self._TYPE_TO_READER[metadata_type]
        read_object = reader(filename, schema)
        skeleton_object = self.type_to_outline(metadata_type=metadata_type, debug=False)

        read_object_dict = read_object.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)
        combined_dict = self._merge_dicts(
            skeleton_object.model_dump(),
            read_object_dict,
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        schema = self._TYPE_TO_SCHEMA[metadata_type]
        new_ob = schema(**combined_dict)
        return new_ob

    def _raise_if_unsupported_metadata_type(self, metadata_type: str):
        """
        If the type is specifically unsupported - geospatial or image - a NotImplementedError is raised
        If the type is simply unknown then a ValueError is raised.
        """
        if metadata_type == "image":
            raise NotImplementedError("Due to an issue with image metadata schema definition causing __root__ errors")
        if metadata_type not in self._TYPE_TO_SCHEMA.keys():
            raise ValueError(f"'{metadata_type}' not supported. Must be: {list(self._TYPE_TO_SCHEMA.keys())}")
