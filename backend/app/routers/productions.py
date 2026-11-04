from fastapi import APIRouter, HTTPException
from backend.app.config import DATA_DIR
from backend.app.core.storage import (
    read_all_from_dir,
    read_json,
    write_json_atomic,
    delete_file,
    invalidate_cache
)
from backend.app.core.path_guard import safe_file_name, is_path_inside

router = APIRouter(prefix="/api/productions", tags=["productions"])
PRODUCTIONS_DIR = DATA_DIR / "productions"
PRODUCTS_DIR = DATA_DIR / "products"

def stock_moves(changes: dict, skip_missing: bool = False):
    if not isinstance(changes, dict):
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
    out = []
    for p_id, change in changes.items():
        file = PRODUCTS_DIR / f"{safe_file_name(p_id)}.json"
        if not is_path_inside(file, PRODUCTS_DIR):
            raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
        try:
            num_change = float(change)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
            
        product = read_json(file, None)
        if not product:
            if skip_missing:
                continue
            raise HTTPException(status_code=400, detail={"error": "Product not found. Reload the page and try again."})
        if product.get("kind") == "service":
            continue
            
        curr_stock = float(product.get("stock") or 0.0)
        new_stock = round((curr_stock + num_change) * 1000) / 1000
        out.append({
            "file": file,
            "before": product,
            "after": {**product, "stock": new_stock}
        })
    return out

def commit_stock(moves, finish_callback):
    done = []
    try:
        for m in moves:
            write_json_atomic(m["file"], m["after"])
            done.append(m)
        finish_callback()
    except Exception as e:
        for m in done:
            try:
                write_json_atomic(m["file"], m["before"])
            except Exception:
                pass
        raise e

@router.get("")
def get_productions():
    rows = read_all_from_dir("productions")
    rows.sort(key=lambda r: (str(r.get("date") or ""), str(r.get("createdAt") or "")), reverse=True)
    return rows

@router.post("")
def save_production(entry: dict):
    if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
    file = PRODUCTIONS_DIR / f"{safe_file_name(entry['id'])}.json"
    if not is_path_inside(file, PRODUCTIONS_DIR):
        raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
    if file.exists():
        raise HTTPException(status_code=409, detail={"error": "Conflict with existing resource", "code": "conflict"})
        
    moves = stock_moves(entry.get("stockApplied", {}), False)
    commit_stock(moves, lambda: write_json_atomic(file, entry))
    invalidate_cache("products")
    return {"success": True, "id": entry["id"]}

@router.delete("/{production_id}")
def delete_production(production_id: str):
    file = PRODUCTIONS_DIR / f"{safe_file_name(production_id)}.json"
    if not is_path_inside(file, PRODUCTIONS_DIR):
        raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
    entry = read_json(file, None)
    if not entry:
        raise HTTPException(status_code=404, detail={"error": "Not found", "code": "not-found"})
        
    back = {p_id: -(float(ch or 0.0)) for p_id, ch in (entry.get("stockApplied") or {}).items()}
    moves = stock_moves(back, True)
    commit_stock(moves, lambda: delete_file(file))
    invalidate_cache("products")
    return {"success": True}
