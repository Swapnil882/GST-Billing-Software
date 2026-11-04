import os
import json
import time
import shutil
from pathlib import Path
from typing import Any
from backend.app.config import DATA_DIR, DIRS, META_PATH, LOCK_KEY
from backend.app.core.path_guard import safe_file_name, is_path_inside
from backend.app.core.logging_util import log_error
from backend.app.core.security import RESET_PIN_FILES

# 5-second TTL in-memory cache for directory reads
DIR_CACHE: dict[str, dict[str, Any]] = {}
DIR_CACHE_TTL_SEC = 5.0
REPORTED_DAMAGED: set[str] = set()

def invalidate_cache(dir_name: str | None = None):
    """Invalidate cache for specific dir or all dirs."""
    if dir_name:
        DIR_CACHE.pop(dir_name, None)
    else:
        DIR_CACHE.clear()

def read_json(file_path: str | Path, fallback: Any = None) -> Any:
    """Read a JSON file, stripping UTF-8 BOM if present."""
    p = Path(file_path)
    if not p.is_file():
        return fallback
    try:
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read().lstrip('\ufeff')
            return json.loads(content)
    except Exception:
        return fallback

def write_json_atomic(file_path: str | Path, data: Any):
    """Atomic write via temporary file and replace to prevent corruption."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = p.with_name(f"{p.name}.tmp")
    
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
        
    tmp_path.replace(p)
    
    parent_dir_name = p.parent.name
    if parent_dir_name in DIRS:
        invalidate_cache(parent_dir_name)
        try:
            from backend.app.db.sync_service import mirror_write_to_db
            mirror_write_to_db(parent_dir_name, p.stem, data)
        except Exception:
            pass

def delete_file(file_path: str | Path):
    """Delete file and invalidate parent dir cache."""
    p = Path(file_path)
    if p.exists():
        p.unlink()
        parent_dir_name = p.parent.name
        if parent_dir_name in DIRS:
            invalidate_cache(parent_dir_name)
            try:
                from backend.app.db.sync_service import mirror_delete_from_db
                mirror_delete_from_db(parent_dir_name, p.stem)
            except Exception:
                pass

def read_all_from_dir(dir_name: str) -> list[dict]:
    """Read all JSON files from data/<dir_name> with 5-second cache TTL."""
    now = time.time()
    cached = DIR_CACHE.get(dir_name)
    if cached and (now - cached['at']) < DIR_CACHE_TTL_SEC:
        return cached['value']

    dir_path = DATA_DIR / dir_name
    if not dir_path.is_dir():
        return []

    results = []
    for entry in dir_path.glob('*.json'):
        try:
            with open(entry, 'r', encoding='utf-8') as f:
                content = f.read().lstrip('\ufeff')
                val = json.loads(content)
                if isinstance(val, dict):
                    results.append(val)
                    continue
        except Exception:
            pass
        
        # Report damaged file once
        key = f"{dir_name}/{entry.name}"
        if key not in REPORTED_DAMAGED:
            REPORTED_DAMAGED.add(key)
            log_error(f"Skipped damaged file data/{key} - restore from backup", "data")

    DIR_CACHE[dir_name] = {'at': now, 'value': results}
    return results

def get_current_lock() -> dict | None:
    """Retrieve current PIN lock from meta.json, honoring RESET-PIN triggers."""
    meta = read_json(META_PATH, {})
    reset_found = [f for f in RESET_PIN_FILES if f.exists()]
    if reset_found:
        if LOCK_KEY in meta:
            del meta[LOCK_KEY]
            write_json_atomic(META_PATH, meta)
        for f in reset_found:
            try:
                f.unlink()
            except Exception:
                pass
        log_error("RESET-PIN file found: PIN lock removed", "lock")
        return None
    return meta.get(LOCK_KEY)

def find_credit_dependents(bill_id: str) -> list[dict]:
    """Check if any bill in data/bills/ relies on bill_id as a client-credit source."""
    bills_dir = DATA_DIR / 'bills'
    if not bills_dir.is_dir():
        return []
    dependents = []
    for f in bills_dir.glob('*.json'):
        other = read_json(f, None)
        if not other or other.get('id') == bill_id:
            continue
        payments = other.get('payments') or (other.get('data', {}).get('payments') if isinstance(other.get('data'), dict) else []) or []
        for p in payments:
            if isinstance(p, dict) and p.get('mode') == 'credit-applied':
                sources = p.get('creditSourceBillIds', [])
                if bill_id in sources:
                    dependents.append({
                        "id": other.get("id"),
                        "invoiceNumber": other.get("invoiceNumber"),
                        "amount": p.get("amount")
                    })
                    break
    return dependents
