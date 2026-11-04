import datetime
from fastapi import APIRouter
from backend.app.config import DATA_DIR, PROFILE_PATH, META_PATH, DEFAULT_PROFILE, LOCK_KEY
from backend.app.core.storage import read_all_from_dir, read_json, write_json_atomic
from backend.app.core.path_guard import safe_file_name

router = APIRouter(tags=["export-import"])

@router.get("/api/export")
def export_all():
    meta = read_json(META_PATH, {})
    meta_clean = {k: v for k, v in meta.items() if k != LOCK_KEY}
    
    return {
        "bills": read_all_from_dir("bills"),
        "profile": read_json(PROFILE_PATH, DEFAULT_PROFILE),
        "clients": read_all_from_dir("clients"),
        "termsTemplates": read_all_from_dir("templates"),
        "products": read_all_from_dir("products"),
        "expenses": read_all_from_dir("expenses"),
        "recurring": read_all_from_dir("recurring"),
        "receipts": read_all_from_dir("receipts"),
        "profiles": read_all_from_dir("profiles"),
        "purchases": read_all_from_dir("purchases"),
        "productions": read_all_from_dir("productions"),
        "purchaseOrders": read_all_from_dir("purchase-orders"),
        "cashBook": read_all_from_dir("cash-book"),
        "meta": meta_clean,
        "exportedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

@router.post("/api/import")
def import_all(data: dict, overwrite: str | None = None):
    is_overwrite = overwrite in ("1", "true", True)
    counts = {
        "billCount": 0, "billSkipped": 0,
        "clientCount": 0, "clientSkipped": 0,
        "templateCount": 0, "templateSkipped": 0,
        "productCount": 0, "productSkipped": 0,
        "expenseCount": 0, "expenseSkipped": 0,
        "recurringCount": 0, "recurringSkipped": 0,
        "receiptCount": 0, "receiptSkipped": 0,
        "profileCount": 0, "profileSkipped": 0,
        "purchaseCount": 0, "purchaseSkipped": 0,
        "productionCount": 0, "productionSkipped": 0,
        "purchaseOrderCount": 0, "purchaseOrderSkipped": 0,
        "cashBookCount": 0, "cashBookSkipped": 0,
    }
    
    def upsert_one(dir_name: str, entity: dict, count_key: str, skip_key: str):
        if not isinstance(entity, dict) or not entity.get("id"):
            return
        p = DATA_DIR / dir_name / f"{safe_file_name(entity['id'])}.json"
        if not is_overwrite and p.exists():
            counts[skip_key] += 1
            return
        write_json_atomic(p, entity)
        counts[count_key] += 1

    if data.get("profile"):
        if is_overwrite or not PROFILE_PATH.exists():
            write_json_atomic(PROFILE_PATH, data["profile"])
            
    for b in data.get("bills") or []:
        upsert_one("bills", b, "billCount", "billSkipped")
    for c in data.get("clients") or []:
        upsert_one("clients", c, "clientCount", "clientSkipped")
    for t in data.get("termsTemplates") or []:
        upsert_one("templates", t, "templateCount", "templateSkipped")
    for p in data.get("products") or []:
        upsert_one("products", p, "productCount", "productSkipped")
    for e in data.get("expenses") or []:
        upsert_one("expenses", e, "expenseCount", "expenseSkipped")
    for r in data.get("recurring") or []:
        upsert_one("recurring", r, "recurringCount", "recurringSkipped")
    for r in data.get("receipts") or []:
        upsert_one("receipts", r, "receiptCount", "receiptSkipped")
    for p in data.get("profiles") or []:
        upsert_one("profiles", p, "profileCount", "profileSkipped")
    for p in data.get("purchases") or []:
        upsert_one("purchases", p, "purchaseCount", "purchaseSkipped")
    for p in data.get("productions") or []:
        upsert_one("productions", p, "productionCount", "productionSkipped")
    for p in data.get("purchaseOrders") or []:
        upsert_one("purchase-orders", p, "purchaseOrderCount", "purchaseOrderSkipped")
    for c in data.get("cashBook") or []:
        upsert_one("cash-book", c, "cashBookCount", "cashBookSkipped")

    return {**counts, "hasProfile": bool(data.get("profile"))}
