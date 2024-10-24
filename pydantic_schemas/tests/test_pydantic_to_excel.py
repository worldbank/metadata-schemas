import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import pytest
from pydantic import BaseModel, Field

from pydantic_schemas.document_schema import ScriptSchemaDraft
from pydantic_schemas.geospatial_schema import GeospatialSchema
from pydantic_schemas.indicator_schema import TimeseriesSchema
from pydantic_schemas.indicators_db_schema import TimeseriesDatabaseSchema

# from pydantic_schemas.image_schema import ImageDataTypeSchema
from pydantic_schemas.microdata_schema import MicrodataSchema
from pydantic_schemas.script_schema import ResearchProjectSchemaDraft
from pydantic_schemas.table_schema import Model as TableModel
from pydantic_schemas.utils.excel_to_pydantic import (
    excel_doc_to_pydantic,
    excel_sheet_to_pydantic,
    excel_single_sheet_to_pydantic,
)
from pydantic_schemas.utils.pydantic_to_excel import (
    correct_column_widths,
    create_sheet,
    open_or_create_workbook,
    shade_30_rows_and_protect_sheet,
    shade_locked_cells,
    write_across_many_sheets,
    write_pydantic_to_sheet,
    write_title_and_version_info,
    write_to_single_sheet,
)
from pydantic_schemas.utils.quick_start import make_skeleton
from pydantic_schemas.video_schema import Model as VideoModel


def test_simple_schema(tmpdir, index_above=False):
    class Simple(BaseModel):
        idno: str
        title: str
        author: str

    simple_original = Simple(idno="AVal", title="BVal", author="CVal")

    filename = tmpdir.join(f"integration_test_simple_schema_.xlsx")
    write_to_single_sheet(filename, simple_original, "simple_original", "Simple Metadata")

    parsed_simple = excel_sheet_to_pydantic(filename, "metadata", Simple)
    assert parsed_simple == simple_original, parsed_simple


def test_two_layer_simple_schema(tmpdir, index_above=False):
    class Production(BaseModel):
        idno: str
        title: str
        author: str

    class Country(BaseModel):
        name: str
        initials: str

    class ProductionAndCountries(BaseModel):
        production: Production
        countries: Country

    inp = ProductionAndCountries(
        production=Production(idno="AVal", title="BVal", author="CVal"),
        countries=Country(name="MyCountry", initials="MC"),
    )

    filename = tmpdir.join(f"integration_test_two_layer_simple_schema.xlsx")
    write_to_single_sheet(filename, inp, "ProductionAndCountries", "Production and Countries")

    parsed_outp = excel_sheet_to_pydantic(filename, "metadata", ProductionAndCountries)
    assert parsed_outp == inp, parsed_outp


def test_multilayer_simple_schema(tmpdir):
    class Production(BaseModel):
        idno: str
        title: str
        author: str

    class Country(BaseModel):
        name: str
        initials: str

    class Language(BaseModel):
        name: Optional[str] = Field(None, description="Language title", title="Name")
        code: Optional[str] = Field(None, title="code")

    class Topic(BaseModel):
        id: Optional[str] = Field(None, title="Unique Identifier")
        name: str = Field(..., title="Topic")

    class SeriesDescription(BaseModel):
        language: Language
        topic: Topic

    class ProductionAndCountries(BaseModel):
        production: Production
        countries: Country
        series_description: SeriesDescription
        idno: str
        title: Optional[str] = None
        subtitle: Optional[str] = None

    series_description = SeriesDescription(
        language=Language(name="English", code="EN"), topic=Topic(id="topic1", name="topic1")
    )

    inp = ProductionAndCountries(
        production=Production(idno="AVal", title="BVal", author="CVal"),
        countries=Country(name="MyCountry", initials="MC"),
        series_description=series_description,
        idno="example_idno",
        title="example_title",
    )

    filename = tmpdir.join(f"integration_test_multilayer_simple_schema_.xlsx")
    write_to_single_sheet(filename, inp, "ProductionAndCountries", "Production and Countries")
    parsed_outp = excel_sheet_to_pydantic(filename, "metadata", ProductionAndCountries)
    assert parsed_outp == inp, parsed_outp


