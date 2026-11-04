import os
import sys
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.app.config import DATA_DIR, BASE_DIR, DEFAULT_PORT, PORT_FILE
from backend.app.core.storage import read_json

router = APIRouter(prefix="/api/control-panel", tags=["control-panel"])

@router.get("/status")
def control_panel_status():
    total_size = 0
    if DATA_DIR.is_dir():
        for root, _, files in os.walk(DATA_DIR):
            for f in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
                    
    active_port = DEFAULT_PORT
    if PORT_FILE.exists():
        try:
            active_port = int(PORT_FILE.read_text().strip())
        except Exception:
            pass
            
    is_win = sys.platform.startswith("win")
    is_mac = sys.platform == "darwin"
    
    return {
        "platform": sys.platform,
        "node": sys.version.split()[0],
        "controlScriptsAvailable": False,
        "actions": [],
        "dataFolder": str(DATA_DIR),
        "dataSizeBytes": total_size,
        "port": active_port,
        "launcherType": "none",
        "canRemove": False,
        "appFolder": str(BASE_DIR),
    }

@router.post("/open-data-folder")
def open_data_folder():
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(DATA_DIR))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(DATA_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(DATA_DIR)])
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/open-backups-folder")
def open_backups_folder():
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
    backups_home = Path(home) / "Documents" / "FreeGSTBill Backups"
    try:
        backups_home.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(str(backups_home))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(backups_home)])
        else:
            subprocess.Popen(["xdg-open", str(backups_home)])
        return {"ok": True, "path": str(backups_home)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/launch-script")
def launch_script(payload: dict):
    action = payload.get("action")
    if action == "stop":
        sys.exit(0)
    return {"ok": False, "error": f"Script action {action} not applicable in source development mode"}

@router.post("/backup")
def control_panel_backup():
    from backend.app.services.backup_service import run_daily_backup
    run_daily_backup()
    return {"ok": True}

@router.post("/restart")
def control_panel_restart():
    import time
    import threading
    def _do_restart():
        time.sleep(0.5)
        run_script = BASE_DIR / "run.py"
        subprocess.Popen([sys.executable, str(run_script), "--no-open"])
        os._exit(0)
    threading.Thread(target=_do_restart, daemon=True).start()
    return {"ok": True}

@router.post("/uninstall")
def control_panel_uninstall(payload: dict):
    confirm = payload.get("confirm")
    if confirm != "REMOVE":
        raise HTTPException(status_code=400, detail={"ok": False, "error": "Not confirmed"})
    return {"ok": False, "error": "Remove works only in an installed distribution package, not in source development mode."}

@router.post("/{action}")
def control_panel_dynamic_action(action: str):
    if action == "backup":
        return control_panel_backup()
    if action == "open-data-folder":
        return open_data_folder()
    if action == "open-backups-folder":
        return open_backups_folder()
    if action == "restart":
        return control_panel_restart()
    return {"ok": False, "error": f"Action {action} is not configured in source development mode"}
