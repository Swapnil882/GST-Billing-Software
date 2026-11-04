from fastapi import APIRouter, HTTPException
from backend.app.config import META_PATH, LOCK_KEY
from backend.app.core.storage import read_json, write_json_atomic
from backend.app.services.invoice_math import next_counter_value

router = APIRouter(tags=["meta"])

@router.get("/api/meta/{key}")
def get_meta_key(key: str):
    if key == LOCK_KEY:
        raise HTTPException(status_code=403, detail={"error": "Refused", "code": "forbidden"})
    meta = read_json(META_PATH, {})
    return {"value": meta.get(key, None)}

@router.post("/api/meta/{key}")
def set_meta_key(key: str, payload: dict):
    if key == LOCK_KEY:
        raise HTTPException(status_code=403, detail={"error": "Refused", "code": "forbidden"})
    if not isinstance(payload, dict) or "value" not in payload:
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
    meta = read_json(META_PATH, {})
    meta[key] = payload["value"]
    write_json_atomic(META_PATH, meta)
    return {"success": True}

@router.post("/api/meta/{key}/increment")
def increment_counter(key: str, payload: dict | None = None):
    if key == LOCK_KEY:
        raise HTTPException(status_code=403, detail={"error": "Refused", "code": "forbidden"})
    meta = read_json(META_PATH, {})
    start = (payload or {}).get("start", 1)
    next_val = next_counter_value(meta.get(key), start)
    meta[key] = next_val
    write_json_atomic(META_PATH, meta)
    return {"value": next_val}

@router.post("/api/number-series/rename")
def rename_number_series(payload: dict):
    from_key = payload.get("from")
    to_key = payload.get("to")
    if not from_key or not to_key or not isinstance(from_key, str) or not isinstance(to_key, str) or from_key == to_key:
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
        
    meta = read_json(META_PATH, {})
    series = meta.get("invoiceNumberSeries") or {}
    if from_key not in series or to_key in series:
        return {"moved": False}
        
    series[to_key] = series[from_key]
    del series[from_key]
    meta["invoiceNumberSeries"] = series
    
    for k in list(meta.keys()):
        suffix = f"@{from_key}"
        if k.startswith("counter_") and k.endswith(suffix):
            target = k[:-len(from_key)] + to_key
            try:
                curr_target = int(meta.get(target) or 0)
                curr_source = int(meta.get(k) or 0)
                meta[target] = max(curr_target, curr_source)
            except Exception:
                meta[target] = meta.get(k)
            del meta[k]
            
    write_json_atomic(META_PATH, meta)
    return {"moved": True}
