import argparse
import sqlite3

DB_PATH = "cellar.db"


def get_distinct_values(column: str) -> list[str]:
    """Query distinct values for a given column from the wines table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT {column} FROM wines WHERE {column} IS NOT NULL ORDER BY {column}")
    values = [row[0] for row in cursor.fetchall()]
    conn.close()
    return values


def print_values(title: str, values: list) -> None:
    """Print a list of values with a title."""
    print(f"\n{title} ({len(values)}):")
    print("-" * 40)
    for value in values:
        print(f"  {value}")


def main():
    parser = argparse.ArgumentParser(
        description="WineBuddy - Wine cellar management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--colors", action="store_true", help="List distinct wine colors in the cellar")
    parser.add_argument("--producers", action="store_true", help="List distinct producers in the cellar")
    parser.add_argument("--varietals", action="store_true", help="List distinct varietals in the cellar")
    parser.add_argument("--countries", action="store_true", help="List distinct countries in the cellar")
    parser.add_argument("--regions", action="store_true", help="List distinct regions in the cellar")
    parser.add_argument("--vintages", action="store_true", help="List distinct vintages in the cellar")

    args = parser.parse_args()

    # Track if any option was selected
    any_option = any([args.colors, args.producers, args.varietals, args.countries, args.regions, args.vintages])

    if not any_option:
        parser.print_help()
        return

    if args.colors:
        values = get_distinct_values("color")
        print_values("Colors", values)

    if args.producers:
        values = get_distinct_values("producer")
        print_values("Producers", values)

    if args.varietals:
        values = get_distinct_values("varietal")
        print_values("Varietals", values)

    if args.countries:
        values = get_distinct_values("country")
        print_values("Countries", values)

    if args.regions:
        values = get_distinct_values("region")
        print_values("Regions", values)

    if args.vintages:
        values = get_distinct_values("vintage")
        print_values("Vintages", values)


if __name__ == "__main__":
    main()
