from typing import Any, Iterable, Mapping

import gspread

CellFormat = gspread.worksheet.CellFormat

def shared_formats(ranges: Iterable[str], shared_format: Mapping[str, Any]) -> list[CellFormat]:
    """Returns a list of CellFormats - one per element in ranges - that all share the same format."""
    return [CellFormat(range=r, format=shared_format) for r in ranges]

def rgb_color(hex_color: str) -> dict[str, dict[str, float]]:
    return {"rgbColor": dict(gspread.utils.convert_hex_to_colors_dict(hex_color))}

def background_color_style(hex_color: str) -> dict[str, dict[str, dict[str, float]]]:
    return {"backgroundColorStyle": rgb_color(hex_color)}

def grid_ranges(a1_ranges: Iterable[str], sheet_id: int | None = None) -> list[dict[str, int]]:
    return [gspread.utils.a1_range_to_grid_range(a1_range, sheet_id) for a1_range in a1_ranges]

def col_index_to_letter(col_index: int) -> str:
    return gspread.utils.rowcol_to_a1(1, col_index + 1)[:-1]

def grid_range_to_a1_range(grid_range: dict[str, int]) -> str:
    start_row = str(grid_range["startRowIndex"] + 1) if "startRowIndex" in grid_range else ""
    end_row = str(grid_range["endRowIndex"]) if "endRowIndex" in grid_range else ""
    start_col = col_index_to_letter(grid_range["startColumnIndex"]) if "startColumnIndex" in grid_range else ""
    end_col = col_index_to_letter(grid_range["endColumnIndex"] - 1) if "endColumnIndex" in grid_range else ""

    if not (start_a1 := f"{start_col}{start_row}"):
        raise ValueError('Need values for at least one of: "startRowIndex", "startColumnIndex"')
    if not (end_a1 := f"{end_col}{end_row}"):
        raise ValueError('Need values for at least one of: "endRowIndex", "endColumnIndex"')

    if end_row and not start_row:
        raise ValueError('Value for "endRowIndex" not allowed if "startRowIndex" not present')
    if end_col and not start_col:
        raise ValueError('Value for "endColumnIndex" not allowed if "startColumnIndex" not present')

    return f"{start_a1}:{end_a1}"

def auto_resize_columns(sheet: gspread.Worksheet, padding_px: int = 8) -> Any:
    column_count = sheet.column_count
    sheet.columns_auto_resize(0, column_count)

    metadata = sheet.spreadsheet.fetch_sheet_metadata(
        {"includeGridData": True, "ranges": sheet.title, "fields": "sheets(data(columnMetadata(pixelSize)))"})
    column_sizes_px = tuple(m["pixelSize"] for m in metadata["sheets"][0]["data"][0]["columnMetadata"])
    if len(column_sizes_px) != column_count:
        raise RuntimeError(
            f"Found sizes for {len(column_sizes_px)} columns, but sheet {sheet.title!r} has {column_count} columns")

    batch_update_requests = []
    for column_index, column_size_px in enumerate(column_sizes_px):
        batch_update_requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet.id,
                    "dimension": "COLUMNS",
                    "startIndex": column_index,
                    "endIndex": column_index + 1
                },
                "properties": {"pixelSize": column_size_px + padding_px},
                "fields": "pixelSize"
            }
        })

    return sheet.spreadsheet.batch_update({"requests": batch_update_requests})