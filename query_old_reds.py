import sqlite3

DB_PATH = "cellar.db"


def query_old_red_wines():
    """Query red wines with vintage older than 2016 (i.e., 2015 and earlier)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            wine_name,
            vintage,
            producer,
            varietal,
            region,
            quantity
        FROM wines
        WHERE color = 'Red'
          AND vintage < 2016
          AND vintage > 1000
        ORDER BY vintage ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    print(f"Found {len(rows)} red wines older than 2016:\n")
    for row in rows:
        print(f"  {row['vintage']} - {row['wine_name']}")
        print(f"    Producer: {row['producer']}")
        print(f"    Varietal: {row['varietal']}")
        print(f"    Region: {row['region']}")
        print(f"    Quantity: {row['quantity']}")
        print()

    return rows


if __name__ == "__main__":
    query_old_red_wines()
