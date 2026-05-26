import sqlite3
import os
import hashlib
import binascii
import hmac
from typing import Optional, Dict

DEFAULT_DB_PATH = os.path.join("data", "app.db")

def _get_conn(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    with _get_conn(db_path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()

def _hash_password(password: str, salt: bytes = None) -> (str, str):
    if salt is None: salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(hashed).decode('ascii'), binascii.hexlify(salt).decode('ascii')

def authenticate_user(username: str, password: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict]:
    with _get_conn(db_path) as conn:
        row = conn.execute("SELECT id, username, password_hash, salt FROM users WHERE username = ?", (username,)).fetchone()
        if row and hmac.compare_digest(binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), binascii.unhexlify(row["salt"].encode('ascii')), 100000)).decode('ascii'), row["password_hash"]):
            return {"id": row["id"], "username": row["username"]}
        return None

def create_user(username: str, password: str, db_path: str = DEFAULT_DB_PATH) -> int:
    ph, salt = _hash_password(password)
    with _get_conn(db_path) as conn:
        cur = conn.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, ph, salt))
        conn.commit()
        return cur.lastrowid
