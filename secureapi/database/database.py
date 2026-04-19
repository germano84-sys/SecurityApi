import sqlite3
from datetime import datetime

DB_NAME = "scans.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        endpoints TEXT,
        headers TEXT,
        https_status TEXT,
        risk TEXT,
        fecha TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_scan(url, endpoints, headers, https_status, risk):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO scans (url, endpoints, headers, https_status, risk, fecha)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        url,
        str(endpoints),
        str(headers),
        https_status,
        risk,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()