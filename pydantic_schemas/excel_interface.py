from typing import Optional

from pydantic import BaseModel

from . import (
    document_schema,
    microdata_schema,
    script_schema,
    series_schema,
    table_schema,
    timeseries_db_schema,
    timeseries_schema,
    video_schema,
)
from .utils.excel_to_pydantic import excel_doc_to_pydantic, excel_single_sheet_to_pydantic
from .utils.pydantic_to_excel import write_across_many_sheets, write_to_single_sheet
from .utils.quick_start import make_skeleton
from .utils.utils import standardize_keys_in_dict


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

    _NAME_FUNCTION_MAP = {
        "document": (document_schema.ScriptSchemaDraft, write_across_many_sheets, excel_doc_to_pydantic),
        # "geospatial":GeospatialSchema,
        # "image":ImageDataTypeSchema,
        "script": (script_schema.ResearchProjectSchemaDraft, write_across_many_sheets, excel_doc_to_pydantic),
        "series": (series_schema.Series, write_to_single_sheet, excel_single_sheet_to_pydantic),  # one sheet
        "survey_microdata": (microdata_schema.MicrodataSchema, write_across_many_sheets, excel_doc_to_pydantic),
        "table": (table_schema.Model, write_across_many_sheets, excel_doc_to_pydantic),
        "timeseries": (timeseries_schema.TimeseriesSchema, write_across_many_sheets, excel_doc_to_pydantic),
        "timeseries_db": (
            timeseries_db_schema.TimeseriesDatabaseSchema,
            write_to_single_sheet,
            excel_single_sheet_to_pydantic,
        ),  # one sheet
        "video": (video_schema.Model, write_to_single_sheet, excel_single_sheet_to_pydantic),  # one sheet
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

    def write_empty_metadata_to_excel(
        self, metadata_type: str, filename: Optional[str] = None, title: Optional[str] = None
    ):
        """
        Create an Excel document formatted for writing the given metadata_type metadata.

        Args:
            metadata_type (str): the name of a supported metadata type, currently:
                    document, script, series, survey_microdata, table, timeseries, timeseries_DB, video
                Currently not supported:
                    geospatial, image
            filename (Optional[str]): The path to the Excel file. If None, defaults to {metadata_type}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. If None, defaults to '{metadata_type} Metadata'

        Outputs:
            An Excel file into which metadata can be entered
        """
        metadata_type = metadata_type.lower()
        self.raise_if_unsupported_metadata_type(metadata_type=metadata_type)
        schema = self._NAME_FUNCTION_MAP[metadata_type][0]
        writer = self._NAME_FUNCTION_MAP[metadata_type][1]
        if filename is None:
            filename = f"{metadata_type}_metadata.xlsx"
        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        if title is None:
            title = f"{metadata_type.capitalize()} Metadata"
        skeleton_object = make_skeleton(schema, debug=False)
        writer(filename, skeleton_object, title)

    def save_metadata_to_excel(
        self, metadata_type: str, object: BaseModel, filename: Optional[str] = None, title: Optional[str] = None
    ):
        """
        Save an Excel document of the given metadata_type metadata.

        Args:
            metadata_type (str): the name of a supported metadata type, currently:
                    document, script, series, survey_microdata, table, timeseries, timeseries_db, video
                Currently not supported:
                    geospatial, image
            object (BaseModel): The pydantic object to save to the Excel file.
            filename (Optional[str]): The path to the Excel file. Defaults to {name}_metadata.xlsx
            title (Optional[str]): The title for the Excel sheet. Defaults to '{name} Metadata'

        Outputs:
            An Excel file containing the metadata from the pydantic object. This file can be updated as needed.
        """
        metadata_type = metadata_type.lower()
        self.raise_if_unsupported_metadata_type(metadata_type=metadata_type)
        schema = self._NAME_FUNCTION_MAP[metadata_type][0]
        writer = self._NAME_FUNCTION_MAP[metadata_type][1]
        if filename is None:
            filename = f"{metadata_type}_metadata.xlsx"
        if not str(filename).endswith(".xlsx"):
            filename += ".xlsx"
        if title is None:
            title = f"{metadata_type.capitalize()} Metadata"

        skeleton_object = make_skeleton(schema, debug=False)
        combined_dict = self._merge_dicts(
            skeleton_object.model_dump(),
            object.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True),
        )
        combined_dict = standardize_keys_in_dict(combined_dict)
        new_ob = schema(**combined_dict)
        writer(filename, new_ob, title)

    def read_metadata_excel(self, metadata_type: str, filename: str) -> BaseModel:
        """
        Read in metadata_type metadata from an appropriately formatted Excel file as a pydantic object.

        Args:
            filename (str): The path to the Excel file.

        Returns:
            BaseModel: a pydantic object containing the metadata from the file
        """
        metadata_type = metadata_type.lower()
        self.raise_if_unsupported_metadata_type(metadata_type=metadata_type)
        schema = self._NAME_FUNCTION_MAP[metadata_type][0]
        reader = self._NAME_FUNCTION_MAP[metadata_type][2]
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
        for metadata_type in self._NAME_FUNCTION_MAP.keys():
            self._generate_methods(metadata_type.lower())

    def _generate_methods(self, metadata_type):
        def write_skeleton_method(
            filename=f"{metadata_type}_metadata.xlsx", title=f"{metadata_type.capitalize()} Metadata"
        ):
            self.write_empty_metadata_to_excel(metadata_type=metadata_type, filename=filename, title=title)

        write_skeleton_method.__name__ = f"write_empty_metadata_to_excel_for_{metadata_type}"
        write_skeleton_doc_template = """
        Create an Excel document formatted for writing {name} metadata.

        Args:
            filename (str): The path to the Excel file. Defaults to {name}_metadata.xlsx
            title (str): The title for the Excel sheet. Defaults to '{name_capitalized} Metadata'

        Outputs:
            An Excel file into which {name} metadata can be entered
        """
        write_skeleton_method.__doc__ = write_skeleton_doc_template.format(
            name=metadata_type, name_capitalized=metadata_type.capitalize()
        )
        setattr(self, write_skeleton_method.__name__, write_skeleton_method)

        def save_to_excel_method(
            object, filename=f"{metadata_type}_metadata.xlsx", title=f"{metadata_type.capitalize()} Metadata"
        ):
            self.save_metadata_to_excel(metadata_type=metadata_type, object=object, filename=filename, title=title)

        save_to_excel_method.__name__ = f"save_metadata_to_excel_for_{metadata_type}"
        save_doc_template = """
        Save an Excel document of the {name} metadata.

        Args:
            object (BaseModel): The pydantic object to save to the Excel file.
            filename (str): The path to the Excel file. Defaults to {name}_metadata.xlsx
            title (str): The title for the Excel sheet. Defaults to '{name_capitalized} Metadata'

        Outputs:
            An Excel file containing the {name} metadata from the pydantic object. This file can be updated as needed.
        """
        save_to_excel_method.__doc__ = save_doc_template.format(
            name=metadata_type, name_capitalized=metadata_type.capitalize()
        )
        setattr(self, save_to_excel_method.__name__, save_to_excel_method)

        def read_method(filename):
            return self.read_metadata_excel(metadata_type, filename=filename)

        read_method.__name__ = f"read_metadata_excel_of_{metadata_type}"
        read_doc_template = """
        Read in {name} metadata from an appropriately formatted Excel file as a pydantic object.

        Args:
            filename (str): The path to the Excel file.
        
        Returns:
            BaseModel: a pydantic object containing the metadata from the file
        """
        read_method.__doc__ = read_doc_template.format(name=metadata_type)
        setattr(self, read_method.__name__, read_method)

    def raise_if_unsupported_metadata_type(self, metadata_type: str):
        """
        If the type is specifically unsupported - geospatial or image - a NotImplementedError is raised
        If the type is simply unknown then a ValueError is raised.
        """
        metadata_type = metadata_type.lower()
        if metadata_type == "geospatial":
            raise NotImplementedError("Geospatial schema contains an infinite loop so cannot be written to excel")
        if metadata_type == "image":
            raise NotImplementedError("Due to an issue with image metadata schema definition causing __root__ errors")
        if metadata_type not in self._NAME_FUNCTION_MAP.keys():
            raise ValueError(f"'{metadata_type}' not supported. Must be: {list(self._NAME_FUNCTION_MAP.keys())}")
