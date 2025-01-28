from typing import Optional

from pydantic import BaseModel, ConfigDict, PrivateAttr
from rich import print as print_rich

# from rich.pretty import pretty_repr


class SchemaBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True, protected_namespaces=(), use_enum_values=True, extra="ignore"
    )  # if a subclass has a model_config then this will be overridden

    def pretty_print(self):
        print_rich(self)

    def pprint(self):
        print_rich(self)

    _metadata_type__: Optional[str] = PrivateAttr(default=None)  # None
    _metadata_type_version__: Optional[str] = PrivateAttr(default=None)  # None
    _template_name__: Optional[str] = PrivateAttr(default=None)  # None
    _template_uid__: Optional[str] = PrivateAttr(default=None)  # None

    # def __repr__(self):
    #     return pretty_repr(self)

    # def __str__(self):
    #     return pretty_repr(self)
