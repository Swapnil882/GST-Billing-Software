from fastapi import APIRouter, HTTPException
from backend.app.config import PROFILE_PATH, DEFAULT_PROFILE, DATA_DIR
from backend.app.core.storage import read_json, write_json_atomic, read_all_from_dir, delete_file
from backend.app.core.path_guard import safe_file_name

router = APIRouter(tags=["profile"])

@router.get("/api/profile")
def get_profile():
    return read_json(PROFILE_PATH, DEFAULT_PROFILE)

@router.post("/api/profile")
def save_profile(profile: dict):
    write_json_atomic(PROFILE_PATH, profile)
    return {"success": True}

@router.get("/api/profiles")
def get_profiles():
    return read_all_from_dir("profiles")

@router.post("/api/profiles")
def save_business_profile(profile: dict):
    if not profile or not profile.get("id"):
        raise HTTPException(status_code=400, detail={"error": "Profile must have an id"})
    file_path = DATA_DIR / "profiles" / f"{safe_file_name(profile['id'])}.json"
    write_json_atomic(file_path, profile)
    return {"success": True}

@router.delete("/api/profiles/{profile_id}")
def delete_business_profile(profile_id: str):
    file_path = DATA_DIR / "profiles" / f"{safe_file_name(profile_id)}.json"
    delete_file(file_path)
    return {"success": True}
