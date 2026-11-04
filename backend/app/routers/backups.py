import os
import time
import shutil
import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response
from backend.app.config import DATA_DIR, BACKUPS_DIR, META_PATH, LOCK_KEY, BACKUP_FOLDER_KEY, EXTRA_BACKUP_SUBDIR, DIRS
from backend.app.core.storage import read_json, write_json_atomic, invalidate_cache
from backend.app.core.path_guard import is_path_inside
from backend.app.services.backup_service import (
    extra_backups_dir,
    backup_source_dir,
    run_daily_backup,
    copy_dir_recursive,
    last_extra_backup_error
)

router = APIRouter(tags=["backups"])
last_backup_now_ms = 0

@router.get("/api/backups")
def get_backups():
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    dates = {d.name for d in BACKUPS_DIR.iterdir() if d.is_dir() and len(d.name) == 10 and d.name[4] == '-' and d.name[7] == '-'}
    
    extra = extra_backups_dir()
    extra_dates = set()
    if extra and extra.is_dir():
        extra_dates = {d.name for d in extra.iterdir() if d.is_dir() and len(d.name) == 10 and d.name[4] == '-' and d.name[7] == '-'}
        
    all_dates = sorted(list(dates | extra_dates), reverse=True)
    out = []
    for name in all_dates:
        src = backup_source_dir(name)
        created_at = datetime.datetime.fromtimestamp(src.stat().st_mtime, tz=datetime.timezone.utc).isoformat()
        out.append({
            "date": name,
            "createdAt": created_at,
            "inBackupFolder": name in extra_dates,
            "onlyInBackupFolder": name not in dates
        })
    return out

@router.delete("/api/backups/{date}")
def delete_backup(date: str):
    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
    target = BACKUPS_DIR / date
    if not is_path_inside(target, BACKUPS_DIR):
        raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
    if not target.exists():
        raise HTTPException(status_code=404, detail={"error": "Not found", "code": "not-found"})
    shutil.rmtree(target, ignore_errors=True)
    return {"success": True, "date": date}

@router.post("/api/backups/{date}/restore")
def restore_backup(date: str):
    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
        
    backup_dir = backup_source_dir(date)
    if not backup_dir.is_dir():
        raise HTTPException(status_code=404, detail={"error": "Not found", "code": "not-found"})
        
    meta_before = read_json(META_PATH, {})
    lock_before = meta_before.get(LOCK_KEY)
    backup_folder_before = meta_before.get(BACKUP_FOLDER_KEY)
    
    snapshot_dir = BACKUPS_DIR / f"pre-restore-{int(time.time() * 1000)}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    restored_dirs = []
    try:
        # Create pre-restore snapshot
        for entry in DATA_DIR.iterdir():
            if entry.name in ('backups', 'errors.log', 'port.txt'):
                continue
            dst = snapshot_dir / entry.name
            if entry.is_dir():
                copy_dir_recursive(entry, dst)
            else:
                shutil.copy2(entry, dst)
                
        # Perform restore
        for entry in backup_dir.iterdir():
            dst = DATA_DIR / entry.name
            if not is_path_inside(dst, DATA_DIR):
                continue
            if entry.is_dir():
                if dst.exists():
                    shutil.rmtree(dst, ignore_errors=True)
                copy_dir_recursive(entry, dst)
            else:
                shutil.copy2(entry, dst)
            restored_dirs.append(entry.name)
            
        # Re-apply preserved lock and backup-folder
        meta_after = read_json(META_PATH, {})
        if lock_before:
            meta_after[LOCK_KEY] = lock_before
        else:
            meta_after.pop(LOCK_KEY, None)
        if backup_folder_before:
            meta_after[BACKUP_FOLDER_KEY] = backup_folder_before
        else:
            meta_after.pop(BACKUP_FOLDER_KEY, None)
        write_json_atomic(META_PATH, meta_after)
        
        invalidate_cache()
        
        # Prune snapshots: keep at most 5 newest
        snaps = sorted([d for d in BACKUPS_DIR.iterdir() if d.is_dir() and d.name.startswith("pre-restore-")], key=lambda d: d.name)
        while len(snaps) > 5:
            old_snap = snaps.pop(0)
            shutil.rmtree(old_snap, ignore_errors=True)
            
        return {"success": True, "restored": date, "snapshot": snapshot_dir.name}
    except Exception as e:
        # Rollback from snapshot
        if snapshot_dir.is_dir():
            for name in restored_dirs:
                dst = DATA_DIR / name
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst, ignore_errors=True)
                    else:
                        dst.unlink()
                snap = snapshot_dir / name
                if snap.exists():
                    if snap.is_dir():
                        copy_dir_recursive(snap, dst)
                    else:
                        shutil.copy2(snap, dst)
        invalidate_cache()
        raise HTTPException(status_code=500, detail={"error": "Internal server error", "code": "server-error", "detail": str(e)})

@router.get("/api/backup-folder")
def get_backup_folder():
    folder = read_json(META_PATH, {}).get(BACKUP_FOLDER_KEY, "")
    copies_in = str(extra_backups_dir()) if folder else None
    return {"path": folder, "copiesIn": copies_in, "error": last_extra_backup_error}

@router.post("/api/backup-folder")
def set_backup_folder(payload: dict):
    raw = str(payload.get("path") or "").strip()
    meta = read_json(META_PATH, {})
    if not raw:
        meta.pop(BACKUP_FOLDER_KEY, None)
        write_json_atomic(META_PATH, meta)
        return {"ok": True, "path": ""}
        
    folder_path = Path(raw)
    if not folder_path.is_absolute():
        raise HTTPException(status_code=400, detail={"ok": False, "error": "Give the full folder path, for example D:\\Backups"})
    target_dir = folder_path / EXTRA_BACKUP_SUBDIR
    if is_path_inside(target_dir, DATA_DIR):
        raise HTTPException(status_code=400, detail={"ok": False, "error": "Choose a folder outside the app's data folder."})
        
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        probe = target_dir / f".write-test-{int(time.time() * 1000)}"
        with open(probe, 'w') as f:
            f.write("ok")
        probe.unlink()
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "error": f"Cannot write to that folder: {e}"})
        
    meta[BACKUP_FOLDER_KEY] = raw
    write_json_atomic(META_PATH, meta)
    run_daily_backup()
    return {"ok": True, "path": raw, "copiesIn": str(target_dir), "error": last_extra_backup_error}

@router.post("/api/backups/now")
def backup_now():
    global last_backup_now_ms
    now = time.time()
    if now - last_backup_now_ms < 5.0:
        return Response(content='{"error":"Too many requests","code":"rate-limited"}', status_code=429, media_type="application/json")
    last_backup_now_ms = now
    run_daily_backup()
    return {"success": True}
