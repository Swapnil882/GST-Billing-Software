#!/usr/bin/env python3
import sys
from pathlib import Path
import httpx

APP_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = APP_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.main import app
from backend.app.db.session import is_db_connected, SessionLocal
from backend.app.db.models import InvoiceRecord, ClientRecord, ProductRecord

def test_postgres_integration():
    print("\n========================================================")
    print("  Testing PostgreSQL Integration & Tables")
    print("========================================================")
    
    assert is_db_connected(), "PostgreSQL connection check failed!"
    print("  [OK] PostgreSQL database is connected and active.")
    
    db = SessionLocal()
    try:
        invoices_count = db.query(InvoiceRecord).count()
        clients_count = db.query(ClientRecord).count()
        products_count = db.query(ProductRecord).count()
        print(f"  [OK] PostgreSQL Invoices count: {invoices_count}")
        print(f"  [OK] PostgreSQL Clients count:  {clients_count}")
        print(f"  [OK] PostgreSQL Products count: {products_count}")
        assert invoices_count >= 1, "Expected at least 1 invoice in PostgreSQL"
    finally:
        db.close()
        
    from starlette.testclient import TestClient
    with TestClient(app) as client:
        res = client.get("/api/db/status")
        assert res.status_code == 200
        data = res.json()
        print(f"  [OK] /api/db/status: {data}")
        assert data["connected"] is True
        assert data["database"] == "GST-Billing"
        
    print("\n========================================================")
    print("  POSTGRESQL INTEGRATION TEST PASSED SUCCESSFULLY!")
    print("========================================================\n")

if __name__ == "__main__":
    test_postgres_integration()
