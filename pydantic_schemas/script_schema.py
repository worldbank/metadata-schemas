# generated by datamodel-codegen:
#   filename:  script-schema.json
#   timestamp: 2024-09-05T20:34:02+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Extra, Field

from .utils.schema_base_model import SchemaBaseModel


class Overwrite(Enum):
    """
    Overwrite document if already exists?
    """

    yes = "yes"
    no = "no"


class Producer(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Name (required)", title="Name")
    abbr: Optional[str] = Field(None, title="Abbreviation")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")


class DocDesc(SchemaBaseModel):
    """
    Document description; the Document is the file containing the structured metadata
    """

    class Config:
        extra = Extra.forbid

    title: Optional[str] = Field(None, description="Document title", title="Document title")
    idno: Optional[str] = Field(None, title="Unique ID number for the document")
    producers: Optional[List[Producer]] = Field(
        None, description="List of producers of the document", title="Producers"
    )
    prod_date: Optional[str] = Field(
        None, description="Document production date using format(YYYY-MM-DD)", title="Date of production"
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
    Project title
    """

    idno: str = Field(
        ...,
        description=(
            "The ID number of a research project is a unique number that is used to identify a particular project."
            " Define and use a consistent scheme to use."
        ),
        title="Unique user defined ID",
    )
    identifiers: Optional[List[Identifier]] = Field(None, description="Other identifiers", title="Other identifiers")
    title: str = Field(
        ...,
        description=(
            "The title is the name of the project, which may correspond to the title of an academic paper, of a project"
            " impact evaluation, etc."
        ),
        title="Project title",
    )
    sub_title: Optional[str] = Field(None, description="A short subtitle for the project", title="Project subtitle")
    alternate_title: Optional[str] = Field(
        None,
        description=(
            "The abbreviation of a project is usually the first letter of each word of the project title. The project"
            " reference year(s) may be included."
        ),
        title="Abbreviation or acronym",
    )
    translated_title: Optional[str] = Field(
        None,
        description="In countries with more than one official language, a translation of the title may be provided.",
        title="Translated title",
    )


class OutputItem(SchemaBaseModel):
    type: Optional[str] = Field(
        None,
        description=(
            "Type of outputs of the script/research project. Example: `Working paper`, `On-line interactive data"
            " visualization` (ideally, a controlled vocabulary should be used)"
        ),
        title="Type of output",
    )
    title: str = Field(..., description="Title of the output", title="Title")
    authors: Optional[str] = Field(None, description="Authors", title="Authors")
    description: Optional[str] = Field(
        None,
        description=(
            "Brief description of the output; for articles and working papers, this can include the bibliographic"
            " citation."
        ),
        title="Description",
    )
    abstract: Optional[str] = Field(None, description="Abstract (for papers, articles, books)", title="Abstract")
    uri: Optional[str] = Field(None, description="On-line location of the output", title="URI")
    doi: Optional[str] = Field(None, description="Digital Object Identifier (DOI) of the output", title="DOI")


class ApprovalProces(SchemaBaseModel):
    approval_phase: Optional[str] = Field(None, title="A name of the approval phase")
    approval_authority: Optional[str] = Field(None, title="Approval authority")
    submission_date: Optional[str] = Field(None, title="Date submitted")
    reviewer: Optional[str] = Field(None, title="Reviewer")
    review_status: Optional[str] = Field(None, title="Review status")
    approval_date: Optional[str] = Field(None, title="Date of approval")


class LanguageItem(SchemaBaseModel):
    name: str = Field(..., title="Name")
    code: Optional[str] = Field(None, title="Code")


class VersionStatement(SchemaBaseModel):
    """
    Version statement
    """

    version: Optional[str] = Field(None, title="Version")
    version_date: Optional[str] = Field(None, title="Version date")
    version_resp: Optional[str] = Field(
        None,
        description="The organization or person responsible for the version of the work",
        title="Version responsibility statement",
    )
    version_notes: Optional[str] = Field(None, title="Version notes")


class Erratum(SchemaBaseModel):
    date: Optional[str] = Field(
        None, description="Date when the erratum was reported or published", title="Date of erratum"
    )
    description: Optional[str] = Field(
        None,
        description="A description of the erratum, with information on which data, scripts, or output were impacted",
        title="Description of the erratum",
    )


class Proces(SchemaBaseModel):
    name: Optional[str] = Field(None, description="A short name for the implementation phase", title="Phase name")
    date_start: Optional[str] = Field(
        None,
        description="Start date of the phase period (as a string; recommended ISO format YYY or YYY-MM or YYY-MM-DD)",
        title="Phase start date",
    )
    date_end: Optional[str] = Field(
        None,
        description="End date of the phase period (as a string; recommended ISO format YYY or YYY-MM or YYY-MM-DD)",
        title="Phase end date",
    )
    description: Optional[str] = Field(
        None, description="Description of the implementation phase", title="Phase description"
    )


class AuthorIdItem(SchemaBaseModel):
    type: Optional[str] = Field(None, description="Source of identifier, e.g. ORCID", title="Type")
    id: Optional[str] = Field(
        None, description="Author's unique identifier for the corresponding source", title="Identifier"
    )


class AuthoringEntityItem(SchemaBaseModel):
    name: str = Field(
        ...,
        description=(
            "Name of the person, corporate body, or agency responsible for the work's substantive and intellectual"
            " content. If a person, invert first and last name and use commas."
        ),
        title="Author (or primary investigator) name",
    )
    role: Optional[str] = Field(
        None,
        description="Title of the person (if any) responsible for the work's substantive and intellectual content.",
        title="Role",
    )
    affiliation: Optional[str] = Field(None, title="Affiliation of the author/primary investigator")
    abbreviation: Optional[str] = Field(None, description="Abbreviation", title="Abbreviation")
    email: Optional[str] = Field(None, description="Email", title="Email")
    author_id: Optional[List[AuthorIdItem]] = Field(
        None,
        description="Unique identifier of an author, which may be provided by services like ORCID or other",
        title="Author ID",
    )


class Contributor(SchemaBaseModel):
    name: str = Field(
        ...,
        description=(
            "Name of the person, corporate body, or agency responsible for the work's substantive and intellectual"
            " content. If a person, invert first and last name and use commas."
        ),
        title="Name",
    )
    role: Optional[str] = Field(
        None,
        description="Title of the person (if any) responsible for the work's substantive and intellectual content.",
        title="Role",
    )
    affiliation: Optional[str] = Field(None, title="Affiliation")
    abbreviation: Optional[str] = Field(None, description="Abbreviation", title="Abbreviation")
    email: Optional[str] = Field(None, description="Email", title="Email")
    url: Optional[str] = Field(None, description="URL", title="URL")


class Sponsor(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Funding Agency/Sponsor")
    abbr: Optional[str] = Field(None, title="Abbreviation")
    role: Optional[str] = Field(None, title="Role")
    grant_no: Optional[str] = Field(None, title="Grant number")


class Curator(SchemaBaseModel):
    name: str = Field(
        ...,
        description=(
            "Name of the person, corporate body, or agency responsible for the project curation. If a person, invert"
            " first and last name and use commas."
        ),
        title="Name",
    )
    role: Optional[str] = Field(
        None, description="Title of the person (if any) responsible for the project curation.", title="Role"
    )
    affiliation: Optional[str] = Field(None, title="Affiliation")
    abbreviation: Optional[str] = Field(None, description="Abbreviation", title="Abbreviation")
    email: Optional[str] = Field(None, description="Email", title="Email")
    url: Optional[str] = Field(None, description="URL", title="URL")


class ReviewsComment(SchemaBaseModel):
    """
    List and description of reviews and comments received on the project
    """

    comment_date: Optional[str] = Field(
        None, description="Date when the comment was provided", title="Date of the comment"
    )
    comment_by: Optional[str] = Field(
        None,
        description="Name and title of the comment provider (individual or organization)",
        title="Provider of the comment",
    )
    comment_description: Optional[str] = Field(
        None, description="A description of the comment", title="Description of the comment"
    )
    comment_response: Optional[str] = Field(
        None,
        description="Response by the primary investigator or research team on the comment",
        title="Response on the comment",
    )


class Acknowledgement(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    role: Optional[str] = Field(None, title="Role")


class RelatedProject(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    uri: Optional[str] = Field(None, title="URI")
    note: Optional[str] = Field(None, title="Note")


class GeographicUnit(SchemaBaseModel):
    name: str = Field(
        ..., description="Name of the geographic unit e.g. 'World', 'Africa', 'Afghanistan'", title="Location name"
    )
    code: Optional[str] = Field(
        None, description="Code of the geographic unit (for countries, preferred = ISO3 code)", title="Location code"
    )
    type: Optional[str] = Field(
        None, description="Type of geographic unit e.g. country, state, region, province, town, etc", title="Type"
    )


class Keyword(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Keyword, composed of one or multiple words", title="Name")
    vocabulary: Optional[str] = Field(
        None,
        description="Vocabulary name (for keywords extracted from controlled vocabularies)",
        title="Vocabulary name",
    )
    uri: Optional[str] = Field(None, title="Vocabulary URI")


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
    id: str = Field(..., title="Unique identifier")
    name: str = Field(..., title="Topic")
    parent_id: Optional[str] = Field(
        None, description="For subtopics, provide the ID of the parent topic", title="Parent topic identifier"
    )
    vocabulary: Optional[str] = Field(
        None, description="Name of the controlled vocabulary, if the topic is from a taxonomy.", title="Vocabulary name"
    )
    uri: Optional[str] = Field(
        None,
        description="Link to the controlled vocabulary web page, if the topic is from a taxonomy.",
        title="Vocabulary URI",
    )


class Discipline(SchemaBaseModel):
    id: Optional[str] = Field(None, title="Unique Identifier")
    name: str = Field(..., title="Discipline title or name")
    parent_id: Optional[str] = Field(None, description="Parent discipline ID", title="Parent discipline Identifier")
    vocabulary: Optional[str] = Field(None, description="Vocabulary", title="Vocabulary")
    uri: Optional[str] = Field(None, description="Website link", title="URI")


class RepositoryUriItem(SchemaBaseModel):
    name: str = Field(
        ...,
        description="Name of the repository where code is hosted. e.g. `Github`, `Bitbucket`, etc.",
        title="Repository name",
    )
    type: Optional[str] = Field(None, description="Repo type e.g. `git`, `svn`, `other`", title="Type")
    uri: Optional[Any] = Field(None, description="URI of the project repository", title="URI")


class LicenseItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="License")
    uri: Optional[str] = Field(None, title="URI")


class Method(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Method name")
    note: Optional[str] = Field(None, title="Description")


class SoftwareItem(SchemaBaseModel):
    class Config:
        extra = Extra.forbid

    name: Optional[str] = Field(None, title="Name")
    version: Optional[str] = Field(None, title="Version")
    library: Optional[List[str]] = Field(
        None, description="Software-specific libraries or packages used", title="Libraries or packages used"
    )


class Author(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Person or organization name")
    abbr: Optional[str] = Field(None, title="Abbreviation")
    role: Optional[str] = Field(None, title="Role")


class LicenseItem1(SchemaBaseModel):
    name: Optional[str] = Field(None, title="License name")
    uri: Optional[str] = Field(None, title="License URI")


class Script(SchemaBaseModel):
    file_name: Optional[str] = Field(None, title="File name")
    zip_package: Optional[str] = Field(
        None, description="Provide the name of the zip file, if the file is included in a zip", title="Zip file"
    )
    title: str = Field(..., title="Title")
    authors: Optional[List[Author]] = Field(None, description="Author(s) of the script", title="Authors")
    date: Optional[str] = Field(None, title="Date")
    format: Optional[str] = Field(None, title="Format")
    software: Optional[str] = Field(None, title="Software")
    description: Optional[str] = Field(None, title="Description")
    methods: Optional[str] = Field(None, title="Methods")
    dependencies: Optional[str] = Field(None, title="Dependencies")
    instructions: Optional[str] = Field(None, title="Instructions or note for running the script")
    source_code_repo: Optional[str] = Field(None, title="Source code repositor")
    notes: Optional[str] = Field(None, title="Notes")
    license: Optional[List[LicenseItem1]] = Field(None, title="License")


class Dataset(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Dataset name")
    idno: Optional[str] = Field(None, description="unique ID of the dataset", title="Dataset ID")
    note: Optional[str] = Field(
        None,
        description=(
            "Brief description of the dataset (note: ideally, the dataset will be documented using a specific metadata"
            " schema like the DDI)."
        ),
        title="Description",
    )
    access_type: Optional[str] = Field(None, title="Data access policy")
    license: Optional[str] = Field(None, title="License")
    license_uri: Optional[str] = Field(None, title="License URI")
    uri: Optional[str] = Field(
        None,
        description="Link to the website where the data may be accessed or more information on access can be found",
        title="Dataset URI",
    )


class Contact(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    role: Optional[str] = Field(None, title="Role")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    email: Optional[str] = Field(None, title="Email")
    telephone: Optional[str] = Field(None, title="Telephone")
    uri: Optional[str] = Field(None, title="URI")


class ProjectDesc(SchemaBaseModel):
    """
    Description of the research project
    """

    title_statement: Optional[TitleStatement] = Field(None, description="Project title")
    abstract: Optional[str] = Field(None, title="Abstract")
    review_board: Optional[str] = Field(
        None,
        description=(
            "Information on whether and when the project was submitted, reviewed, and approved by an institutional"
            " review board (or independent ethics committee, ethical review board (ERB), research ethics board, or"
            " equivalent)."
        ),
        title="Institutional review board",
    )
    output: Optional[List[OutputItem]] = Field(
        None, description="Description of outputs of the research project", title="Output"
    )
    approval_process: Optional[List[ApprovalProces]] = Field(
        None, description="A description of the project output review process", title="Approval process"
    )
    project_website: Optional[List[str]] = Field(None, description="Project website link", title="Project website")
    language: Optional[List[LanguageItem]] = Field(
        None, description="Documentation language e.g. English, French, etc.", title="Language"
    )
    production_date: Optional[List[str]] = Field(
        None,
        description=(
            "Date in ISO format when the dissemination-ready version of the research project was produced. It can be a"
            " year (YYYY), year-month (YYYY-MM), or year-month-day (YYYY-MM-DD)"
        ),
        title="Date of production (YYYY-MM-DD)",
    )
    version_statement: Optional[VersionStatement] = Field(
        None, description="Version statement", title="Version statement"
    )
    errata: Optional[List[Erratum]] = Field(
        None, description="List of corrected errors in data, scripts or output", title="Errata"
    )
    process: Optional[List[Proces]] = Field(
        None,
        description=(
            "A description, following a logical sequence, of the various phases of the research project implementation."
            " This field may be used to document explorations steps that may have resulted in dead ends, to document"
            " intermediary steps at which a project may have been reviewed and approved, etc."
        ),
        title="Process",
    )
    authoring_entity: Optional[List[AuthoringEntityItem]] = Field(
        None,
        description=(
            "The person, corporate body, or agency responsible for the project's substantive and intellectual content."
            " Repeat the element for each author/primary investigator, and use 'affiliation' attribute if available."
            " Invert first and last name and use commas."
        ),
        title="Authoring entity",
    )
    contributors: Optional[List[Contributor]] = Field(
        None, description="The person, corporate body, or agency who contributed to the project.", title="Contributors"
    )
    sponsors: Optional[List[Sponsor]] = Field(
        None,
        description=(
            "The source(s) of funds for production of the work. If different funding agencies sponsored different"
            " stages of the production process, use the 'role' attribute to distinguish them."
        ),
        title="Sponsors / Funding agencies",
    )
    curators: Optional[List[Curator]] = Field(
        None, description="The person, corporate body, or agency who curated the project.", title="Curators"
    )
    reviews_comments: Optional[List[ReviewsComment]] = None
    acknowledgements: Optional[List[Acknowledgement]] = Field(
        None,
        description="Acknowledgments of persons or organizations (other than sponsors) who contributed to the project.",
        title="Other acknowledgments",
    )
    acknowledgement_statement: Optional[str] = Field(
        None, description="Acknowledgement statement", title="Acknowledgement statement"
    )
    disclaimer: Optional[str] = Field(None, title="Disclaimer")
    confidentiality: Optional[str] = Field(None, title="Confidentiality")
    citation_requirement: Optional[str] = Field(
        None, description="Citation requirement (can include a specific recommended citation)"
    )
    related_projects: Optional[List[RelatedProject]] = Field(
        None, description="A list and bried description of related research projects", title="Related research projects"
    )
    geographic_units: Optional[List[GeographicUnit]] = Field(
        None,
        description=(
            "List of geographic locations (regions, countries, states, provinces, etc.) describing the geographic"
            " coverahe of the research project."
        ),
        title="Geographic locations",
    )
    keywords: Optional[List[Keyword]] = Field(None, title="Keywords")
    themes: Optional[List[Theme]] = Field(None, description="Themes")
    topics: Optional[List[Topic]] = Field(
        None,
        description=(
            "Topics covered by the project (ideally, a controlled vocabulary should be used). This can be a"
            " hierarchical list of topics."
        ),
        title="Topics",
    )
    disciplines: Optional[List[Discipline]] = Field(
        None,
        description="Disciplines e.g. `Social sciences, economics`, `Natural sciences, biology`",
        title="Disciplines",
    )
    repository_uri: Optional[List[RepositoryUriItem]] = Field(
        None, description="Source code repository", title="Source code repository"
    )
    license: Optional[List[LicenseItem]] = Field(
        None,
        description=(
            "Overall statement on license. Note: information on license specific to scripts and/or datasets should be"
            " provided in the documentation of scripts and datasets."
        ),
        title="License",
    )
    copyright: Optional[str] = Field(None, title="Copyright")
    technology_environment: Optional[str] = Field(
        None,
        description="Notes about the technology environment used by the authors to implement the project",
        title="Technology environment",
    )
    technology_requirements: Optional[str] = Field(
        None,
        description="Software/hardware or other technology requirements needed to replicate the scripts",
        title="Technology requirements",
    )
    reproduction_instructions: Optional[str] = Field(None, description="Reproduction instructions")
    methods: Optional[List[Method]] = Field(
        None, description="Methods or algorithms applied", title="Methods or algorithms applied"
    )
    software: Optional[List[SoftwareItem]] = Field(
        None, description="List of software applications used for the project", title="Software"
    )
    scripts: Optional[List[Script]] = Field(None, description="Description of each script file", title="Script files")
    data_statement: Optional[str] = Field(
        None,
        description=(
            "Overall statement on data used by the project. More detailed description of the datasets should be"
            " provided in the 'datasets' field."
        ),
    )
    datasets: Optional[List[Dataset]] = Field(
        None, description="List and description of datasets used by the research project", title="Datasets"
    )
    contacts: Optional[List[Contact]] = Field(None, description="Contacts", title="Contacts")


class Tag(SchemaBaseModel):
    tag: Optional[str] = Field(None, title="Tag")
    tag_group: Optional[str] = Field(None, title="Tag group")


class ModelInfoItem(SchemaBaseModel):
    source: Optional[str] = Field(None, title="Source")
    author: Optional[str] = Field(None, title="Author")
    version: Optional[str] = Field(None, title="Version")
    model_id: Optional[str] = Field(None, title="Model Identifier")
    nb_topics: Optional[float] = Field(None, title="Number of topics")
    description: Optional[str] = Field(None, title="Description")
    corpus: Optional[str] = Field(None, title="Corpus name")
    uri: Optional[str] = Field(None, title="URI")


class TopicWord(SchemaBaseModel):
    word: Optional[str] = Field(None, title="Word")
    word_weight: Optional[float] = Field(None, title="Word weight")


class TopicDescriptionItem(SchemaBaseModel):
    topic_id: Optional[Union[int, str]] = Field(None, title="Topic identifier")
    topic_score: Optional[Union[float, str]] = Field(None, title="Topic score")
    topic_label: Optional[str] = Field(None, title="Topic label")
    topic_words: Optional[List[TopicWord]] = Field(None, description="Words", title="Topic words")


class LdaTopic(SchemaBaseModel):
    class Config:
        extra = Extra.forbid

    model_info: Optional[List[ModelInfoItem]] = Field(None, title="Model information")
    topic_description: Optional[List[TopicDescriptionItem]] = Field(None, title="Topic information")


class Embedding(SchemaBaseModel):
    id: str = Field(..., title="Vector Model ID")
    description: Optional[str] = Field(None, title="Vector Model Description")
    date: Optional[str] = Field(None, title="Date (YYYY-MM-DD)")
    vector: Dict[str, Any] = Field(..., title="Vector")


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


class ResearchProjectSchemaDraft(SchemaBaseModel):
    """
    Schema for documenting research projects and data analysis scripts
    """

    repositoryid: Optional[str] = Field(
        None,
        description="Abbreviation for the collection that owns the research project",
        title="Collection ID that owns the project",
    )
    published: Optional[int] = Field(0, description="Status of the project - 0=draft, 1=published", title="Status")
    overwrite: Optional[Overwrite] = Field("no", description="Overwrite document if already exists?")
    doc_desc: Optional[DocDesc] = Field(
        None,
        description="Document description; the Document is the file containing the structured metadata",
        title="Document description",
    )
    project_desc: Optional[ProjectDesc] = Field(
        None, description="Description of the research project", title="Project description"
    )
    provenance: Optional[List[ProvenanceSchema]] = Field(None, description="Provenance")
    tags: Optional[List[Tag]] = Field(None, description="Tags", title="Tags (user-defined)")
    lda_topics: Optional[List[LdaTopic]] = Field(None, description="LDA topics", title="LDA topics")
    embeddings: Optional[List[Embedding]] = Field(None, description="Word embeddings", title="Word embeddings")
    additional: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
