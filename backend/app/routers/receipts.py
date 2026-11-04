import time
import secrets
from fastapi import APIRouter
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name

router = APIRouter(prefix="/api/receipts", tags=["receipts"])
RECEIPTS_DIR = DATA_DIR / "receipts"

@router.get("")
def get_receipts():
    receipts = read_all_from_dir("receipts")
    receipts.sort(key=lambda r: str(r.get("date") or ""), reverse=True)
    return receipts

@router.post("")
def save_receipt(receipt: dict):
    if not receipt.get("id"):
        receipt["id"] = f"rcpt_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    file_path = RECEIPTS_DIR / f"{safe_file_name(receipt['id'])}.json"
    write_json_atomic(file_path, receipt)
    return {"success": True, "id": receipt["id"]}

@router.delete("/{receipt_id}")
def delete_receipt(receipt_id: str):
    file_path = RECEIPTS_DIR / f"{safe_file_name(receipt_id)}.json"
    delete_file(file_path)
    return {"success": True}
