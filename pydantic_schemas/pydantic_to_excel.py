import os
from typing import Optional, Type

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Protection
from pydantic import BaseModel


def protect_and_shade_given_cell(sheet, row: int, col: int):
    grey_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    sheet.cell(row=row, column=col).fill = grey_fill
    sheet.cell(row=row, column=col).protection = Protection(locked=True)


def protect_and_shade_row(sheet, row: int, colmin: int = 1, colmax: Optional[int] = None):
    if colmax is None:
        colmax = max(colmin, 27, sheet.max_column)
    for col in range(colmin, colmax):
        protect_and_shade_given_cell(sheet, row, col)


def protect_and_shade_col(sheet, col: int, rowmin: int, rowmax: int):
    for row in range(rowmin, rowmax):
        protect_and_shade_given_cell(sheet, row, col)


def unprotect_cell(sheet, row, column):
    sheet.cell(row=row, column=column).protection = Protection(locked=False)


def unprotect_row(sheet, row, colmin: int, colmax: Optional[int] = None):
    if colmax is None:
        colmax = max(colmin, 27, sheet.max_column)
    for col in range(colmin, colmax):
        unprotect_cell(sheet, row, col)


def unprotect_given_col(sheet, col: int, rowmin: int, rowmax: int):
    for row in range(rowmin, rowmax):
        unprotect_cell(sheet, row, col)


def shade_30_rows(doc_filepath: str, sheet_name: str, startrow: int):
    wb = load_workbook(doc_filepath)
    ws = wb[sheet_name]
    for r in range(startrow, startrow + 30):
        protect_and_shade_row(ws, r)
    wb.save(doc_filepath)


def correct_column_widths(filename: str, sheet_name: str):
    """
    Adjusts the column widths of an Excel sheet based on the maximum length of the content in each column.
    If a column has no filled values, its width remains unchanged.

    Args:
        filename (str): The path to the Excel file.
        sheet_name (str): The name of the sheet to adjust column widths for.
    """
    # Load the existing workbook
    wb = load_workbook(filename)
    ws = wb[sheet_name]

    # Adjust column widths based on the maximum length of the content in each column
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        if max_length > 0:  # Only adjust if there are filled values in the column
            adjusted_width = max_length + 2
            ws.column_dimensions[column].width = adjusted_width

    # Save the workbook
    wb.save(filename)


def shade_locked_cells(filename: str, sheet_name: str):
    """
    Shades every cell grey if it is locked and leaves it unshaded if it is not locked.

    Args:
        filename (str): The path to the Excel file.
        sheet_name (str): The name of the sheet to apply the shading.
    """
    # Load the existing workbook
    wb = load_workbook(filename)
    ws = wb[sheet_name]

    # Define the grey fill
    grey_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

    # Iterate through each cell in the worksheet
    for row in ws.iter_rows():
        for cell in row:
            if cell.protection.locked:
                cell.fill = grey_fill
            else:
                cell.fill = PatternFill()  # Remove any fill (reset to default)

    # Save the workbook
    wb.save(filename)


def write_to_cell(filename: str, sheet_name: str, row: int, col: int, text: str, isBold=False):
    """
    Writes text to a specified cell in the Excel file.

    Args:
        filename (str): The path to the Excel file.
        sheet_name (str): The name of the sheet.
        row_num (int): The row number (1-based index).
        col_num (int): The column number (1-based index).
        text (str): The text to write to the cell.
    """
    # Load the existing workbook or create a new one if it doesn't exist
    try:
        wb = load_workbook(filename)
    except FileNotFoundError:
        wb = Workbook()

    # Select the worksheet by name
    ws = wb[sheet_name]

    # Write text to the specified cell
    cell = ws.cell(row=row, column=col, value=text)
    cell.font = Font(bold=isBold)

    protect_and_shade_row(ws, row=row, colmin=col)

    # Save the workbook
    wb.save(filename)

    return row + 1


