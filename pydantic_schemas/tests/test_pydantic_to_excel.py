from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pytest
from pydantic import BaseModel

from ..excel_to_pydantic import excel_to_pydantic
from ..pydantic_to_excel import (
    create_sheet_and_write_title,
    shade_30_rows,
    shade_locked_cells,
    write_simple_pydantic_to_sheet,
)


@pytest.mark.parametrize("index_above", [True, False])
def test_simple_schema(tmpdir, index_above):
    class Simple(BaseModel):
        idno: str
        title: str
        author: str

    simple_original = Simple(idno="AVal", title="BVal", author="CVal")

    filename = tmpdir.join(f"integration_test_simple_{index_above}.xlsx")
    sheetname = "Document Metadata"
    sheet_title = "Document Metadata"
    current_row = create_sheet_and_write_title(filename, sheetname, sheet_title)

    current_row = write_simple_pydantic_to_sheet(
        filename, sheetname, simple_original, current_row + 1, index_above=index_above
    )

    shade_30_rows(filename, sheetname, current_row + 1)
    shade_locked_cells(filename, sheetname)

    parsed_output = excel_to_pydantic("GORDON.xlsx", "Document Metadata", {"simple": Simple})
    assert parsed_output["simple"] == simple_original
