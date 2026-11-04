import os
import sys
import time
import socket
import subprocess
import threading
import webbrowser
from pathlib import Path
import uvicorn

# Force unbuffered output so live logs stream to console immediately
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass

# Setup path so `backend` package can be imported
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.config import (
    DATA_DIR,
    PORT_FILE,
    DEFAULT_PORT,
    APP_HOST,
    AUTO_OPEN_BROWSER,
    LOG_LEVEL,
    APP_NAME,
)

PID_FILE = DATA_DIR / "server.pid"

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a service is actively listening on this port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            return s.connect_ex((host, port)) == 0
        except Exception:
            return False

def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if we can bind exclusively to this port."""
    if is_port_in_use(port, host):
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            s.bind((host, port))
            return True
        except OSError:
            return False

def kill_process_on_port(port: int):
    """Terminate stale or background processes on this port so the foreground terminal takes over."""
    # 1. Check PID_FILE
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text().strip())
            if old_pid != os.getpid():
                if sys.platform.startswith("win"):
                    subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    os.kill(old_pid, 9)
        except Exception:
            pass

    # 2. Check listening PID via netstat on Windows
    if sys.platform.startswith("win") and is_port_in_use(port):
        try:
            cmd = f'netstat -ano | findstr :{port}'
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
            for line in out.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5 and "LISTENING" in parts:
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) != os.getpid():
                        subprocess.run(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def find_open_port(starting_port: int, max_scan: int = 50) -> int:
    for port in range(starting_port, starting_port + max_scan):
        if is_port_available(port):
            return port
    return starting_port

def get_preferred_port() -> int:
    if PORT_FILE.exists():
        try:
            p = int(PORT_FILE.read_text().strip())
            if 1024 <= p <= 65535:
                return p
        except Exception:
            pass
    return DEFAULT_PORT

def main():
    preferred = get_preferred_port()
    
    # If the preferred port is currently occupied by a previous/background instance,
    # release it so this terminal session becomes the foreground server with live logs.
    if is_port_in_use(preferred):
        print(f"[Server] Port {preferred} was held by a previous background instance.")
        print(f"[Server] Terminating previous process to stream live logs in this terminal...")
        kill_process_on_port(preferred)
        time.sleep(1.0)

    port = preferred if is_port_available(preferred) else find_open_port(preferred)
    
    # Persist active port & PID for frontends and process tracking
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        PORT_FILE.write_text(str(port))
    except Exception:
        pass
    try:
        PID_FILE.write_text(str(os.getpid()))
    except Exception:
        pass
        
    url = f"http://{APP_HOST}:{port}"
    print(f"\n========================================================")
    print(f"  {APP_NAME} - FastAPI Backend")
    print(f"  Listening on:   {url}")
    print(f"  API Docs:       {url}/docs")
    print(f"  Data folder:    {DATA_DIR}")
    print(f"  Process PID:    {os.getpid()}")
    print(f"  Status:         Active & Streaming Logs Below (Ctrl+C to stop)")
    print(f"========================================================\n")
    
    if "--open" in sys.argv or (AUTO_OPEN_BROWSER and "--no-open" not in sys.argv):
        # Open browser in a separate thread after giving uvicorn a moment to bind
        def _open():
            time.sleep(1.0)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()
        
    try:
        uvicorn.run(
            "backend.app.main:app",
            host=APP_HOST,
            port=port,
            reload=False,
            log_level=LOG_LEVEL,
            access_log=True,
        )
    except KeyboardInterrupt:
        print("\n[Server] Shutdown requested by user (Ctrl+C). Exiting cleanly...")
    finally:
        try:
            if PID_FILE.exists():
                PID_FILE.unlink()
        except Exception:
            pass

if __name__ == "__main__":
    main()
