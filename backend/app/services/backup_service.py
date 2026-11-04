import os
import shutil
import datetime
from pathlib import Path
from backend.app.config import DATA_DIR, BACKUPS_DIR, BILL_TRASH_DIR, META_PATH, BACKUP_FOLDER_KEY, EXTRA_BACKUP_SUBDIR
from backend.app.core.storage import read_json, write_json_atomic, invalidate_cache
from backend.app.core.logging_util import log_error

last_extra_backup_error: str = ""

def extra_backups_dir() -> Path | None:
    folder = read_json(META_PATH, {}).get(BACKUP_FOLDER_KEY)
    if not folder:
        return None
    return Path(folder) / EXTRA_BACKUP_SUBDIR

def backup_source_dir(date_str: str) -> Path:
    local = BACKUPS_DIR / date_str
    if local.is_dir():
        return local
    extra = extra_backups_dir()
    if extra:
        extra_date = extra / date_str
        if extra_date.is_dir():
            return extra_date
    return local

def copy_dir_recursive(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        target = dst / entry.name
        if entry.is_dir():
            copy_dir_recursive(entry, target)
        else:
            shutil.copy2(entry, target)

def run_daily_backup():
    """Create today's backup snapshot and prune old backups (>30 days)."""
    global last_extra_backup_error
    try:
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.date.today().isoformat()
        target = BACKUPS_DIR / today
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            for item in DATA_DIR.iterdir():
                if item.name in ('backups', 'errors.log', 'port.txt'):
                    continue
                dst = target / item.name
                if item.is_dir():
                    copy_dir_recursive(item, dst)
                else:
                    shutil.copy2(item, dst)
            print(f"[backup] Daily snapshot saved: {target}")
            
        # Prune local backups older than 30 days
        all_backups = sorted([d.name for d in BACKUPS_DIR.iterdir() if d.is_dir() and len(d.name) == 10 and d.name[4] == '-' and d.name[7] == '-'])
        while len(all_backups) > 30:
            oldest = all_backups.pop(0)
            shutil.rmtree(BACKUPS_DIR / oldest, ignore_errors=True)
            
        # Copy to extra backup folder if set
        extra = extra_backups_dir()
        if extra and target.is_dir():
            extra.mkdir(parents=True, exist_ok=True)
            dst_extra = extra / today
            if not dst_extra.exists():
                tmp = extra / f"{today}.partial"
                shutil.rmtree(tmp, ignore_errors=True)
                copy_dir_recursive(target, tmp)
                tmp.replace(dst_extra)
            all_extra = sorted([d.name for d in extra.iterdir() if d.is_dir() and len(d.name) == 10 and d.name[4] == '-' and d.name[7] == '-'])
            while len(all_extra) > 30:
                oldest_extra = all_extra.pop(0)
                shutil.rmtree(extra / oldest_extra, ignore_errors=True)
            last_extra_backup_error = ""
    except Exception as e:
        last_extra_backup_error = f"The last copy to backup folder failed: {e}"
        log_error(f"Daily backup failed: {e}", "backup")

def purge_old_trash():
    """Purge soft-deleted invoices older than 30 days."""
    try:
        BILL_TRASH_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now().timestamp()
        thirty_days = 30 * 24 * 3600
        for item in BILL_TRASH_DIR.glob('*.json'):
            if now - item.stat().st_mtime > thirty_days:
                try:
                    item.unlink()
                except Exception:
                    pass
    except Exception as e:
        log_error(f"Purge trash failed: {e}", "trash")
