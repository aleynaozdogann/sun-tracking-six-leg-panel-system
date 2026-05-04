import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "predictions.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sun_x REAL,
            sun_y REAL,
            sun_z REAL,
            predicted_zenith REAL,
            analytic_zenith REAL,
            error REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_prediction(sun_x, sun_y, sun_z, predicted_zenith, analytic_zenith):
    error = abs(analytic_zenith - predicted_zenith)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions (
            sun_x,
            sun_y,
            sun_z,
            predicted_zenith,
            analytic_zenith,
            error
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        sun_x,
        sun_y,
        sun_z,
        predicted_zenith,
        analytic_zenith,
        error
    ))

    conn.commit()
    conn.close()

def get_predictions(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM predictions
    ORDER BY id DESC 
    LIMIT ?
    """,(limit,))

    rows = cursor.fetchall()
    conn.close()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "sun_x": row[1],
            "sun_y": row[2],
            "sun_z": row[3],
            "predicted_zenith": row[4],
            "analytic_zenith": row[5],
            "error": row[6]
        })
    return results



if __name__ == "__main__":
    init_db()
    print("database ready")