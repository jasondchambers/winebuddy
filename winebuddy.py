#!/usr/bin/env python3
"""Wine cellar query CLI tool."""

import csv
import io
import json
import os
import sqlite3
import sys
from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

import typer

# Default cellar name and derived paths (can be overridden via --cellar-name)
CELLAR_NAME = "cellar"
DB_PATH = f"{CELLAR_NAME}.db"
CSV_PATH = f"{CELLAR_NAME}.csv"


def set_cellar_paths(cellar_name: str) -> None:
    """Set the global DB and CSV paths based on cellar name."""
    global CELLAR_NAME, DB_PATH, CSV_PATH
    CELLAR_NAME = cellar_name
    DB_PATH = f"{cellar_name}.db"
    CSV_PATH = f"{cellar_name}.csv"


def print_setup_instructions():
    """Print instructions for exporting data from CellarTracker."""
    instructions = f"""
WineBuddy Setup
===============

{CSV_PATH} file found.

To get started, you need to export your wine data from CellarTracker:

1. Go to CellarTracker: https://mobileapp.cellartracker.com
2. Log in to your account
3. Navigate to your cellar and click "Export"
4. Configure the export:
   - Include wines from ALL pages
   - Export Format: Comma Separated Values
   - Select these columns:
     Color, Category, Size, Currency, Value, Price, TotalQuantity,
     Quantity, Pending, Vintage, Wine, Locale, Producer, Varietal,
     Country, Region, SubRegion, BeginConsume, EndConsume, PScore, CScore
5. Download and save the file as {CSV_PATH} in the current directory
6. Run winebuddy again
"""
    print(instructions)


def init_database():
    """Initialize the SQLite database with the wines table schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT NOT NULL,
            category TEXT NOT NULL,
            size TEXT NOT NULL,
            currency TEXT NOT NULL,
            value REAL,
            price REAL,
            total_quantity INTEGER NOT NULL DEFAULT 0,
            quantity INTEGER NOT NULL DEFAULT 0,
            pending INTEGER NOT NULL DEFAULT 0,
            vintage INTEGER,
            wine_name TEXT NOT NULL,
            locale TEXT,
            producer TEXT,
            varietal TEXT,
            country TEXT,
            region TEXT,
            subregion TEXT,
            begin_consume INTEGER,
            end_consume INTEGER,
            professional_score REAL,
            community_score REAL
        )
    """)

    conn.commit()
    conn.close()


def parse_float(value):
    """Parse a float value, returning None for empty strings."""
    if value == "" or value is None:
        return None
    return float(value)


def parse_int(value):
    """Parse an integer value, returning None for empty strings."""
    if value == "" or value is None:
        return None
    return int(value)


def parse_vintage(value):
    """Parse vintage, returning None for non-vintage wines (1001)."""
    if value == "" or value is None:
        return None
    vintage = int(value)
    if vintage == 1001:
        return None
    return vintage


