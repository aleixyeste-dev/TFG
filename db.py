import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "estado.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_estado():
    if not os.path.exists(DB_PATH):
        return None

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS estado (id INTEGER PRIMARY KEY, data TEXT)"
    )

    cur.execute("SELECT data FROM estado WHERE id = 1")
    row = cur.fetchone()

    conn.close()

    if row is None:
        return None

    return json.loads(row[0])


def save_estado(estado):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS estado (id INTEGER PRIMARY KEY, data TEXT)"
    )

    cur.execute(
        "REPLACE INTO estado (id, data) VALUES (1, ?)",
        (json.dumps(estado),)
    )

    conn.commit()
    conn.close()
