#!/usr/bin/env python3
"""
Free GST Billing Software - Unified Launcher
Builds frontend (if needed) and launches FastAPI backend.
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"

def ensure_frontend_built():
    index_file = FRONTEND_DIST / "index.html"
    if not index_file.exists():
        print("Frontend build not found. Building frontend now...")
        npm_cmd = "npm.cmd" if sys.platform.startswith("win") else "npm"
        try:
            subprocess.run([npm_cmd, "run", "build"], cwd=str(FRONTEND_DIR), check=True)
            print("Frontend built successfully!")
        except Exception as e:
            print(f"Warning: Failed to auto-build frontend ({e}). Continuing with server...")

def main():
    ensure_frontend_built()
    
    # Add root to sys.path
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
        
    from backend.run import main as backend_main
    # Forward arguments or add --open if none provided
    if len(sys.argv) == 1:
        sys.argv.append("--open")
    backend_main()

if __name__ == "__main__":
    main()