def load_csv_to_database():
    """Load wine data from CSV file into the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(CSV_PATH, "r", encoding="latin-1") as f:
        reader = csv.DictReader(f)

        insert_sql = """
            INSERT INTO wines (
                color, category, size, currency, value, price,
                total_quantity, quantity, pending, vintage, wine_name,
                locale, producer, varietal, country, region, subregion,
                begin_consume, end_consume, professional_score, community_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        rows_inserted = 0
        for row in reader:
            values = (
                row["Color"],
                row["Category"],
                row["Size"],
                row["Currency"],
                parse_float(row["Value"]),
                parse_float(row["Price"]),
                parse_int(row["TotalQuantity"]),
                parse_int(row["Quantity"]),
                parse_int(row["Pending"]),
                parse_vintage(row["Vintage"]),
                row["Wine"],
                row["Locale"],
                row["Producer"],
                row["Varietal"],
                row["Country"],
                row["Region"],
                row["SubRegion"],
                parse_int(row["BeginConsume"]),
                parse_int(row["EndConsume"]),
                parse_float(row["PScore"]),
                parse_float(row["CScore"]),
            )
            cursor.execute(insert_sql, values)
            rows_inserted += 1

    conn.commit()
    conn.close()
    return rows_inserted


def ensure_database():
    """Ensure the database exists, creating it from CSV if needed.

    Returns True if database is ready, False if setup instructions were shown.
    """
    if os.path.exists(DB_PATH):
        return True

    if os.path.exists(CSV_PATH):
        print("Database not found. Initializing from cellar.csv...", file=sys.stderr)
        init_database()
        rows = load_csv_to_database()
        print(f"Successfully loaded {rows} wines into the database.\n", file=sys.stderr)
        return True

    print_setup_instructions()
    return False


class SortField(str, Enum):
    vintage = "vintage"
    producer = "producer"
    score = "score"
    value = "value"
    name = "name"


class OutputFormat(str, Enum):
    table = "table"
    json = "json"
    csv = "csv"


# Whitelist mapping for sort columns (security)
SORT_COLUMNS = {
    "vintage": "vintage",
    "producer": "producer",
    "score": "professional_score",
    "value": "value",
    "name": "wine_name",
}

app = typer.Typer(help="Query and filter wines from the cellar database.")
discover_app = typer.Typer(help="Discover distinct values in the cellar database.")
app.add_typer(discover_app, name="discover")


@app.callback()
def main(
    cellar_name: Annotated[
        Optional[str],
        typer.Option(
            "--cellar-name",
            help="Over-ride default name for cellar files (useful for testing)",
        ),
    ] = None,
):
    """
    WineBuddy - Query and filter wines from your cellar database.
    """
    if cellar_name is not None:
        set_cellar_paths(cellar_name)


def get_distinct_values(column: str) -> list[str]:
    """Query distinct values for a given column from the wines table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Column name is hardcoded by callers, not user input
    cursor.execute(
        f"SELECT DISTINCT {column} FROM wines WHERE {column} IS NOT NULL ORDER BY {
            column
        }"
    )
    values = [row[0] for row in cursor.fetchall()]
    conn.close()
    return values


def print_values(title: str, values: list) -> None:
    """Print a list of values with a title."""
    print(f"\n{title} ({len(values)}):")
    print("-" * 40)
    for value in values:
        print(f"  {value}")


@discover_app.command("colors")
def discover_colors():
    """List distinct wine colors in the cellar."""
    if not ensure_database():
        raise typer.Exit()
    values = get_distinct_values("color")
    print_values("Colors", values)


@discover_app.command("producers")
def discover_producers():
    """List distinct producers in the cellar."""
    if not ensure_database():
        raise typer.Exit()
    values = get_distinct_values("producer")
    print_values("Producers", values)


@discover_app.command("varietals")
def discover_varietals():
    """List distinct varietals in the cellar."""
    if not ensure_database():
        raise typer.Exit()
    values = get_distinct_values("varietal")
    print_values("Varietals", values)


@discover_app.command("countries")
def discover_countries():
    """List distinct countries in the cellar."""
    if not ensure_database():
        raise typer.Exit()
    values = get_distinct_values("country")
    print_values("Countries", values)


@discover_app.command("regions")
def discover_regions():
    """List distinct regions in the cellar."""
    if not ensure_database():
        raise typer.Exit()
    values = get_distinct_values("region")
    print_values("Regions", values)


@discover_app.command("vintages")
def discover_vintages():
    """List distinct vintages in the cellar."""
    if not ensure_database():
        raise typer.Exit()
    values = get_distinct_values("vintage")
    print_values("Vintages", values)


def build_query(
    color: Optional[str],
    producer: Optional[str],
    varietal: Optional[str],
    country: Optional[str],
    region: Optional[str],
    vintage: Optional[int],
    vintage_min: Optional[int],
    vintage_max: Optional[int],
    score_min: Optional[float],
    in_stock: bool,
    ready: bool,
    sort: SortField,
    desc: bool,
    limit: Optional[int],
) -> tuple[str, list]:
    """Build parameterized SQL query from filters.

    Returns (sql_string, parameters_list) for secure execution.
    """
    conditions = []
    params = []

    if color:
        conditions.append("color = ?")
        params.append(color)

    if producer:
        conditions.append("producer LIKE ?")
        params.append(f"%{producer}%")

    if varietal:
        conditions.append("varietal LIKE ?")
        params.append(f"%{varietal}%")

    if country:
        conditions.append("country = ?")
        params.append(country)

    if region:
        conditions.append("region LIKE ?")
        params.append(f"%{region}%")

    if vintage is not None:
        conditions.append("vintage = ?")
        params.append(vintage)

    if vintage_min is not None:
        conditions.append("vintage >= ?")
        params.append(vintage_min)

    if vintage_max is not None:
        conditions.append("vintage <= ?")
        params.append(vintage_max)

    if score_min is not None:
        conditions.append("professional_score >= ?")
        params.append(score_min)

    if in_stock:
        conditions.append("quantity > 0")

    if ready:
        current_year = datetime.now().year
        conditions.append("begin_consume <= ?")
        conditions.append("end_consume >= ?")
        conditions.append("begin_consume != 9999")
        conditions.append("end_consume != 9999")
        params.append(current_year)
        params.append(current_year)

    sql = """
        SELECT
            id,
            wine_name,
            vintage,
            producer,
            varietal,
            color,
            country,
            region,
            subregion,
            quantity,
            value,
            professional_score,
            begin_consume,
            end_consume
        FROM wines
    """

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    # Use whitelisted column name for sorting (prevents SQL injection)
    sort_column = SORT_COLUMNS[sort.value]
    sort_direction = "DESC" if desc else "ASC"
    sql += f" ORDER BY {sort_column} {sort_direction}"

    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    return sql, params


def format_table(rows: list[sqlite3.Row]) -> str:
    """Format results as an ASCII table."""
    if not rows:
        return "No wines found."

    # Column headers and widths
    headers = ["Vintage", "Wine Name", "Producer", "Varietal", "Region", "Qty", "Score"]

    # Build rows data
    data = []
    for row in rows:
        score = row["professional_score"]
        score_str = f"{score:.1f}" if score else "-"
        data.append(
            [
                str(row["vintage"]) if row["vintage"] else "NV",
                (row["wine_name"] or "-")[:40],
                (row["producer"] or "-")[:20],
                (row["varietal"] or "-")[:15],
                (row["region"] or "-")[:15],
                str(row["quantity"]),
                score_str,
            ]
        )

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row_data in data:
        for i, cell in enumerate(row_data):
            widths[i] = max(widths[i], len(cell))

    # Build table
    lines = []

    # Header
    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in widths)
    lines.append(header_line)
    lines.append(separator)

    # Data rows
    for row_data in data:
        line = " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row_data))
        lines.append(line)

    lines.append(f"\n{len(rows)} wine(s) found.")
    return "\n".join(lines)


def format_json(rows: list[sqlite3.Row]) -> str:
    """Format results as JSON."""
    data = []
    for row in rows:
        data.append(
            {
                "id": row["id"],
                "wine_name": row["wine_name"],
                "vintage": row["vintage"],
                "producer": row["producer"],
                "varietal": row["varietal"],
                "color": row["color"],
                "country": row["country"],
                "region": row["region"],
                "subregion": row["subregion"],
                "quantity": row["quantity"],
                "value": row["value"],
                "professional_score": row["professional_score"],
                "begin_consume": row["begin_consume"],
                "end_consume": row["end_consume"],
            }
        )
    return json.dumps(data, indent=2)


def format_csv(rows: list[sqlite3.Row]) -> str:
    """Format results as CSV."""
    if not rows:
        return ""

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    columns = [
        "id",
        "wine_name",
        "vintage",
        "producer",
        "varietal",
        "color",
        "country",
        "region",
        "subregion",
        "quantity",
        "value",
        "professional_score",
        "begin_consume",
        "end_consume",
    ]
    writer.writerow(columns)

    # Data
    for row in rows:
        writer.writerow([row[col] for col in columns])

    return output.getvalue()


@app.command()
def query(
    color: Annotated[
        Optional[str],
        typer.Option("--color", "-c", help="Filter by wine color (e.g., Red, White)"),
    ] = None,
    producer: Annotated[
        Optional[str],
        typer.Option("--producer", "-p", help="Filter by producer (contains match)"),
    ] = None,
    varietal: Annotated[
        Optional[str],
        typer.Option("--varietal", "-v", help="Filter by varietal (contains match)"),
    ] = None,
    country: Annotated[
        Optional[str], typer.Option("--country", help="Filter by country")
    ] = None,
    region: Annotated[
        Optional[str],
        typer.Option("--region", "-r", help="Filter by region (contains match)"),
    ] = None,
    vintage: Annotated[
        Optional[int], typer.Option("--vintage", help="Filter by exact vintage year")
    ] = None,
    vintage_min: Annotated[
        Optional[int], typer.Option("--vintage-min", help="Minimum vintage year")
    ] = None,
    vintage_max: Annotated[
        Optional[int], typer.Option("--vintage-max", help="Maximum vintage year")
    ] = None,
    score_min: Annotated[
        Optional[float], typer.Option("--score-min", help="Minimum professional score")
    ] = None,
    in_stock: Annotated[
        bool, typer.Option("--in-stock", help="Only show wines with quantity > 0")
    ] = False,
    ready: Annotated[
        bool,
        typer.Option("--ready", help="Only show wines within their drinking window"),
    ] = False,
    sort: Annotated[
        SortField, typer.Option("--sort", "-s", help="Sort by field")
    ] = SortField.vintage,
    desc: Annotated[bool, typer.Option("--desc", "-d", help="Sort descending")] = False,
    limit: Annotated[
        Optional[int], typer.Option("--limit", "-l", help="Limit number of results")
    ] = None,
    output_format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.table,
):
    """Query wines from the cellar database with various filters."""
    if not ensure_database():
        raise typer.Exit()

    sql, params = build_query(
        color=color,
        producer=producer,
        varietal=varietal,
        country=country,
        region=region,
        vintage=vintage,
        vintage_min=vintage_min,
        vintage_max=vintage_max,
        score_min=score_min,
        in_stock=in_stock,
        ready=ready,
        sort=sort,
        desc=desc,
        limit=limit,
    )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    # Format output
    if output_format == OutputFormat.table:
        print(format_table(rows))
    elif output_format == OutputFormat.json:
        print(format_json(rows))
    elif output_format == OutputFormat.csv:
        print(format_csv(rows))


if __name__ == "__main__":
    app()
