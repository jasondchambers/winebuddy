#!/usr/bin/env python3
"""Wine cellar query CLI tool."""

import csv
import io
import json
import os
import sqlite3
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

import typer


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class CellarConfig:
    """Configuration for cellar database and CSV paths."""

    db_path: str
    csv_path: str

    @classmethod
    def from_name(cls, name: str = "cellar") -> "CellarConfig":
        # If name contains a path separator, use it as-is (for testing)
        # Otherwise, use ~/.winebuddy/ as the base directory
        if os.sep in name or (os.altsep and os.altsep in name):
            return cls(db_path=f"{name}.db", csv_path=f"{name}.csv")
        base_dir = os.path.expanduser("~/.winebuddy")
        return cls(db_path=os.path.join(base_dir, f"{name}.db"), csv_path=os.path.join(base_dir, f"{name}.csv"))


# =============================================================================
# Enums
# =============================================================================


class SortField(str, Enum):
    vintage = "vintage"
    producer = "producer"
    score = "score"
    price = "price"
    wine_name = "wine_name"


class OutputFormat(str, Enum):
    table = "table"
    json = "json"
    csv = "csv"


# =============================================================================
# Shared Constants
# =============================================================================

# Columns returned by queries (used by QueryBuilder and OutputFormatter)
QUERY_COLUMNS = [
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
    "community_score",
    "begin_consume",
    "end_consume",
]

# Discover command configuration: maps command name to (column, title)
# Single source of truth for discover functionality
DISCOVER_COMMANDS = {
    "colors": ("color", "Colors"),
    "producers": ("producer", "Producers"),
    "varietals": ("varietal", "Varietals"),
    "countries": ("country", "Countries"),
    "regions": ("region", "Regions"),
    "vintages": ("vintage", "Vintages"),
}

# Whitelist of valid discover columns (derived from config)
DISCOVER_COLUMNS = frozenset(col for col, _ in DISCOVER_COMMANDS.values())


# =============================================================================
# Database Class
# =============================================================================


