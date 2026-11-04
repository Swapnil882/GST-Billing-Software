import time
import secrets
import datetime
from fastapi import APIRouter, HTTPException
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name, is_path_inside

router = APIRouter(prefix="/api/cash-book", tags=["cash-book"])
CASH_DIR = DATA_DIR / "cash-book"

def validate_cash_entry(e: dict) -> str:
    if not isinstance(e, dict):
        return "Invalid entry"
    if e.get("type") not in ("in", "out"):
        return "Choose Money in or Money out"
    try:
        amt = float(e.get("amount") or 0.0)
        if amt <= 0:
            return "Enter an amount more than 0"
        if amt > 1e11:
            return "The amount is too large"
    except (ValueError, TypeError):
        return "Enter an amount more than 0"
    if not e.get("date"):
        return "Enter a date"
    return ""

def clean_cash_entry(e: dict) -> dict:
    cleaned = {
        "type": e.get("type"),
        "date": e.get("date"),
        "amount": round(float(e.get("amount") or 0.0), 2),
        "name": str(e.get("name") or "").strip(),
        "note": str(e.get("note") or "").strip(),
        "category": str(e.get("category") or "").strip(),
        "ownerGstin": str(e.get("ownerGstin") or "").strip(),
        "ownerName": str(e.get("ownerName") or "").strip(),
    }
    if e.get("id"):
        cleaned["id"] = e["id"]
    if e.get("createdAt"):
        cleaned["createdAt"] = e["createdAt"]
    return cleaned

@router.get("")
def get_cash_entries():
    entries = read_all_from_dir("cash-book")
    entries.sort(key=lambda c: (str(c.get("date") or ""), str(c.get("createdAt") or "")), reverse=True)
    return entries

@router.post("")
def save_cash_entry(entry: dict):
    problem = validate_cash_entry(entry)
    if problem:
        raise HTTPException(status_code=400, detail={"error": problem, "code": "bad-request"})
    clean = clean_cash_entry(entry)
    if not clean.get("id"):
        clean["id"] = f"cash_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    if not clean.get("createdAt"):
        clean["createdAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    file_path = CASH_DIR / f"{safe_file_name(clean['id'])}.json"
    if not is_path_inside(file_path, CASH_DIR):
        raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
    write_json_atomic(file_path, clean)
    return {"success": True, "id": clean["id"]}

@router.delete("/{entry_id}")
def delete_cash_entry(entry_id: str):
    file_path = CASH_DIR / f"{safe_file_name(entry_id)}.json"
    if not is_path_inside(file_path, CASH_DIR):
        raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
    delete_file(file_path)
    return {"success": True}