def test_optional_missing_deprecated_new_simple(tmpdir):
    class Production(BaseModel):
        idno: Optional[str] = None
        title: Optional[str] = None
        subtitle: Optional[str] = None
        author: str
        deprecatedFeature: str

    original_production = Production(idno="", subtitle=None, author="author", deprecatedFeature="toberemoved")

    filename = tmpdir.join(f"integration_test_optional_missing_deprecated_new_simple_.xlsx")
    write_to_single_sheet(filename, original_production, "Production", "Production")

    class Production(BaseModel):
        idno: Optional[str] = None
        title: Optional[str] = None
        author: str
        newFeature: Optional[str] = None
        requiredNewFeature: str

    new_production = excel_sheet_to_pydantic(filename=filename, sheetname="metadata", model_type=Production)
    assert new_production.idno is None
    assert new_production.title is None
    assert new_production.author == "author"
    assert new_production.newFeature is None
    assert new_production.requiredNewFeature == ""


def test_optional_missing_deprecated_new_two_level(tmpdir):
    class Production(BaseModel):
        idno: Optional[str] = None
        title: Optional[str] = None
        subtitle: Optional[str] = None
        author: str
        deprecatedFeature: str

    class Country(BaseModel):
        name: str
        initials: str

    class ProductionAndCountries(BaseModel):
        production: Production
        countries: Country

    example_production = Production(idno="", subtitle=None, author="author", deprecatedFeature="toberemoved")
    example_country = Country(name="MadeupCountry", initials="MC")
    example_production_and_country = ProductionAndCountries(production=example_production, countries=example_country)

    filename = tmpdir.join(f"integration_test_optional_missing_deprecated_new_two_level_.xlsx")

    write_to_single_sheet(
        filename, example_production_and_country, "ProductionAndCountries", "Production and Countries"
    )

    class Production(BaseModel):
        idno: Optional[str] = None
        title: Optional[str] = None
        author: str
        newFeature: Optional[str] = None
        requiredNewFeature: str

    class NewTopLevel(BaseModel):
        val1: str
        val2: str

    class ProductionAndCountries(BaseModel):
        production: Production
        countries: Country
        newTopLevelFeature: Optional[NewTopLevel] = None

    new_pandc = excel_sheet_to_pydantic(filename=filename, sheetname="metadata", model_type=ProductionAndCountries)
    assert new_pandc.production.idno is None
    assert new_pandc.production.title is None
    assert new_pandc.production.author == "author"
    assert new_pandc.production.newFeature is None
    assert new_pandc.production.requiredNewFeature == ""
    assert new_pandc.countries.name == "MadeupCountry"
    assert new_pandc.countries.initials == "MC"


