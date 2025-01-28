# generated by datamodel-codegen:
#   filename:  document-schema.json

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, Field, PrivateAttr

from .utils.schema_base_model import SchemaBaseModel


class Producer(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Name (required)", title="Name")
    abbr: Optional[str] = Field(None, title="Abbreviation")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")


class MetadataInformation(SchemaBaseModel):
    """
    Document description
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    title: Optional[str] = Field(
        None, description="Document title", title="Document title"
    )
    idno: Optional[str] = Field(None, title="Unique ID number for the document")
    producers: Optional[List[Producer]] = Field(
        None, description="List of producers", title="Producers"
    )
    production_date: Optional[str] = Field(
        None,
        description="Document production date using format(YYYY-MM-DD)",
        title="Date of Production",
    )
    version: Optional[str] = Field(
        None,
        description="Identify and describe the current version of the document",
        title="Document version",
    )


class TitleStatement(SchemaBaseModel):
    """
    Study title
    """

    idno: str = Field(
        ...,
        description="The ID number of a dataset is a unique number that is used to identify a document.",
        title="Unique user defined ID",
    )
    title: str = Field(..., title="Title")
    sub_title: Optional[str] = Field(None, title="Subtitle")
    alternate_title: Optional[str] = Field(None, title="Abbreviation or Acronym")
    translated_title: Optional[str] = Field(None, title="Translated Title")


class AuthorIdItem(SchemaBaseModel):
    type: Optional[Any] = Field(
        None, description="Source of identifier, e.g. ORCID", title="Type"
    )
    id: Optional[Any] = Field(
        None,
        description="Author's unique identifier for the corresponding source",
        title="Identifier",
    )


class Author(SchemaBaseModel):
    first_name: Optional[str] = Field(None, title="First name")
    initial: Optional[str] = Field(None, title="Initial")
    last_name: Optional[str] = Field(None, title="Last name")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    author_id: Optional[List[AuthorIdItem]] = Field(
        None,
        description="Unique identifier of an author, which may be provided by services like ORCID or other",
        title="Author ID",
    )
    full_name: Optional[str] = Field(
        None,
        description="Full name of the author. This element to be used only when first or last name cannot be distinguished.",
        title="Full name",
    )


class Editor(SchemaBaseModel):
    first_name: Optional[str] = Field(None, title="First name")
    initial: Optional[str] = Field(None, title="Initial")
    last_name: Optional[str] = Field(None, title="Last name")
    affiliation: Optional[str] = Field(None, title="Affiliation")


class Identifier(SchemaBaseModel):
    type: Optional[str] = Field(
        None,
        description="Type of identifier e.g. `doi`, `handle`, `other`",
        title="Identifier type",
    )
    identifier: str = Field(..., title="Identifier")


class TocStructuredItem(SchemaBaseModel):
    id: str = Field(..., title="ID or Number")
    parent_id: Optional[str] = Field(
        None,
        description="For sub levels, provide the ID of the parent TOC ID",
        title="Parent Identifier",
    )
    name: str = Field(..., title="Title")


class Note(SchemaBaseModel):
    note: Optional[str] = Field(None, title="Note")


class RefCountryItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Country name")
    code: Optional[str] = Field(None, title="Country code")


class GeographicUnit(SchemaBaseModel):
    name: str = Field(
        ...,
        description="Name of the geographic unit e.g. 'World', 'Africa', 'Afghanistan'",
        title="Location name",
    )
    code: Optional[str] = Field(
        None,
        description="Code of the geographic unit (for countries, preferred = ISO3 code)",
        title="Location code",
    )
    type: Optional[str] = Field(
        None,
        description="Type of geographic unit e.g. country, state, region, province, town, etc",
        title="Type",
    )


class BboxItem(SchemaBaseModel):
    west: Optional[str] = Field(None, title="West")
    east: Optional[str] = Field(None, title="East")
    south: Optional[str] = Field(None, title="South")
    north: Optional[str] = Field(None, title="North")


class Language(SchemaBaseModel):
    name: str = Field(..., title="Name")
    code: Optional[str] = Field(None, title="Code")


class LicenseItem(SchemaBaseModel):
    name: str = Field(..., title="License")
    uri: Optional[str] = Field(None, title="URI")


class BibliographicCitationItem(SchemaBaseModel):
    style: Optional[str] = Field(None, title="Style")
    citation: str = Field(..., title="Citation")


class Translator(Editor):
    pass


class Contributor(SchemaBaseModel):
    first_name: Optional[str] = Field(None, title="First name")
    initial: Optional[str] = Field(None, title="Initial")
    last_name: Optional[str] = Field(None, title="Last name")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")
    contribution: Optional[str] = Field(None, title="Contribution")


class Contact(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    role: Optional[str] = Field(None, title="Role")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    email: Optional[str] = Field(None, title="Email")
    telephone: Optional[str] = Field(None, title="Telephone")
    uri: Optional[str] = Field(None, title="URI")


class Source(SchemaBaseModel):
    source_origin: Optional[str] = Field(
        None,
        description="For historical materials, information about the origin(s) of the sources and the rules followed in establishing the sources should be specified. May not be relevant to survey data. ",
        title="Origin of Source",
    )
    source_char: Optional[str] = Field(
        None,
        description="Assessment of characteristics and quality of source material. May not be relevant to survey data.",
        title="Characteristics of Source Noted",
    )
    source_doc: Optional[str] = Field(
        None,
        description="Documentation and Access to Sources",
        title="Source documentation",
    )


class DataSource(SchemaBaseModel):
    name: str = Field(..., title="Dataset name")
    uri: Optional[str] = Field(None, description="Link to the dataset", title="URI")
    note: Optional[str] = Field(None, title="Note")


class Theme(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Unique Identifier")
    name: str = Field(..., title="Name")
    parent_id: Optional[str] = Field(None, title="Parent Identifier")
    vocabulary: Optional[str] = Field(
        None, description="Name of the controlled vocabulary", title="Vocabulary"
    )
    uri: Optional[str] = Field(
        None,
        description="Link to the controlled vocabulary web page, if the theme is from a taxonomy.",
        title="Vocabulary URI",
    )


class Topic(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Unique Identifier")
    name: str = Field(..., title="Topic")
    parent_id: Optional[str] = Field(
        None,
        description="For subtopics, provide the ID of the parent topic",
        title="Parent topic Identifier",
    )
    vocabulary: Optional[str] = Field(
        None,
        description="Name of the controlled vocabulary, if the topic is from a taxonomy.",
        title="Vocabulary",
    )
    uri: Optional[str] = Field(
        None,
        description="Link to the controlled vocabulary web page, if the topic is from a taxonomy.",
        title="Vocabulary URI",
    )


class Discipline(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Unique Identifier")
    name: str = Field(..., title="Discipline title or name")
    parent_id: Optional[str] = Field(
        None, description="Parent discipline ID", title="Parent discipline Identifier"
    )
    vocabulary: Optional[str] = Field(
        None, description="Vocabulary", title="Vocabulary"
    )
    uri: Optional[str] = Field(None, description="Website link", title="URI")


class Type(Enum):
    isPartOf = "isPartOf"
    hasPart = "hasPart"
    isVersionOf = "isVersionOf"
    isFormatOf = "isFormatOf"
    hasFormat = "hasFormat"
    references = "references"
    isReferencedBy = "isReferencedBy"
    isBasedOn = "isBasedOn"
    isBasisFor = "isBasisFor"
    requires = "requires"
    isRequiredBy = "isRequiredBy"


class Relation(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    type: Optional[Type] = Field(None, title="Type")


class Link(SchemaBaseModel):
    uri: str = Field(..., title="URI")
    description: Optional[str] = Field(None, title="Description")


class Reproducibility(SchemaBaseModel):
    statement: Optional[str] = Field(None, title="Statement")
    links: Optional[List[Link]] = Field(None, title="Link")


class Tag(SchemaBaseModel):
    tag: Optional[str] = Field(None, title="Tag")
    tag_group: Optional[str] = Field(None, title="Tag group")


class OriginDescription(SchemaBaseModel):
    harvest_date: Optional[str] = Field(
        None, description="Harvest date using UTC date format"
    )
    altered: Optional[bool] = Field(
        None,
        description="If the metadata was altered before dissemination",
        title="Metadata altered",
    )
    base_url: Optional[str] = Field(
        None, description="Base URL of the originating repository"
    )
    identifier: Optional[str] = Field(
        None,
        description="Unique idenifiter of the item from the originating repository",
    )
    date_stamp: Optional[str] = Field(
        None,
        description="Datestamp (UTC date format) of the metadata record disseminated by the originating repository",
    )
    metadata_namespace: Optional[str] = Field(
        None,
        description="Metadata namespace URI of the metadata format of the record harvested from the originating repository",
    )


class ProvenanceSchema(SchemaBaseModel):
    """
    Provenance of metadata based on the OAI provenance schema (http://www.openarchives.org/OAI/2.0/provenance.xsd)
    """

    origin_description: Optional[OriginDescription] = Field(
        None, title="Origin description"
    )


class KeywordItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    vocabulary: Optional[str] = Field(None, title="Vocabulary name")
    uri: Optional[str] = Field(None, title="Vocabulary URI")


class DocumentDescription(SchemaBaseModel):
    """
    Document Description
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    title_statement: TitleStatement = Field(..., description="Study title")
    authors: Optional[List[Author]] = Field(
        None, description="Authors", title="Authors"
    )
    editors: Optional[List[Editor]] = Field(
        None, description="Editors", title="Editors"
    )
    date_created: Optional[str] = Field(
        None, description="Date of creation", title="Date created"
    )
    date_available: Optional[str] = Field(
        None,
        description="Date (often a range) that the resource will become or did become available.",
        title="Date available",
    )
    date_modified: Optional[str] = Field(
        None,
        description="Date on which the resource was changed.",
        title="Date last modified",
    )
    date_published: Optional[str] = Field(
        None,
        description="Date on which document was published.",
        title="Date published",
    )
    identifiers: Optional[List[Identifier]] = Field(
        None, description="Other identifiers", title="Other identifiers"
    )
    type: Optional[str] = Field(
        None,
        description="Valid values include - `article`, `book`, `booklet`, `collection`, `conference`, `inbook`, `incollection`, `inproceeding`,`manual`, `masterthesis`, `patent`, `phdthesis`, `proceedings`, `techreport`, `working-paper`, `website`, `other` ",
        title="Resource type",
    )
    status: Optional[str] = Field(
        None,
        description="Status of the document - e.g. `Draft`, `Draft released for comment`, `Final draft released for comment`, `Final` ",
        title="Status",
    )
    description: Optional[str] = Field(
        None,
        description="An account of the content of the resource.",
        title="Description",
    )
    toc: Optional[str] = Field(
        None, description="Table of contents", title="Table of contents"
    )
    toc_structured: Optional[List[TocStructuredItem]] = Field(
        None, description="Table of contents", title="Table of contents"
    )
    abstract: Optional[str] = Field(
        None, description="A summary of the content", title="Abstract"
    )
    notes: Optional[List[Note]] = Field(None, title="Notes")
    scope: Optional[str] = Field(
        None,
        description="The extent or scope of the content of the resource. This fields maps to Dublin Core's coverage field.",
        title="Scope",
    )
    ref_country: Optional[List[RefCountryItem]] = Field(None, title="Reference country")
    geographic_units: Optional[List[GeographicUnit]] = Field(
        None,
        description="List of geographic locations (regions, countries, states, provinces, etc.) describing the geographic coverahe of the research project.",
        title="Geographic locations",
    )
    bbox: Optional[List[BboxItem]] = Field(None, title="Geographic bounding box")
    spatial_coverage: Optional[str] = Field(
        None,
        description="The spatial extent or scope of the content of the resource.",
        title="Spatial coverage",
    )
    temporal_coverage: Optional[str] = Field(
        None,
        description="The temporal extent or scope of the content of the resource.",
        title="Temporal coverage",
    )
    publication_frequency: Optional[str] = Field(
        None,
        description="Current stated publication frequency of either an item or an update to an item. Dates are included when the beginning date of the current frequency is not the same as the beginning date of publication.",
        title="Publication frequency",
    )
    languages: Optional[List[Language]] = Field(
        None,
        description="Documentation language e.g. English, French, etc.",
        title="Language",
    )
    license: Optional[List[LicenseItem]] = Field(None, title="License")
    bibliographic_citation: Optional[List[BibliographicCitationItem]] = Field(
        None,
        description="A bibliographic reference for the resource.",
        title="Bibliographic citation",
    )
    chapter: Optional[str] = Field(
        None, description="A chapter or section number", title="Chapter number"
    )
    edition: Optional[str] = Field(
        None, description="The edition of a book", title="Edition"
    )
    institution: Optional[str] = Field(
        None,
        description="The sponsoring institution of a document.",
        title="Institution",
    )
    journal: Optional[str] = Field(
        None, description="Name of the Journal", title="Journal name"
    )
    volume: Optional[str] = Field(
        None, description="Volume number", title="Volume number"
    )
    number: Optional[str] = Field(
        None,
        description="The number of a journal, magazine, technical report, or of a work in a series. An issue of a journal or magazine is usually identified by its volume and number; the organization that issues a technical report usually gives it a number; and sometimes books are given numbers in a named series.",
        title="Number",
    )
    pages: Optional[str] = Field(
        None,
        description="One or more page numbers or ranges of number, such as 37--42, or 7,53,82--94",
        title="Page numbers",
    )
    series: Optional[str] = Field(
        None,
        description="The name given to a series or set of books. When citing an entire book, the title field gives its title and the optional series field gives the name of a series in which the book was published.",
        title="Series name",
    )
    publisher: Optional[str] = Field(
        None,
        description="Entity responsible for making the resource available",
        title="Publisher",
    )
    publisher_address: Optional[str] = Field(
        None,
        description="For major publishing houses, just the city is given. For small publishers, you can help the reader by giving the complete address.",
        title="Publisher's address",
    )
    annote: Optional[str] = Field(
        None,
        description="For annotation, element will not be used by standard bibliography styles like the MLA, APA or Chicago, but may be used by others that produce an annotated bibliography.",
        title="Annotation",
    )
    booktitle: Optional[str] = Field(
        None,
        description="Title of a book, part of which is being cited",
        title="Book title",
    )
    crossref: Optional[str] = Field(
        None,
        description="The database key of the entry being cross referenced",
        title="Cross reference",
    )
    howpublished: Optional[str] = Field(
        None,
        description="The element is used to store the notice for unusual publications. The first word should be capitalized. For example, `WebPage`, or `Distributed at the local tourist office`",
        title="Store the notice for unusual publications",
    )
    key: Optional[str] = Field(
        None,
        description="A key is a field used for alphabetizing, cross referencing, and creating a label when the `author' information is missing",
        title="Key",
    )
    organization: Optional[str] = Field(
        None,
        description="The organization that sponsors a conference or that publishes a manual",
        title="Organization",
    )
    url: Optional[List[str]] = Field(
        None, description="URL of the document, preferably a permanent URL", title="URL"
    )
    translators: Optional[List[Translator]] = Field(
        None, description="Translators", title="Translators"
    )
    contributors: Optional[List[Contributor]] = Field(
        None, description="Contributors", title="Contributors"
    )
    acknowledgement_statement: Optional[str] = Field(
        None, description="Acknowledgement statement", title="Acknowledgement statement"
    )
    contacts: Optional[List[Contact]] = Field(
        None, description="Contacts", title="Contacts"
    )
    rights: Optional[str] = Field(
        None,
        description="Information about rights held in and over the resource.",
        title="Rights",
    )
    copyright: Optional[str] = Field(
        None,
        description="Statement and identifier indicating the legal ownership and rights regarding use and re-use of all or part of the resource.",
        title="Copyright",
    )
    usage_terms: Optional[str] = Field(
        None,
        description="Terms Governing Use and Reproduction",
        title="Terms governing use and reproduction",
    )
    disclaimer: Optional[str] = Field(
        None, description="Disclaimer", title="Disclaimer"
    )
    security_classification: Optional[str] = Field(
        None,
        description="Specifics pertaining to the security classification associated with the document, title, abstract, contents note, and/or the author. In addition, it can contain handling instructions and external dissemination information pertaining to the dissemination of the document, title, abstract, contents note, and author.",
        title="Security classification control",
    )
    access_restrictions: Optional[str] = Field(
        None,
        description="Information about restrictions imposed on access to the described materials.",
        title="Restrictions on Access",
    )
    sources: Optional[List[Source]] = Field(
        None,
        description="Description of sources used. The element is nestable so that the sources statement might encompass a series of discrete source statements, each of which could contain the facts about an individual source. ",
        title="Sources",
    )
    data_sources: Optional[List[DataSource]] = Field(
        None,
        description="Used to list the book(s), article(s), serial(s), and/or machine-readable data file(s)--if any--that served as the source(s) of the data collection.",
        title="Data Sources",
    )
    keywords: Optional[List[KeywordItem]] = Field(
        None, description="Keywords", title="Keywords"
    )
    themes: Optional[List[Theme]] = Field(None, description="Themes")
    topics: Optional[List[Topic]] = Field(
        None,
        description="Topics covered by the table (ideally, the list of topics will be a controlled vocabulary)",
        title="Topics",
    )
    disciplines: Optional[List[Discipline]] = Field(
        None,
        description="Disciplines e.g. `Social sciences, economics`, `Natural sciences, biology`",
        title="Disciplines",
    )
    audience: Optional[str] = Field(
        None,
        description="A category of user for whom the resource is intended.",
        title="Audience",
    )
    mandate: Optional[str] = Field(
        None,
        description="A category of user for whom the resource is intended.",
        title="Audience",
    )
    pricing: Optional[str] = Field(
        None,
        description="Current price of an item or the special export price of an item in any currency.",
        title="Pricing",
    )
    relations: Optional[List[Relation]] = Field(
        None, description="Related documents", title="Document relations"
    )
    reproducibility: Optional[Reproducibility] = Field(None, title="Reproducibility")


class ScriptSchemaDraft(SchemaBaseModel):
    """
    Schema for Document data type
    """
    _metadata_type__:str = PrivateAttr("document")
    _metadata_type_version__:str = PrivateAttr("0.1.0") 

    idno: Optional[str] = Field(
        None, description="Project unique identifier", title="Project unique identifier"
    )
    metadata_information: Optional[MetadataInformation] = Field(
        None, description="Document description", title="Document metadata information"
    )
    document_description: DocumentDescription = Field(
        ..., description="Document Description", title="Document Description"
    )
    provenance: Optional[List[ProvenanceSchema]] = Field(None, description="Provenance")
    tags: Optional[List[Tag]] = Field(None, description="Tags", title="Tags")
    additional: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )
