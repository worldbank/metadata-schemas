import importlib.metadata
import os
import re
from subprocess import run

SCHEMA_DIR = "schemas"
OUTPUT_DIR = os.path.join("pydantic_schemas")
PYTHON_VERSION = "3.11"
BASE_CLASS = ".utils.schema_base_model.SchemaBaseModel"
__version__ = importlib.metadata.version("metadataschemas")

INPUTS_TO_OUTPUTS = {
    "document-schema.json": ("document_schema.py", "Document", "ScriptSchemaDraft"),
    "geospatial-schema.json": ("geospatial_schema.py", "Geospatial", "GeospatialSchema"),
    "image-schema.json": ("image_schema.py", "Image", "ImageDataTypeSchema"),
    "microdata-schema.json": ("microdata_schema.py", "Microdata", "DdiSchema"),
    "resource-schema.json": ("resource_schema.py", "Resource", "Model"),
    "script-schema.json": ("script_schema.py", "Script", "ResearchProjectSchemaDraft"),
    "table-schema.json": ("table_schema.py", "Table", "Model"),
    "timeseries-db-schema.json": ("indicators_db_schema.py", "Indicators_DB", "TimeseriesDatabaseSchema"),
    "timeseries-schema.json": ("indicator_schema.py", "Indicator", "TimeseriesSchema"),
    "video-schema.json": ("video_schema.py", "Video", "Model"),
}


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for input_file, (output_file, metadata_type, schema_class_name) in INPUTS_TO_OUTPUTS.items():
    print(f"Generating pydantic schema for {input_file}")
    input_path = os.path.join(SCHEMA_DIR, input_file)
    output_path = os.path.join(OUTPUT_DIR, output_file).replace("-", "_")
    run(
        [
            "datamodel-codegen",
            "--input",
            input_path,
            "--input-file-type",
            "jsonschema",
            "--reuse-model",
            "--use-schema-description",
            "--target-python-version",
            PYTHON_VERSION,
            "--use-double-quotes",
            "--wrap-string-literal",
            "--collapse-root-models",
            "--disable-timestamp",
            "--base-class",
            BASE_CLASS,
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--output",
            output_path,
        ]
    )

    with open(output_path, "r") as file:
        content = file.read()

    updated_content = re.sub(
        f'class {schema_class_name}\(SchemaBaseModel\):\n(    """\n.*\n    """)',  #
        lambda match: f"class {schema_class_name}(SchemaBaseModel):\n{match.group(1)}\n    __metadata_type__ = '{metadata_type}'\n    __metadata_type_version__='{__version__}'",
        content,
    )

    with open(output_path, "w") as file:
        file.write(updated_content)