def test_lists(tmpdir):
    class ContactMethod(Enum):
        phone = "PHONE"
        email = "EMAIL"

    class Contact(BaseModel):
        method: Optional[ContactMethod] = None
        contact_address: Optional[str] = None

    class Person(BaseModel):
        name: str
        affiliations: Optional[List[str]] = None
        contact_details: Optional[List[Contact]] = None

    class Production(BaseModel):
        idno: Optional[str] = None
        title: Optional[str] = None
        authors: List[Person]

    class Country(BaseModel):
        name: str
        initials: str

    class ProductionAndCountries(BaseModel):
        production: Production
        countries: List[Country]
        dates: List[str]
        other: List[str]
        otherOptional: Optional[List[str]] = None

    author0 = Person(name="person_0")
    author1 = Person(
        name="person_1",
        affiliations=["Org1", "Org2"],
        contact_details=[
            Contact(method=ContactMethod.email, contact_address="example@example.com"),
            Contact(method=ContactMethod.phone, contact_address="123456789"),
        ],
    )
    author2 = Person(name="person_2", contact_details=[Contact()])
    author3 = Person(name="person_3", affiliations=["Org3"])
    example_production = Production(idno="", authors=[author0, author1, author2, author3])
    example_country = Country(name="MadeupCountry", initials="MC")
    example_other_country = Country(name="MadeupCountry2", initials="MC2")
    example_dates = ["April", "May", "June"]
    example_production_and_country = ProductionAndCountries(
        production=example_production,
        countries=[example_country, example_other_country],
        dates=["April", "May", "June"],
        other=[],
        otherOptional=None,
    )

    filename = tmpdir.join(f"integration_test_lists_.xlsx")
    # filename = "integration_test_lists_.xlsx"
    write_to_single_sheet(
        filename, example_production_and_country, "ProductionAndCountries", "Production and Countries"
    )

    new_pandc = excel_sheet_to_pydantic(
        filename=filename, sheetname="metadata", model_type=ProductionAndCountries, debug=True
    )
    assert new_pandc.production.idno is None
    assert new_pandc.production.title is None
    assert len(new_pandc.production.authors) == 4
    assert author0 in new_pandc.production.authors
    assert author1 in new_pandc.production.authors
    assert author2 in new_pandc.production.authors
    assert author3 in new_pandc.production.authors
    assert len(new_pandc.countries) == 2
    assert example_country in new_pandc.countries
    assert example_other_country in new_pandc.countries
    assert new_pandc.dates == example_dates
    assert new_pandc.other == []
    assert new_pandc.otherOptional is None or new_pandc.otherOptional == []


def test_metadata_over_several_sheets(tmpdir):
    class Person(BaseModel):
        name: str
        affiliations: Optional[List[str]] = None

    class Production(BaseModel):
        idno: Optional[str] = None
        title: Optional[str] = None
        authors: List[Person]

    class Country(BaseModel):
        name: str
        initials: str

    class ProductionAndCountries(BaseModel):
        production: Production
        countries: List[Country]
        dates: List[str]
        other: List[str]
        otherOptional: Optional[List[str]] = None
        single_val: str

    author0 = Person(name="person_0")
    author1 = Person(name="person_1", affiliations=["Org1", "Org2"])
    author2 = Person(name="person_2")
    author3 = Person(name="person_3", affiliations=["Org3"])
    example_production = Production(idno="myidno", authors=[author0, author1, author2, author3])
    example_country = Country(name="MadeupCountry", initials="MC")
    example_other_country = Country(name="MadeupCountry2", initials="MC2")
    example_dates = ["April", "May", "June"]
    example_production_and_country = ProductionAndCountries(
        production=example_production,
        countries=[example_country, example_other_country],
        dates=example_dates,
        other=["12"],
        otherOptional=None,
        single_val="single",
    )

    filename = tmpdir.join(f"integration_test_optional_missing_deprecated_new_two_level_.xlsx")
    # filename = f"integration_test_optional_missing_deprecated_new_two_level_.xlsx"
    write_across_many_sheets(
        filename, example_production_and_country, "ProductionAndCountries", "Production and Countries"
    )

    new_pandc = excel_doc_to_pydantic(filename, ProductionAndCountries, verbose=True)
    assert new_pandc.production.idno == "myidno"
    assert new_pandc.production.title is None
    assert len(new_pandc.production.authors) == 4
    assert author1 in new_pandc.production.authors
    assert author1 in new_pandc.production.authors
    assert author2 in new_pandc.production.authors
    assert author3 in new_pandc.production.authors
    assert len(new_pandc.countries) == 2
    assert example_country in new_pandc.countries
    assert example_other_country in new_pandc.countries
    assert new_pandc.dates == example_dates
    assert new_pandc.other == ["12"]
    assert new_pandc.otherOptional is None or new_pandc.otherOptional == []
    assert new_pandc.single_val == "single"


