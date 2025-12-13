import sqlite3
import json

DB_FILE = "partida.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS partida (
            id INTEGER PRIMARY KEY,
            estado TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_estado():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT estado FROM partida WHERE id=1")
    row = cur.fetchone()

    if row is None:
        conn.close()
        return None

    estado = json.loads(row[0])
    conn.close()
    return estado

def save_estado(estado):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO partida (id, estado) VALUES (1, ?)",
        (json.dumps(estado),)
    )
    conn.commit()
    conn.close()
