import importlib.metadata
import importlib.util
import os

import yaml

from pydantic_schemas.metadata_manager import MetadataManager


def test_yaml_file():
    # Load the YAML file
    with open("json_to_python_config.yaml", "r") as file:
        data = yaml.safe_load(file)

    # Get the version from importlib.metadata
    __version__ = importlib.metadata.version("metadataschemas")

    for section, details in data.items():
        # Check that each value is non-null
        assert details["version"] is not None, f"Version is null in section {section}"
        assert details["json_file"] is not None, f"JSON file is null in section {section}"
        assert details["python_file"] is not None, f"Python file is null in section {section}"
        assert details["model_name"] is not None, f"Model name is null in section {section}"

        # Check that the JSON and Python files exist
        json_file = os.path.join("schemas", details["json_file"])
        assert os.path.exists(json_file), f"JSON file {json_file} does not exist in section {section}"
        python_file = os.path.join("pydantic_schemas", details["python_file"])
        assert os.path.exists(python_file), f"Python file {python_file} does not exist in section {section}"

        # Check that the version is equal to or less than the version from importlib.metadata
        assert (
            details["version"] <= __version__
        ), f"Version {details['version']} in section {section} is greater than {__version__}"

        # Check the version is a string fomatted as digits.digits.digits
        assert isinstance(details["version"], str), f"Version {details['version']} in section {section} is not a string"
        assert (
            details["version"].count(".") == 2
        ), f"Version {details['version']} in section {section} is not formatted as digits.digits.digits"
        assert all(
            [x.isdigit() for x in details["version"].split(".")]
        ), f"Version {details['version']} in section {section} is not formatted as digits.digits.digits"


def test_every_schema_has_version():
    mm = MetadataManager()
    for v in mm.metadata_type_names:
        m = mm.create_metadata_outline(mm.metadata_class_from_name(v))
        assert m.__metadata_type__ is not None, f"__metadata_type__ is None for {v}"
        assert m.__metadata_type_version__ is not None, f"__metadata_type_version__ is None for {v}"
        assert hasattr(m, "__template_name__"), f"__template_name__ not in {v}"
        assert hasattr(m, "__template_uid__"), f"__template_uid__ not in {v}"
        assert m.__template_name__ is None, f"__template_name__ is not None for {v} = {m.__template_name__}"
        assert m.__template_uid__ is None, f"__template_uid__ is not None for {v} = {m.__template_uid__}"

        m = mm.create_metadata_outline(v)
        assert m.__metadata_type__ is not None, f"__metadata_type__ is None for {v}"
        assert m.__metadata_type_version__ is not None, f"__metadata_type_version__ is None for {v}"
        assert hasattr(m, "__template_name__"), f"__template_name__ not in {v}"
        assert hasattr(m, "__template_uid__"), f"__template_uid__ not in {v}"
        assert m.__template_name__ is None, f"__template_name__ is not None for {v} = {m.__template_name__}"
        assert m.__template_uid__ is None, f"__template_uid__ is not None for {v} = {m.__template_uid__}"

        m = mm._TYPE_TO_SCHEMA[v]
        assert m.__metadata_type__ is not None, f"__metadata_type__ is None for {v}"
        assert m.__metadata_type_version__ is not None, f"__metadata_type_version__ is None for {v}"
        assert hasattr(m, "__template_name__"), f"__template_name__ not in {v}"
        assert hasattr(m, "__template_uid__"), f"__template_uid__ not in {v}"
        assert m.__template_name__ is None, f"__template_name__ is not None for {v} = {m.__template_name__}"
        assert m.__template_uid__ is None, f"__template_uid__ is not None for {v} = {m.__template_uid__}"
