import os
from subprocess import run

from pydantic import BaseModel

SCHEMA_DIR = "schemas"
OUTPUT_DIR = os.path.join("pydantic_schemas")
PYTHON_VERSION = "3.11"
BASE_CLASS = ".utils.schema_base_model.SchemaBaseModel"

INPUTS_TO_OUTPUTS = {
    "document-schema.json": "document_schema.py",
    "geospatial-schema.json": "geospatial_schema.py",
    "image-schema.json": "image_schema.py",
    "microdata-schema.json": "microdata_schema.py",
    "resource-schema.json": "resource_schema.py",
    "script-schema.json": "script_schema.py",
    "table-schema.json": "table_schema.py",
    "timeseries-db-schema.json": "indicators_db_schema.py",
    "timeseries-schema.json": "indicator_schema.py",
    "video-schema.json": "video_schema.py",
}


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for input_file, output_file in INPUTS_TO_OUTPUTS.items():
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
