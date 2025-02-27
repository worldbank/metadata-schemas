# generated by datamodel-codegen:
#   filename:  resource-schema.json

from __future__ import annotations

from typing import Optional

from pydantic import Field, PrivateAttr

from .utils.schema_base_model import SchemaBaseModel


class Model(SchemaBaseModel):
    """
    External resource schema
    """
    _metadata_type__:str = PrivateAttr("resource")
    _metadata_type_version__:str = PrivateAttr("0.1.0") 

    dctype: Optional[str] = Field(
        "doc/oth",
        description="Document types for external resource e.g. `doc/adm` \n* `doc/adm` - Document, Administrative [doc/adm] \n* `doc/anl` - Document, Analytical [doc/anl] \n* `doc/oth` - Document, Other [doc/oth] \n* `doc/qst` - Document, Questionnaire [doc/qst] \n* `doc/ref` - Document, Reference [doc/ref] \n* `doc/rep` - Document, Report [doc/rep]  \n* `doc/tec` - Document, Technical [doc/tec] \n* `aud` - Audio [aud]\n* `dat` - Database [dat]\n* `map` - Map [map]\n* `dat/micro` - Microdata File [dat/micro]\n* `pic` - Photo [pic]\n* `prg` - Program [prg]\n* `tbl` - Table [tbl]\n* `vid` - Video [vid]  \n* `web` - Web Site [web]",
        title="Resource type",
    )
    dcformat: Optional[str] = Field(
        None,
        description="Document file format e.g. `application/zip` \n* `application/x-compressed` - Compressed, Generic \n* `application/zip` - Compressed, ZIP  \n* `application/x-cspro` - Data, CSPro  \n* `application/dbase` - Data, dBase   \n* `application/msaccess` - Data, Microsoft Access  \n* `application/x-sas` - Data, SAS  \n* `application/x-spss` - Data, SPSS   \n* `application/x-stata` - Data, Stata   \n* `text` - Document, Generic  \n* `text/html` - Document, HTML  \n* `application/msexcel` - Document, Microsoft Excel  \n* `application/mspowerpoint` - Document, Microsoft PowerPoint \n* `application/msword` - Document, Microsoft Word  \n* `application/pdf` - Document, PDF  \n* `application/postscript` - Document, Postscript  \n* `text/plain` - Document, Plain \n* `text/wordperfect` - Document, WordPerfect  \n* `image/gif` - Image, GIF  \n* `image/jpeg` - Image, JPEG   \n* `image/png` - Image, PNG   \n* `image/tiff` - Image, TIFF",
        title="Resource Format",
    )
    title: str = Field(..., description="Title")
    author: Optional[str] = Field(None, description="Author")
    dcdate: Optional[str] = Field(None, description="Date")
    country: Optional[str] = Field(None, description="Country")
    language: Optional[str] = Field(None, description="Language")
    contributor: Optional[str] = Field(None, description="Contributor")
    publisher: Optional[str] = Field(None, description="Publisher")
    rights: Optional[str] = Field(None, description="Rights")
    description: Optional[str] = Field(None, description="Description")
    abstract: Optional[str] = Field(None, description="Abstract")
    toc: Optional[str] = Field(None, description="TOC")
    filename: Optional[str] = Field(
        None,
        description="Resource file name or URL. For uploading a file, use the field `file` in formData or use the `Upload file` endpoint.",
    )
