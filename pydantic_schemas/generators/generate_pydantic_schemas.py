# import importlib.metadata
import os
import re
from subprocess import run

import yaml

SCHEMA_DIR = "schemas"
OUTPUT_DIR = os.path.join("pydantic_schemas")
PYTHON_VERSION = "3.11"
BASE_CLASS = ".utils.schema_base_model.SchemaBaseModel"
# __version__ = importlib.metadata.version("metadataschemas")


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

with open("json_to_python_config.yaml", "r") as file:
    data = yaml.safe_load(file)

# for json_file, (python_file, metadata_type, schema_class_name) in INPUTS_TO_OUTPUTS.items():
for section, details in data.items():
    json_file = details["json_file"]
    python_file = details["python_file"]
    model_name = details["model_name"]
    version = details["version"]

    print(f"Generating pydantic schema for {json_file}")
    input_path = os.path.join(SCHEMA_DIR, json_file)
    output_path = os.path.join(OUTPUT_DIR, python_file).replace("-", "_")
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
        f'class {model_name}\(SchemaBaseModel\):\n(    """\n.*\n    """)',  #
        lambda match: f"""class {model_name}(SchemaBaseModel):\n{match.group(1)}\n    __metadata_type__ = "{section}"\n    __metadata_type_version__ = "{version}" """,
        content,
    )

    with open(output_path, "w") as file:
        file.write(updated_content)
