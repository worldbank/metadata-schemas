from pydantic import BaseModel, ConfigDict


class SchemaBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True, protected_namespaces=(), use_enum_values=True
    )  # if a subclass has a model_config then this will be overridden

    def __setitem__(self, key, value):
        """Allow dict like setting: Model[key] = value"""
        setattr(self, key, value)