def test_union_list(tmpdir):
    class Method(BaseModel):
        """
        Methodology and processing
        """

        study_class: Optional[Union[str, List[Any]]] = Field(
            None,
            description=(
                "Generally used to give the data archive's class or study status number, which indicates the processing"
                " status of the study. May also be used as a text field to describe processing status. Example: `DDA Class"
                " C`, `Study is available from http://example.com` "
            ),
            title="Class of the Study",
        )

    class StudyDesc(BaseModel):
        """
        Study Description
        """

        method: Optional[Method] = Field(
            None, description="Methodology and processing", title="Methodology and Processing"
        )

    class MicrodataSchema(BaseModel):
        """
        Schema for Microdata data type based on DDI 2.5
        """

        study_desc: Optional[StudyDesc] = None

    ms = MicrodataSchema(study_desc=StudyDesc(method=Method(study_class=["a1", "b2"])))
    filename = tmpdir.join(f"integration_test_union_list_.xlsx")
    write_across_many_sheets(filename, ms, "UnionList", "Looking at a union with a list")

    parsed_outp = excel_doc_to_pydantic(filename, MicrodataSchema)
    assert parsed_outp == ms, parsed_outp


def test_dictionaries(tmpdir):
    class SubDict(BaseModel):
        sub_additional: Optional[Dict[str, Any]] = Field(None, description="Additional metadata at a lower level")

    class WithDict(BaseModel):
        additional: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
        optional_dict: Optional[Dict[str, Any]] = None
        sub: SubDict

    wd = WithDict(additional={"s": "sa", "a": "va"}, sub=SubDict(sub_additional={"sub": "subval", "sub2": "subval2"}))
    filename = tmpdir.join(f"integration_test_dictionaries_.xlsx")
    write_across_many_sheets(filename, wd, "WithDict", "Looking at dictionaries")

    parsed_outp = excel_doc_to_pydantic(filename, WithDict)
    assert parsed_outp == wd, parsed_outp


def test_list_of_lists(tmpdir):
    class Citation(BaseModel):
        """
        A set of elements to describe a resource citation
        """

        title: Optional[str] = Field(None, description="Resource title", title="Title")
        alternateTitle: Optional[List[str]] = Field(
            None, description="Resource alternate title", title="Alternate Title"
        )

    class IdentificationInfo(BaseModel):
        """
        Identification(s) of the resource
        """

        citation: Optional[Citation] = Field(None, description="Dataset citation", title="Citation")

    class LegalConstraints(BaseModel):
        """
        Legal constraints associated to the resource
        """

        useLimitation: Optional[List[str]] = None
        accessConstraints: Optional[List[str]] = Field(
            None,
            description=(
                "A restriction to access/use a resource. e.g. 'dataset'. Recommended code following the [ISO/TS"
                " 19139](http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode) Restriction"
                " codelist. Suggested values: {`copyright`, `patent`, `patentPending`, `trademark`, `license`,"
                " `intellectualPropertyRights`, `restricted`, `otherRestrictions`, `unrestricted`, `licenceUnrestricted`,"
                " `licenceEndUser`, `licenceDistributor`, `private`, `statutory`, `confidential`, `SBU`, `in-confidence`}"
            ),
            title="Access constraints",
        )

    class Constraints(BaseModel):
        """
        Constraints associated to the resource
        """

        legalConstraints: Optional[LegalConstraints] = Field(
            None, description="Legal constraints associated to the resource", title="Legal constraints"
        )

    class ServiceIdentification(BaseModel):
        """
        Service identification
        """

        restrictions: Optional[List[Constraints]] = Field(
            None, description="Constraints associated to the service", title="Service constraints"
        )

    class MetaDataOfVariousHierarchies(BaseModel):
        citation: Optional[Citation] = None
        identification_info: Optional[IdentificationInfo] = None
        lst: Optional[List[str]] = (None,)
        service_identification: Optional[ServiceIdentification] = None

    inp = MetaDataOfVariousHierarchies(
        citation=Citation(title="topleveltitle", alternateTitle=[]),
        identification_info=IdentificationInfo(
            citation=Citation(title="citation_title", alternateTitle=["alt_title_1", "alt_title_2"])
        ),
        lst=["a", "b", "c"],
        service_identification=ServiceIdentification(
            restrictions=[
                Constraints(legalConstraints=LegalConstraints(useLimitation=["s1", "s2"], accessConstraints=["s3"]))
            ]
        ),
    )

    # index = pd.MultiIndex.from_tuples([("identification_info", "citation", "title"), ("identification_info", "citation", "alternateTitle"), ("service_identification", "restrictions", "legalConstraints", "useLimitation"), ("service_identification", "restrictions", "legalConstraints", "accessConstraints")])

    # expected = pd.DataFrame([["citation_title", None], ["alt_title_1", "alt_title_2"], [[], None], [[], None]], index=index)

    filename = tmpdir.join(f"integration_test_list_of_lists_.xlsx")
    # filename = "integration_test_list_of_lists_.xlsx"
    if os.path.exists(filename):
        os.remove(filename)
    write_across_many_sheets(filename, inp, "ListOfLists", "Looking at lists of lists")

    expected = inp
    expected.citation.alternateTitle = None
    actual = excel_doc_to_pydantic(filename, MetaDataOfVariousHierarchies, verbose=True)
    # assert actual == inp, actual

    # outp = pydantic_to_dataframe(inp)
    # actual = outp[0]
    # list_indices = outp[1]
    # enums = outp[2]
    assert expected.citation == actual.citation, actual.citation
    assert expected.identification_info == actual.identification_info, actual.identification_info
    assert expected.service_identification == actual.service_identification, actual.service_identification
    assert expected.lst == actual.lst, actual.lst
    assert expected == actual, actual
    # assert list_indices == [1, 2, 3], list_indices
    # assert enums == {}, enums


