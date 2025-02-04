# metadata-schemas

[![PyPI version](https://badge.fury.io/py/metadataschemas.svg)](https://badge.fury.io/py/metadataschemas)

This repository contains both the definitions of Metadata Schemas and a python library for creating schema objects with pydantic and Excel.

## Defining Metadata Schemas

The schemas are defined in the JSON Schema format in the folder `schemas`. For more information you can view documentation at https://worldbank.github.io/metadata-schemas/

## Excel

Excel sheets formatted for each metadata type are located in this repo in the excel_sheets folder.

## Python library

To install the library run

```pip install metadataschemas```

### Creating a pydantic metadata object

To create a timeseries metadata object run

```python
from metadataschemas import indicator_schema

indicator_metadata = indicator_schema.TimeseriesSchema(idno='project_idno',series_description=indicator_schema.SeriesDescription(idno='project_idno', name='project_name'))

indicator_metadata.pretty_print()
```
And the print statement will show you the metadata object in a pleasant format.
```python
TimeseriesSchema(
    idno='project_idno',
    series_description=series_description(
        idno='project_idno',
        name='project_name'
    )
)
```

Depending on your IDE, selecting `TimeseriesSchema` could show you what fields the schema contains and their corresponding object definitions.

There are metadata objects for each of the following metadata types:

| Metadata Type    | Metadata Object                                 |
|------------------|-------------------------------------------------|
| document         | `document_schema.ScriptSchemaDraft`             |
| geospatial       | `geospatial_schema.GeospatialSchema`            |
| image            | `image_schema.ImageDataTypeSchema`              |
| indicator        | `indicator_schema.TimeseriesSchema`             |
| indicators_db    | `indicators_db_schema.TimeseriesDatabaseSchema` |
| microdata        | `microdata_schema.MicrodataSchema`              |
| resource         | `resource_schema.Model`                         |
| script           | `script_schema.ResearchProjectSchemaDraft`      |
| table            | `table_schema.Model`                            |
| video            | `video_schema.Model`                            |

### Python - Metadata Manager

The Manager exists to be an interface with Excel and to lightly assist creating schemas.

For Excel we can:

1. Create blank Excel files formatted for a given metadata type
2. Write metadata objects to Excel
3. Read an appropriately formatted Excel file containing metadata into a pydantic metadata object

To use it run:

```python
from metadataschemas import MetadataManager

mm = MetadataManager()

filename = mm.write_metadata_outline_to_excel('indicator')

filename = mm.save_metadata_to_excel(indicator_metadata)

# Then after you have updated the metadata in the Excel file

updated_indicator_metadata = mm.read_metadata_from_excel(filename)
```
The manager also offers a convenient way to get started creating metadata in pydantic by creating an empty pydantic object for a given metadata type which can then be updated as needed.

```python
# list the supported metadata types
mm.metadata_type_names

# get the pydantic class for a given metadata type
microdata_type = mm.metadata_class_from_name("microdata")

# create an instantiated pydantic object and then fill in your data
microdata_metadata = mm.create_metadata_outline("microdata")
microdata_metadata.repositoryid = "repository id"
microdata_metadata.study_desc.title_statement.idno = "project_idno"
```


## Updating Schemas

First create a branch from the main branch. Branch names should follow the pattern 'schema/\<your user name\>/\<short description of change\>'.

Then make the change you want to the json schema in the schemas folder.

Then in pyproject.toml update the version number, changing either the major, minor or patch number as appropriate given the conventions below.

After, update the version number of the **specific schema you updated** in the json_to_python_config.yaml file to match the version number in pyproject.toml.

Next update the pydantic schemas so that they match the latest json schemas by running

    python pydantic_schemas/generators/generate_pydantic_schemas.py

Finally update the Excel sheets by running

    python -m pydantic_schemas.generators.generate_excel_files

## Versioning conventions for schemas

### Major Changes

- field type changes that break convention and cannot be coerced such as a field moving from string to an array
- a mandatory field added or optional field changed to mandatory

### Minor Changes

- field removed
- optional field added

### Patch Changes

- field type changes that can be coerced such as int to string