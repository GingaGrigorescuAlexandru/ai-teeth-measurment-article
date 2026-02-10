import argparse
import base64
import datetime
from decimal import Decimal
from io import BytesIO
import os
from pathlib import Path
import re
import zipfile

from psycopg2 import sql
from xml.sax.saxutils import escape

from modules.insert_opg_record import get_connection


# ------------------------------
# Fetch all rows from a table
# ------------------------------
def fetch_table_data(table_name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return columns, rows


# ------------------------------
# Helpers for XLSX generation
# ------------------------------
def build_content_types_xml(sheet_count: int) -> str:
    overrides = "\n".join(
        f'    <Override PartName="/xl/worksheets/sheet{i}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '    <Default Extension="xml" ContentType="application/xml"/>\n'
        '    <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>\n'
        f"{overrides}\n"
        '    <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>\n'
        "</Types>\n"
    )

ROOT_RELS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""

def build_workbook_xml(sheet_names) -> str:
    sheets_xml = "\n".join(
        f'        <sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        "    <sheets>\n"
        f"{sheets_xml}\n"
        "    </sheets>\n"
        "</workbook>\n"
    )

def build_workbook_rels_xml(sheet_count: int) -> str:
    sheet_rels = "\n".join(
        f'    <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{i}.xml"/>'
        for i in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f"{sheet_rels}\n"
        f'    <Relationship Id="rId{sheet_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\n'
        "</Relationships>\n"
    )

STYLES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
    <fonts count="1"><font/></fonts>
    <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
    <borders count="1"><border/></borders>
    <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
    <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
</styleSheet>
"""


def column_letter(idx: int) -> str:
    """Convert 0-based column index to Excel column letter (A, B, ..., AA, AB)."""
    idx += 1
    letters = ""
    while idx:
        idx, remainder = divmod(idx - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def classify_value(value):
    """Return a tuple of (type, string_value) for the XLSX cell."""
    if value is None:
        return "empty", ""
    if isinstance(value, memoryview):
        value = bytes(value)
    if isinstance(value, (bytes, bytearray)):
        encoded = base64.b64encode(value).decode("ascii")
        return "string", encoded
    if isinstance(value, bool):
        return "string", "TRUE" if value else "FALSE"
    if isinstance(value, (int, float, Decimal)):
        return "number", str(value)
    if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
        return "string", value.isoformat()
    return "string", str(value)


def build_cell(ref: str, value) -> str:
    kind, text = classify_value(value)
    if kind == "empty":
        return f'<c r="{ref}"/>'
    if kind == "number":
        return f'<c r="{ref}"><v>{text}</v></c>'
    return (
        f'<c r="{ref}" t="inlineStr">'
        f"<is><t>{escape(text)}</t></is>"
        f"</c>"
    )


def build_sheet_xml(columns, rows) -> str:
    header_cells = [
        build_cell(f"{column_letter(idx)}1", col) for idx, col in enumerate(columns)
    ]
    header_row = f'<row r="1">{"".join(header_cells)}</row>'

    body_rows = []
    for row_idx, row in enumerate(rows, start=2):
        cells = [
            build_cell(f"{column_letter(col_idx)}{row_idx}", value)
            for col_idx, value in enumerate(row)
        ]
        body_rows.append(f'<row r="{row_idx}">{"".join(cells)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{header_row}{''.join(body_rows)}</sheetData>"
        "</worksheet>"
    )


def write_xlsx(path: Path, sheets):
    sheet_xmls = [build_sheet_xml(s["columns"], s["rows"]) for s in sheets]
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", build_content_types_xml(len(sheet_xmls)))
        zf.writestr("_rels/.rels", ROOT_RELS_XML)
        zf.writestr(
            "xl/workbook.xml",
            build_workbook_xml([s["name"] for s in sheets]),
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            build_workbook_rels_xml(len(sheet_xmls)),
        )
        zf.writestr("xl/styles.xml", STYLES_XML)
        for idx, xml in enumerate(sheet_xmls, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", xml)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(buffer.getvalue())


# ------------------------------
# Entry point
# ------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Export a PostgreSQL table to an Excel .xlsx file without extra dependencies."
    )
    parser.add_argument(
        "--table",
        default="opgs",
        help="Table name to export (default: opgs)",
    )
    parser.add_argument(
        "--output",
        default="exports/opgs_export.xlsx",
        help="Output .xlsx path (default: exports/opgs_export.xlsx)",
    )
    parser.add_argument(
        "--include-binary",
        action="store_true",
        help="Include bytea columns as base64 strings (default: skip them).",
    )
    args = parser.parse_args()

    columns, rows = fetch_table_data(args.table)

    desired_columns = [
        "id",
        "title",
        "sex",
        "age",
        "canine_13_length",
        "canine_23_length",
        "canine_33_length",
        "canine_43_length",
        "distance_13_23",
        "distance_33_43",
    ]

    missing = [c for c in desired_columns if c not in columns]
    if missing:
        print(f"Warning: missing columns in '{args.table}': {', '.join(missing)}")

    selected_columns = [c for c in desired_columns if c in columns]
    col_index = {name: columns.index(name) for name in selected_columns}

    def normalize_sex(value):
        if value is None:
            return None
        text = str(value).strip().upper()
        return text if text in {"B", "F"} else None

    def infer_sex_from_title(title):
        if not title:
            return None
        # Match -B-/-F- as well as -B/_B before extension (keeps parity with parse_filename).
        match = re.search(r"(?:^|[-_])(B|F)(?:[-_.]|$)", str(title), re.IGNORECASE)
        return match.group(1).upper() if match else None

    def title_sort_key(title):
        if not title:
            return float("inf")
        name = os.path.basename(str(title))
        match = re.match(r"^(\d+)", name)
        return int(match.group(1)) if match else float("inf")

    def build_row_map(row):
        return {col: row[idx] for col, idx in col_index.items()}

    males = []
    females = []
    for row in rows:
        row_map = build_row_map(row)
        title = row_map.get("title")
        inferred = infer_sex_from_title(title)
        final_sex = normalize_sex(row_map.get("sex")) or inferred
        if final_sex not in {"B", "F"}:
            continue
        row_map["sex"] = final_sex
        if final_sex == "B":
            males.append(row_map)
        else:
            females.append(row_map)

    males.sort(key=lambda r: title_sort_key(r.get("title")))
    females.sort(key=lambda r: title_sort_key(r.get("title")))

    def to_rows(items):
        return [[item.get(c) for c in selected_columns] for item in items]

    output_path = Path(args.output)
    write_xlsx(
        output_path,
        [
            {"name": "Males", "columns": selected_columns, "rows": to_rows(males)},
            {"name": "Females", "columns": selected_columns, "rows": to_rows(females)},
        ],
    )
    print(
        "Exported "
        f"{len(males)} male rows and {len(females)} female rows "
        f"with {len(selected_columns)} columns from '{args.table}' to {output_path.resolve()}"
    )


if __name__ == "__main__":
    main()
