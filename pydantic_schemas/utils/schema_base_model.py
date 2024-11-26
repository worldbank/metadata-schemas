from pydantic import BaseModel, ConfigDict
from rich import print as print_rich

# from rich.pretty import pretty_repr


class SchemaBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True, protected_namespaces=(), use_enum_values=True, extra="ignore"
    )  # if a subclass has a model_config then this will be overridden

    def pretty_print(self):
        print_rich(self)

    # def __repr__(self):
    #     return pretty_repr(self)

    # def __str__(self):
    #     return pretty_repr(self)
