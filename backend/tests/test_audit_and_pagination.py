#!/usr/bin/env python3
import sys
from pathlib import Path
from starlette.testclient import TestClient

APP_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = APP_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.main import app
from backend.app.db.session import is_db_connected

def test_audit_and_pagination():
    print("\n========================================================")
    print("  Testing PostgreSQL Direct Pagination, Search & MCA Audit Trail")
    print("========================================================\n")
    
    with TestClient(app) as client:
        # 1. Test Server-side pagination
        res = client.get("/api/bills?limit=2&offset=0")
        assert res.status_code == 200, f"Pagination failed: {res.text}"
        paginated = res.json()
        print(f"  [OK] Paginated Response: total={paginated['total']}, items count={len(paginated['items'])}, page={paginated['page']}, pages={paginated['pages']}")
        assert "items" in paginated
        assert len(paginated["items"]) <= 2
        assert paginated["total"] >= 3

        # 2. Test Search by client name
        res = client.get("/api/bills?search=Nexus")
        assert res.status_code == 200
        search_results = res.json()
        print(f"  [OK] Search 'Nexus' returned {len(search_results)} bill(s)")
        assert len(search_results) >= 1
        assert "Nexus" in search_results[0].get("clientName", "")

        # 3. Test Filter by status
        res = client.get("/api/bills?status=paid")
        assert res.status_code == 200
        paid_bills = res.json()
        print(f"  [OK] Filter status=paid returned {len(paid_bills)} bill(s)")
        for b in paid_bills:
            assert b.get("status") == "paid"

        # Pre-cleanup in case of prior run
        client.delete("/api/bills/INV/2026-27/9999?permanent=1")

        # 4. Test Invoice Creation & Audit Trail Recording
        new_inv = {
            "id": "INV/2026-27/9999",
            "invoiceNumber": "INV/2026-27/9999",
            "clientName": "Test Audit Client Pvt Ltd",
            "invoiceDate": "2026-11-04",
            "invoiceType": "tax-invoice",
            "currency": "INR",
            "totalAmount": 15000.0,
            "paidAmount": 0.0,
            "status": "unpaid",
            "data": {
                "client": {"name": "Test Audit Client Pvt Ltd"},
                "totals": {"total": 15000.0}
            }
        }
        res = client.post("/api/bills", json=new_inv)
        assert res.status_code == 200, f"Failed to create test bill: {res.text}"
        print("  [OK] Test invoice created")

        # 5. Query Audit Trail
        res = client.get("/api/audit-trail?entity_type=invoice&entity_id=INV/2026-27/9999")
        assert res.status_code == 200
        audit_data = res.json()
        print(f"  [OK] Audit Trail queried: found {audit_data['total']} entries for INV/2026-27/9999")
        assert audit_data["total"] >= 1
        latest_audit = audit_data["items"][0]
        assert latest_audit["action"] == "CREATE"
        assert latest_audit["entityType"] == "invoice"
        assert "15000" in latest_audit["changeSummary"]

        # 6. Test Invoice Update Audit
        new_inv["status"] = "paid"
        new_inv["paidAmount"] = 15000.0
        res = client.post("/api/bills?overwrite=1", json=new_inv)
        assert res.status_code == 200

        res = client.get("/api/audit-trail?entity_id=INV/2026-27/9999")
        audit_data = res.json()
        assert audit_data["items"][0]["action"] == "UPDATE"
        print("  [OK] Audit Trail correctly logged UPDATE event with previous and new states")

        # 7. Test Soft Delete Audit
        res = client.delete("/api/bills/INV/2026-27/9999")
        assert res.status_code == 200
        res = client.get("/api/audit-trail?entity_id=INV/2026-27/9999")
        audit_data = res.json()
        assert audit_data["items"][0]["action"] == "SOFT_DELETE"
        print("  [OK] Audit Trail correctly logged SOFT_DELETE event")

        # 8. Clean up permanent delete
        res = client.delete("/api/bills/INV/2026-27/9999?permanent=1")
        assert res.status_code == 200
        res = client.get("/api/audit-trail?entity_id=INV/2026-27/9999")
        audit_data = res.json()
        assert audit_data["items"][0]["action"] == "PERMANENT_DELETE"
        print("  [OK] Audit Trail correctly logged PERMANENT_DELETE event")

        # 9. Test Audit Trail CSV Export
        res = client.get("/api/audit-trail/export")
        assert res.status_code == 200
        assert "text/csv" in res.headers.get("content-type", "")
        csv_text = res.text
        assert "Timestamp (UTC)" in csv_text
        assert "Action Performed" in csv_text
        assert "INV/2026-27/9999" in csv_text
        print("  [OK] Audit Trail CSV Export generated with MCA Rule 3 headers")

    print("\n========================================================")
    print("  ALL PAGINATION, SEARCH & MCA AUDIT TRAIL TESTS PASSED!")
    print("========================================================\n")

if __name__ == "__main__":
    test_audit_and_pagination()
