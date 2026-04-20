import sqlite3
from datetime import datetime
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent.parent / "scans.db"


def get_connection():
    conn = sqlite3.connect(str(DB_NAME))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(cursor, table_name, column_name, ddl_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_definition}")


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            endpoints TEXT,
            headers TEXT,
            https_status TEXT,
            risk TEXT,
            fecha TEXT,
            active INTEGER DEFAULT 1
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'usuario',
            active INTEGER DEFAULT 1,
            created_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            milestone TEXT,
            issue_type TEXT,
            assigned_to INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            status TEXT DEFAULT 'pendiente',
            due_at TEXT,
            completion_notes TEXT,
            completed_at TEXT,
            created_at TEXT,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (assigned_to) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )

    ensure_column(cursor, "users", "active", "INTEGER DEFAULT 1")
    ensure_column(cursor, "users", "created_at", "TEXT")
    ensure_column(cursor, "scans", "active", "INTEGER DEFAULT 1")

    # Backward-compatible role migration.
    cursor.execute("UPDATE users SET role = 'super_admin' WHERE role = 'admin'")
    cursor.execute("UPDATE users SET role = 'usuario' WHERE role = 'user'")

    conn.commit()
    conn.close()


def save_scan(url, endpoints, headers, https_status, risk):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO scans (url, endpoints, headers, https_status, risk, fecha, active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """,
        (
            url,
            str(endpoints),
            str(headers),
            https_status,
            risk,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    conn.commit()
    conn.close()


def get_all_scans():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE active = 1 ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password, role, active FROM users WHERE username = ? AND active = 1",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username, password_hash, role="usuario"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, role, active, created_at) VALUES (?, ?, ?, 1, ?)",
        (username, password_hash, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE active = 1 ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_user_role(username, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE username = ? AND active = 1", (role, username))
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated > 0


def deactivate_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET active = 0 WHERE username = ? AND active = 1", (username,))
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated > 0


def create_task(title, description, milestone, issue_type, assigned_to, created_by, due_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (title, description, milestone, issue_type, assigned_to, created_by, status, due_at, created_at, active)
        VALUES (?, ?, ?, ?, ?, ?, 'pendiente', ?, ?, 1)
        """,
        (
            title,
            description,
            milestone,
            issue_type,
            assigned_to,
            created_by,
            due_at,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def list_tasks_for_supervisor():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            t.id,
            t.title,
            t.description,
            t.milestone,
            t.issue_type,
            t.status,
            t.due_at,
            t.completion_notes,
            t.completed_at,
            t.created_at,
            u.username AS assigned_to,
            c.username AS created_by
        FROM tasks t
        JOIN users u ON u.id = t.assigned_to
        JOIN users c ON c.id = t.created_by
        WHERE t.active = 1
        ORDER BY t.id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_tasks_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            id,
            title,
            description,
            milestone,
            issue_type,
            status,
            due_at,
            completion_notes,
            completed_at,
            created_at
        FROM tasks
        WHERE active = 1 AND assigned_to = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def complete_task(task_id, user_id, completion_notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tasks
        SET status = 'finalizada', completion_notes = ?, completed_at = ?
        WHERE id = ? AND assigned_to = ? AND active = 1
        """,
        (completion_notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id, user_id),
    )
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated > 0


def deactivate_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET active = 0 WHERE id = ? AND active = 1", (task_id,))
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated > 0
