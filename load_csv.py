import csv
import sqlite3

DB_PATH = "cellar.db"
CSV_PATH = "cellar.csv"


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
    print(f"Successfully loaded {rows_inserted} wines into the database.")


if __name__ == "__main__":
    load_csv_to_database()
