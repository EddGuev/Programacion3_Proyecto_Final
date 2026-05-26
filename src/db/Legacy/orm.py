# src/db/orm.py
import sqlite3
import os
import hashlib
import binascii
import hmac
from typing import Optional, List, Dict

# Ruta a la base de datos (relativa a la ubicación de orm.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB = os.path.join(BASE_DIR, "data", "app.db")

def _conn(db_path: str = DEFAULT_DB):
    """
    Obtiene una conexión a SQLite.
    Si db_path incluye carpeta, la crea. Si no (p. ej. 'test.db'), no intenta crearla.
    """
    dirpath = os.path.dirname(db_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = DEFAULT_DB):
    schema_path = os.path.join(BASE_DIR, "docs", "schema.sql")
    with _conn(db_path) as conn:
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf8") as f:
                conn.executescript(f.read())
        else:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT, salt TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, created_at TIMESTAMP, updated_at TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id));
            CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, sender TEXT, content TEXT, created_at TIMESTAMP, FOREIGN KEY(conversation_id) REFERENCES conversations(id));
            CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, user_id INTEGER, conversation_id INTEGER, filename TEXT, file_type TEXT, filepath TEXT, mongo_id TEXT, extracted_text TEXT, uploaded_at TIMESTAMP);
            """)
        conn.commit()

# --- Seguridad de Contraseñas ---
def _hash_password(password: str, salt: bytes = None):
    if salt is None: salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(hashed).decode('ascii'), binascii.hexlify(salt).decode('ascii')

def _verify_password(stored_hash: str, stored_salt: str, attempt: str) -> bool:
    salt = binascii.unhexlify(stored_salt.encode('ascii'))
    new_hash, _ = _hash_password(attempt, salt)
    return hmac.compare_digest(new_hash, stored_hash)

# --- Usuarios ---
def create_user(username: str, password: str, db_path: str = DEFAULT_DB) -> int:
    ph, salt = _hash_password(password)
    with _conn(db_path) as conn:
        cur = conn.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, ph, salt))
        conn.commit()
        return cur.lastrowid

def authenticate_user(username: str, password: str, db_path: str = DEFAULT_DB) -> Optional[Dict]:
    with _conn(db_path) as conn:
        row = conn.execute("SELECT id, username, password_hash, salt FROM users WHERE username = ?", (username,)).fetchone()
        if row and _verify_password(row["password_hash"], row["salt"], password):
            return {"id": row["id"], "username": row["username"]}
        return None

# --- Conversaciones ---
def create_conversation(user_id: int, title: str = "Nueva Conversación", db_path: str = DEFAULT_DB) -> int:
    with _conn(db_path) as conn:
        cur = conn.execute("INSERT INTO conversations (user_id, title) VALUES (?, ?)", (user_id, title))
        conn.commit()
        return cur.lastrowid

def get_conversations_for_user(user_id: int, db_path: str = DEFAULT_DB) -> List[Dict]:
    with _conn(db_path) as conn:
        rows = conn.execute("SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC", (user_id,)).fetchall()
        return [dict(r) for r in rows]

# --- Mensajes ---
def add_message(conversation_id: int, sender: str, content: str, db_path: str = DEFAULT_DB) -> int:
    with _conn(db_path) as conn:
        cur = conn.execute("INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)", (conversation_id, sender, content))
        conn.execute("UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (conversation_id,))
        conn.commit()
        return cur.lastrowid

def get_messages(conversation_id: int, db_path: str = DEFAULT_DB) -> List[Dict]:
    with _conn(db_path) as conn:
        rows = conn.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (conversation_id,)).fetchall()
        return [dict(r) for r in rows]

# --- Archivos ---
def store_file_metadata(user_id: int, filename: str, file_type: str, conversation_id: int = None, extracted_text: str = None, mongo_id: str = None, db_path: str = DEFAULT_DB) -> int:
    with _conn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO files (user_id, conversation_id, filename, file_type, extracted_text, mongo_id) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, conversation_id, filename, file_type, extracted_text, mongo_id)
        )
        conn.commit()
        return cur.lastrowid
