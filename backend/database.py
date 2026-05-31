import sqlite3
import hashlib
import os
import uuid
from datetime import datetime

DB_PATH = "helpdesk.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            user_name TEXT,
            session_id TEXT,
            issue TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    # Create default admin if not exists
    admin_id = str(uuid.uuid4())
    admin_pass = hash_password(os.getenv("ADMIN_PASSWORD", "nist@admin"))
    try:
        c.execute(
            "INSERT INTO users (id, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (admin_id, "Admin", "admin@nist.ac.in", admin_pass, "admin")
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(name: str, email: str, password: str) -> dict:
    conn = get_conn()
    c = conn.cursor()
    user_id = str(uuid.uuid4())
    hashed = hash_password(password)
    try:
        c.execute(
            "INSERT INTO users (id, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, hashed, "user")
        )
        conn.commit()
        return {"id": user_id, "name": name, "email": email, "role": "user"}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def login_user(email: str, password: str) -> dict:
    conn = get_conn()
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_session(user_id: str, title: str = "New Chat") -> str:
    conn = get_conn()
    c = conn.cursor()
    session_id = str(uuid.uuid4())
    c.execute(
        "INSERT INTO chat_sessions (id, user_id, title) VALUES (?, ?, ?)",
        (session_id, user_id, title)
    )
    conn.commit()
    conn.close()
    return session_id

def update_session_title(session_id: str, title: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE chat_sessions SET title=? WHERE id=?", (title[:50], session_id))
    conn.commit()
    conn.close()

def save_message(session_id: str, role: str, content: str):
    conn = get_conn()
    c = conn.cursor()
    msg_id = str(uuid.uuid4())
    c.execute(
        "INSERT INTO chat_messages (id, session_id, role, content) VALUES (?, ?, ?, ?)",
        (msg_id, session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_sessions(user_id: str) -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM chat_sessions WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_messages(session_id: str) -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM chat_messages WHERE session_id=? ORDER BY created_at ASC",
        (session_id,)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def create_ticket(user_id: str, user_name: str, session_id: str, issue: str) -> str:
    conn = get_conn()
    c = conn.cursor()
    ticket_id = "TKT-" + str(uuid.uuid4())[:8].upper()
    c.execute(
        "INSERT INTO tickets (id, user_id, user_name, session_id, issue) VALUES (?, ?, ?, ?, ?)",
        (ticket_id, user_id, user_name, session_id, issue)
    )
    conn.commit()
    conn.close()
    return ticket_id

def get_all_tickets() -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def update_ticket_status(ticket_id: str, status: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE tickets SET status=? WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()

def get_stats() -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tickets WHERE status='open'")
    open_tickets = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tickets WHERE status='resolved'")
    resolved_tickets = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM chat_messages")
    total_messages = c.fetchone()[0]
    conn.close()
    return {
        "total_users": total_users,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "total_messages": total_messages
    }
