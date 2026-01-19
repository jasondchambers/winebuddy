import sqlite3

DB_PATH = "cellar.db"

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
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_database()
