import datetime
from fastapi import APIRouter, HTTPException
from backend.app.config import DATA_DIR, BILL_TRASH_DIR
from backend.app.core.storage import read_json, invalidate_cache
from backend.app.core.path_guard import safe_file_name

router = APIRouter(prefix="/api/trash", tags=["trash"])

@router.get("")
def get_trash():
    BILL_TRASH_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for entry in BILL_TRASH_DIR.glob("*.json"):
        bill = read_json(entry, None)
        if bill:
            trashed_at = datetime.datetime.fromtimestamp(entry.stat().st_mtime, tz=datetime.timezone.utc).isoformat()
            bill["_trashedAt"] = trashed_at
            out.append(bill)
    return out

@router.post("/{bill_id}/restore")
def restore_trash(bill_id: str):
    fname = f"{safe_file_name(bill_id)}.json"
    trash_path = BILL_TRASH_DIR / fname
    bills_path = DATA_DIR / "bills" / fname
    
    if not trash_path.exists():
        raise HTTPException(status_code=404, detail={"error": "Not in trash"})
    if bills_path.exists():
        raise HTTPException(status_code=409, detail={"error": "An invoice with this number exists again. Rename or delete it first."})
        
    trash_path.replace(bills_path)
    invalidate_cache("bills")
    return {"success": True}

@router.delete("/{bill_id}")
def purge_trash(bill_id: str):
    fname = f"{safe_file_name(bill_id)}.json"
    trash_path = BILL_TRASH_DIR / fname
    if trash_path.exists():
        trash_path.unlink()
    return {"success": True}
