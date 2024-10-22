from copy import copy
from typing import Dict, List, Optional, Type, Union

from openpyxl import load_workbook
from pydantic import BaseModel

from . import (  # image_schema,
    document_schema,
    geospatial_schema,
    indicator_schema,
    indicators_db_schema,
    microdata_schema,
    resource_schema,
    script_schema,
    table_schema,
    video_schema,
)
from .utils.excel_to_pydantic import excel_doc_to_pydantic, excel_single_sheet_to_pydantic
from .utils.pydantic_to_excel import write_across_many_sheets, write_to_single_sheet
from .utils.quick_start import make_skeleton
from .utils.utils import merge_dicts, standardize_keys_in_dict


class MetadataManager:
    """
    Interface with Excel for creating, saving and updating metadata for various types:
      document, indicator, indicators_db, microdata, resource, script, table, video

    Retrieve pydantic model definitions for each metadata type
    """

    _TYPE_TO_SCHEMA = {
        "document": document_schema.ScriptSchemaDraft,
        "geospatial": geospatial_schema.GeospatialSchema,
        # "image":image_schema.ImageDataTypeSchema,
        "resource": resource_schema.Model,
        "script": script_schema.ResearchProjectSchemaDraft,
        "microdata": microdata_schema.MicrodataSchema,
        "table": table_schema.Model,
        "indicator": indicator_schema.TimeseriesSchema,
        "indicators_db": indicators_db_schema.TimeseriesDatabaseSchema,
        "video": video_schema.Model,
    }

    _TYPE_TO_WRITER = {
        "document": write_across_many_sheets,
        "geospatial": write_across_many_sheets,
        # "image":,
        "resource": write_to_single_sheet,
        "script": write_across_many_sheets,
        "microdata": write_across_many_sheets,
        "table": write_across_many_sheets,
        "indicator": write_across_many_sheets,
        "indicators_db": write_to_single_sheet,  # one sheet
        "video": write_to_single_sheet,  # one sheet
    }

    _TYPE_TO_READER = {
        "document": excel_doc_to_pydantic,
        "geospatial": excel_doc_to_pydantic,
        # "image":,
        "resource": excel_single_sheet_to_pydantic,
        "script": excel_doc_to_pydantic,
        "microdata": excel_doc_to_pydantic,
        "table": excel_doc_to_pydantic,
        "indicator": excel_doc_to_pydantic,
        "indicators_db": excel_single_sheet_to_pydantic,  # one sheet
        "video": excel_single_sheet_to_pydantic,  # one sheet
    }

    def metadata_class_from_name(self, metadata_name: str) -> Type[BaseModel]:
        metadata_name = self.standardize_metadata_name(metadata_name)
        schema = self._TYPE_TO_SCHEMA[metadata_name]
        return copy(schema)

    @property
    def metadata_type_names(self) -> List[str]:
        return list(self._TYPE_TO_SCHEMA.keys())

    def standardize_metadata_name(self, metadata_name: str) -> str:
        metadata_name = metadata_name.lower()
        metadata_name = metadata_name.replace("-", "_").replace(" ", "_")
        if metadata_name == "survey" or metadata_name == "survey_microdata":
            metadata_name = "microdata"
        elif metadata_name == "timeseries":
            metadata_name = "indicator"
        elif metadata_name == "timeseries_db":
            metadata_name = "indicators_db"
        self._raise_if_unsupported_metadata_name(metadata_name=metadata_name)
        return metadata_name

    def create_metadata_outline(
        self, metadata_name_or_class: Union[str, Type[BaseModel]], debug: bool = False
    ) -> BaseModel:
        if isinstance(metadata_name_or_class, str):
            schema = self.metadata_class_from_name(metadata_name_or_class)
        else:
            schema = metadata_name_or_class
        skeleton_object = make_skeleton(schema, debug=debug)
        return skeleton_object

    def write_metadata_outline_to_excel(
        self,
        metadata_name_or_class: Union[str, Type[BaseModel]],
        filename: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        Create an Excel file formatted for writing the given metadata_name metadata.

        Args:
            metadata_name_or_class (str or type[BaseModel]): the name of a supported metadata type, currently:
                    document, indicator, indicators_db, microdata, resource, script, table, video
                Currently not supported:
                    geospatial, image
                If passed as a BaseModel type, for instance this is what you would do with a template, then the writer
                    defaults to a single page.
            filename (Optional[str]): The path to the Excel file. If None, defaults to {metadata_name}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. If None, defaults to '{metadata_name} Metadata'

        Returns:
            str: filename of metadata file

        Outputs:
            An Excel file into which metadata can be entered
        """
        if isinstance(metadata_name_or_class, str):
            metadata_name = self.standardize_metadata_name(metadata_name_or_class)
            # if metadata_name == "geospatial":
            # raise NotImplementedError("Geospatial schema contains an infinite loop so cannot be written to excel")
            skeleton_object = self.create_metadata_outline(metadata_name, debug=False)
            writer = self._TYPE_TO_WRITER[metadata_name]
            if filename is None:
                filename = f"{metadata_name}_metadata.xlsx"
            if title is None:
                title = f"{metadata_name.capitalize()} Metadata"
        else:
            skeleton_object = make_skeleton(metadata_name_or_class, debug=False)
            writer = write_to_single_sheet
            metadata_name = metadata_name_or_class.model_json_schema()["title"]
            if filename is None:
                filename = f"{metadata_name}_metadata.xlsx"
            if title is None:
                title = f"{metadata_name.capitalize()} Metadata"

        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        writer(filename, skeleton_object, metadata_name, title)
        return filename

    def save_metadata_to_excel(
        self,
        metadata_name_or_class: Union[str, Type[BaseModel]],
        object: BaseModel,
        filename: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        Save an Excel document of the given metadata object.

        Args:
            metadata_name_or_class (str or type[BaseModel]): the name of a supported metadata type, currently:
                    document, indicator, indicators_db, microdata, resource, script, table, video
                Currently not supported:
                    geospatial, image
                If passed as a BaseModel type, for instance this is what you would do with a template, then the writer defaults to a single page.
            object (BaseModel): The pydantic object to save to the Excel file.
            filename (Optional[str]): The path to the Excel file. Defaults to {name}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. Defaults to '{name} Metadata'

        Returns:
            str: filename of metadata file

        Outputs:
            An Excel file containing the metadata from the pydantic object. This file can be updated as needed.
        """
        if isinstance(metadata_name_or_class, str):
            metadata_name = self.standardize_metadata_name(metadata_name_or_class)
            # if metadata_name == "geospatial":
            # raise NotImplementedError("Geospatial schema contains an infinite loop so cannot be written to excel")
            schema = self.metadata_class_from_name(metadata_name)
            writer = self._TYPE_TO_WRITER[metadata_name]
        else:
            metadata_name = metadata_name_or_class.model_json_schema()["title"]
            schema = metadata_name_or_class
            writer = write_to_single_sheet
        skeleton_object = self.create_metadata_outline(metadata_name_or_class=metadata_name_or_class, debug=False)

        if filename is None:
            filename = f"{metadata_name}_metadata.xlsx"
        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        if title is None:
            title = f"{metadata_name.capitalize()} Metadata"

        combined_dict = merge_dicts(
            skeleton_object.model_dump(),
            object.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True),
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        new_ob = schema(**combined_dict)

        # writer = self._TYPE_TO_WRITER[metadata_name]
        writer(filename, new_ob, metadata_name, title)
        return filename

    @staticmethod
    def _get_metadata_name_from_excel_file(filename: str) -> str:
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

    def read_metadata_from_excel(self, filename: str, metadata_class: Optional[Type[BaseModel]] = None) -> BaseModel:
        """
        Read in metadata from an appropriately formatted Excel file as a pydantic object.
        If using standard metadata types (document, indicator, indicators_db, microdata, resource, script, table, video) then there is no need to pass in the metadata_class. But if using a template, then the class must be provided.

        Args:
            filename (str): The path to the Excel file.
            metadata_class (Optional type of BaseModel): A pydantic class type correspondong to the type used to write the Excel file

        Returns:
            BaseModel: a pydantic object containing the metadata from the file
        """
        metadata_name = self._get_metadata_name_from_excel_file(filename)
        try:
            metadata_name = self.standardize_metadata_name(metadata_name)
            schema = self._TYPE_TO_SCHEMA[metadata_name]
            reader = self._TYPE_TO_READER[metadata_name]
        except ValueError as e:
            if metadata_class is None:
                raise ValueError(
                    f"'{metadata_name}' not supported. Must be: {list(self._TYPE_TO_SCHEMA.keys())} or try passing in the metadata_class"
                ) from e
            schema = metadata_class
            reader = excel_single_sheet_to_pydantic
        read_object = reader(filename, schema)

        skeleton_object = self.create_metadata_outline(metadata_name_or_class=schema, debug=False)

        read_object_dict = read_object.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)
        combined_dict = merge_dicts(
            skeleton_object.model_dump(),
            read_object_dict,
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        new_ob = schema(**combined_dict)
        return new_ob

    def _raise_if_unsupported_metadata_name(self, metadata_name: str):
        """
        If the type is specifically unsupported - geospatial or image - a NotImplementedError is raised
        If the type is simply unknown then a ValueError is raised.
        """
        if metadata_name == "image":
            raise NotImplementedError("Due to an issue with image metadata schema definition causing __root__ errors")
        if metadata_name not in self._TYPE_TO_SCHEMA.keys():
            raise ValueError(f"'{metadata_name}' not supported. Must be: {list(self._TYPE_TO_SCHEMA.keys())}")
