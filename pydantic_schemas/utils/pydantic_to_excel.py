import os
import typing
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill, Protection
from openpyxl.worksheet.protection import SheetProtection
from pydantic import BaseModel

from .utils import (
    annotation_contains_dict,
    annotation_contains_list,
    assert_dict_annotation_is_strings_or_any,
    seperate_simple_from_pydantic,
    subset_pydantic_model,
)

MAXCOL = 30


def protect_and_shade_given_cell(sheet, row: int, col: int):
    grey_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    sheet.cell(row=row, column=col).fill = grey_fill
    sheet.cell(row=row, column=col).protection = Protection(locked=True)


def protect_and_shade_row(sheet, row: int, colmin: int = 1, colmax: Optional[int] = None):
    if colmax is None:
        colmax = max(colmin, MAXCOL, sheet.max_column)
    for col in range(colmin, colmax):
        protect_and_shade_given_cell(sheet, row, col)


def protect_and_shade_col(sheet, col: int, rowmin: int, rowmax: int):
    for row in range(rowmin, rowmax):
        protect_and_shade_given_cell(sheet, row, col)


def unprotect_cell(sheet, row, column):
    sheet.cell(row=row, column=column).protection = Protection(locked=False)


def unprotect_row(sheet, row, colmin: int, colmax: Optional[int] = None):
    if colmax is None:
        colmax = max(colmin, MAXCOL, sheet.max_column)
    for col in range(colmin, colmax + 1):
        unprotect_cell(sheet, row, col)


def unprotect_given_col(sheet, col: int, rowmin: int, rowmax: int):
    for row in range(rowmin, rowmax):
        unprotect_cell(sheet, row, col)


def open_or_create_workbook(doc_filepath):
    if os.path.exists(doc_filepath):
        workbook = load_workbook(doc_filepath)
    else:
        workbook = Workbook()
        # Remove the default sheet created by Workbook()
        if len(workbook.sheetnames) == 1 and workbook.sheetnames[0] == "Sheet":
            del workbook["Sheet"]
    return workbook


def shade_30_rows_and_protect_sheet(workbook: Workbook, sheet_name: str, startrow: int):
    """For use after all data is written so there is a clear border around the data"""
    ws = workbook[sheet_name]
    for r in range(startrow, startrow + 30):
        protect_and_shade_row(ws, r)
    ws.protection = SheetProtection(
        sheet=True,
        formatCells=False,
        formatColumns=False,
        formatRows=False,
        insertColumns=False,
        insertRows=True,
        insertHyperlinks=False,
        deleteColumns=False,
        deleteRows=True,
        selectLockedCells=False,
        selectUnlockedCells=False,
    )


