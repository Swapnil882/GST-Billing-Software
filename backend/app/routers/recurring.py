import time
import secrets
from fastapi import APIRouter, HTTPException
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name
from backend.app.services.recurring_engine import (
    local_today,
    template_has_ended,
    generate_from_template
)

router = APIRouter(prefix="/api/recurring", tags=["recurring"])
RECURRING_DIR = DATA_DIR / "recurring"

@router.get("")
def get_recurring():
    return read_all_from_dir("recurring")

@router.post("")
def save_recurring(recurring: dict):
    if not recurring.get("id"):
        recurring["id"] = f"rec_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    file_path = RECURRING_DIR / f"{safe_file_name(recurring['id'])}.json"
    write_json_atomic(file_path, recurring)
    return {"success": True, "id": recurring["id"]}

@router.delete("/{recurring_id}")
def delete_recurring(recurring_id: str):
    file_path = RECURRING_DIR / f"{safe_file_name(recurring_id)}.json"
    delete_file(file_path)
    return {"success": True}

@router.post("/{recurring_id}/generate")
def generate_now(recurring_id: str):
    templates = read_all_from_dir("recurring")
    tpl = next((t for t in templates if t.get("id") == recurring_id), None)
    if not tpl:
        raise HTTPException(status_code=404, detail={"error": "Recurring template not found"})
    today = local_today()
    if template_has_ended(tpl, today):
        raise HTTPException(status_code=409, detail={"error": "This template has reached its end date or number of invoices"})
    try:
        invoice_number = generate_from_template(tpl, today)
        return {"success": True, "invoiceNumber": invoice_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e) or "Could not generate the invoice"})