def create_sheet_and_write_title(doc_filepath: str, sheet_name: str, sheet_title: str, sheet_number: int = 0):
    """
    In the given excel document, creates a new sheet called sheet_name and in the top left cell
    writes in sheet_title in bold.

    It will create the excel document at doc_filepath if it does not already exist.

    The new sheet will be inserted at the specified sheet_number position. If sheet_number is
    greater than the total number of sheets, the new sheet will be added at the end.

    Args:
        doc_filepath (str): The path to the Excel document.
        sheet_name (str): The name of the new sheet to create.
        sheet_title (str): The title to write in the top left cell of the new sheet, in bold.
        sheet_number (int): The position to insert the new sheet (0-indexed). If greater than the
                            total number of sheets, the new sheet will be added at the end.

    Returns:
        int: index of next row below the final written row

    Raises:
        ValueError: if a sheet called sheet_name already exists in the document to prevent overwriting.
    """
    # Check if the file exists
    if os.path.exists(doc_filepath):
        workbook = load_workbook(doc_filepath)
    else:
        workbook = Workbook()
        # Remove the default sheet created by Workbook()
        if len(workbook.sheetnames) == 1 and workbook.sheetnames[0] == "Sheet":
            del workbook["Sheet"]

    # Check if the sheet already exists
    if sheet_name in workbook.sheetnames:
        raise ValueError(f"A sheet called '{sheet_name}' already exists in the document.")

    # Create a new sheet
    new_sheet = workbook.create_sheet(title=sheet_name)

    # Write the title in bold in the top left cell (A1)
    bold_font = Font(bold=True, size=14)
    new_sheet["A1"] = sheet_title
    new_sheet["A1"].font = bold_font

    # Shade the background of the cells in the first 2 rows grey and lock them
    for row in range(1, 3):
        protect_and_shade_row(new_sheet, row)

    # Determine the position to insert the new sheet
    total_sheets = len(workbook.sheetnames)
    insert_position = min(sheet_number, total_sheets)

    # Move the new sheet to the specified position
    workbook._sheets.insert(insert_position, workbook._sheets.pop())

    # Save the workbook
    workbook.save(doc_filepath)

    return 3


def write_simple_pydantic_to_sheet(doc_filepath: str, sheet_name: str, ob: BaseModel, startrow: int, index_above=False):
    """
    Returns:
        int: index of next row below the final written row
    """
    startrow = write_to_cell(doc_filepath, sheet_name, startrow, 1, ob.model_json_schema()["title"], isBold=True)
    startcol = 2

    ob_dict = ob.model_dump(mode="json")
    df = pd.json_normalize(ob_dict).T
    if index_above:
        df = df.T

    # Annoyingly, openpyxl uses 1 based indexing but
    # But pandas uses 0 based indexing.

    with pd.ExcelWriter(doc_filepath, mode="a", if_sheet_exists="overlay") as writer:
        df.to_excel(
            writer,
            sheet_name=sheet_name,
            header=index_above,
            index=not index_above,
            startrow=startrow - 1,
            startcol=startcol - 1,
            merge_cells=True,
        )

    # Open the Excel file with openpyxl
    workbook = load_workbook(doc_filepath)
    sheet = workbook[sheet_name]

    # Get the DataFrame dimensions
    rows, cols = df.shape

    if index_above:
        protect_and_shade_row(sheet, startrow)
        for c in range(startcol, cols + startcol):
            cell = sheet.cell(startrow, c)
            cell.font = Font(bold=False)
        for r in range(startrow + 1, startrow + rows + 1):
            unprotect_row(sheet, r, startcol, colmax=startcol + cols)
            protect_and_shade_row(sheet, r, colmin=startcol + cols)
    else:
        protect_and_shade_col(sheet, startcol, startrow, startrow + rows)
        for r in range(startrow, startrow + rows):
            cell = sheet.cell(r, startcol)
            cell.font = Font(bold=False)
            unprotect_row(sheet, r, startcol + 1, colmax=startcol + cols + 1)
            protect_and_shade_row(sheet, r, colmin=cols + startcol + 1)

    sheet.protection.enable()
    # Save the workbook
    workbook.save(doc_filepath)

    return startrow + rows
