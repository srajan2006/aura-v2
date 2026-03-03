from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import sqlite3
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# ── Security config ────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "aura-fallback-secret-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ── Database setup ─────────────────────────────────────────────────────────────
DB_PATH = Path("aura.db")

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # better concurrent access
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            email     TEXT    UNIQUE NOT NULL,
            username  TEXT    UNIQUE NOT NULL,
            full_name TEXT    NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wardrobe_items (
            id                TEXT PRIMARY KEY,
            user_email        TEXT NOT NULL,
            garment_type      TEXT NOT NULL,
            color             TEXT NOT NULL,
            is_multicolor     INTEGER DEFAULT 0,
            pattern           TEXT DEFAULT 'solid',
            color_description TEXT,
            full_description  TEXT,
            image_url         TEXT NOT NULL,
            filename          TEXT NOT NULL,
            created_at        TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ SQLite database initialised at", DB_PATH.resolve())

# ── User helpers ───────────────────────────────────────────────────────────────
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)

def create_user(email: str, username: str, full_name: str, hashed_password: str):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (email, username, full_name, hashed_password) VALUES (?,?,?,?)",
            (email, username, full_name, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError(str(e))
    finally:
        conn.close()

def get_user_by_email(email: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None

def email_exists(email: str) -> bool:
    conn = get_db()
    row = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row is not None

def username_exists(username: str) -> bool:
    conn = get_db()
    row = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row is not None

# ── Wardrobe helpers ───────────────────────────────────────────────────────────
def add_wardrobe_item(user_email: str, item: dict):
    conn = get_db()
    conn.execute("""
        INSERT INTO wardrobe_items
        (id, user_email, garment_type, color, is_multicolor, pattern,
         color_description, full_description, image_url, filename)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        item["id"], user_email,
        item["garment_type"], item["color"],
        1 if item.get("is_multicolor") else 0,
        item.get("pattern", "solid"),
        item.get("color_description", item["color"]),
        item.get("full_description", ""),
        item["image_url"], item["filename"]
    ))
    conn.commit()
    conn.close()

def get_wardrobe_items(user_email: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM wardrobe_items WHERE user_email = ? ORDER BY created_at DESC",
        (user_email,)
    ).fetchall()
    conn.close()
    items = []
    for row in rows:
        item = dict(row)
        item["is_multicolor"] = bool(item["is_multicolor"])
        items.append(item)
    return items

def update_wardrobe_item(item_id: str, user_email: str, updates: dict):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM wardrobe_items WHERE id = ? AND user_email = ?",
        (item_id, user_email)
    ).fetchone()
    if not row:
        conn.close()
        return None

    fields = []
    values = []
    allowed = ["garment_type", "color", "is_multicolor", "pattern", "color_description", "full_description"]
    for key in allowed:
        if key in updates and updates[key] is not None:
            fields.append(f"{key} = ?")
            val = updates[key]
            if key == "is_multicolor":
                val = 1 if val else 0
            values.append(val)

    if fields:
        values.extend([item_id, user_email])
        conn.execute(
            f"UPDATE wardrobe_items SET {', '.join(fields)} WHERE id = ? AND user_email = ?",
            values
        )
        conn.commit()

    updated = conn.execute(
        "SELECT * FROM wardrobe_items WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    item = dict(updated)
    item["is_multicolor"] = bool(item["is_multicolor"])
    return item

def delete_wardrobe_item(item_id: str, user_email: str):
    conn = get_db()
    row = conn.execute(
        "SELECT filename FROM wardrobe_items WHERE id = ? AND user_email = ?",
        (item_id, user_email)
    ).fetchone()
    filename = row["filename"] if row else None
    conn.execute(
        "DELETE FROM wardrobe_items WHERE id = ? AND user_email = ?",
        (item_id, user_email)
    )
    conn.commit()
    conn.close()
    return filename  # return filename so caller can delete the file

# ── JWT ────────────────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception