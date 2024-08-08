# generated by datamodel-codegen:
#   filename:  timeseries-db-schema.json
#   timestamp: 2024-07-24T21:06:31+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Extra, Field

from .schema_base_model import SchemaBaseModel


class Overwrite(Enum):
    """
    Overwrite database if already exists?
    """

    yes = "yes"
    no = "no"


class Producer(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Name (required)", title="Name")
    abbr: Optional[str] = Field(None, title="Abbreviation")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")


class MetadataInformation(SchemaBaseModel):
    """
    Document description
    """

    class Config:
        extra = Extra.forbid

    title: Optional[str] = Field(None, description="Document title", title="Document title")
    idno: Optional[str] = Field(None, title="Unique ID number for the document")
    producers: Optional[List[Producer]] = Field(None, description="List of producers", title="Producers")
    prod_date: Optional[str] = Field(
        None, description="Document production date using format(YYYY-MM-DD)", title="Date of Production"
    )
    version: Optional[str] = Field(
        None, description="Identify and describe the current version of the document", title="Document version"
    )


class Identifier(SchemaBaseModel):
    type: Optional[str] = Field(
        None, description="Type of identifier e.g. `doi`, `handle`, `other`", title="Identifier type"
    )
    identifier: str = Field(..., title="Identifier")


class TitleStatement(SchemaBaseModel):
    """
    Study title
    """

    idno: str = Field(
        ...,
        description="The ID number of a database is a unique number that is used to identify a particular database.",
        title="Unique user defined ID",
    )
    identifiers: Optional[List[Identifier]] = Field(None, description="Other identifiers", title="Other identifiers")
    title: str = Field(
        ...,
        description=(
            "The title is the official name of the survey as it is stated on the questionnaire or as it appears in the"
            " design documents. The following items should be noted:\n - Include the reference year(s) of the survey in"
            " the title. \n - Do not include the abbreviation of the survey name in the title. \n - As the survey title"
            " is a proper noun, the first letter of each word should be capitalized (except for prepositions or other"
            " conjunctions).\n - Including the country name in the title is optional."
        ),
        title="Survey title",
    )
    sub_title: Optional[str] = Field(None, description="A short subtitle for the survey", title="Survey subtitle")
    alternate_title: Optional[str] = Field(
        None,
        description=(
            "The abbreviation of a survey is usually the first letter of each word of the titled survey. The survey"
            " reference year(s) may be included."
        ),
        title="Abbreviation or Acronym",
    )
    translated_title: Optional[str] = Field(
        None,
        description="In countries with more than one official language, a translation of the title may be provided.",
        title="Translated Title",
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
    abbreviation: Optional[str] = Field(None, description="Abbreviation", title="Abbreviation")
    email: Optional[str] = Field(None, description="Email", title="Email")
    uri: Optional[str] = Field(None, title="URI")


class VersionItem(SchemaBaseModel):
    version: str = Field(..., description="Version number e.g. v1.0", title="Version")
    date: str = Field(..., title="Version Date")
    responsibility: Optional[str] = Field(
        None, description="Version Responsibility Statement", title="Version Responsibility Statement"
    )
    notes: Optional[str] = Field(None, title="Version Notes")


class UpdateScheduleItem(SchemaBaseModel):
    update: Optional[str] = Field(None, title="Schedule date")


class TimeCoverageItem(SchemaBaseModel):
    start: Optional[str] = Field(
        None, description="Time coverage, start date (oldest date for which data are available)", title="Start date"
    )
    end: Optional[str] = Field(
        None, description="Time coverage, end date (most recent date for which data are available)", title="End date"
    )


class PeriodicityItem(SchemaBaseModel):
    period: Optional[str] = Field(None, title="Period")


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
    id: str = Field(..., title="Unique Identifier")
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


class Keyword(SchemaBaseModel):
    name: str = Field(..., title="Keyword")
    vocabulary: Optional[str] = Field(None, title="Vocabulary")
    uri: Optional[str] = Field(None, title="URI")


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


class Sponsor(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Name of the sponsoring agency", title="Funding Agency/Sponsor")
    abbreviation: Optional[str] = Field(
        None, description="Abbreviation (acronym) of the sponsoring agency", title="Abbreviation"
    )
    role: Optional[str] = Field(None, description="Specific role of the sponsoring agency", title="Role")
    grant: Optional[str] = Field(None, description="Grant number", title="Grant")
    uri: Optional[str] = Field(None, title="URI")


class Acknowledgment(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")
    uri: Optional[str] = Field(None, title="URI")


class Contact(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    role: Optional[str] = Field(None, title="Role")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    email: Optional[str] = Field(None, title="Email")
    telephone: Optional[str] = Field(None, title="Telephone")
    uri: Optional[str] = Field(None, title="URI")


class Link(SchemaBaseModel):
    uri: Optional[str] = Field(None, title="URI")
    description: Optional[str] = Field(None, title="Description")


class Language(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Language title", title="Name")
    code: Optional[str] = Field(None, title="code")


class AccessOption(SchemaBaseModel):
    type: str = Field(..., description="Access type e.g. API, Bulk, Query, etc", title="Access type")
    uri: Optional[str] = Field(None, title="URI")
    note: Optional[str] = Field(None, description="Note", title="Note")


class LicenseItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    uri: Optional[str] = Field(None, title="URI")
    note: Optional[str] = Field(None, title="Note")


class Note(SchemaBaseModel):
    note: Optional[str] = Field(None, title="Note")


class DatabaseDescription(SchemaBaseModel):
    """
    Database Description
    """

    class Config:
        extra = Extra.forbid

    title_statement: TitleStatement = Field(..., description="Study title")
    authoring_entity: Optional[List[AuthoringEntityItem]] = Field(
        None,
        description=(
            "The person, corporate body, or agency responsible for the work's substantive and intellectual content."
            " Repeat the element for each author, and use 'affiliation' attribute if available. Invert first and last"
            " name and use commas."
        ),
        title="Authoring entity",
    )
    abstract: Optional[str] = Field(None, description="A brief description of the database", title="Abstract")
    url: Optional[str] = Field(None, description="Link to the dataset web page", title="Dataset URL")
    type: Optional[str] = Field(None, description="Dataset type", title="Dataset type")
    doi: Optional[str] = Field(None, description="DOI handle", title="DOI")
    date_created: Optional[str] = Field(
        None, description="Date this version of the dataset was created", title="Date of creation"
    )
    date_published: Optional[str] = Field(
        None, description="Date this version of the dataset was published", title="Dataset published date"
    )
    version: Optional[List[VersionItem]] = Field(None, title="Version Statement")
    update_frequency: Optional[str] = Field(
        None,
        description="Dataset frequency of updates (for datasets updated at regular intervals)",
        title="Frequency of update",
    )
    update_schedule: Optional[List[UpdateScheduleItem]] = Field(
        None, description="Dataset schedule of updates", title="Schedule of updates"
    )
    time_coverage: Optional[List[TimeCoverageItem]] = Field(
        None,
        description=(
            "Time coverage for the whole database. This will typically be the min and max dates for which data are"
            " available in any series contained in the database."
        ),
        title="Range of dates covered by the dataset",
    )
    time_coverage_note: Optional[str] = Field(None, description="Time coverage note", title="Time coverage note")
    periodicity: Optional[List[PeriodicityItem]] = Field(
        None,
        description=(
            "Periodicity of the data contained in the database (NOT the periodicity of update of the database). This"
            " describes the various reference periods for the series. Example: `annual`, `quarterly`, `monthly`,"
            " `daily`."
        ),
        title="Periodicity of series",
    )
    themes: Optional[List[Theme]] = Field(None, description="Themes")
    topics: Optional[List[Topic]] = Field(
        None,
        description="Topics covered by the database (ideally, the list of topics will be a controlled vocabulary)",
        title="Topics",
    )
    keywords: Optional[List[Keyword]] = Field(None, description="Keywords")
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
    geographic_coverage_note: Optional[str] = Field(
        None, description="Notes on geographic coverage", title="Geographic coverage notes"
    )
    bbox: Optional[List[BboxItem]] = Field(None, description="Geographic bounding box", title="Geographic bounding box")
    geographic_granularity: Optional[str] = Field(
        None,
        description="Granularity of geographic coverage e.g. `national`, `regional`, `provincial`",
        title="Geographic granularity",
    )
    geographic_area_count: Optional[str] = Field(None, description="Number of geographic areas")
    sponsors: Optional[List[Sponsor]] = Field(
        None,
        description=(
            "The source(s) of funds for production of the work. If different funding agencies sponsored different"
            " stages of the production process, use the 'role' attribute to distinguish them."
        ),
        title="Sponsor/Funding Agency",
    )
    acknowledgments: Optional[List[Acknowledgment]] = Field(
        None, description="Other Acknowledgments", title="Other Acknowledgments"
    )
    acknowledgment_statement: Optional[str] = Field(
        None,
        title=(
            "An overall statement of acknowledgment, which can be used as an alternative (or supplement) to the"
            " itemized list provided in `acknowledgments`."
        ),
    )
    contacts: Optional[List[Contact]] = Field(None, description="Contacts", title="Contacts")
    links: Optional[List[Link]] = Field(None, description="Related links", title="Related links")
    languages: Optional[List[Language]] = Field(None, description="Supported languages")
    access_options: Optional[List[AccessOption]] = Field(
        None, description="Access options e.g. API, Bulk, Query", title="Access options"
    )
    license: Optional[List[LicenseItem]] = Field(None, description="License information", title="License")
    citation: Optional[str] = Field(None, title="Citation")
    notes: Optional[List[Note]] = Field(None, description="Notes", title="Notes")
    disclaimer: Optional[str] = Field(None, title="Disclaimer")
    copyright: Optional[str] = Field(None, title="Copyright")


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


class TimeseriesDatabaseSchema(SchemaBaseModel):
    """
    Schema for timeseries database
    """

    published: Optional[int] = Field(0, description="0=draft, 1=published", title="Status")
    overwrite: Optional[Overwrite] = Field("no", description="Overwrite database if already exists?")
    metadata_information: Optional[MetadataInformation] = Field(
        None, description="Document description", title="Document metadata information"
    )
    database_description: DatabaseDescription = Field(
        ..., description="Database Description", title="Database Description"
    )
    provenance: Optional[List[ProvenanceSchema]] = Field(None, description="Provenance")
    additional: Optional[Dict[str, Any]] = Field(
        None, description="Any other custom metadata not covered by the schema", title="Additional custom metadata"
    )