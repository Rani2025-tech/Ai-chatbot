import sqlite3
import os
import uuid
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_PATH = "helpdesk.db"
DATABASE_URL = os.getenv("DATABASE_URL")  # Set on Render for PostgreSQL

# Render injects postgres:// but psycopg2 needs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_conn():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _row_to_dict(row, cursor=None):
    """Convert a db row to dict regardless of backend."""
    if DATABASE_URL:
        if isinstance(row, dict):
            return row
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))
    return dict(row)

def _ph():
    """Return correct placeholder — %s for PostgreSQL, ? for SQLite."""
    return "%s" if DATABASE_URL else "?"

def _exec(c, sql, params=()):
    """Execute with correct placeholder style."""
    if DATABASE_URL:
        sql = sql.replace("?", "%s")
    c.execute(sql, params)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            user_name TEXT,
            session_id TEXT,
            issue TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """
        CREATE TABLE IF NOT EXISTS document_uploads (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            uploaded_by TEXT,
            chunks_created INTEGER DEFAULT 0,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            user_id TEXT,
            rating INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """
        CREATE TABLE IF NOT EXISTS query_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            session_id TEXT,
            question TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            response_time_ms INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
    ]
    for ddl in tables:
        c.execute(ddl)
    conn.commit()

    # Create default admin if not exists
    admin_id = str(uuid.uuid4())
    admin_pass = hash_password(os.getenv("ADMIN_PASSWORD", "nist@admin"))
    try:
        _exec(c,
            "INSERT INTO users (id, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (admin_id, "Admin", "admin@nist.ac.in", admin_pass, "admin")
        )
        conn.commit()
    except Exception:
        conn.rollback()
    conn.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    # Support legacy sha256 hashes during migration
    import hashlib
    if len(hashed) == 64:  # sha256 hex digest length
        return hashlib.sha256(plain.encode()).hexdigest() == hashed
    return pwd_context.verify(plain, hashed)

def create_user(name: str, email: str, password: str) -> dict:
    conn = get_conn()
    c = conn.cursor()
    user_id = str(uuid.uuid4())
    hashed = hash_password(password)
    try:
        _exec(c,
            "INSERT INTO users (id, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, hashed, "user")
        )
        conn.commit()
        return {"id": user_id, "name": name, "email": email, "role": "user"}
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()

