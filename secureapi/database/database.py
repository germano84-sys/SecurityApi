import sqlite3
from datetime import datetime
import json
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent.parent / "scans.db"

TASK_STATUS_VALUES = {"no_iniciada", "en_proceso", "cumplida"}
DEFAULT_ROLES = (
    ("admin", "Administrador del sistema"),
    ("supervisor", "Supervisor de tareas y usuarios comunes"),
    ("usuario_comun", "Usuario comun operativo"),
)


def get_connection():
    conn = sqlite3.connect(str(DB_NAME))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(cursor, table_name, column_name, ddl_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_definition}")


def _to_json_blob(value):
    if value is None:
        return json.dumps(None)
    return json.dumps(value, ensure_ascii=False)


def _normalize_status(status: str):
    normalized = (status or "").strip().lower()
    mapping = {
        "pendiente": "no_iniciada",
        "no iniciada": "no_iniciada",
        "en progreso": "en_proceso",
        "en-progreso": "en_proceso",
        "finalizada": "cumplida",
        "completada": "cumplida",
    }
    normalized = mapping.get(normalized, normalized)
    if normalized not in TASK_STATUS_VALUES:
        raise ValueError("Estado de tarea invalido")
    return normalized


def _seed_default_roles(cursor):
    for role_name, description in DEFAULT_ROLES:
        cursor.execute(
            """
            INSERT OR IGNORE INTO rol_usuario (name, description, active)
            VALUES (?, ?, 1)
            """,
            (role_name, description),
        )


def _get_role_id(cursor, role_name: str):
    cursor.execute("SELECT id FROM rol_usuario WHERE name = ? AND active = 1", (role_name,))
    row = cursor.fetchone()
    return row["id"] if row else None


def _migrate_user_roles(cursor):
    mapping = {
        "super_admin": "admin",
        "admin": "admin",
        "supervisor": "supervisor",
        "usuario": "usuario_comun",
        "user": "usuario_comun",
        "usuario_comun": "usuario_comun",
    }

    cursor.execute("SELECT id, role, role_id FROM users")
    for row in cursor.fetchall():
        if row["role_id"]:
            continue

        legacy_role = (row["role"] or "usuario_comun").strip().lower()
        normalized_role = mapping.get(legacy_role, "usuario_comun")
        role_id = _get_role_id(cursor, normalized_role)
        if not role_id:
            continue

        cursor.execute(
            "UPDATE users SET role_id = ?, role = ? WHERE id = ?",
            (role_id, normalized_role, row["id"]),
        )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rol_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            active INTEGER DEFAULT 1
        )
        """
    )

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
            performed_by INTEGER,
            performed_by_username TEXT,
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
            role_id INTEGER,
            active INTEGER DEFAULT 1,
            created_at TEXT,
            created_by INTEGER,
            FOREIGN KEY (role_id) REFERENCES rol_usuario(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS milestone_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            milestone TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            description TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT,
            UNIQUE (milestone, issue_type)
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
            milestone_issue_id INTEGER,
            assigned_to INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            status TEXT DEFAULT 'pendiente',
            due_at TEXT,
            progress_notes TEXT,
            completion_notes TEXT,
            completed_at TEXT,
            created_at TEXT,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (assigned_to) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (milestone_issue_id) REFERENCES milestone_issues(id)
        )
        """
    )

    ensure_column(cursor, "users", "role_id", "INTEGER")
    ensure_column(cursor, "users", "created_by", "INTEGER")
    ensure_column(cursor, "users", "active", "INTEGER DEFAULT 1")
    ensure_column(cursor, "users", "created_at", "TEXT")
    ensure_column(cursor, "scans", "active", "INTEGER DEFAULT 1")
    ensure_column(cursor, "scans", "performed_by", "INTEGER")
    ensure_column(cursor, "scans", "performed_by_username", "TEXT")
    ensure_column(cursor, "tasks", "milestone_issue_id", "INTEGER")
    ensure_column(cursor, "tasks", "progress_notes", "TEXT")

    _seed_default_roles(cursor)
    _migrate_user_roles(cursor)

    cursor.execute("UPDATE tasks SET status = 'no_iniciada' WHERE status = 'pendiente'")
    cursor.execute("UPDATE tasks SET status = 'cumplida' WHERE status = 'finalizada'")
    cursor.execute("UPDATE tasks SET status = 'en_proceso' WHERE status IN ('en progreso', 'en_progreso')")

    conn.commit()
    conn.close()


