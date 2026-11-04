import os
import sys
import time
import httpx
from fastapi import APIRouter, HTTPException, Response
from backend.app.config import PACKAGE_JSON_PATH, CHANGELOG_PATH, ERRORS_LOG, LOCAL_PREFS_PATH
from backend.app.core.storage import read_json
from backend.app.core.logging_util import redact, log_error, rotate_errors_if_large

router = APIRouter(tags=["system"])
START_TIME = time.time()
client_error_times: list[float] = []

def get_pkg_version() -> str:
    pkg = read_json(PACKAGE_JSON_PATH, {})
    return str(pkg.get("version") or "1.10.83")

def compare_semver(a: str, b: str) -> int:
    pa = [int(x) if x.isdigit() else 0 for x in str(a or "0").split(".")][:3]
    pb = [int(x) if x.isdigit() else 0 for x in str(b or "0").split(".")][:3]
    while len(pa) < 3:
        pa.append(0)
    while len(pb) < 3:
        pb.append(0)
    for i in range(3):
        if pa[i] > pb[i]:
            return 1
        if pa[i] < pb[i]:
            return -1
    return 0

@router.get("/api/version")
def get_version():
    return {"current": get_pkg_version()}

@router.get("/api/health")
def health_check():
    uptime_sec = int(time.time() - START_TIME)
    errors_tail = ""
    if ERRORS_LOG.exists():
        try:
            size = ERRORS_LOG.stat().st_size
            read_len = min(size, 4096)
            with open(ERRORS_LOG, "rb") as f:
                f.seek(size - read_len)
                errors_tail = f.read().decode("utf-8", errors="replace")
        except Exception:
            pass
    return {
        "ok": True,
        "version": get_pkg_version(),
        "uptimeSec": uptime_sec,
        "pid": os.getpid(),
        "hasRecentErrors": bool(errors_tail.strip()),
        "errorsTail": errors_tail,
    }

@router.get("/api/db/status")
def get_db_status():
    from backend.app.config import DB_ENABLED, DB_ENGINE, DB_HOST, DB_PORT, DB_NAME, DB_USER
    from backend.app.db.session import is_db_connected
    connected = is_db_connected()
    return {
        "enabled": DB_ENABLED,
        "connected": connected,
        "engine": DB_ENGINE,
        "host": f"{DB_HOST}:{DB_PORT}",
        "database": DB_NAME,
        "user": DB_USER,
        "status": "connected" if connected else "offline"
    }

@router.post("/api/db/sync")
def trigger_db_sync():
    from backend.app.db.sync_service import sync_all_json_to_db
    result = sync_all_json_to_db()
    return result

@router.get("/api/changelog")
def get_changelog():
    if not CHANGELOG_PATH.exists():
        return {"text": ""}
    try:
        with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
            text = f.read()[:400000]
        return {"text": text}
    except Exception:
        return {"text": ""}

@router.get("/api/check-update")
async def check_update(now: str | None = None):
    curr_version = get_pkg_version()
    # Offline and standalone mode: always report up-to-date locally
    return {
        "current": curr_version,
        "latest": curr_version,
        "updateAvailable": False,
        "releaseNotes": "System is running the latest FastAPI + React architecture (v" + curr_version + ").",
        "releaseUrl": None,
    }

@router.post("/api/client-errors")
def log_client_error(payload: dict):
    now = time.time()
    while client_error_times and now - client_error_times[0] > 60.0:
        client_error_times.pop(0)
    if len(client_error_times) >= 30:
        return Response(content='{"error":"Too many reports","code":"rate-limited"}', status_code=429, media_type="application/json")
        
    client_error_times.append(now)
    msg = redact(str(payload.get("message") or "")).replace("\r", " ").replace("\n", " ")[:500]
    if not msg:
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
        
    kind = redact(str(payload.get("kind") or "error"))[:20]
    ver = redact(str(payload.get("version") or ""))[:20]
    view = redact(str(payload.get("view") or ""))[:30]
    stack = redact(str(payload.get("stack") or ""))[:1500]
    browser = redact(str(payload.get("browser") or ""))[:80]
    
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))}] [client:{kind}] v{ver} screen={view} {msg} | {stack} | {browser}"
    try:
        rotate_errors_if_large()
        with open(ERRORS_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    return {"ok": True}

@router.get("/api/errors-log")
def get_errors_log():
    if not ERRORS_LOG.exists():
        return {"lines": []}
    try:
        size = ERRORS_LOG.stat().st_size
        read_len = min(size, 64 * 1024)
        with open(ERRORS_LOG, "rb") as f:
            f.seek(size - read_len)
            content = f.read().decode("utf-8", errors="replace")
        lines = content.splitlines()
        if read_len < size and lines:
            lines = lines[1:] # discard truncated first line
        filtered = [redact(l).strip()[:500] for l in lines if l.strip()][-100:]
        return {"lines": filtered}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Internal server error", "code": "server-error", "detail": str(e)})