def login_user(email: str, password: str) -> dict:
    conn = get_conn()
    c = conn.cursor()
    _exec(c, "SELECT * FROM users WHERE email=?", (email,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    user = _row_to_dict(row, c)
    conn.close()
    if verify_password(password, user["password"]):
        return user
    return None

def create_session(user_id: str, title: str = "New Chat") -> str:
    conn = get_conn()
    c = conn.cursor()
    session_id = str(uuid.uuid4())
    _exec(c,
        "INSERT INTO chat_sessions (id, user_id, title) VALUES (?, ?, ?)",
        (session_id, user_id, title)
    )
    conn.commit()
    conn.close()
    return session_id

def update_session_title(session_id: str, title: str):
    conn = get_conn()
    c = conn.cursor()
    _exec(c, "UPDATE chat_sessions SET title=? WHERE id=?", (title[:50], session_id))
    conn.commit()
    conn.close()

def save_message(session_id: str, role: str, content: str):
    conn = get_conn()
    c = conn.cursor()
    msg_id = str(uuid.uuid4())
    _exec(c,
        "INSERT INTO chat_messages (id, session_id, role, content) VALUES (?, ?, ?, ?)",
        (msg_id, session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_sessions(user_id: str) -> list:
    conn = get_conn()
    c = conn.cursor()
    _exec(c,
        "SELECT * FROM chat_sessions WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    )
    rows = [_row_to_dict(r, c) for r in c.fetchall()]
    conn.close()
    return rows

def get_messages(session_id: str) -> list:
    conn = get_conn()
    c = conn.cursor()
    _exec(c,
        "SELECT * FROM chat_messages WHERE session_id=? ORDER BY created_at ASC",
        (session_id,)
    )
    rows = [_row_to_dict(r, c) for r in c.fetchall()]
    conn.close()
    return rows

def create_ticket(user_id: str, user_name: str, session_id: str, issue: str) -> str:
    conn = get_conn()
    c = conn.cursor()
    ticket_id = "TKT-" + str(uuid.uuid4())[:8].upper()
    _exec(c,
        "INSERT INTO tickets (id, user_id, user_name, session_id, issue) VALUES (?, ?, ?, ?, ?)",
        (ticket_id, user_id, user_name, session_id, issue)
    )
    conn.commit()
    conn.close()
    return ticket_id

def get_all_tickets() -> list:
    conn = get_conn()
    c = conn.cursor()
    _exec(c, "SELECT * FROM tickets ORDER BY created_at DESC")
    rows = [_row_to_dict(r, c) for r in c.fetchall()]
    conn.close()
    return rows

def update_ticket_status(ticket_id: str, status: str):
    conn = get_conn()
    c = conn.cursor()
    _exec(c, "UPDATE tickets SET status=? WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()

def get_stats() -> dict:
    conn = get_conn()
    c = conn.cursor()

    def _scalar(sql):
        _exec(c, sql)
        return c.fetchone()[0] or 0

    total_users       = _scalar("SELECT COUNT(*) FROM users WHERE role='user'")
    total_tickets     = _scalar("SELECT COUNT(*) FROM tickets")
    open_tickets      = _scalar("SELECT COUNT(*) FROM tickets WHERE status='open'")
    resolved_tickets  = _scalar("SELECT COUNT(*) FROM tickets WHERE status='resolved'")
    total_messages    = _scalar("SELECT COUNT(*) FROM chat_messages")
    total_documents   = _scalar("SELECT COUNT(*) FROM document_uploads")
    positive_feedback = _scalar("SELECT COUNT(*) FROM feedback WHERE rating=1")
    total_feedback    = _scalar("SELECT COUNT(*) FROM feedback")

    _exec(c, "SELECT COUNT(*) FROM chat_messages WHERE role='user' AND DATE(created_at)=CURRENT_DATE")
    queries_today = c.fetchone()[0] or 0

    _exec(c, "SELECT AVG(response_time_ms) FROM query_logs WHERE response_time_ms IS NOT NULL")
    avg_response_ms = c.fetchone()[0]

    _exec(c, "SELECT language, COUNT(*) as cnt FROM query_logs GROUP BY language ORDER BY cnt DESC")
    language_breakdown = {row[0]: row[1] for row in c.fetchall()}

    conn.close()
    return {
        "total_users": total_users,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "total_messages": total_messages,
        "queries_today": queries_today,
        "total_documents": total_documents,
        "avg_response_ms": round(avg_response_ms) if avg_response_ms else 0,
        "language_breakdown": language_breakdown,
        "positive_feedback": positive_feedback,
        "total_feedback": total_feedback
    }

def log_document_upload(filename: str, uploaded_by: str, chunks_created: int):
    conn = get_conn()
    c = conn.cursor()
    _exec(c,
        "INSERT INTO document_uploads (id, filename, uploaded_by, chunks_created) VALUES (?, ?, ?, ?)",
        (str(uuid.uuid4()), filename, uploaded_by, chunks_created)
    )
    conn.commit()
    conn.close()

def get_document_uploads() -> list:
    conn = get_conn()
    c = conn.cursor()
    _exec(c, "SELECT * FROM document_uploads ORDER BY uploaded_at DESC")
    rows = [_row_to_dict(r, c) for r in c.fetchall()]
    conn.close()
    return rows

def save_feedback(message_id: str, session_id: str, user_id: str, rating: int):
    conn = get_conn()
    c = conn.cursor()
    _exec(c,
        "INSERT INTO feedback (id, message_id, session_id, user_id, rating) VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), message_id, session_id, user_id, rating)
    )
    conn.commit()
    conn.close()

def log_query(user_id: str, session_id: str, question: str, language: str, response_time_ms: int):
    conn = get_conn()
    c = conn.cursor()
    _exec(c,
        "INSERT INTO query_logs (id, user_id, session_id, question, language, response_time_ms) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), user_id, session_id, question, language, response_time_ms)
    )
    conn.commit()
    conn.close()
