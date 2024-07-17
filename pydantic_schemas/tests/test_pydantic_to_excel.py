from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import pytest
from pydantic import BaseModel, Field

from ..excel_to_pydantic import excel_sheet_to_pydantic, get_instance
from ..pydantic_to_excel import (
    correct_column_widths,
    create_sheet_and_write_title,
    shade_30_rows,
    shade_locked_cells,
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

    current_row = write_simple_pydantic_to_sheet(
        filename, sheetname, simple_original, current_row + 1, index_above=index_above
    )
    correct_column_widths(filename, sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

    parsed_simple = excel_sheet_to_pydantic(filename, sheetname, Simple)
    assert parsed_simple == simple_original


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
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"
    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)

    current_row = write_nested_simple_pydantic_to_sheet(filename, sheetname, inp, current_row, index_above=index_above)
    correct_column_widths(filename, sheetname)
    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

    parsed_outp = excel_sheet_to_pydantic(filename, sheetname, ProductionAndCountries)
    assert parsed_outp == inp


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

    series_description = SeriesDescription(
        language=Language(name="English", code="EN"), topic=Topic(id="topic1", name="topic1")
    )

    inp = ProductionAndCountries(
        production=Production(idno="AVal", title="BVal", author="CVal"),
        countries=Country(name="MyCountry", initials="MC"),
        series_description=series_description,
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
    assert parsed_outp == inp