class CellarDatabase:
    """Handles database connection, initialization, and CSV import."""

    def __init__(self, config: CellarConfig):
        self.config = config

    @contextmanager
    def get_connection(self, row_factory: bool = False):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.config.db_path)
        if row_factory:
            conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def database_exists(self) -> bool:
        return os.path.exists(self.config.db_path)


    def csv_exists(self) -> bool:
        return os.path.exists(self.config.csv_path)

    def has_csv_changed(self) -> bool:
        """Check if the CSV file is newer than the database."""
        if not self.database_exists() or not self.csv_exists():
            return False
        csv_mtime = os.path.getmtime(self.config.csv_path)
        db_mtime = os.path.getmtime(self.config.db_path)
        return csv_mtime > db_mtime

    def rebuild(self) -> int:
        """Delete and recreate the database from CSV. Returns row count."""
        os.remove(self.config.db_path)
        self._init_schema()
        return self._load_csv()

    def create(self) -> int:
        """Create a new database from CSV. Returns row count."""
        db_dir = os.path.dirname(self.config.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_schema()
        return self._load_csv()

    def ensure_ready(self) -> bool:
        """Ensure the database exists, creating it from CSV if needed.

        Returns True if database is ready, False if CSV file is missing.
        """
        if self.database_exists():
            if self.has_csv_changed():
                print("database needs to be rebuilt", file=sys.stderr)
                rows = self.rebuild()
                print(f"Successfully loaded {rows} wines into the database.\n", file=sys.stderr)
            return True

        if self.csv_exists():
            print("Database not found. Initializing from CSV...", file=sys.stderr)
            rows = self.create()
            print(f"Successfully loaded {rows} wines into the database.\n", file=sys.stderr)
            return True

        return False

    def get_distinct_values(self, column: str) -> list[str]:
        """Query distinct values for a given column from the wines table."""
        if column not in DISCOVER_COLUMNS:
            raise ValueError(f"Invalid column: {column}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT DISTINCT {column} FROM wines WHERE {column} IS NOT NULL ORDER BY {column}"  # nosec B608 - column validated against whitelist
            )
            return [row[0] for row in cursor.fetchall()]

    def _init_schema(self):
        """Initialize the SQLite database with the wines table schema."""
        with self.get_connection() as conn:
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

    def _load_csv(self) -> int:
        """Load wine data from CSV file into the SQLite database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            with open(self.config.csv_path, "r", encoding="latin-1") as f:
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
                        self._parse_float(row["Value"]),
                        self._parse_float(row["Price"]),
                        self._parse_int(row["TotalQuantity"]),
                        self._parse_int(row["Quantity"]),
                        self._parse_int(row["Pending"]),
                        self._parse_vintage(row["Vintage"]),
                        row["Wine"],
                        row["Locale"],
                        row["Producer"],
                        row["Varietal"],
                        row["Country"],
                        row["Region"],
                        row["SubRegion"],
                        self._parse_int(row["BeginConsume"]),
                        self._parse_int(row["EndConsume"]),
                        self._parse_float(row["PScore"]),
                        self._parse_float(row["CScore"]),
                    )
                    cursor.execute(insert_sql, values)
                    rows_inserted += 1

            conn.commit()
        return rows_inserted

    @staticmethod
    def _parse_float(value):
        """Parse a float value, returning None for empty strings."""
        if value == "" or value is None:
            return None
        return float(value)

    @staticmethod
    def _parse_int(value):
        """Parse an integer value, returning None for empty strings."""
        if value == "" or value is None:
            return None
        return int(value)

    @staticmethod
    def _parse_vintage(value):
        """Parse vintage, returning None for non-vintage wines (1001)."""
        if value == "" or value is None:
            return None
        vintage = int(value)
        if vintage == 1001:
            return None
        return vintage


# =============================================================================
# QueryBuilder Class
# =============================================================================


class QueryBuilder:
    """Builds parameterized SQL queries from filter options."""

    # Whitelist mapping for sort columns (security)
    SORT_MAP = {
        "vintage": "vintage",
        "producer": "producer",
        "score": "COALESCE(professional_score, community_score)",
        "price": "value",
        "wine_name": "wine_name",
    }

    @classmethod
    def build(
        cls,
        color: Optional[str] = None,
        producer: Optional[str] = None,
        varietal: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        vintage: Optional[int] = None,
        vintage_min: Optional[int] = None,
        vintage_max: Optional[int] = None,
        score_min: Optional[float] = None,
        in_stock: bool = False,
        ready: bool = False,
        sort: SortField = SortField.vintage,
        desc: bool = False,
        limit: Optional[int] = None,
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
            conditions.append("COALESCE(professional_score, community_score) >= ?")
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

        columns_str = ", ".join(QUERY_COLUMNS)
        sql = f"""
            SELECT {columns_str}
            FROM wines
        """  # nosec B608

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        # Use whitelisted column name for sorting (prevents SQL injection)
        sort_column = cls.SORT_MAP[sort.value]
        sort_direction = "DESC" if desc else "ASC"
        sql += f" ORDER BY {sort_column} {sort_direction}"

        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        return sql, params


# =============================================================================
# OutputFormatter Class
# =============================================================================


class OutputFormatter:
    """Formats query results for display."""

    @staticmethod
    def table(rows: list[sqlite3.Row]) -> str:
        """Format results as an ASCII table."""
        if not rows:
            return "No wines found."

        # Column headers and widths
        headers = ["Vintage", "Wine Name", "Producer", "Varietal", "Region", "Qty", "Score"]

        # Build rows data
        data = []
        for row in rows:
            # Prefer professional score, fall back to community score
            score = row["professional_score"] or row["community_score"]
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

    @staticmethod
    def json(rows: list[sqlite3.Row]) -> str:
        """Format results as JSON."""
        data = [{col: row[col] for col in QUERY_COLUMNS} for row in rows]
        return json.dumps(data, indent=2)

    @staticmethod
    def csv(rows: list[sqlite3.Row]) -> str:
        """Format results as CSV."""
        if not rows:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(QUERY_COLUMNS)

        for row in rows:
            writer.writerow([row[col] for col in QUERY_COLUMNS])

        return output.getvalue()

    @staticmethod
    def values_list(title: str, values: list) -> str:
        """Format a list of values with a title."""
        lines = [f"\n{title} ({len(values)}):", "-" * 40]
        for value in values:
            lines.append(f"  {value}")
        return "\n".join(lines)


# =============================================================================
# CLI Layer
# =============================================================================

# Global database instance, set by CLI callback
db: CellarDatabase = CellarDatabase(CellarConfig.from_name())

app = typer.Typer(help="Query and filter wines from the cellar database.")
discover_app = typer.Typer(help="Discover distinct values in the cellar database.")
app.add_typer(discover_app, name="discover")


def _print_setup_instructions(config: CellarConfig) -> None:
    """Print instructions for exporting data from CellarTracker."""
    csv_dir = os.path.dirname(config.csv_path)
    instructions = f"""
WineBuddy Setup
===============

{config.csv_path} file not found.

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
5. Create the directory if needed: mkdir -p {csv_dir}
6. Download and save the file as {config.csv_path}
7. Run winebuddy again
"""
    print(instructions)


def _require_database() -> bool:
    """Ensure database is ready, printing setup instructions if not.

    Returns True if ready, False (after printing instructions) if not.
    """
    if db.ensure_ready():
        return True
    _print_setup_instructions(db.config)
    return False


def _parse_csv_snapshot(csv_path: str) -> dict[tuple, int]:
    """Parse CSV file into a dict keyed by (wine_name, vintage, producer) with quantity values."""
    snapshot = {}
    with open(csv_path, "r", encoding="latin-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vintage = CellarDatabase._parse_vintage(row["Vintage"])
            key = (row["Wine"], vintage, row["Producer"])
            qty = CellarDatabase._parse_int(row["Quantity"]) or 0
            # Aggregate quantities for duplicate keys
            snapshot[key] = snapshot.get(key, 0) + qty
    return snapshot


def _db_snapshot() -> dict[tuple, int]:
    """Read current database into a dict keyed by (wine_name, vintage, producer) with quantity values."""
    snapshot = {}
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT wine_name, vintage, producer, quantity FROM wines")
        for wine_name, vintage, producer, quantity in cursor.fetchall():
            key = (wine_name, vintage, producer)
            snapshot[key] = snapshot.get(key, 0) + (quantity or 0)
    return snapshot


def _format_wine_label(key: tuple) -> str:
    """Format a (wine_name, vintage, producer) tuple as a readable label."""
    wine_name, vintage, producer = key
    vintage_str = str(vintage) if vintage else "NV"
    return f"{vintage_str} {producer} {wine_name}"


def _build_activity_report(old: dict[tuple, int], new: dict[tuple, int]) -> str:
    """Compare old and new cellar snapshots and return a formatted activity report."""
    new_wines = []
    removed_wines = []
    qty_changes = []

    for key in sorted(new.keys() - old.keys(), key=_format_wine_label):
        new_wines.append(f"    {_format_wine_label(key)} (qty: {new[key]})")

    for key in sorted(old.keys() - new.keys(), key=_format_wine_label):
        removed_wines.append(f"    {_format_wine_label(key)} (was qty: {old[key]})")

    for key in sorted(old.keys() & new.keys(), key=_format_wine_label):
        if old[key] != new[key]:
            qty_changes.append(f"    {_format_wine_label(key)}: {old[key]} -> {new[key]}")

    if not new_wines and not removed_wines and not qty_changes:
        return "Activity since last refresh:\n  No changes detected."

    sections = []
    if new_wines:
        sections.append(f"  New wines ({len(new_wines)}):\n" + "\n".join(new_wines))
    if removed_wines:
        sections.append(f"  Removed wines ({len(removed_wines)}):\n" + "\n".join(removed_wines))
    if qty_changes:
        sections.append(f"  Quantity changes ({len(qty_changes)}):\n" + "\n".join(qty_changes))

    return "Activity since last refresh:\n" + "\n".join(sections)


def _refresh_database() -> int:
    """Rebuild database from CSV if changed or missing, otherwise do nothing.

    Returns exit code: 255 = failure/csv missing, 0 = up to date, 1 = created, 2 = rebuilt.
    """
    if not db.csv_exists():
        _print_setup_instructions(db.config)
        return 255
    if db.database_exists() and db.has_csv_changed():
        old_snapshot = _db_snapshot()
        new_snapshot = _parse_csv_snapshot(db.config.csv_path)
        report = _build_activity_report(old_snapshot, new_snapshot)
        rows = db.rebuild()
        print(f"Database rebuilt with {rows} wines.")
        print(f"\n{report}")
        return 2
    if not db.database_exists():
        rows = db.create()
        print(f"Database created with {rows} wines.")
        return 1
    print("Database is up to date.")
    return 0


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    cellar_name: Annotated[
        Optional[str],
        typer.Option(
            "--cellar-name",
            help="Over-ride default name for cellar files (useful for testing)",
        ),
    ] = None,
    refresh: Annotated[
        bool,
        typer.Option(
            "--refresh",
            help="Rebuild database from CSV if changed or missing, then exit",
        ),
    ] = False,
):
    """
    WineBuddy - Query and filter wines from your cellar database.
    """
    global db
    if cellar_name is not None:
        db = CellarDatabase(CellarConfig.from_name(cellar_name))

    if refresh:
        raise typer.Exit(code=_refresh_database())


def _make_discover_command(column: str, title: str):
    """Factory to create discover subcommands."""

    def command():
        if not _require_database():
            raise typer.Exit()
        print(OutputFormatter.values_list(title, db.get_distinct_values(column)))

    command.__doc__ = f"List distinct {title.lower()} in the cellar."
    return command


# Register all discover commands
for _name, (_column, _title) in DISCOVER_COMMANDS.items():
    discover_app.command(_name)(_make_discover_command(_column, _title))


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
        Optional[float], typer.Option("--score-min", help="Minimum score (professional or community)")
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
    if not _require_database():
        raise typer.Exit()

    sql, params = QueryBuilder.build(
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

    with db.get_connection(row_factory=True) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    # Format output
    if output_format == OutputFormat.table:
        print(OutputFormatter.table(rows))
    elif output_format == OutputFormat.json:
        print(OutputFormatter.json(rows))
    elif output_format == OutputFormat.csv:
        print(OutputFormatter.csv(rows))


if __name__ == "__main__":
    app()
