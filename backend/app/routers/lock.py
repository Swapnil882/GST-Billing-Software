import time
from fastapi import APIRouter, HTTPException, Response
from backend.app.config import META_PATH, LOCK_KEY
from backend.app.core.storage import read_json, write_json_atomic, get_current_lock
from backend.app.core.security import (
    PIN_RE,
    pin_limiter,
    pin_hash,
    pin_matches,
    generate_salt
)

router = APIRouter(prefix="/api/lock", tags=["lock"])

@router.get("")
def get_lock_status():
    lock = get_current_lock()
    return {
        "enabled": bool(lock),
        "length": int(lock.get("length") or 0) if lock else 0
    }

@router.post("/verify")
def verify_pin(payload: dict):
    lock = get_current_lock()
    if not lock:
        return {"ok": True}
        
    now = time.time()
    wait = int(pin_limiter.until - now)
    if wait > 0:
        return Response(
            content='{"ok":false,"wait":' + str(wait) + '}',
            status_code=429,
            media_type="application/json"
        )
        
    pin = payload.get("pin")
    if pin_matches(lock, pin):
        pin_limiter.wrong = 0
        return {"ok": True}
        
    pin_limiter.wrong += 1
    if pin_limiter.wrong >= 5:
        pin_limiter.wrong = 0
        pin_limiter.until = now + 30.0
        
    return Response(
        content='{"ok":false,"error":"wrong-pin"}',
        status_code=401,
        media_type="application/json"
    )

@router.post("/set")
def set_lock_pin(payload: dict):
    pin = payload.get("pin")
    current_pin = payload.get("currentPin")
    
    if pin is not None and not PIN_RE.match(str(pin or "")):
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
        
    lock = get_current_lock()
    if lock:
        if not pin_matches(lock, current_pin):
            raise HTTPException(status_code=401, detail={"ok": False, "error": "wrong-pin"})
            
    meta = read_json(META_PATH, {})
    if pin is None:
        meta.pop(LOCK_KEY, None)
    else:
        salt = generate_salt()
        meta[LOCK_KEY] = {
            "salt": salt,
            "hash": pin_hash(pin, salt),
            "length": len(str(pin))
        }
    write_json_atomic(META_PATH, meta)
    return {"ok": True, "enabled": pin is not None}
