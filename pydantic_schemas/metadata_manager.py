import importlib.metadata
from copy import copy
from typing import Dict, List, Optional, Type, Union

from openpyxl import load_workbook
from pydantic import BaseModel

from . import (
    document_schema,
    geospatial_schema,
    image_schema,
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

__version__ = importlib.metadata.version("metadataschemas")


class MetadataManager:
    """
    Interface with Excel for creating, saving and updating metadata for various types:
      document, geospatial, image, indicator, indicators_db, microdata, resource, script, table, video

    Retrieve pydantic model definitions for each metadata type
    """

    _TYPE_TO_SCHEMA = {
        "document": document_schema.ScriptSchemaDraft,
        "geospatial": geospatial_schema.GeospatialSchema,
        "image": image_schema.ImageDataTypeSchema,
        "resource": resource_schema.Model,
        "script": script_schema.ResearchProjectSchemaDraft,
        "microdata": microdata_schema.MicrodataSchema,
        "table": table_schema.Model,
        "indicator": indicator_schema.TimeseriesSchema,
        "indicators_db": indicators_db_schema.TimeseriesDatabaseSchema,
        "video": video_schema.Model,
    }

    _SCHEMA_TO_TYPE = {v: k for k, v in _TYPE_TO_SCHEMA.items()}

    _TYPE_TO_WRITER = {
        "document": write_across_many_sheets,
        "geospatial": write_across_many_sheets,
        "image": write_across_many_sheets,
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
        "image": excel_doc_to_pydantic,
        "resource": excel_single_sheet_to_pydantic,
        "script": excel_doc_to_pydantic,
        "microdata": excel_doc_to_pydantic,
        "table": excel_doc_to_pydantic,
        "indicator": excel_doc_to_pydantic,
        "indicators_db": excel_single_sheet_to_pydantic,  # one sheet
        "video": excel_single_sheet_to_pydantic,  # one sheet
    }

    def metadata_class_from_name(self, metadata_name: str) -> Type[BaseModel]:
        """
        Retrieve the pydantic model class for the given metadata type.

        Args:
            metadata_name (str): The name of the metadata type. Must be one of:
                document, geospatial, image, indicator, indicators_db, microdata, resource, script, table, video

        Returns:
            Type[BaseModel]: The pydantic model class for the metadata type.

        Raises:
            ValueError: If the metadata name is not supported.

        Example:
            >>> from pydantic_schemas.metadata_manager import MetadataManager
            >>> manager = MetadataManager()
            >>> document_class = manager.metadata_class_from_name("document")
        """
        metadata_name = self.standardize_metadata_name(metadata_name)
        schema = self._TYPE_TO_SCHEMA[metadata_name]
        return copy(schema)

    @property
    def metadata_type_names(self) -> List[str]:
        return list(self._TYPE_TO_SCHEMA.keys())

    def standardize_metadata_name(self, metadata_name: str) -> str:
        """
        Standardize the metadata name to a consistent format. In particular, it converts the name to lowercase and
        replaces spaces and hyphens with underscores. It also maps certain metadata names to their standard
        counterparts. For example, "survey" and "survey_microdata" are both mapped to "microdata". "timeseries" is
        mapped to "indicator" and "timeseries_db" is mapped to "indicators_db".

        Args:
            metadata_name (str): The name of the metadata type.

        Returns:
            str: The standardized metadata name.

        Raises:
            ValueError: If the metadata name is not supported.

        Example:
            >>> from pydantic_schemas.metadata_manager import MetadataManager
            >>> manager = MetadataManager()
            >>> standardized_name = manager.standardize_metadata_name("Document")
        """
        metadata_name = metadata_name.lower()
        metadata_name = metadata_name.replace("-", "_").replace(" ", "_")
        if metadata_name == "survey" or metadata_name == "survey_microdata":
            metadata_name = "microdata"
        elif metadata_name == "timeseries":
            metadata_name = "indicator"
        elif metadata_name == "timeseries_db" or metadata_name == "indicator_db":
            metadata_name = "indicators_db"
        self._raise_if_unsupported_metadata_name(metadata_name=metadata_name)
        return metadata_name

    def create_metadata_outline(
        self, metadata_name_or_class: Union[str, Type[BaseModel]], debug: bool = False
    ) -> BaseModel:
        """
        Create a skeleton pydantic object for the given metadata type.

        Args:
            metadata_name_or_class (str or type[BaseModel]): The name of the metadata type or the metadata class.
            debug (bool): If True, print debug information on the skeleton creation.

        Returns:
            BaseModel: A pydantic object with the metadata schema and default values.

        Example:
            >>> from pydantic_schemas.metadata_manager import MetadataManager
            >>> manager = MetadataManager()
            >>> document_skeleton = manager.create_metadata_outline("document")
        """
        if isinstance(metadata_name_or_class, str):
            schema = self.metadata_class_from_name(metadata_name_or_class)
        else:
            schema = metadata_name_or_class
        skeleton_object = make_skeleton(schema, debug=debug)
        return skeleton_object

    def _get_name_version_schema_writer(self, metadata_name_or_class):
        """
        Determines the metadata name, version, schema, and writer based on the provided metadata name or class.

        Args:
            metadata_name_or_class (str or class): The metadata name as a string or the metadata class.

        Returns:
            tuple: A tuple containing:
                - metadata_name (str): The standardized metadata name.
                - version (str): The version information of the metadata.
                - schema (type(BaseModel)): The schema associated with the metadata.
                - writer (function): The writer function for the metadata.

        If `metadata_name_or_class` is a string or is one of the standard metadata types (document,
        geospatial, image, indicator, indicators_db, microdata, resource, script, table, video),
        it retrieves the corresponding metadata name, schema, version, and writer from the internal
        mappings. Otherwise, it assumes this is a template and retrieves the title from the class,
        and uses a default single page writer function.
        """
        if (
            isinstance(metadata_name_or_class, str)
            or metadata_name_or_class in self._TYPE_TO_SCHEMA.values()
            or type(metadata_name_or_class) in self._TYPE_TO_SCHEMA.values()
        ):
            if isinstance(metadata_name_or_class, str):
                metadata_name = self.standardize_metadata_name(metadata_name_or_class)
                schema = self._TYPE_TO_SCHEMA[metadata_name]
            else:
                for metadata_name, schema in self._TYPE_TO_SCHEMA.items():
                    if schema is metadata_name_or_class or schema is type(metadata_name_or_class):
                        break
            version = f"{metadata_name} type metadata version {__version__}"
            writer = self._TYPE_TO_WRITER[metadata_name]
        else:
            writer = write_to_single_sheet
            metadata_name = metadata_name_or_class.model_json_schema()["title"]
            version = f"Template: {metadata_name}"
            schema = metadata_name_or_class
        return metadata_name, version, schema, writer

    def write_metadata_outline_to_excel(
        self,
        metadata_name_or_class: Union[str, Type[BaseModel]],
        filename: Optional[str] = None,
        title: Optional[str] = None,
        metadata_type: Optional[str] = None,
    ) -> str:
        """
        Create an Excel file formatted for writing the given metadata_name metadata.

        Args:
            metadata_name_or_class (str or type[BaseModel]): the name of a supported metadata type, currently:
                    document, geospatial, image, indicator, indicators_db, microdata, resource, script, table, video
                If passed as a BaseModel type, for instance this is what you would do with a template, then the writer
                    is determined from the metadata_type. If the metadata_type is not provided, then the
                    writer defaults to write_to_single_sheet.
            filename (Optional[str]): The path to the Excel file. If None, defaults to {metadata_name}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. If None, defaults to '{metadata_name} Metadata'
            metadata_type (Optional[str]): The name of the metadata type, used if the metadata_name_or_class is
                    an instance of a template. For example 'geospatial', 'document' etc. The name is used to determine
                    the number of sheets in the Excel file.

        Returns:
            str: filename of metadata file

        Outputs:
            An Excel file into which metadata can be entered
        """
        # determine the metadata_name_or_class is a class instance or the actual class
        if (
            metadata_type is not None
            and not isinstance(metadata_name_or_class, str)
            and metadata_name_or_class not in self._TYPE_TO_SCHEMA.values()
            and type(metadata_name_or_class) not in self._TYPE_TO_SCHEMA.values()
        ):
            metadata_type = self.standardize_metadata_name(metadata_type)
            _, _, _, writer = self._get_name_version_schema_writer(metadata_type)
            metadata_name, version, schema, _ = self._get_name_version_schema_writer(metadata_name_or_class)
        else:
            metadata_name, version, schema, writer = self._get_name_version_schema_writer(metadata_name_or_class)
        skeleton_object = self.create_metadata_outline(schema, debug=False)

        if filename is None:
            filename = f"{metadata_name}_metadata.xlsx"
        if title is None:
            title = f"{metadata_name.capitalize()} Metadata"

        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        writer(filename, skeleton_object, version, title)
        return filename

    def save_metadata_to_excel(
        self,
        object: BaseModel,
        filename: Optional[str] = None,
        title: Optional[str] = None,
        metadata_type: Optional[str] = None,
        verbose: bool = False,
    ) -> str:
        """
        Save an Excel document of the given metadata object.

        Args:
            object (BaseModel): The pydantic object to save to the Excel file.
            filename (Optional[str]): The path to the Excel file. Defaults to {name}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. Defaults to '{name} Metadata'
                metadata_type (Optional[str]): The name of the metadata type such as 'geospatial', 'document', etc. Used if
                the metadata_name_or_class is an instance of a template. The name is used to determine the number of sheets
                in the Excel file.
            verbose (bool): If True, print debug information on the file creation.

        Returns:
            str: filename of metadata file

        Outputs:
            An Excel file containing the metadata from the pydantic object. This file can be updated as needed.
        """
        if (
            metadata_type is not None
            # and object not in self._TYPE_TO_SCHEMA.values()
            and type(object) not in self._TYPE_TO_SCHEMA.values()
        ):
            metadata_type = self.standardize_metadata_name(metadata_type)
            _, _, _, writer = self._get_name_version_schema_writer(metadata_type)
            metadata_name, version, schema, _ = self._get_name_version_schema_writer(type(object))
        else:
            metadata_name, version, schema, writer = self._get_name_version_schema_writer(type(object))
        # metadata_name, version, schema, writer = self._get_name_version_schema_writer(
        #     type(object)
        # )  # metadata_name_or_class)
        skeleton_object = self.create_metadata_outline(metadata_name_or_class=schema, debug=False)

        if filename is None:
            filename = f"{metadata_name}_metadata.xlsx"
        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        if title is None:
            title = f"{metadata_name.capitalize()} Metadata"

        combined_dict = merge_dicts(
            skeleton_object.model_dump(),
            object.model_dump(exclude_none=False, exclude_unset=True, exclude_defaults=True),
            skeleton_mode=True,
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        new_ob = schema.model_validate(combined_dict)
        writer(filename, new_ob, version, title, verbose=verbose)
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
            raise ValueError(f"Cell C1 is empty or not a string. {error_message}")

        cell_values = type_info.split(" ")

        if cell_values[0] == "Template:":
            return " ".join(cell_values[1:])

        if len(cell_values) < 3 or cell_values[1] != "type" or cell_values[2] != "metadata":
            raise ValueError(f"Cell C1 is improperly formatted. {error_message}")

        return cell_values[0]

    def read_metadata_from_excel(
        self,
        filename: str,
        metadata_class: Optional[Type[BaseModel]] = None,
        metadata_type: Optional[str] = None,
        verbose: bool = False,
    ) -> BaseModel:
        """
        Read in metadata from an appropriately formatted Excel file as a pydantic object.
        If using standard metadata types (document, geospatial, image, indicator, indicators_db, microdata, resource, script, table, video) then there is no need to pass in the metadata_class. But if using a template, then the class must be provided.

        Args:
            filename (str): The path to the Excel file.
            metadata_class (Optional type of BaseModel): A pydantic class type correspondong to the type used to write the Excel file
            metadata_type (Optional[str]): The name of the metadata type, such as 'geospatial', 'document', etc. Used if
                the metadata_name_or_class is an instance of a template. The name is used to determine the number of
                sheets in the Excel file.
            verbose (bool): If True, print debug information on the file reading.


        Returns:
            BaseModel: a pydantic object containing the metadata from the file

        Raises:
            ValueError: If the metadata type is not supported or if the Excel file is improperly formatted

        Example:
            >>> from pydantic_schemas.metadata_manager import MetadataManager
            >>> manager = MetadataManager()
            >>> document_metadata = manager.read_metadata_from_excel("document_metadata.xlsx")
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
            if metadata_type is not None:
                metadata_type = self.standardize_metadata_name(metadata_type)
                reader = self._TYPE_TO_READER[metadata_type]
            else:
                reader = excel_single_sheet_to_pydantic
                if verbose:
                    print("reader is falling back to excel_single_sheet_to_pydantic")
        read_object = reader(filename, schema, verbose=verbose)

        skeleton_object = self.create_metadata_outline(metadata_name_or_class=schema, debug=verbose)

        read_object_dict = read_object.model_dump(
            mode="json", exclude_none=False, exclude_unset=True, exclude_defaults=True
        )
        if verbose:
            print("read object dict", read_object_dict)

        combined_dict = merge_dicts(
            skeleton_object.model_dump(mode="json"),
            read_object_dict,
            skeleton_mode=True,
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        new_ob = schema.model_validate(combined_dict)
        return new_ob

    def _raise_if_unsupported_metadata_name(self, metadata_name: str):
        """
        If the type is specifically unsupported a NotImplementedError is raised
        If the type is simply unknown then a ValueError is raised.
        """
        if metadata_name not in self._TYPE_TO_SCHEMA.keys():
            raise ValueError(f"'{metadata_name}' not supported. Must be: {list(self._TYPE_TO_SCHEMA.keys())}")
