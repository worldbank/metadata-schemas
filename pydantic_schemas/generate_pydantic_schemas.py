import os
from subprocess import run

SCHEMA_DIR = "schemas"
OUTPUT_DIR = os.path.join("pydantic_schemas", "definitions")
PYTHON_VERSION = "3.11"
BASE_CLASS = ".schema_base_model.SchemaBaseModel"
INPUTS = [
    "document-schema.json",
    "geospatial-schema.json",
    "image-schema.json",
    "microdata-schema.json",
    "script-schema.json",
    "series-schema.json",
    "table-schema.json",
    "timeseries-db-schema.json",
    "timeseries-schema.json",
    "video-schema.json",
]


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for input_file in INPUTS:
    print(f"Generating pydantic schema for {input_file}")
    input_path = os.path.join(SCHEMA_DIR, input_file)
    output_file = os.path.splitext(input_file)[0] + ".py"
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
            "--base-class",
            BASE_CLASS,
            "--output",
            output_path,
        ]
    )
