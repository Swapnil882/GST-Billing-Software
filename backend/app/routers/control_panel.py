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