def correct_column_widths(workbook: Workbook, sheet_name: str):
    """
    Adjusts the column widths of an Excel sheet based on the maximum length of the content in each column.
    If a column has no filled values, its width remains unchanged.

    Args:
        workbook (Workbook): The openPyxl Workbook of an Excel file.
        sheet_name (str): The name of the sheet to adjust column widths for.
    """
    # Load the existing workbook
    ws = workbook[sheet_name]
    # Adjust column widths based on the maximum length of the content in each column
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column letter
        for cell in col:
            if column != "A":
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            if cell.value is not None:
                cell_length = len(str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
        if max_length > 0:  # Only adjust if there are filled values in the column
            max_length = max(min(max_length, 28), 11)
            adjusted_width = max_length + 2
            ws.column_dimensions[column].width = adjusted_width


def shade_locked_cells(workbook: Workbook, sheet_name: str):
    """
    Shades every cell grey if it is locked and leaves it unshaded if it is not locked.

    Args:
        workbook (Workbook): The openPyxl Workbook of an Excel file.
        sheet_name (str): The name of the sheet to apply the shading.
    """
    # Load the existing workbook
    ws = workbook[sheet_name]

    # Define the grey fill
    grey_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

    # Iterate through each cell in the worksheet
    for row in ws.iter_rows():
        for cell in row:
            if cell.protection.locked:
                cell.fill = grey_fill
            else:
                cell.fill = PatternFill()  # Remove any fill (reset to default)


def write_to_cell(
    filename: str, sheet_name: str, row: int, col: int, text: str, isBold=False, size=14, debug: bool = False
):
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
    cell.font = Font(bold=isBold, size=size)

    protect_and_shade_row(ws, row=row, colmin=col)

    # Save the workbook
    wb.save(filename)

    return row + 1


def create_sheet_and_write_title(
    doc_filepath: str,
    sheet_name: str,
    sheet_title: Optional[str] = None,
    sheet_number: int = 0,
    protect_title: bool = True,
    debug=False,
):
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
    workbook = open_or_create_workbook(doc_filepath)

    # Check if the sheet already exists
    if sheet_name in workbook.sheetnames:
        raise ValueError(f"A sheet called '{sheet_name}' already exists in the document.")

    # Create a new sheet
    new_sheet = workbook.create_sheet(title=sheet_name)

    if sheet_title is not None:
        # Write the title in bold in the top left cell (A1)
        bold_font = Font(bold=True, size=14)
        new_sheet["A1"] = sheet_title.replace("_", " ")
        new_sheet["A1"].font = bold_font

        # Shade the background of the cells in the first 2 rows grey and lock them
        # for row in range(1, 3):
        #     protect_and_shade_row(new_sheet, row)
        if protect_title:
            protect_and_shade_given_cell(new_sheet, 1, 1)
        else:
            unprotect_cell(new_sheet, 1, 1)
        protect_and_shade_row(new_sheet, 1, 2)
        protect_and_shade_row(new_sheet, 2)

    # Determine the position to insert the new sheet
    total_sheets = len(workbook.sheetnames)
    insert_position = min(sheet_number, total_sheets)

    # Move the new sheet to the specified position
    workbook._sheets.insert(insert_position, workbook._sheets.pop())

    # Save the workbook
    workbook.save(doc_filepath)

    if sheet_title is not None:
        return 3
    else:
        return 0


def replace_row_with_multiple_rows(original_df, new_df, row_to_replace):
    """
    Replace a specified row in the original DataFrame with multiple rows from the new DataFrame.

    Parameters:
    original_df (pd.DataFrame): The original DataFrame.
    new_df (pd.DataFrame): The new DataFrame with the rows to insert.
    row_to_replace (str): The name of the row to be replaced.

    Returns:
    pd.DataFrame: The updated DataFrame with the specified row replaced by the new rows.
    """
    # Split the original DataFrame into two parts: before and after the row to be replaced
    df_before = original_df.loc[:row_to_replace].iloc[:-1]
    df_after = original_df.loc[row_to_replace:].drop(row_to_replace, axis=0)

    # Concatenate the parts with the new rows
    df_replaced = pd.concat([df_before, new_df, df_after])
    # df_replaced = df_replaced.dropna(how="all", axis=1)
    return df_replaced


def pydantic_to_dataframe(
    ob: Union[BaseModel, Dict, List[Dict]],
    annotations: Optional[Dict[str, typing._UnionGenericAlias]] = None,
    debug: bool = False,
) -> Tuple[pd.DataFrame, List[int]]:
    """
    Convert to a dataframe, identifying rows that are made of lists and exploding them over multiple rows with
    hierarchical indices if needed.

    Returns the dataframe and also a list of the indexs (denoted by zero-based numbers) that are of list types.
    The list of indexs is intended to be used for appropriately shading the excel sheet.
    """
    if isinstance(ob, BaseModel):
        ob_dict = ob.model_dump(mode="json")
    else:
        ob_dict = ob
    try:
        df = pd.json_normalize(ob_dict).T
    except NotImplementedError:
        raise NotImplementedError(ob)
    if debug:
        print("pydantic_to_dataframe")
        print(df)
    list_indices = []
    if isinstance(ob, list):
        list_indices = list(range(len(df)))
    else:
        for idx, _ in ob_dict.items():
            if annotations is not None and annotation_contains_dict(annotations[idx]):
                if debug:
                    print("Found a dictionary")
                assert_dict_annotation_is_strings_or_any(annotations[idx])
                field = ob_dict[idx]
                if field is None or len(field) == 0:
                    dict_df = pd.DataFrame(["", ""], index=["key", "value"])
                else:
                    dict_df = pd.DataFrame([field.keys(), field.values()], index=["key", "value"])
                dict_df.index = dict_df.index.map(lambda x: f"{idx}.{x}")
                df = df[~df.index.str.startswith(f"{idx}.")]
                df = df[df.index != idx]
                df = pd.concat([df, dict_df])
        i = 0
        for idx in df.index:
            if debug:
                print(f"pydantic_to_dataframe::283 idx = {idx}, df = {df}")
            vals = df.loc[idx][0]
            field = ob_dict[idx.split(".")[0]]

            if (
                isinstance(vals, list)
                or (annotations is not None and annotation_contains_list(annotations[idx.split(".")[0]]))
                or (annotations is not None and annotation_contains_dict(annotations[idx.split(".")[0]]))
            ):  # (hasattr(ob, "annotation") and annotation_contains_list(ob.annotation)):
                if vals is not None and len(vals) > 0 and (isinstance(vals[0], BaseModel) or isinstance(vals[0], Dict)):
                    if debug:
                        print("list of base models", vals[0])
                    sub = pd.json_normalize(df.loc[idx].values[0]).reset_index(drop=True).T
                    sub.index = sub.index.map(lambda x: f"{idx}." + x)
                    df = replace_row_with_multiple_rows(df, sub, idx)
                    list_indices += list(range(i, i + len(sub)))
                    i += len(sub)
                else:
                    if debug:
                        print("list of builtins or else empty")
                    df = replace_row_with_multiple_rows(
                        df, df.loc[idx].explode().to_frame().reset_index(drop=True).T, idx
                    )
                    list_indices.append(i)
                    i += 1
            else:
                i += 1
    if debug:
        print(df)
    if len(df):
        df.index = df.index.str.split(".", expand=True)
    return df, list_indices


def write_simple_pydantic_to_sheet(
    doc_filepath: str,
    sheet_name: str,
    ob: BaseModel,
    startrow: int,
    index_above=False,
    write_title=True,
    title: Optional[str] = None,
    annotations=None,
    debug: bool = False,
):
    """
    Assumes a pydantic object made up of built in types or pydantic objects utimately made of built in types or Lists.
    Do not use if the object or it's children contain  Dicts or enums.

    Starting from startrow, it writes the name of the pydantic object in the first column. It then writes the data
    starting in the row below and from the second column.

    If index_above = False then the data is printed with indexs down the second column and values down the third column
    If index_above = True then the data is printed with indexs along the second row and values along the third row

    Example:

        class Simple(BaseModel):
            a: str
            b: str

        example = Simple(a="value_a", b="value_b")
        # with index_above=True
        write_simple_pydantic_to_sheet("filename", "sheetname", example, startrow=1, index_above=True)

        gives:

            Simple
                   a            b
                   value_a      value_b

        # with index_above=False
        write_simple_pydantic_to_sheet("filename", "sheetname", example, startrow=1, index_above=False)

        gives:

            Simple

                    a     value_a
                    b     value_b

    Args:
        doc_filepath (str): The path to the Excel document.
        sheet_name (str): The name of the new sheet to create.
        ob (BaseModel): a pydantic class
        startrow (int): the row from which to start writing the data
        index_above (bool): if True then the index is written along a row with the data below, if False then the data is
            written in a column with the data to the right. Default is False

    Returns:
        int: index of next row below the final written row
    """
    if write_title:
        if title is None:
            title = ob.model_json_schema()["title"]
        if startrow == 1:
            title = title.replace("_", " ")
            size = 14
        else:
            size = 12
        startrow = write_to_cell(doc_filepath, sheet_name, startrow, 1, title, isBold=True, size=size, debug=debug)
    startcol = 2

    df, list_rows = pydantic_to_dataframe(ob=ob, annotations=annotations, debug=debug)
    index_levels = df.index.nlevels
    # if index_above and index_levels > 1:
    #     warnings.warn(
    #         "Setting index_above=True is incompatible with a hierarchical index. Setting index_above to False.",
    #         UserWarning,
    #     )
    #     index_above = False

    # if index_above:
    #     df = df.T

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

    # if index_above:
    #     protect_and_shade_row(sheet, startrow)
    #     for c in range(startcol, cols + startcol):
    #         cell = sheet.cell(startrow, c)
    #         cell.font = Font(bold=False)
    #     for r in range(startrow + 1, startrow + rows + 1):
    #         unprotect_row(sheet, r, startcol, colmax=startcol + cols)
    #         protect_and_shade_row(sheet, r, colmin=startcol + cols)
    #     next_row = startrow + rows + 2
    # else:
    for col in range(startcol, startcol + index_levels):
        protect_and_shade_col(sheet, col, startrow, startrow + rows)
        for r in range(startrow, startrow + rows):
            cell = sheet.cell(r, col)
            cell.font = Font(bold=False)
    firstdatacol = startcol + index_levels
    for i, r in enumerate(range(startrow, startrow + rows)):
        if i in list_rows:
            unprotect_row(sheet, r, firstdatacol)
        else:
            unprotect_row(sheet, r, firstdatacol, colmax=firstdatacol + 1)
            protect_and_shade_row(sheet, r, colmin=firstdatacol + 1)
    next_row = startrow + rows

    sheet.protection.enable()
    # Save the workbook
    workbook.save(doc_filepath)

    return next_row


def write_nested_simple_pydantic_to_sheet(
    doc_filepath: str, sheet_name: str, ob: BaseModel, startrow: int, index_above=False, debug=False
):
    """
    Assumes the pydantic object is made up only of other pydantic objects that are themselves made up only of built in types
    """
    if debug:
        print(ob)
    children = seperate_simple_from_pydantic(ob)
    if debug:
        print(children["simple"])
    if len(children["simple"]):
        child_object = subset_pydantic_model(ob, children["simple"])
        startrow = write_simple_pydantic_to_sheet(
            doc_filepath,
            sheet_name,
            child_object,
            startrow,
            index_above=False,
            write_title=False,
            annotations={k: v.annotation for k, v in child_object.model_fields.items()},
            debug=debug,
        )
        if debug:
            print("Done with simple children, now nesting pydantic objects")
    for mfield in children["pydantic"]:
        field = ob.model_dump(mode="json")[mfield]
        if debug:
            print(f"write_nested_simple_pydantic_to_sheet::428, field={field}")
        startrow = write_simple_pydantic_to_sheet(
            doc_filepath, sheet_name, field, startrow, index_above=index_above, title=mfield, debug=debug
        )

    return startrow


def write_metadata_type_and_version(doc_filepath: str, metadata_type: str):
    wb = open_or_create_workbook(doc_filepath)
    sheet = wb["metadata"]

    sheet["C1"] = f"{metadata_type} type metadata version 20240809.1"

    version_font = Font(name="Consolas", size=9)
    sheet["C1"].font = version_font

    wb.save(doc_filepath)


def write_to_single_sheet(
    doc_filepath: str, ob: BaseModel, metadata_type: str, title: Optional[str] = None, debug=False
):
    if title is None:
        title = "Metadata"
    sheet_name = "metadata"
    current_row = create_sheet_and_write_title(
        doc_filepath, sheet_name, title, sheet_number=0, protect_title=False, debug=debug
    )
    write_metadata_type_and_version(doc_filepath=doc_filepath, metadata_type=metadata_type)
    current_row = write_nested_simple_pydantic_to_sheet(doc_filepath, sheet_name, ob, current_row + 1)
    workbook = open_or_create_workbook(doc_filepath)
    correct_column_widths(workbook, sheet_name=sheet_name)
    shade_30_rows_and_protect_sheet(workbook, sheet_name, current_row + 1)
    shade_locked_cells(workbook, sheet_name)
    workbook.save(doc_filepath)


def write_across_many_sheets(
    doc_filepath: str, ob: BaseModel, metadata_type: str, title: Optional[str] = None, debug=False
):
    children = seperate_simple_from_pydantic(ob)
    if debug:
        print(f"children: {children}")
    sheet_number = 0
    if len(children["simple"]):
        if title is None:
            title = "Metadata"
        sheet_name = "metadata"
        current_row = create_sheet_and_write_title(
            doc_filepath, sheet_name, title, sheet_number=sheet_number, protect_title=False, debug=debug
        )
        write_metadata_type_and_version(doc_filepath=doc_filepath, metadata_type=metadata_type)

        child_object = subset_pydantic_model(ob, children["simple"])

        current_row = write_simple_pydantic_to_sheet(
            doc_filepath,
            sheet_name,
            child_object,
            current_row + 1,
            index_above=False,
            write_title=False,
            annotations={k: v.annotation for k, v in child_object.model_fields.items()},
            debug=debug,
        )
        workbook = open_or_create_workbook(doc_filepath)
        correct_column_widths(workbook, sheet_name=sheet_name)
        shade_30_rows_and_protect_sheet(workbook, sheet_name, current_row + 1)
        shade_locked_cells(workbook, sheet_name)
        workbook.save(doc_filepath)
        sheet_number += 1

    for fieldname in children["pydantic"]:
        if debug:
            print(f"\n\n{fieldname}\n")
        field = getattr(ob, fieldname)
        if not isinstance(field, BaseModel):
            field = subset_pydantic_model(ob, [fieldname], name=fieldname)
            sheet_title = None
        else:
            sheet_title = fieldname
        current_row = create_sheet_and_write_title(
            doc_filepath, fieldname, sheet_title, sheet_number=sheet_number, protect_title=True, debug=debug
        )

        current_row = write_nested_simple_pydantic_to_sheet(doc_filepath, fieldname, field, current_row + 1)
        workbook = open_or_create_workbook(doc_filepath)
        correct_column_widths(workbook, sheet_name=fieldname)
        shade_30_rows_and_protect_sheet(workbook, fieldname, current_row + 1)
        shade_locked_cells(workbook, fieldname)
        workbook.save(doc_filepath)
        sheet_number += 1
