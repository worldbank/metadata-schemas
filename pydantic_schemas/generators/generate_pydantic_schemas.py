import os
import re
from subprocess import run

import yaml

SCHEMA_DIR = "schemas"
OUTPUT_DIR = os.path.join("pydantic_schemas")
PYTHON_VERSION = "3.11"
BASE_CLASS = ".utils.schema_base_model.SchemaBaseModel"


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

with open("json_to_python_config.yaml") as file:
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
            # "--wrap-string-literal",
            "--collapse-root-models",
            "--disable-timestamp",
            "--base-class",
            BASE_CLASS,
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--output",
            output_path,
        ],
        check=False,
    )

    with open(output_path) as file:
        content = file.read()

    # version=version: f"""class {model_name}(SchemaBaseModel):\n{match.group(1)}\n    _metadata_type__:str = PrivateAttr("{section}")\n    _metadata_type_version__:str = PrivateAttr("{version}") """,
    # version = f"""class {model_name}(SchemaBaseModel):\n{match.group(1)}\n\n    def __init__(self, **kwargs):\n        super().__init__(**kwargs)\n        self._metadata_type__ = "{section}"\n        self._metadata_type_version__ = "{version}"\n"""
    updated_content = re.sub(
        f'class {model_name}\(SchemaBaseModel\):\n(    """\n.*\n    """)',  #
        lambda match,
        model_name=model_name,
        section=section,
        # version=version: f"""class {model_name}(SchemaBaseModel):\n{match.group(1)}\n    _metadata_type__ = "{section}"\n    _metadata_type_version__ = "{version}" """,
        # version = version: f"""class {model_name}(SchemaBaseModel):\n{match.group(1)}\n\n    def __init__(self, **kwargs):\n        super().__init__(**kwargs)\n        self._metadata_type__ = "{section}"\n        self._metadata_type_version__ = "{version}"\n""",
        version=version: f"""class {model_name}(SchemaBaseModel):\n{match.group(1)}\n    _metadata_type__:str = PrivateAttr("{section}")\n    _metadata_type_version__:str = PrivateAttr("{version}") """,
        content,
    )

    # find the line in updated_content that begins "from pydantic import " and append to that line ", PrivateAttr"
    updated_content = re.sub(
        r"from pydantic import (.*)",
        lambda match: f"from pydantic import {match.group(1)}, PrivateAttr",
        updated_content,
    )

    # replace from enum import Enum with rom .utils.enum_with_value_or_key import EnumWithValueOrKey
    updated_content = re.sub(
        r"from enum import Enum",
        "from .utils.enum_with_value_or_key import EnumWithValueOrKey",
        updated_content,
    )

    # replace (Enum) with (EnumWithValueOrKey)
    updated_content = re.sub(r"\(Enum\)", "(EnumWithValueOrKey)", updated_content)

    with open(output_path, "w") as file:
        file.write(updated_content)