def create_role(role_name, description=""):
    normalized = (role_name or "").strip().lower()
    if not normalized:
        raise ValueError("Nombre de rol invalido")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO rol_usuario (name, description, active)
        VALUES (?, ?, 1)
        """,
        (normalized, description),
    )
    conn.commit()
    role_id = cursor.lastrowid
    conn.close()
    return role_id


def list_roles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM rol_usuario WHERE active = 1 ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_scan(url, endpoints, headers, https_status, risk, performed_by=None, performed_by_username=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO scans (url, endpoints, headers, https_status, risk, fecha, performed_by, performed_by_username, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            url,
            _to_json_blob(endpoints),
            _to_json_blob(headers),
            https_status,
            risk,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            performed_by,
            performed_by_username,
        ),
    )

    conn.commit()
    conn.close()


def get_all_scans(performed_by=None):
    conn = get_connection()
    cursor = conn.cursor()

    if performed_by is None:
        cursor.execute("SELECT * FROM scans WHERE active = 1 ORDER BY id DESC")
    else:
        cursor.execute(
            "SELECT * FROM scans WHERE active = 1 AND performed_by = ? ORDER BY id DESC",
            (performed_by,),
        )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            u.id,
            u.username,
            u.password,
            COALESCE(r.name, u.role, 'usuario_comun') AS role,
            u.active
        FROM users u
        LEFT JOIN rol_usuario r ON r.id = u.role_id
        WHERE u.username = ? AND u.active = 1
        """,
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username, password_hash, role="usuario_comun", created_by=None):
    normalized_role = (role or "usuario_comun").strip().lower()

    conn = get_connection()
    cursor = conn.cursor()
    role_id = _get_role_id(cursor, normalized_role)
    if not role_id:
        conn.close()
        raise ValueError("Rol no encontrado en catalogo")

    cursor.execute(
        """
        INSERT INTO users (username, password, role, role_id, active, created_at, created_by)
        VALUES (?, ?, ?, ?, 1, ?, ?)
        """,
        (
            username,
            password_hash,
            normalized_role,
            role_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            created_by,
        ),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def upsert_admin_user(username, password_hash):
    conn = get_connection()
    cursor = conn.cursor()

    role_id = _get_role_id(cursor, "admin")
    if not role_id:
        conn.close()
        raise ValueError("Rol admin no encontrado en catalogo")

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            """
            UPDATE users
            SET password = ?, role = 'admin', role_id = ?, active = 1
            WHERE id = ?
            """,
            (password_hash, role_id, existing["id"]),
        )
        user_id = existing["id"]
    else:
        cursor.execute(
            """
            INSERT INTO users (username, password, role, role_id, active, created_at, created_by)
            VALUES (?, ?, 'admin', ?, 1, ?, NULL)
            """,
            (
                username,
                password_hash,
                role_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return user_id


def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            u.id,
            u.username,
            COALESCE(r.name, u.role, 'usuario_comun') AS role,
            u.created_at
        FROM users u
        LEFT JOIN rol_usuario r ON r.id = u.role_id
        WHERE u.active = 1
        ORDER BY u.id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_user_role(username, role):
    normalized_role = (role or "").strip().lower()

    conn = get_connection()
    cursor = conn.cursor()
    role_id = _get_role_id(cursor, normalized_role)
    if not role_id:
        conn.close()
        return False

    cursor.execute(
        "UPDATE users SET role = ?, role_id = ? WHERE username = ? AND active = 1",
        (normalized_role, role_id, username),
    )
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


def create_milestone_issue(milestone, issue_type, description=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO milestone_issues (milestone, issue_type, description, active, created_at)
        VALUES (?, ?, ?, 1, ?)
        """,
        (
            milestone.strip(),
            issue_type.strip(),
            description.strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    milestone_issue_id = cursor.lastrowid

    if not milestone_issue_id:
        cursor.execute(
            "SELECT id FROM milestone_issues WHERE milestone = ? AND issue_type = ?",
            (milestone.strip(), issue_type.strip()),
        )
        row = cursor.fetchone()
        milestone_issue_id = row["id"] if row else None

    conn.close()
    return milestone_issue_id


def list_milestone_issues():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, milestone, issue_type, description
        FROM milestone_issues
        WHERE active = 1
        ORDER BY milestone ASC, issue_type ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_task(
    title,
    description,
    milestone,
    issue_type,
    assigned_to,
    created_by,
    due_at,
    milestone_issue_id=None,
):
    resolved_milestone_issue_id = milestone_issue_id
    if resolved_milestone_issue_id is None and milestone and issue_type:
        resolved_milestone_issue_id = create_milestone_issue(milestone, issue_type)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (
            title,
            description,
            milestone,
            issue_type,
            milestone_issue_id,
            assigned_to,
            created_by,
            status,
            due_at,
            created_at,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'no_iniciada', ?, ?, 1)
        """,
        (
            title,
            description,
            milestone,
            issue_type,
            resolved_milestone_issue_id,
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


def list_tasks_for_supervisor(status=None, assigned_to_username=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT
            t.id,
            t.title,
            t.description,
            t.milestone,
            t.issue_type,
            t.status,
            t.due_at,
            t.progress_notes,
            t.completion_notes,
            t.completed_at,
            t.created_at,
            mi.id AS milestone_issue_id,
            mi.milestone AS catalog_milestone,
            mi.issue_type AS catalog_issue_type,
            u.username AS assigned_to,
            COALESCE(ru.name, u.role, 'usuario_comun') AS assigned_role,
            c.username AS created_by,
            COALESCE(rc.name, c.role, 'usuario_comun') AS created_by_role
        FROM tasks t
        JOIN users u ON u.id = t.assigned_to
        JOIN users c ON c.id = t.created_by
        LEFT JOIN rol_usuario ru ON ru.id = u.role_id
        LEFT JOIN rol_usuario rc ON rc.id = c.role_id
        LEFT JOIN milestone_issues mi ON mi.id = t.milestone_issue_id
        WHERE t.active = 1
          AND COALESCE(ru.name, u.role, 'usuario_comun') = 'usuario_comun'
    """

    params = []
    if status:
        query += " AND t.status = ?"
        params.append(_normalize_status(status))

    if assigned_to_username:
        query += " AND u.username = ?"
        params.append(assigned_to_username)

    query += " ORDER BY t.id DESC"
    cursor.execute(query, tuple(params))
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
            progress_notes,
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


def update_task_status(task_id, user_id, status, progress_notes=""):
    normalized_status = _normalize_status(status)

    completed_at = None
    completion_notes = None
    if normalized_status == "cumplida":
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        completion_notes = progress_notes or "Tarea marcada como cumplida"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tasks
        SET status = ?,
            progress_notes = ?,
            completion_notes = COALESCE(?, completion_notes),
            completed_at = COALESCE(?, completed_at)
        WHERE id = ? AND assigned_to = ? AND active = 1
        """,
        (normalized_status, progress_notes, completion_notes, completed_at, task_id, user_id),
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
