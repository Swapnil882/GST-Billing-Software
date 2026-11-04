import os
import sys
import socket
import webbrowser
from pathlib import Path
import uvicorn

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

def is_already_running(port: int) -> bool:
    """Check if the GST Billing FastAPI server is already running on this port."""
    if not is_port_in_use(port):
        return False
    import urllib.request
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/profile")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False

def main():
    preferred = get_preferred_port()
    
    # Check if existing instance is already running
    if is_already_running(preferred):
        url = f"http://127.0.0.1:{preferred}"
        print(f"\n========================================================")
        print(f"  Free GST Billing Software is already running!")
        print(f"  URL:       {url}")
        print(f"  API Docs:  {url}/docs")
        print(f"========================================================\n")
        if "--open" in sys.argv:
            print("Opening application in your default browser...")
            webbrowser.open(url)
        return

    port = find_open_port(preferred)
    
    # Persist active port for frontend proxy & launchers
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        PORT_FILE.write_text(str(port))
    except Exception:
        pass
        
    url = f"http://{APP_HOST}:{port}"
    print(f"\n========================================================")
    print(f"  {APP_NAME} - FastAPI Backend")
    print(f"  Listening on: {url}")
    print(f"  API Docs:     {url}/docs")
    print(f"  Data folder:  {DATA_DIR}")
    print(f"========================================================\n")
    
    if "--open" in sys.argv or (AUTO_OPEN_BROWSER and "--no-open" not in sys.argv):
        webbrowser.open(url)
        
    uvicorn.run(
        "backend.app.main:app",
        host=APP_HOST,
        port=port,
        reload=False,
        log_level=LOG_LEVEL
    )

if __name__ == "__main__":
    main()
