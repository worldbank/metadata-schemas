from pydantic import BaseModel, ConfigDict


class SchemaBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True, protected_namespaces=(), use_enum_values=True, extra="ignore"
    )  # if a subclass has a model_config then this will be overridden
