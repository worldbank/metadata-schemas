from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from rich import print as print_rich

# from rich.pretty import pretty_repr


class SchemaBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True, protected_namespaces=(), use_enum_values=True, extra="ignore"
    )  # if a subclass has a model_config then this will be overridden

    def pretty_print(self):
        print_rich(self)

    __metadata_type__: Optional[str] = None
    __metadata_type_version__: Optional[str] = None
    __template_name__: Optional[str] = None
    __template_uid__: Optional[str] = None

    # metadata_type_: Optional[str] = Field(default=None, alias="__metadata_type__")
    # metadata_type_version_: Optional[str] = Field(default=None, alias="__metadata_type_version__")
    # template_name_: Optional[str] = Field(default=None, alias="__template_name__")
    # template_uid_: Optional[str] = Field(default=None, alias="__template_uid__")

    # @property
    # def __metadata_type__(self):
    #     return self.metadata_type_

    # @property
    # def __metadata_type_version__(self):
    #     return self.metadata_type_version_

    # @property
    # def __template_name__(self):
    #     return self.template_name_
    # @property
    # def __template_uid__(self):
    #     return self.template_uid_

    # def __repr__(self):
    #     return pretty_repr(self)

    # def __str__(self):
    #     return pretty_repr(self)
