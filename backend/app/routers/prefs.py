from fastapi import APIRouter, HTTPException
from backend.app.config import LOCAL_PREFS_PATH
from backend.app.core.storage import read_json, write_json_atomic

router = APIRouter(prefix="/api/local-prefs", tags=["prefs"])

@router.get("")
def get_local_prefs():
    return {"value": read_json(LOCAL_PREFS_PATH, {})}

@router.post("")
def update_local_prefs(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
    set_dict = payload.get("set") or {}
    remove_list = payload.get("remove") or []
    if not isinstance(set_dict, dict) or not isinstance(remove_list, list):
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
        
    prefs = read_json(LOCAL_PREFS_PATH, {})
    for k, v in set_dict.items():
        if isinstance(v, str):
            prefs[k] = v
    for k in remove_list:
        prefs.pop(str(k), None)
        
    write_json_atomic(LOCAL_PREFS_PATH, prefs)
    return {"success": True}
