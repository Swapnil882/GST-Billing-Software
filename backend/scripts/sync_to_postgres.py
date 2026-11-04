#!/usr/bin/env python3
import sys
from pathlib import Path

# Setup path
APP_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = APP_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.db.session import init_db, is_db_connected
from backend.app.db.sync_service import sync_all_json_to_db

def main():
    print("\n========================================================")
    print("  Connecting to PostgreSQL...")
    print("========================================================")
    
    if not is_db_connected():
        print("[FAIL] Could not connect to PostgreSQL. Please check your credentials in .env")
        sys.exit(1)
        
    print("[OK] Connected to PostgreSQL successfully!")
    print("Initializing tables...")
    init_db()
    
    print("Syncing all existing data (Invoices, Clients, Products, Cash Book, etc.) into PostgreSQL...")
    res = sync_all_json_to_db()
    
    if res.get("synced"):
        print("[OK] All data successfully synced into PostgreSQL!")
        for k, v in res.get("counts", {}).items():
            print(f"  - {k.capitalize()}: {v} records")
    else:
        print(f"[FAIL] Sync failed: {res.get('reason')}")
        
    print("\n========================================================")
    print("  PostgreSQL Connection & Sync Complete!")
    print("========================================================\n")

if __name__ == "__main__":
    main()
