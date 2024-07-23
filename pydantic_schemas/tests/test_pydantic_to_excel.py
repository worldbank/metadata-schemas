import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import pytest
from pydantic import BaseModel, Field

from ..excel_to_pydantic import excel_sheet_to_pydantic
from ..pydantic_to_excel import (
    correct_column_widths,
    create_sheet_and_write_title,
    shade_30_rows,
    shade_locked_cells,
    write_across_many_sheets,
    write_nested_simple_pydantic_to_sheet,
    write_simple_pydantic_to_sheet,
)


@pytest.mark.parametrize("index_above", [True, False])
def test_simple_schema(tmpdir, index_above):
    class Simple(BaseModel):
        idno: str
        title: str
        author: str

    simple_original = Simple(idno="AVal", title="BVal", author="CVal")

    filename = tmpdir.join(f"integration_test_simple_schema_{index_above}.xlsx")
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"
    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)

    current_row = write_nested_simple_pydantic_to_sheet(
        filename, sheetname, simple_original, current_row + 1, index_above=index_above
    )
    correct_column_widths(filename, sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

    parsed_simple = excel_sheet_to_pydantic(filename, sheetname, Simple)
    assert parsed_simple == simple_original, parsed_simple


@pytest.mark.parametrize("index_above", [True, False])
def test_two_layer_simple_schema(tmpdir, index_above):
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

    filename = tmpdir.join(f"integration_test_two_layer_simple_schema_{index_above}.xlsx")
    # filename = "GORDON_twolayer.xlsx"
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"
    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)

    current_row = write_nested_simple_pydantic_to_sheet(filename, sheetname, inp, current_row, index_above=index_above)
    correct_column_widths(filename, sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

    parsed_outp = excel_sheet_to_pydantic(filename, sheetname, ProductionAndCountries)
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
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"

    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)
    current_row = write_nested_simple_pydantic_to_sheet(filename, sheetname, inp, current_row + 1)
    correct_column_widths(filename, sheet_name=sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

    parsed_outp = excel_sheet_to_pydantic(filename, sheetname, ProductionAndCountries)
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
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"

    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)
    current_row = write_nested_simple_pydantic_to_sheet(filename, sheetname, original_production, current_row + 1)
    correct_column_widths(filename, sheet_name=sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

    class Production(BaseModel):
        idno: Optional[str] = None
        title: Optional[str] = None
        author: str
        newFeature: Optional[str] = None
        requiredNewFeature: str

    new_production = excel_sheet_to_pydantic(filename=filename, sheetname=sheetname, model_type=Production)
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
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"

    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)
    current_row = write_nested_simple_pydantic_to_sheet(
        filename, sheetname, example_production_and_country, current_row + 1
    )
    correct_column_widths(filename, sheet_name=sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

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

    new_pandc = excel_sheet_to_pydantic(filename=filename, sheetname=sheetname, model_type=ProductionAndCountries)
    assert new_pandc.production.idno is None
    assert new_pandc.production.title is None
    assert new_pandc.production.author == "author"
    assert new_pandc.production.newFeature is None
    assert new_pandc.production.requiredNewFeature == ""
    assert new_pandc.countries.name == "MadeupCountry"
    assert new_pandc.countries.initials == "MC"


def test_lists(tmpdir):
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

    author0 = Person(name="person_0")
    author1 = Person(name="person_1", affiliations=["Org1", "Org2"])
    author2 = Person(name="person_2")
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
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"

    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)
    current_row = write_nested_simple_pydantic_to_sheet(
        filename, sheetname, example_production_and_country, current_row + 1
    )
    correct_column_widths(filename, sheet_name=sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)
    new_pandc = excel_sheet_to_pydantic(filename=filename, sheetname=sheetname, model_type=ProductionAndCountries)
    assert new_pandc.production.idno is None
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
    title = "Example"
    write_across_many_sheets(filename, example_production_and_country, title)


def test_demo():
    filename = "demo_output.xlsx"
    sheetname = "metadata"
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

    class MetaDataOfVariousHierarchies(BaseModel):
        idno: Optional[str] = None
        database_name: Optional[str] = None
        single_level_data: SingleLevelData
        multi_level_data: MultiLevelAndListData
        top_level_list: List[str]
        top_level_optional_list: Optional[List[str]] = None
        top_level_list_of_pydantic_objects: List[SubObject]

    example = MetaDataOfVariousHierarchies(
        single_level_data=SingleLevelData(title="Metadata demo", author="FirstName LastName"),
        multi_level_data=MultiLevelAndListData(
            description=Description(statement="Data can be hierarchical", abstract="Or it can be in lists"),
            countries=[
                Country(name="MyCountry", initials="MC", list_of_alternative_names=["Lists", "can have lists"]),
                Country(name="YourCountry", initials="YC"),
            ],
            organization="Example Org",
        ),
        top_level_list=["a", "b"],
        top_level_list_of_pydantic_objects=[SubObject(a="a", b="b")],
    )

    if os.path.exists(filename):
        os.remove(filename)

    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)
    current_row = write_nested_simple_pydantic_to_sheet(filename, sheetname, example, current_row + 1)
    correct_column_widths(filename, sheet_name=sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)
