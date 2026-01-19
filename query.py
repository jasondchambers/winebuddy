#!/usr/bin/env python3
"""Wine cellar query CLI tool."""

import csv
import io
import json
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

import typer

DB_PATH = "cellar.db"


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
        data.append([
            str(row["vintage"]) if row["vintage"] else "NV",
            (row["wine_name"] or "-")[:40],
            (row["producer"] or "-")[:20],
            (row["varietal"] or "-")[:15],
            (row["region"] or "-")[:15],
            str(row["quantity"]),
            score_str,
        ])

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
        data.append({
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
        })
    return json.dumps(data, indent=2)


def format_csv(rows: list[sqlite3.Row]) -> str:
    """Format results as CSV."""
    if not rows:
        return ""

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    columns = ["id", "wine_name", "vintage", "producer", "varietal", "color",
               "country", "region", "subregion", "quantity", "value",
               "professional_score", "begin_consume", "end_consume"]
    writer.writerow(columns)

    # Data
    for row in rows:
        writer.writerow([row[col] for col in columns])

    return output.getvalue()


@app.command()
def query(
    color: Annotated[
        Optional[str],
        typer.Option("--color", "-c", help="Filter by wine color (e.g., Red, White)")
    ] = None,
    producer: Annotated[
        Optional[str],
        typer.Option("--producer", "-p", help="Filter by producer (contains match)")
    ] = None,
    varietal: Annotated[
        Optional[str],
        typer.Option("--varietal", "-v", help="Filter by varietal (contains match)")
    ] = None,
    country: Annotated[
        Optional[str],
        typer.Option("--country", help="Filter by country")
    ] = None,
    region: Annotated[
        Optional[str],
        typer.Option("--region", "-r", help="Filter by region (contains match)")
    ] = None,
    vintage: Annotated[
        Optional[int],
        typer.Option("--vintage", help="Filter by exact vintage year")
    ] = None,
    vintage_min: Annotated[
        Optional[int],
        typer.Option("--vintage-min", help="Minimum vintage year")
    ] = None,
    vintage_max: Annotated[
        Optional[int],
        typer.Option("--vintage-max", help="Maximum vintage year")
    ] = None,
    score_min: Annotated[
        Optional[float],
        typer.Option("--score-min", help="Minimum professional score")
    ] = None,
    in_stock: Annotated[
        bool,
        typer.Option("--in-stock", help="Only show wines with quantity > 0")
    ] = False,
    ready: Annotated[
        bool,
        typer.Option("--ready", help="Only show wines within their drinking window")
    ] = False,
    sort: Annotated[
        SortField,
        typer.Option("--sort", "-s", help="Sort by field")
    ] = SortField.vintage,
    desc: Annotated[
        bool,
        typer.Option("--desc", "-d", help="Sort descending")
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", "-l", help="Limit number of results")
    ] = None,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.table,
):
    """Query wines from the cellar database with various filters."""
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
