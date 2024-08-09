# metadata-schemas
Metadata JSON Schemas

View documentation - https://worldbank.github.io/metadata-schemas/


## Pydantic

To update the pydantic schemas so that they match the json schemas run

    `python pydantic_schemas\\generators\\generate_pydantic_schemas.py`

Then to update the Excel sheets run

    `python pydantic_schemas\\generators\\generate_excel_files.py`