NAME_TO_TYPE = {
    "Document": (ScriptSchemaDraft, write_across_many_sheets, excel_doc_to_pydantic),
    "Geospatial": (GeospatialSchema, write_across_many_sheets, excel_doc_to_pydantic),
    # "Image":ImageDataTypeSchema,
    "Microdata": (MicrodataSchema, write_across_many_sheets, excel_doc_to_pydantic),
    "Script": (ResearchProjectSchemaDraft, write_across_many_sheets, excel_doc_to_pydantic),
    "Table": (TableModel, write_across_many_sheets, excel_doc_to_pydantic),
    "Indicator_DB": (
        TimeseriesDatabaseSchema,
        write_to_single_sheet,
        excel_single_sheet_to_pydantic,
    ),  # could be one sheet
    "Indicator": (TimeseriesSchema, write_across_many_sheets, excel_doc_to_pydantic),
    "Video": (VideoModel, write_to_single_sheet, excel_single_sheet_to_pydantic),  # could be one sheet
}


@pytest.mark.parametrize("name, type_writer_reader", [(k, v) for k, v in NAME_TO_TYPE.items()])
def test_write_real_skeleton(tmpdir, name, type_writer_reader):
    type, writer, reader = type_writer_reader
    # folder = "excel_sheets"
    filename = os.path.join(tmpdir, f"{name}_metadata.xlsx")
    # filename = f"{name}_metadata_real_sckele.xlsx"
    if os.path.exists(filename):
        os.remove(filename)
    ob = make_skeleton(type)

    writer(filename, ob, name, f"{name} Metadata")
    reader(filename, type, verbose=True)
    # assert False


