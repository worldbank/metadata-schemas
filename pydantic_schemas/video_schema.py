# generated by datamodel-codegen:
#   filename:  video-schema.json

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


class MetadataInformation(SchemaBaseModel):
    """
    Document description
    """

    class Config:
        extra = Extra.forbid

    title: Optional[str] = Field(None, description="Document title", title="Document title")
    idno: Optional[str] = Field(None, title="Unique ID number for the document")
    producers: Optional[List[Producer]] = Field(None, description="List of producers", title="Producers")
    production_date: Optional[str] = Field(
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


class Keyword(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    vocabulary: Optional[str] = Field(None, title="Vocabulary name")
    uri: Optional[str] = Field(None, title="Vocabulary URI")


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


class Person(SchemaBaseModel):
    name: str = Field(..., title="Name")
    role: Optional[str] = Field(None, title="Role")


class CountryItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Country name")
    code: Optional[str] = Field(None, title="Country code")


class BboxItem(SchemaBaseModel):
    west: Optional[str] = Field(None, title="West")
    east: Optional[str] = Field(None, title="East")
    south: Optional[str] = Field(None, title="South")
    north: Optional[str] = Field(None, title="North")


class LanguageItem(SchemaBaseModel):
    name: Optional[str] = Field(None, description="Language name", title="Name")
    code: Optional[str] = Field(None, title="code")


class Contact(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name")
    role: Optional[str] = Field(None, title="Role")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    email: Optional[str] = Field(None, title="Email")
    telephone: Optional[str] = Field(None, title="Telephone")
    uri: Optional[str] = Field(None, title="URI")


class Contributor(SchemaBaseModel):
    name: str = Field(..., title="Name")
    affiliation: Optional[str] = Field(None, title="Affiliation")
    abbreviation: Optional[str] = Field(None, title="Abbreviation")
    role: Optional[str] = Field(None, title="Role")
    uri: Optional[str] = Field(None, title="URI")


class Sponsor(SchemaBaseModel):
    name: str = Field(..., title="Funding Agency/Sponsor")
    abbr: Optional[str] = Field(None, title="Abbreviation")
    grant: Optional[str] = Field(None, title="Grant Number")
    role: Optional[str] = Field(None, title="Role")


class Translator(SchemaBaseModel):
    first_name: Optional[str] = Field(None, title="First name")
    initial: Optional[str] = Field(None, title="Initial")
    last_name: Optional[str] = Field(None, title="Last name")
    affiliation: Optional[str] = Field(None, title="Affiliation")


class TranscriptItem(SchemaBaseModel):
    language: Optional[str] = Field(None, title="Language")
    text: Optional[str] = Field(None, title="Text")


class AlbumItem(SchemaBaseModel):
    name: Optional[str] = Field(None, title="Name of album")
    description: Optional[str] = Field(None, title="Description")
    owner: Optional[str] = Field(None, title="Owner")
    uri: Optional[str] = Field(None, title="URI")


class VideoDescription(SchemaBaseModel):
    """
    Video description
    """

    idno: str = Field(..., title="Unique video identifier")
    identifiers: Optional[List[Identifier]] = Field(None, description="Other identifiers", title="Other identifiers")
    title: str = Field(..., description="Title")
    alt_title: Optional[str] = Field(None, description="Alternate title or other title")
    description: Optional[str] = Field(None, description="Description")
    genre: Optional[str] = Field(None, description="Genre")
    keywords: Optional[List[Keyword]] = None
    topics: Optional[List[Topic]] = Field(
        None,
        description="Topics covered by the table (ideally, the list of topics will be a controlled vocabulary)",
        title="Topics",
    )
    persons: Optional[List[Person]] = Field(None, title="Persons shown in the video")
    main_entity: Optional[str] = Field(None, description="Primary entity described in the video")
    date_created: Optional[str] = Field(None, description="Date of creation (YYYY-MM-DD)")
    date_published: Optional[str] = Field(None, description="Date published (YYYY-MM-DD)")
    version: Optional[str] = Field(None, description="Version")
    status: Optional[str] = Field(
        None,
        description=(
            "Status of a creative work in terms of its stage in lifecycle. e.g. `incomplete`, `draft`, `published`,"
            " `obsolete`"
        ),
        title="Creative work status",
    )
    country: Optional[List[CountryItem]] = Field(None, title="Countries")
    spatial_coverage: Optional[str] = Field(None, description="Place(s) which are the focus of the content")
    content_reference_time: Optional[str] = Field(
        None,
        description=(
            "Specific time described by a creative work, for works that emphasize a particular moment within an Event"
        ),
    )
    temporal_coverage: Optional[str] = Field(
        None, description="Period that the content applies to using ISO 8601 date time format"
    )
    recorded_at: Optional[str] = Field(None, description="Location where video was recorded")
    audience: Optional[str] = Field(None, description="Intended audience")
    bbox: Optional[List[BboxItem]] = Field(None, title="Geographic bounding box")
    language: Optional[List[LanguageItem]] = Field(None, description="languages")
    creator: Optional[str] = Field(None, description="Creator")
    production_company: Optional[str] = Field(None, description="Production company")
    publisher: Optional[str] = Field(None, description="Publisher")
    repository: Optional[str] = Field(None, title="Repository")
    contacts: Optional[List[Contact]] = Field(None, description="Contacts", title="Contacts")
    contributors: Optional[List[Contributor]] = None
    sponsors: Optional[List[Sponsor]] = Field(None, title="Funding Agency/Sponsor")
    translators: Optional[List[Translator]] = Field(None, description="Translators", title="Translators")
    is_based_on: Optional[str] = Field(
        None,
        description="A resource from which this work is derived or from which it is a modification or adaption",
        title="A resource from which this work is derived",
    )
    is_part_of: Optional[str] = Field(None, title="Indicate an item that this item is part of")
    relations: Optional[List[str]] = Field(
        None,
        title=(
            "Defines, as a free text field, the relation between the video being documented and other resources. This"
            " is a Dublin Core element."
        ),
    )
    video_provider: Optional[str] = Field(None, description="Video provider e.g.  youtube, vimeo, facebook")
    video_url: Optional[str] = Field(None, description="Video URL")
    embed_url: Optional[str] = Field(None, description="Video embed URL")
    encoding_format: Optional[str] = Field(None, description="Media type using a MIME format", title="Encoding format")
    duration: Optional[str] = Field(
        None, description="The duration of the video in ISO 8601 date time format - `hh:mm:ss`", title="Duration"
    )
    rights: Optional[str] = Field(None, description="Rights")
    copyright_holder: Optional[str] = Field(
        None, description="The party holding the legal copyright", title="Copyright holder"
    )
    copyright_notice: Optional[str] = Field(
        None, description="Text of a notice describing the copyright", title="Copyright text"
    )
    copyright_year: Optional[str] = Field(
        None, description="Year during which claimed copyright for the video was first asserted", title="Copyright year"
    )
    credit_text: Optional[str] = Field(
        None,
        description=(
            "This element that can be used to credit the person(s) and/or organization(s) associated with a published"
            " video. It corresponds to the `creditText` element of VideoObject."
        ),
        title="Credits",
    )
    citation: Optional[str] = Field(
        None,
        description="This element provides a required or recommended citation of the audio file.",
        title="Citation",
    )
    transcript: Optional[List[TranscriptItem]] = Field(None, title="Transcript")
    media: Optional[List[str]] = Field(None, title="Media")
    album: Optional[List[AlbumItem]] = Field(None, title="Album")


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


class Model(SchemaBaseModel):
    """
    Video schema based on the elements from Dublin Core and Schema.org's VideoObject
    """

    repositoryid: Optional[str] = Field(
        None,
        description="Abbreviation for the collection that owns the document",
        title="Collection ID that owns the document",
    )
    published: Optional[int] = Field(0, description="Status  - 0=draft, 1=published", title="Status")
    overwrite: Optional[Overwrite] = Field("no", description="Overwrite document if already exists?")
    metadata_information: Optional[MetadataInformation] = Field(
        None, description="Document description", title="Document metadata information"
    )
    video_description: VideoDescription = Field(
        ..., description="Video description", title="Video metadata information"
    )
    provenance: Optional[List[ProvenanceSchema]] = Field(None, description="Provenance")
    tags: Optional[List[Tag]] = Field(None, description="Tags", title="Tags")
    lda_topics: Optional[List[LdaTopic]] = Field(None, description="LDA topics", title="LDA topics")
    embeddings: Optional[List[Embedding]] = Field(None, description="Word embeddings", title="Word embeddings")
    additional: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
