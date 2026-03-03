from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
from pathlib import Path
from PIL import Image as PILImage
import shutil
import uuid
import os

import auth
from auth import (
    init_db, get_user_by_email, email_exists, username_exists,
    create_user, get_password_hash, verify_password,
    create_access_token, get_current_user,
    add_wardrobe_item, get_wardrobe_items,
    update_wardrobe_item, delete_wardrobe_item,
)
from v1_enhanced_detector import v1_detector
from outfit_recommender import recommender

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(title="AURA V2 API", version="2.0.0")

# Initialise SQLite DB on startup
init_db()

# ── CORS ───────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Upload config ──────────────────────────────────────────────────────────────
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

# ── Pydantic models ────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UpdateItem(BaseModel):
    garment_type: Optional[str] = None
    color: Optional[str] = None
    pattern: Optional[str] = None
    is_multicolor: Optional[bool] = None
    color_description: Optional[str] = None
    full_description: Optional[str] = None

# ── Image compression ──────────────────────────────────────────────────────────
def compress_image(file_path: Path, max_dimension: int = 800, quality: int = 85) -> Path:
    """Resize + compress uploaded image to save disk and speed up loads."""
    try:
        img = PILImage.open(file_path)
        img = img.convert("RGB")
        img.thumbnail((max_dimension, max_dimension), PILImage.LANCZOS)
        compressed_path = file_path.with_suffix(".jpg")
        img.save(compressed_path, "JPEG", quality=quality, optimize=True)
        if compressed_path != file_path:
            file_path.unlink(missing_ok=True)
        return compressed_path
    except Exception as e:
        print(f"⚠️  Compression failed, using original: {e}")
        return file_path

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Health check for Railway / Render / any uptime monitor."""
    return {"status": "ok", "version": "2.0.0", "service": "AURA API"}

@app.get("/")
def read_root():
    return {"message": "Welcome to AURA V2 API!", "status": "running", "docs": "/docs"}

# ── Auth endpoints ─────────────────────────────────────────────────────────────
@app.post("/api/auth/register")
def register(user: UserRegister):
    if len(user.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    if len(user.username) < 3:
        raise HTTPException(400, "Username must be at least 3 characters")
    if email_exists(user.email):
        raise HTTPException(400, "Email already registered")
    if username_exists(user.username):
        raise HTTPException(400, "Username already taken")
    try:
        create_user(user.email, user.username, user.full_name, get_password_hash(user.password))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"message": "Account created successfully", "email": user.email}

@app.post("/api/auth/login", response_model=Token)
def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/user/me")
def get_me(current_user: str = Depends(get_current_user)):
    user = get_user_by_email(current_user)
    if not user:
        raise HTTPException(404, "User not found")
    return {"email": user["email"], "username": user["username"], "full_name": user["full_name"]}

# ── Wardrobe endpoints ─────────────────────────────────────────────────────────
@app.post("/api/wardrobe/upload")
async def upload_garment(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    # Validate extension
    ext = (file.filename or "").split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Only {', '.join(ALLOWED_EXTENSIONS)} files allowed")

    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.")
    await file.seek(0)

    # Save raw file
    raw_filename = f"{uuid.uuid4()}.{ext}"
    raw_path = UPLOAD_DIR / raw_filename
    with raw_path.open("wb") as buf:
        buf.write(contents)

    # Compress image
    compressed_path = compress_image(raw_path)
    final_filename = compressed_path.name

    # AI analysis
    try:
        analysis = v1_detector.analyze_garment(str(compressed_path))
    except Exception as e:
        compressed_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Could not analyse image. Try another photo.")

    # Build item dict
    item = {
        "id": str(uuid.uuid4()),
        "garment_type": analysis["garment_type"],
        "color": analysis["color"],
        "is_multicolor": analysis["is_multicolor"],
        "pattern": analysis["pattern"],
        "color_description": analysis["color_description"],
        "full_description": analysis["full_description"],
        "image_url": f"/uploads/{final_filename}",
        "filename": final_filename,
    }

    # Save to SQLite
    try:
        add_wardrobe_item(current_user, item)
    except Exception as e:
        compressed_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to save item: {e}")

    return item

@app.get("/api/wardrobe/items")
def get_items(current_user: str = Depends(get_current_user)):
    return get_wardrobe_items(current_user)

@app.patch("/api/wardrobe/items/{item_id}")
def update_item(
    item_id: str,
    updates: UpdateItem,
    current_user: str = Depends(get_current_user)
):
    updated = update_wardrobe_item(item_id, current_user, updates.dict(exclude_none=True))
    if not updated:
        raise HTTPException(404, "Item not found")
    return updated

@app.delete("/api/wardrobe/items/{item_id}")
def delete_item(item_id: str, current_user: str = Depends(get_current_user)):
    filename = delete_wardrobe_item(item_id, current_user)
    if filename:
        (UPLOAD_DIR / filename).unlink(missing_ok=True)
    return {"message": "Item deleted"}

# ── Recommendations ────────────────────────────────────────────────────────────
@app.get("/api/recommendations")
def get_recommendations(
    max_outfits: int = 5,
    refresh: bool = True,
    current_user: str = Depends(get_current_user)
):
    wardrobe = get_wardrobe_items(current_user)

    if len(wardrobe) < 2:
        return {
            "message": "Add at least one top (shirt/tshirt/jacket) and one bottom (jeans) to get outfit suggestions",
            "outfits": [],
            "total_items": len(wardrobe)
        }

    try:
        outfits = recommender.get_recommendations(wardrobe, max_outfits, shuffle=refresh)
    except Exception as e:
        raise HTTPException(500, f"Recommendation engine error: {e}")

    if not outfits:
        return {
            "message": "Add more variety — need at least one top and one bottom",
            "outfits": [],
            "total_items": len(wardrobe)
        }

    return {
        "message": f"Found {len(outfits)} outfit suggestion{'s' if len(outfits) != 1 else ''}",
        "total_items": len(wardrobe),
        "outfits": outfits
    }

@app.get("/admin/stats")
def admin_stats():
    conn = get_db()
    users = conn.execute("SELECT email, username, full_name, created_at FROM users").fetchall()
    items = conn.execute("SELECT COUNT(*) as total FROM wardrobe_items").fetchone()
    conn.close()
    return {
        "total_users": len(users),
        "total_items": items["total"],
        "users": [dict(u) for u in users]
    }
# ── Static files — ALWAYS LAST ─────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")