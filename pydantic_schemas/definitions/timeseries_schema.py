# generated by datamodel-codegen:
#   filename:  timeseries-schema.json
#   timestamp: 2024-07-12T20:05:57+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Extra, Field

from .schema_base_model import SchemaBaseModel


class Producer(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Name (required)", title="Name")
    abbr: Optional[str] = Field(None, title="Abbreviation")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")


class VersionStatement(SchemaBaseModel):
    """
    Version Statement
    """

    version: Optional[str] = Field(None, title="Version")
    version_date: Optional[str] = Field(None, title="Version Date")
    version_resp: Optional[str] = Field(
        None,
        description="The organization or person responsible for the version of the work",
        title="Version Responsibility Statement",
    )
    version_notes: Optional[str] = Field(None, title="Version Notes")


class MetadataInformation(SchemaBaseModel):
    """
    Information on the production of the metadata
    """

    class Config:
        extra = Extra.forbid

    title: Optional[str] = Field(None, description="Document title", title="Document title")
    idno: Optional[str] = Field(None, title="Unique ID number for the document")
    producers: Optional[List[Producer]] = Field(None, description="List of producers", title="Producers")
    prod_date: Optional[str] = Field(
        None, description="Document production date using format(YYYY-MM-DD)", title="Date of Production"
    )
    version_statement: Optional[VersionStatement] = Field(
        None, description="Version Statement", title="Version Statement"
    )


class AuthoringEntityItem(SchemaBaseModel):
    name: str = Field(
        ...,
        description=(
            "Name of the person, corporate body, or agency responsible for the work's substantive and intellectual"
            " content. If a person, invert first and last name and use commas."
        ),
        title="Agency Name",
    )
    affiliation: Optional[str] = Field(None, title="Affiliation")
    abbreviation: Optional[Any] = Field(None, description="Abbreviation", title="Abbreviation")
    email: Optional[Any] = Field(None, description="Email", title="Email")
    uri: Optional[str] = Field(None, title="URI")


class Alias(SchemaBaseModel):
    alias: Optional[str] = Field(None, title="Alias")


class AlternateIdentifier(SchemaBaseModel):
    identifier: str = Field(..., title="Identifier")
    name: Optional[str] = Field(None, title="Identifier name")
    database: Optional[str] = Field(None, title="Database")
    uri: Optional[str] = Field(None, title="URI")
    notes: Optional[str] = Field(None, title="Notes")


class Language(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Language title", title="Name")
    code: Optional[str] = Field(None, title="code")


class Dimension(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    label: str = Field(..., title="Label")
    description: Optional[str] = Field(None, title="Description")


class DefinitionReference(SchemaBaseModel):
    source: Optional[str] = Field(None, title="Source")
    uri: str = Field(..., description="URI", title="URI")
    note: Optional[str] = Field(None, description="Note", title="Note")


class StatisticalConceptReference(DefinitionReference):
    pass


class Concept(SchemaBaseModel):
    name: str = Field(..., title="Name")
    definition: Optional[str] = Field(None, description="Definition", title="Definition")
    uri: Optional[str] = Field(None, description="Website link", title="URI")


class DataCollection(SchemaBaseModel):
    """
    This description should include, when applicable, the sample frame used, the questions used to collect the data, the type of interview, the dates/duration of fieldwork, the sample size and the response rate. Some additional information on questionnaire design and testing, interviewer training, methods used to monitor non-response etc.
    """

    data_source: Optional[str] = Field(None, title="Data source")
    method: Optional[str] = Field(None, title="Data collection method")
    period: Optional[str] = Field(None, title="Data collection period")
    note: Optional[str] = Field(None, title="Data collection note")
    uri: Optional[str] = Field(None, title="Data collection URL")


class MethodologyReference(DefinitionReference):
    pass


class DerivationReference(DefinitionReference):
    pass


class ImputationReference(DefinitionReference):
    pass


class Theme(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Unique Identifier")
    name: str = Field(..., title="Name")
    parent_id: Optional[str] = Field(None, title="Parent Identifier")
    vocabulary: Optional[str] = Field(None, description="Name of the controlled vocabulary", title="Vocabulary")
    uri: Optional[str] = Field(
        None,
        description="Link to the controlled vocabulary web page, if the theme is from a taxonomy.",
        title="Vocabulary URI",
    )


class Topic(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Unique Identifier")
    name: str = Field(..., title="Topic")
    parent_id: Optional[str] = Field(
        None, description="For subtopics, provide the ID of the parent topic", title="Parent topic Identifier"
    )
    vocabulary: Optional[str] = Field(
        None, description="Name of the controlled vocabulary, if the topic is from a taxonomy.", title="Vocabulary"
    )
    uri: Optional[str] = Field(
        None,
        description="Link to the controlled vocabulary web page, if the topic is from a taxonomy.",
        title="Vocabulary URI",
    )


class Discipline(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Unique Identifier")
    name: str = Field(..., title="Discipline title or name")
    parent_id: Optional[str] = Field(None, title="Parent Identifier")
    vocabulary: Optional[str] = Field(None, description="Vocabulary", title="Vocabulary")
    uri: Optional[str] = Field(None, description="Website link", title="URI")


class Mandate(SchemaBaseModel):
    """
    Mandate
    """

    mandate: Optional[str] = Field(None, title="Mandate")
    uri: Optional[str] = Field(None, title="URL")


class TimePeriod(SchemaBaseModel):
    start: Optional[str] = Field(None, title="Start")
    end: Optional[str] = Field(None, title="End")
    notes: Optional[str] = Field(None, title="Notes")


class RefCountryItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Country name")
    code: Optional[str] = Field(None, title="Country code")


class GeographicUnit(SchemaBaseModel):
    name: str = Field(
        ..., description="Name of the geographic unit e.g. 'World', 'Africa', 'Afghanistan'", title="Location name"
    )
    code: Optional[str] = Field(
        None, description="Code of the geographic unit (for countries, preferred = ISO3 code)", title="Location code"
    )
    type: Optional[str] = Field(
        None, description="Type of geographic unit e.g. country, state, region, province etc", title="Type"
    )


class BboxItem(SchemaBaseModel):
    west: Optional[str] = Field(None, title="West")
    east: Optional[str] = Field(None, title="East")
    south: Optional[str] = Field(None, title="South")
    north: Optional[str] = Field(None, title="North")


class AggregationMethodReference(DefinitionReference):
    pass


class LicenseItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    uri: Optional[str] = Field(None, title="URI")
    note: Optional[str] = Field(None, title="Note")


class Link(SchemaBaseModel):
    type: Optional[str] = Field(None, description="Link types - API, website, etc.", title="Link type")
    description: Optional[str] = Field(None, title="Description")
    uri: Optional[str] = Field(None, title="URI")


class ApiDocumentationItem(SchemaBaseModel):
    description: Optional[str] = Field(None, title="Description")
    uri: Optional[str] = Field(None, title="URI")


class OtherIdentifier(SchemaBaseModel):
    type: Optional[str] = Field(None, title="Type")
    identifier: Optional[str] = Field(None, title="Identifier")


class AuthorIdItem(SchemaBaseModel):
    type: Optional[str] = Field(None, title="Type")
    id: Optional[str] = Field(None, title="Identifier")


class Author(SchemaBaseModel):
    first_name: Optional[str] = Field(None, title="First name")
    initial: Optional[str] = Field(None, title="Initial")
    last_name: Optional[str] = Field(None, title="Last name")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    author_id: Optional[List[AuthorIdItem]] = Field(None, title="Author ID")
    full_name: Optional[str] = Field(None, title="Full name")


class Dataset(SchemaBaseModel):
    idno: Optional[str] = Field(None, title="Identifier (IDNO)")
    title: Optional[str] = Field(
        None, description="Title of the dataset inluding the country and year if relevant", title="Title"
    )
    uri: Optional[str] = Field(None, title="URI")


class Source(SchemaBaseModel):
    idno: Optional[str] = Field(None, title="Source ID")
    other_identifiers: Optional[List[OtherIdentifier]] = Field(None, title="Identifiers")
    type: Optional[str] = Field(None, title="Source type")
    name: str = Field(..., description="Source name", title="Name")
    organization: Optional[str] = Field(None, title="Organization")
    authors: Optional[List[Author]] = Field(None, title="Authors")
    datasets: Optional[List[Dataset]] = Field(None, title="Datasets")
    publisher: Optional[str] = Field(None, title="Publisher")
    publication_date: Optional[str] = Field(None, title="Publication date")
    uri: Optional[str] = Field(None, title="URI")
    access_date: Optional[str] = Field(None, title="Access date")
    note: Optional[str] = Field(None, title="Note")


class DirectSource(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    organization: Optional[str] = Field(None, title="Organization")
    uri: Optional[str] = Field(None, title="URI")
    note: Optional[str] = Field(None, title="Note")


class Keyword(SchemaBaseModel):
    name: str = Field(..., title="Keyword")
    vocabulary: Optional[str] = Field(None, title="Vocabulary")
    uri: Optional[str] = Field(None, title="URI")


class Acronym(SchemaBaseModel):
    acronym: str = Field(..., title="Acronym or abbreviation")
    expansion: str = Field(..., title="Expansion of the acronym or abbreviation")
    occurrence: Optional[float] = Field(None, title="Occurrence of the acronym in the document")


class Erratum(SchemaBaseModel):
    date: Optional[str] = Field(
        None, description="Date when the erratum was reported or published", title="Date of erratum"
    )
    description: Optional[str] = Field(
        None,
        description="A description of the erratum, with information on which data or metadata were impacted",
        title="Description of the erratum",
    )
    uri: Optional[str] = Field(None, title="URI")


class Acknowledgement(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")


class Note(SchemaBaseModel):
    note: Optional[str] = Field(None, title="Note")
    type: Optional[str] = Field(None, description="Type of note", title="Note type")
    uri: Optional[str] = Field(None, title="URI")


class RelatedIndicator(SchemaBaseModel):
    code: Optional[str] = Field(None, title="Indicator code")
    label: Optional[str] = Field(None, title="Indicator name")
    uri: Optional[str] = Field(None, title="URI")
    relationship: Optional[str] = Field(None, title="Relationship")
    type: Optional[str] = Field(None, title="Type")


class ComplianceItem(SchemaBaseModel):
    standard: str = Field(..., title="Standard name")
    abbreviation: Optional[str] = Field(None, title="Abbreviation")
    custodian: Optional[str] = Field(None, title="Name of the custodian organization")
    uri: Optional[str] = Field(None, title="URI")


class FrameworkItem(SchemaBaseModel):
    name: str = Field(..., title="Name")
    abbreviation: Optional[str] = Field(None, title="Abbreviation")
    custodian: Optional[str] = Field(None, title="Custodian")
    description: Optional[str] = Field(None, title="Description")
    goal_id: Optional[str] = Field(None, title="Goal ID")
    goal_name: Optional[str] = Field(None, title="Goal name")
    goal_description: Optional[str] = Field(None, title="Goal description")
    target_id: Optional[str] = Field(None, title="target ID")
    target_name: Optional[str] = Field(None, title="Target name")
    target_description: Optional[str] = Field(None, title="Target description")
    indicator_id: Optional[str] = Field(None, title="Indicator ID")
    indicator_name: Optional[str] = Field(None, title="Indicator name")
    indicator_description: Optional[str] = Field(None, title="Indicator description")
    uri: Optional[str] = Field(None, title="URI")
    notes: Optional[str] = Field(None, title="Description")


class SeriesGroup(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    description: Optional[str] = Field(
        None, description="A brief description of the series group.", title="Description"
    )
    version: Optional[str] = Field(None, title="Version")
    uri: Optional[str] = Field(None, title="URI")


class Contact(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    role: Optional[str] = Field(None, title="Role")
    position: Optional[str] = Field(None, title="Position")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    email: Optional[str] = Field(None, title="Email")
    telephone: Optional[str] = Field(None, title="Telephone")
    uri: Optional[str] = Field(None, title="URI")


class SeriesDescription(SchemaBaseModel):
    """
    Series information
    """

    idno: str = Field(..., description="Unique series ID", title="Series unique ID")
    doi: Optional[str] = Field(None, title="DOI handle")
    name: str = Field(..., title="Series Name")
    display_name: Optional[str] = Field(None, title="Display Name")
    authoring_entity: Optional[List[AuthoringEntityItem]] = Field(
        None,
        description=(
            "The person, corporate body, or agency responsible for the work's substantive and intellectual content."
            " Repeat the element for each author, and use 'affiliation' attribute if available. Invert first and last"
            " name and use commas."
        ),
        title="Authoring entity",
    )
    database_id: Optional[str] = Field(None, description="Series database ID", title="Database ID")
    database_name: Optional[str] = Field(None, description="Series database name", title="Database name")
    date_last_update: Optional[str] = Field(None, title="Last updated date")
    date_released: Optional[str] = Field(None, title="Date released")
    version_statement: Optional[VersionStatement] = Field(
        None, description="Version Statement", title="Version Statement"
    )
    aliases: Optional[List[Alias]] = Field(None, title="Series other names")
    alternate_identifiers: Optional[List[AlternateIdentifier]] = Field(None, title="Alternate identifiers")
    languages: Optional[List[Language]] = Field(None, description="Supported languages")
    measurement_unit: Optional[str] = Field(None, title="Series unit of measure")
    power_code: Optional[str] = Field(
        None,
        description=(
            "Power of 10 by which the reported statistics should be multiplied. e.g. '6' indicating millions of units"
        ),
        title="Power code",
    )
    dimensions: Optional[List[Dimension]] = Field(None, title="Dimensions")
    release_calendar: Optional[str] = Field(None, description="Release calendar", title="Release calendar")
    periodicity: Optional[str] = Field(None, title="Periodicity of data")
    base_period: Optional[str] = Field(None, title="Base period")
    definition_short: Optional[str] = Field(None, title="Definition short")
    definition_long: Optional[str] = Field(None, title="Definition long")
    definition_references: Optional[List[DefinitionReference]] = Field(
        None,
        description="URL to standard definition of the indicator (international or national standard)",
        title="Definition references",
    )
    statistical_concept: Optional[str] = Field(None, title="Statistical concept")
    statistical_concept_references: Optional[List[StatisticalConceptReference]] = Field(
        None, description="URLs for statistical concept references", title="Statistical concept references"
    )
    concepts: Optional[List[Concept]] = Field(None, description="Related concepts", title="Related concepts")
    universe: Optional[str] = Field(
        None,
        description="Target population (the statistical universe about which information is sought)",
        title="Universe",
    )
    data_collection: Optional[DataCollection] = Field(
        None,
        description=(
            " This description should include, when applicable, the sample frame used, the questions used to collect"
            " the data, the type of interview, the dates/duration of fieldwork, the sample size and the response rate."
            " Some additional information on questionnaire design and testing, interviewer training, methods used to"
            " monitor non-response etc."
        ),
        title="Data collection",
    )
    methodology: Optional[str] = Field(None, title="Methodology")
    methodology_references: Optional[List[MethodologyReference]] = Field(
        None, description="URLs for methodology references", title="Methodology references"
    )
    derivation: Optional[str] = Field(None, title="Derivation")
    derivation_references: Optional[List[DerivationReference]] = Field(
        None, description="URLs for derivation references", title="Derivation references"
    )
    imputation: Optional[str] = Field(None, title="Imputations")
    imputation_references: Optional[List[ImputationReference]] = Field(
        None, description="URLs for imputation references", title="Imputation references"
    )
    seasonal_adjustment: Optional[str] = Field(
        None,
        description=(
            "Application of statistical techniques to time series data in order to remove seasonal fluctuations and to"
            " better understand underlying trends."
        ),
        title="Seasonal adjustment",
    )
    adjustments: Optional[List[str]] = Field(
        None,
        description=(
            "Description of any adjustments with respect to use of standard classifications and harmonization of"
            " breakdowns for age group and other dimensions, or adjustments made for compliance with specific"
            " international or national definitions."
        ),
        title="Other adjustments",
    )
    missing: Optional[str] = Field(None, title="Treatment of missing values")
    validation_rules: Optional[List[str]] = Field(
        None, description="Set of rules to validate values for indicators, e.g. range checks", title="Validation rules"
    )
    quality_checks: Optional[str] = Field(None, title="Quality control methods")
    quality_note: Optional[str] = Field(None, title="Note on data quality")
    sources_discrepancies: Optional[str] = Field(None, title="Discrepency sources")
    series_break: Optional[str] = Field(None, title="Breaks in series")
    limitation: Optional[str] = Field(None, title="Limitations  and exceptions")
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
    relevance: Optional[str] = Field(None, title="Relavance")
    mandate: Optional[Mandate] = Field(None, description="Mandate", title="Mandate")
    time_periods: Optional[List[TimePeriod]] = Field(None, title="Series dates")
    ref_country: Optional[List[RefCountryItem]] = Field(
        None, description="List of countries for which data are available", title="Reference country"
    )
    geographic_units: Optional[List[GeographicUnit]] = Field(
        None,
        description=(
            "List of geographic units (regions, countries, states, provinces, etc.) for which data are available in the"
            " database."
        ),
        title="Geographic locations",
    )
    bbox: Optional[List[BboxItem]] = Field(None, title="Geographic bounding box")
    aggregation_method: Optional[str] = Field(None, title="Aggregation method")
    aggregation_method_references: Optional[List[AggregationMethodReference]] = Field(
        None, description="URLs for aggregation method references", title="Aggregation method references"
    )
    disaggregation: Optional[str] = Field(None, title="Dissaggregation")
    license: Optional[List[LicenseItem]] = Field(None, description="License information", title="License")
    confidentiality: Optional[str] = Field(
        None, description="Confidentiality statement", title="Confidentiality statement"
    )
    confidentiality_status: Optional[str] = Field(None, title="Confidentiality status")
    confidentiality_note: Optional[str] = Field(None, title="Confidentiality note")
    citation_requirement: Optional[str] = Field(
        None, description="Citation requirement (can include a specific recommended citation)"
    )
    links: Optional[List[Link]] = Field(None, description="Links to API calls, websites, etc.", title="Series links")
    api_documentation: Optional[List[ApiDocumentationItem]] = Field(None, description="API Documentation")
    sources: Optional[List[Source]] = Field(None, description="Sources", title="Sources")
    sources_note: Optional[str] = Field(None, title="Notes form original sources")
    direct_sources: Optional[List[DirectSource]] = Field(
        None, description="Refers to the sources from where the data was directly collected", title="Direct sources"
    )
    keywords: Optional[List[Keyword]] = Field(None, description="Keywords")
    acronyms: Optional[List[Acronym]] = Field(None, description="Acronyms")
    errata: Optional[List[Erratum]] = Field(
        None, description="List of corrected errors in data or metadata", title="Errata"
    )
    acknowledgements: Optional[List[Acknowledgement]] = Field(
        None, description="Acknowledgments of persons or organizations", title="Other acknowledgments"
    )
    acknowledgement_statement: Optional[str] = Field(
        None, description="Acknowledgement statement", title="Acknowledgement statement"
    )
    disclaimer: Optional[str] = Field(None, title="Disclaimer")
    notes: Optional[List[Note]] = Field(None, description="Notes", title="Notes")
    related_indicators: Optional[List[RelatedIndicator]] = Field(None, description="Related indicators")
    compliance: Optional[List[ComplianceItem]] = Field(
        None, description="Compliance with international resolution", title="Compliance with international resolution"
    )
    framework: Optional[List[FrameworkItem]] = Field(None, title="Framework")
    series_groups: Optional[List[SeriesGroup]] = Field(
        None, description="Series included in groups", title="Series groups"
    )
    contacts: Optional[List[Contact]] = Field(None, description="Contacts", title="Contacts")


class DataType(Enum):
    string = "string"
    integer = "integer"
    float = "float"
    date = "date"
    boolean = "boolean"


class ColumnType(Enum):
    dimension = "dimension"
    time_period = "time_period"
    measure = "measure"
    attribute = "attribute"
    indicator_id = "indicator_id"
    indicator_name = "indicator_name"
    annotation = "annotation"
    geography = "geography"
    observation_value = "observation_value"


class TimePeriodFormat(Enum):
    YYYY = "YYYY"
    YYYY_MM = "YYYY-MM"
    YYYY_MM_DD = "YYYY-MM-DD"
    YYYY_MM_DDTHH_MM_SS = "YYYY-MM-DDTHH:MM:SS"
    YYYY_MM_DDTHH_MM_SSZ = "YYYY-MM-DDTHH:MM:SSZ"


class CodeListItem(SchemaBaseModel):
    code: Optional[str] = Field(None, title="Code")
    name: Optional[str] = Field(None, title="Name")
    description: Optional[str] = Field(None, title="Description")


class CodeListReference(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Identifier (ID)")
    name: Optional[str] = Field(None, title="Name")
    version: Optional[str] = Field(None, title="Version")
    uri: str = Field(..., description="URI", title="URI")
    note: Optional[str] = Field(None, description="Note", title="Note")


class DataStructureItem(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Name (required)", title="Name")
    label: Optional[str] = Field(None, title="Label")
    description: Optional[str] = Field(None, title="Description")
    data_type: Optional[DataType] = Field(None, title="Data type")
    column_type: Optional[ColumnType] = Field(None, title="Column type")
    time_period_format: Optional[TimePeriodFormat] = Field(None, title="Time period format")
    code_list: Optional[List[CodeListItem]] = Field(None, title="Code list")
    code_list_reference: Optional[CodeListReference] = Field(None, title="Code list reference")


class Operator(Enum):
    field_ = "="
    field__ = "!="
    field__1 = "<"
    field___1 = "<="
    field__2 = ">"
    field___2 = ">="
    in_ = "in"
    field_in = "!in"


class Filter(SchemaBaseModel):
    field: Optional[str] = Field(None, title="Field")
    operator: Optional[Operator] = Field(None, title="Operator")
    value: Optional[Union[str, float, bool, List[Any]]] = Field(None, title="Value")


class DataNote(SchemaBaseModel):
    filters: Optional[List[Filter]] = Field(None, description="Filters", title="Filters")
    note: Optional[str] = Field(None, title="Note")


class Tag(SchemaBaseModel):
    tag: Optional[str] = Field(None, title="Tag")
    tag_group: Optional[str] = Field(None, title="Tag group")


class NameType(Enum):
    Personal = "Personal"
    Organizational = "Organizational"


class Creator(SchemaBaseModel):
    name: str = Field(..., title="Name")
    nameType: Optional[NameType] = Field(None, title="Name type")
    givenName: Optional[str] = Field(None, title="Given name")
    familyName: Optional[str] = Field(None, title="Family name")


class TitleType(Enum):
    AlternativeTitle = "AlternativeTitle"
    Subtitle = "Subtitle"
    TranslatedTitle = "TranslatedTitle"
    Other = "Other"


class Title(SchemaBaseModel):
    title: str = Field(..., title="Title")
    titleType: Optional[TitleType] = Field(None, title="Title type")
    lang: Optional[str] = Field(None, title="Language")


class ResourceTypeGeneral(Enum):
    Audiovisual = "Audiovisual"
    Collection = "Collection"
    DataPaper = "DataPaper"
    Dataset = "Dataset"
    Event = "Event"
    Image = "Image"
    InteractiveResource = "InteractiveResource"
    Model = "Model"
    PhysicalObject = "PhysicalObject"
    Service = "Service"
    Software = "Software"
    Sound = "Sound"
    Text = "Text"
    Workflow = "Workflow"
    Other = "Other"


class Types(SchemaBaseModel):
    resourceType: str = Field(..., title="Resource type")
    resourceTypeGeneral: Optional[ResourceTypeGeneral] = Field(None, title="Resource type general")


class DataciteSchema(SchemaBaseModel):
    """
    Schema based on Datacite elements
    """

    doi: Optional[str] = Field(None, title="DOI")
    prefix: Optional[str] = Field(None, title="Prefix")
    suffix: Optional[str] = Field(None, title="Suffix")
    creators: Optional[List[Creator]] = Field(None, title="Creators")
    titles: Optional[List[Title]] = Field(None, title="Titles")
    publisher: Optional[str] = Field(None, title="Publisher")
    publicationYear: Optional[str] = Field(None, title="Publication year")
    types: Optional[Types] = Field(None, title="Types")
    url: Optional[str] = Field(None, title="URL")
    language: Optional[str] = Field(None, title="Language")


class OriginDescription(SchemaBaseModel):
    harvest_date: Optional[str] = Field(None, description="Harvest date using UTC date format")
    altered: Optional[bool] = Field(
        None, description="If the metadata was altered before dissemination", title="Metadata altered"
    )
    base_url: Optional[str] = Field(None, description="Base URL of the originating repository")
    identifier: Optional[str] = Field(None, description="Unique idenifiter of the item from the originating repository")
    date_stamp: Optional[str] = Field(
        None,
        description="Datestamp (UTC date format) of the metadata record disseminated by the originating repository",
    )
    metadata_namespace: Optional[str] = Field(
        None,
        description=(
            "Metadata namespace URI of the metadata format of the record harvested from the originating repository"
        ),
    )


class ProvenanceSchema(SchemaBaseModel):
    """
    Provenance of metadata based on the OAI provenance schema (http://www.openarchives.org/OAI/2.0/provenance.xsd)
    """

    origin_description: Optional[OriginDescription] = Field(None, title="Origin description")


class TimeseriesSchema(SchemaBaseModel):
    """
    Schema for timeseries data type
    """

    idno: Optional[str] = Field(None, description="Project unique identifier", title="Project unique identifier")
    metadata_information: Optional[MetadataInformation] = Field(
        None, description="Information on the production of the metadata", title="Metadata creation"
    )
    series_description: SeriesDescription = Field(..., description="Series information")
    data_structure: Optional[List[DataStructureItem]] = Field(None, description="Data structure definition")
    data_notes: Optional[List[DataNote]] = Field(None, description="Data notes", title="Data notes")
    datacite: Optional[DataciteSchema] = Field(None, description="DataCite metadata for generating DOI")
    provenance: Optional[List[ProvenanceSchema]] = Field(None, description="Provenance")
    tags: Optional[List[Tag]] = Field(None, description="Tags", title="Tags (user-defined)")
    additional: Optional[Dict[str, Any]] = Field(
        None, description="Any other custom metadata not covered by the schema", title="Additional custom metadata"
    )