def test_demo():
    filename = "demo_output.xlsx"
    sheet_title = "Formatting metadata examples"

    class SingleLevelData(BaseModel):
        title: Optional[str] = None
        author: str

    class Country(BaseModel):
        name: str
        initials: str
        list_of_alternative_names: Optional[List[str]] = None

    class Description(BaseModel):
        statement: str
        abstract: str

    class MultiLevelAndListData(BaseModel):
        description: Description
        countries: List[Country]
        organization: str

    class SubObject(BaseModel):
        a: str
        b: str

    class Citation(BaseModel):
        """
        A set of elements to describe a resource citation
        """

        title: Optional[str] = Field(None, description="Resource title", title="Title")
        alternateTitle: Optional[List[str]] = Field(
            None, description="Resource alternate title", title="Alternate Title"
        )

    class IdentificationInfo(BaseModel):
        """
        Identification(s) of the resource
        """

        citation: Optional[Citation] = Field(None, description="Dataset citation", title="Citation")

    class LegalConstraints(BaseModel):
        """
        Legal constraints associated to the resource
        """

        useLimitation: Optional[List[str]] = None
        accessConstraints: Optional[List[str]] = Field(
            None,
            description=(
                "A restriction to access/use a resource. e.g. 'dataset'. Recommended code following the [ISO/TS"
                " 19139](http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode) Restriction"
                " codelist. Suggested values: {`copyright`, `patent`, `patentPending`, `trademark`, `license`,"
                " `intellectualPropertyRights`, `restricted`, `otherRestrictions`, `unrestricted`, `licenceUnrestricted`,"
                " `licenceEndUser`, `licenceDistributor`, `private`, `statutory`, `confidential`, `SBU`, `in-confidence`}"
            ),
            title="Access constraints",
        )

    class Constraints(BaseModel):
        """
        Constraints associated to the resource
        """

        legalConstraints: Optional[LegalConstraints] = Field(
            None, description="Legal constraints associated to the resource", title="Legal constraints"
        )

    class ServiceIdentification(BaseModel):
        """
        Service identification
        """

        restrictions: Optional[List[Constraints]] = Field(
            None, description="Constraints associated to the service", title="Service constraints"
        )

    class MetaDataOfVariousHierarchies(BaseModel):
        idno: Optional[str] = None
        database_name: Optional[str] = None
        single_level_data: SingleLevelData
        multi_level_data: MultiLevelAndListData
        top_level_list: List[str]
        top_level_optional_list: Optional[List[str]] = None
        top_level_list_of_pydantic_objects: List[SubObject]
        dictionary: Dict[str, str]
        identification_info: Optional[IdentificationInfo] = None
        service_identification: Optional[ServiceIdentification] = None

    example = MetaDataOfVariousHierarchies(
        single_level_data=SingleLevelData(title="Metadata demo", author="FirstName LastName"),
        multi_level_data=MultiLevelAndListData(
            description=Description(statement="Data can be hierarchical", abstract="like this"),
            countries=[
                Country(name="MyCountry", initials="MC", list_of_alternative_names=["And Lists", "can have lists"]),
                Country(name="YourCountry", initials="YC"),
            ],
            organization="Example Org",
        ),
        top_level_list=["a", "b"],
        top_level_list_of_pydantic_objects=[SubObject(a="asub", b="b")],
        dictionary={"example_key": "example_value"},
        identification_info=IdentificationInfo(
            citation=Citation(title="citation_title", alternateTitle=["alt_title_1", "alt_title_2"])
        ),
        service_identification=ServiceIdentification(
            restrictions=[Constraints(legalConstraints=LegalConstraints(useLimitation=[], accessConstraints=[]))]
        ),
    )

    if os.path.exists(filename):
        os.remove(filename)

    write_to_single_sheet(filename, example, "MetaDataOfVariousHierarchies", sheet_title, verbose=True)

    # current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)
    # current_row = write_nested_simple_pydantic_to_sheet(filename, sheetname, example, current_row + 1)
    # worksheet = open_or_create_workbook(filename)
    # correct_column_widths(worksheet, sheet_name=sheetname)
    # shade_30_rows_and_protect_sheet(worksheet, sheetname, current_row + 1)
    # shade_locked_cells(worksheet, sheetname)
    # worksheet.save(filename)
