# metadata-schemas
This repository contains both the definitions of Metadata Schemas and a python library for creating schema objects with pydantic and Excel.

## Defining Metadata Schemas

The schemas are defined in the JSON Schema format in the folder `schemas`. For more information you can view documentation at https://worldbank.github.io/metadata-schemas/

## Python library

To install the library run

```pip install metadataschemas```

### Creating a pydantic metadata object

To create a timeseries metadata object run

```python
from metadataschemas import timeseries_schema

timeseries_metadata = timeseries_schema.TimeseriesSchema(idno='project_idno',series_description=timeseries_schema.SeriesDescription(idno='project_idno', name='project_name'))
```

Depending on your IDE, selecting `TimeseriesSchema` could show you what fields the schema contains and their corresponding object definitions.

There are metadata objects for each of the following metadata types:

| Metadata Type    | Metadata Object                                 |
|------------------|-------------------------------------------------|
| document         | `document_schema.ScriptSchemaDraft`             |
| geospatial       | `geospatial_schema.GeospatialSchema`            |
| script           | `script_schema.ResearchProjectSchemaDraft`      |
| series           | `series_schema.Series`                          |
| survey           | `microdata_schema.MicrodataSchema`              |
| table            | `table_schema.Model`                            |
| timeseries       | `timeseries_schema.TimeseriesSchema`            |
| timeseries_db    | `timeseries_db_schema.TimeseriesDatabaseSchema` |
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

filename = mm.write_metadata_outline_to_excel('timeseries')

filename = mm.save_metadata_to_excel('timeseries', 
                                     object=timeseries_metadata)

# Then after you have updated the metadata in the Excel file

updated_timeseries_metadata = mm.read_metadata_from_excel(timeseries_metadata_filename)
```

Note that the Excel write and save functions do not currently support Geospatial metadata.

The manager also offers a convenient way to get started creating metadata in pydantic by creating an empty pydantic object for a given metadata type which can then be updated as needed.

```python
# list the supported metadata types
mm.metadata_type_names

# get the pydantic class for a given metadata type
survey_type = mm.metadata_class_from_name("survey")

# create an instantiated pydantic object and then fill in your data
survey_metadata = mm.type_to_outline(metadata_type="survey")
survey_metadata.repositoryid = "repository id"
survey_metadata.study_desc.title_statement.idno = "project_idno"
```


## Updating Pydantic definitions and Excel sheets

To update the pydantic schemas so that they match the latest json schemas run

    `python pydantic_schemas/generators/generate_pydantic_schemas.py`

Then to update the Excel sheets run

    `python pydantic_schemas/generators/generate_excel_files.py`