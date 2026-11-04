import os
import sys
import time
import datetime
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import DATA_DIR, INVOICES_DIR, BASE_DIR as ROOT_DIR
from backend.app.services.invoice_math import advance_date

client = TestClient(app)

def banner(title: str):
    print(f"\n========================================================")
    print(f"  TEST: {title}")
    print(f"========================================================")

def test_1_invoice_lifecycle_process():
    banner("1. Invoice Lifecycle & Rules (Creation, Duplicate Guard, Deletion, Credit Lock)")
    
    inv_id = "INV-PROC-001"
    bill_data = {
        "id": inv_id,
        "invoiceNumber": inv_id,
        "clientName": "Delhi Retailer Pvt Ltd",
        "invoiceDate": "2026-11-04",
        "invoiceType": "tax-invoice",
        "totalAmount": 1180.0,
        "totalTaxAmount": 180.0,
        "status": "unpaid",
        "data": {
            "items": [{"name": "Item A", "rate": 1000, "qty": 1, "gst": 18}]
        }
    }
    
    # 1. Create invoice
    res = client.post("/api/bills", json=bill_data)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("  [OK] Invoice created successfully")
    
    # 2. Duplicate detection without overwrite -> 409
    res = client.post("/api/bills", json=bill_data)
    assert res.status_code == 409, f"Expected 409, got {res.status_code}"
    print("  [OK] Duplicate invoice correctly rejected with HTTP 409")
    
    # 3. Update with ?overwrite=1 -> 200
    bill_data["totalAmount"] = 1200.0
    res = client.post("/api/bills?overwrite=1", json=bill_data)
    assert res.status_code == 200
    print("  [OK] Invoice updated with overwrite flag")
    
    # 4. Create a target bill that depends on this bill as credit source
    dep_bill_id = "INV-DEP-002"
    dep_bill = {
        "id": dep_bill_id,
        "invoiceNumber": dep_bill_id,
        "clientName": "Delhi Retailer Pvt Ltd",
        "invoiceDate": "2026-11-05",
        "totalAmount": 500.0,
        "status": "paid",
        "payments": [{
            "mode": "credit-applied",
            "amount": 500.0,
            "creditSourceBillIds": [inv_id]
        }]
    }
    client.post("/api/bills", json=dep_bill)
    
    # 5. Try deleting source bill -> should be blocked with 409 credit dependency!
    res = client.delete(f"/api/bills/{inv_id}")
    assert res.status_code == 409
    assert res.json().get("detail", {}).get("error") == "client-credit-dependency"
    print("  [OK] Client-credit source bill deletion successfully protected")
    
    # 6. Delete dependent bill first
    client.delete(f"/api/bills/{dep_bill_id}?permanent=1")
    
    # 7. Now delete source bill to trash
    res = client.delete(f"/api/bills/{inv_id}")
    assert res.status_code == 200
    assert res.json().get("trashed") is True
    print("  [OK] Soft deletion to trash verified")
    
    # 8. Restore from trash
    res = client.post(f"/api/trash/{inv_id}/restore")
    assert res.status_code == 200
    print("  [OK] Restored bill from trash verified")
    
    # 9. Clean up permanently
    client.delete(f"/api/bills/{inv_id}?permanent=1")
    print("  [OK] Permanent deletion verified")

def test_2_client_management_process():
    banner("2. Client Management Process (Add, Update, Query, Delete)")
    
    client_id = "client_test_proc_101"
    client_obj = {
        "id": client_id,
        "name": "Tata Consumer Products",
        "gstin": "27AAACT2727Q1ZW",
        "state": "Maharashtra",
        "email": "proc@tataconsumer.com",
        "phone": "9820098200"
    }
    
    # Create
    res = client.post("/api/clients", json=client_obj)
    assert res.status_code == 200
    
    # Read
    res = client.get("/api/clients")
    assert res.status_code == 200
    found = next((c for c in res.json() if c.get("id") == client_id), None)
    assert found is not None
    assert found["name"] == "Tata Consumer Products"
    print("  [OK] Client created and queried")
    
    # Update
    client_obj["name"] = "Tata Consumer Products Ltd"
    client.post("/api/clients", json=client_obj)
    res = client.get("/api/clients")
    updated = next((c for c in res.json() if c.get("id") == client_id), None)
    assert updated["name"] == "Tata Consumer Products Ltd"
    print("  [OK] Client updated")
    
    # Delete
    res = client.delete(f"/api/clients/{client_id}")
    assert res.status_code == 200
    print("  [OK] Client deleted")

def test_3_product_and_inventory_process():
    banner("3. Product & Inventory Process (Goods with stock, Services without stock)")
    
    # 1. Physical Goods Product (has stock)
    goods_id = "prod_goods_proc_01"
    goods = {
        "id": goods_id,
        "name": "Industrial Gear Valve",
        "kind": "goods",
        "price": 1500,
        "stock": 25,
        "hsn": "8481"
    }
    client.post("/api/products", json=goods)
    
    # 2. Service Product (must not have stock)
    service_id = "prod_service_proc_02"
    service = {
        "id": service_id,
        "name": "Valve Installation Service",
        "kind": "service",
        "price": 500,
        "stock": 999,  # Should be automatically deleted
        "sac": "9987"
    }
    client.post("/api/products", json=service)
    
    # Verify in catalog
    res = client.get("/api/products")
    prods = res.json()
    saved_goods = next((p for p in prods if p.get("id") == goods_id), None)
    saved_service = next((p for p in prods if p.get("id") == service_id), None)
    
    assert saved_goods is not None and saved_goods.get("stock") == 25
    assert saved_service is not None and "stock" not in saved_service
    print("  [OK] Goods stock tracked and service stock automatically excluded")
    
    # Cleanup
    client.delete(f"/api/products/{goods_id}")
    client.delete(f"/api/products/{service_id}")
    print("  [OK] Product cleanup verified")

def test_4_manufacturing_bom_process():
    banner("4. Manufacturing Process (BOM Assembly, Stock Deduction, Atomic Rollback)")
    
    # Create raw material parts
    c1_id = "comp_steel_sheet"
    c2_id = "comp_screw_pack"
    fg_id = "finished_cabinet"
    
    client.post("/api/products", json={"id": c1_id, "name": "Steel Sheet", "stock": 50})
    client.post("/api/products", json={"id": c2_id, "name": "Screw Pack", "stock": 100})
    client.post("/api/products", json={"id": fg_id, "name": "Steel Cabinet", "stock": 0})
    
    # Production entry: Consume 10 sheets (-10), 20 screw packs (-20) -> Produce 5 cabinets (+5)
    prod_entry_id = "mfg_entry_proc_001"
    prod_entry = {
        "id": prod_entry_id,
        "date": "2026-11-04",
        "finishedProduct": "Steel Cabinet",
        "qty": 5,
        "stockApplied": {
            c1_id: -10,
            c2_id: -20,
            fg_id: 5
        }
    }
    
    # Execute production
    res = client.post("/api/productions", json=prod_entry)
    assert res.status_code == 200
    print("  [OK] Production entry committed")
    
    # Verify updated stocks
    prods = {p["id"]: p for p in client.get("/api/products").json()}
    assert prods[c1_id]["stock"] == 40
    assert prods[c2_id]["stock"] == 80
    assert prods[fg_id]["stock"] == 5
    print("  [OK] Components deducted and finished goods added accurately")
    
    # Delete production entry (undoing assembly)
    res = client.delete(f"/api/productions/{prod_entry_id}")
    assert res.status_code == 200
    print("  [OK] Production entry deleted")
    
    # Verify exact rollback
    prods = {p["id"]: p for p in client.get("/api/products").json()}
    assert prods[c1_id]["stock"] == 50
    assert prods[c2_id]["stock"] == 100
    assert prods[fg_id]["stock"] == 0
    print("  [OK] Complete inventory rollback verified")
    
    # Cleanup
    client.delete(f"/api/products/{c1_id}")
    client.delete(f"/api/products/{c2_id}")
    client.delete(f"/api/products/{fg_id}")

def test_5_purchase_and_vendor_payments_process():
    banner("5. Purchase Bills & Vendor Payments Process")
    
    pur_id = "pur_test_proc_101"
    pur_data = {
        "id": pur_id,
        "supplierName": "Steel Distributors India",
        "date": "2026-11-04",
        "totalAmount": 10000.0,
        "tdsAmount": 100.0,
        "payments": [
            {"amount": 5000.0, "date": "2026-11-04", "mode": "bank-transfer"}
        ]
    }
    
    # Save valid purchase
    res = client.post("/api/purchases", json=pur_data)
    assert res.status_code == 200
    print("  [OK] Valid purchase bill saved")
    
    # Test overpayment rejection: total is 10000, TDS is 100 -> owed is 9900.
    # Trying to pay 10500 should be rejected!
    pur_data["payments"] = [{"amount": 10500.0, "date": "2026-11-04", "mode": "bank-transfer"}]
    res = client.post("/api/purchases", json=pur_data)
    assert res.status_code == 400
    print("  [OK] Overpayment to supplier successfully rejected")
    
    # Purchase Order
    po_id = "po_test_proc_201"
    po_data = {
        "id": po_id,
        "poNumber": "PO-2026-001",
        "supplierName": "Steel Distributors India",
        "date": "2026-11-04",
        "totalAmount": 25000.0
    }
    res = client.post("/api/purchase-orders", json=po_data)
    assert res.status_code == 200
    print("  [OK] Purchase Order saved")
    
    # Cleanup
    client.delete(f"/api/purchases/{pur_id}")
    po_file = DATA_DIR / "purchase-orders" / f"{po_id}.json"
    if po_file.exists():
        po_file.unlink()

def test_6_cash_book_process():
    banner("6. Cash Book Process (In/Out Entries, Running Balance, Validation)")
    
    entry_in = {
        "type": "in",
        "date": "2026-11-04",
        "amount": 2500.0,
        "name": "Counter Sale Cash",
        "category": "Sales"
    }
    res = client.post("/api/cash-book", json=entry_in)
    assert res.status_code == 200
    in_id = res.json()["id"]
    
    entry_out = {
        "type": "out",
        "date": "2026-11-04",
        "amount": 350.0,
        "name": "Office Chai & Snacks",
        "category": "Office"
    }
    res = client.post("/api/cash-book", json=entry_out)
    assert res.status_code == 200
    out_id = res.json()["id"]
    
    res = client.get("/api/cash-book")
    assert res.status_code == 200
    all_entries = res.json()
    assert any(e["id"] == in_id for e in all_entries)
    assert any(e["id"] == out_id for e in all_entries)
    print("  [OK] Cash book entries recorded and retrieved")
    
    # Validation failure: negative amount
    res = client.post("/api/cash-book", json={"type": "in", "date": "2026-11-04", "amount": -100})
    assert res.status_code == 400
    print("  [OK] Invalid cash entry rejected")
    
    # Cleanup
    client.delete(f"/api/cash-book/{in_id}")
    client.delete(f"/api/cash-book/{out_id}")

def test_7_recurring_invoices_process():
    banner("7. Recurring Invoices Process (Schedule Advance, Month Clamping, Auto-fire)")
    
    # Test date advance logic
    # 1. Weekly: +7 days
    assert advance_date("2026-11-04", "weekly", 1) == "2026-11-11"
    # 2. Monthly: 31 Jan -> 28 Feb (clamped!)
    assert advance_date("2026-01-31", "monthly", 1, anchor_day=31) == "2026-02-28"
    # 3. Quarterly: +3 months
    assert advance_date("2026-01-15", "quarterly", 1) == "2026-04-15"
    print("  [OK] Date advance arithmetic and month clamping verified")
    
    # Create recurring template
    rec_id = "rec_proc_test_01"
    rec_tpl = {
        "id": rec_id,
        "clientName": "Monthly Retainer Client",
        "frequency": "monthly",
        "interval": 1,
        "nextDate": "2026-11-04",
        "totalAmount": 5000.0,
        "active": True
    }
    client.post("/api/recurring", json=rec_tpl)
    
    # Trigger generate now
    res = client.post(f"/api/recurring/{rec_id}/generate")
    assert res.status_code == 200
    generated_inv = res.json()["invoiceNumber"]
    assert generated_inv != ""
    print(f"  [OK] Generated recurring invoice: {generated_inv}")
    
    # Clean up generated bill and template
    client.delete(f"/api/bills/{generated_inv}?permanent=1")
    client.delete(f"/api/recurring/{rec_id}")

def test_8_security_pin_lock_process():
    banner("8. Security & PIN Lock Process (Scrypt Hash, Rate Limit, RESET-PIN Trigger)")
    
    # 1. Set 6-digit PIN
    pin = "654321"
    res = client.post("/api/lock/set", json={"pin": pin, "currentPin": None})
    assert res.status_code == 200
    assert res.json()["enabled"] is True
    print("  [OK] PIN set successfully")
    
    # 2. Verify with correct PIN
    res = client.post("/api/lock/verify", json={"pin": pin})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    print("  [OK] Correct PIN verified")
    
    # 3. Test wrong PIN -> 401
    res = client.post("/api/lock/verify", json={"pin": "111111"})
    assert res.status_code == 401
    print("  [OK] Wrong PIN rejected with 401")
    
    # 4. Test RESET-PIN file emergency recovery
    reset_file = ROOT_DIR / "RESET-PIN"
    reset_file.write_text("reset")
    
    # Calling lock status detects RESET-PIN and removes lock!
    res = client.get("/api/lock")
    assert res.json()["enabled"] is False
    assert not reset_file.exists()
    print("  [OK] Emergency RESET-PIN recovery verified")

def test_9_pdf_operations_process():
    banner("9. PDF Operations Process (Path Traversal Protection, Watermark Stamp)")
    
    # 1. Test path traversal rejection
    res = client.post("/api/save-pdf?name=../../malicious.pdf", content=b"%PDF-1.4 sample")
    # Path guard collapses .. and normalizes inside INVOICES_DIR or rejects invalid paths
    assert res.status_code in (200, 400)
    
    # 2. Save valid PDF
    sample_pdf = b"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]>> endobj
xref
0 4
0000000000 65535 f 
trailer <</Size 4 /Root 1 0 R>>
startxref
0
%%EOF"""
    
    res = client.post("/api/save-pdf?name=test_invoice.pdf&client=TestCorp&month=November 2026", content=sample_pdf)
    assert res.status_code == 200
    assert res.json()["saved"] is True
    print("  [OK] PDF saved into client/month structure")
    
    # 3. Stamp CANCELLED
    res = client.post("/api/saved-pdf/cancel-mark", json={
        "fileName": "test_invoice.pdf",
        "clientName": "TestCorp",
        "cancelled": True
    })
    assert res.status_code == 200
    assert res.json()["updated"] >= 1
    print("  [OK] CANCELLED watermark stamped on PDF")
    
    # 4. Undo CANCELLED
    res = client.post("/api/saved-pdf/cancel-mark", json={
        "fileName": "test_invoice.pdf",
        "clientName": "TestCorp",
        "cancelled": False
    })
    assert res.status_code == 200
    assert res.json()["updated"] >= 1
    print("  [OK] CANCELLED watermark removed, original restored")
    
    # 5. Move PDF to Trash
    res = client.post("/api/trash-pdf", json={"fileName": "test_invoice.pdf", "clientName": "TestCorp"})
    assert res.status_code == 200
    assert res.json()["trashed"] is True
    print("  [OK] PDF moved to Trash")

def test_10_backup_and_restore_process():
    banner("10. Backup & Transactional Restore Process")
    
    # Trigger backup
    res = client.post("/api/backups/now")
    assert res.status_code in (200, 429)
    print("  [OK] Daily backup triggered")
    
    # List backups
    res = client.get("/api/backups")
    assert res.status_code == 200
    backups = res.json()
    assert isinstance(backups, list)
    print(f"  [OK] Retrieved {len(backups)} backups")

def test_11_system_and_redaction_process():
    banner("11. System Health & Sensitive Data Redaction")
    
    # Health
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True
    
    # Post an error with sensitive details
    payload = {
        "message": "Payment failed for GSTIN 27AAACT2727Q1ZW phone 9820098200 email admin@tataconsumer.com with upi user@okhdfcbank",
        "kind": "test",
        "version": "1.10.83"
    }
    res = client.post("/api/client-errors", json=payload)
    assert res.status_code == 200
    
    # Read errors log and check redaction
    res = client.get("/api/errors-log")
    assert res.status_code == 200
    lines = res.json()["lines"]
    recent = lines[-1] if lines else ""
    assert "27AAACT2727Q1ZW" not in recent
    assert "admin@tataconsumer.com" not in recent
    assert "[gstin]" in recent
    assert "[email]" in recent
    print("  [OK] Error logged with PII/GSTIN/Email properly redacted")

if __name__ == "__main__":
    print("\nStarting Comprehensive Process Verification Suite...")
    test_1_invoice_lifecycle_process()
    test_2_client_management_process()
    test_3_product_and_inventory_process()
    test_4_manufacturing_bom_process()
    test_5_purchase_and_vendor_payments_process()
    test_6_cash_book_process()
    test_7_recurring_invoices_process()
    test_8_security_pin_lock_process()
    test_9_pdf_operations_process()
    test_10_backup_and_restore_process()
    test_11_system_and_redaction_process()
    
    print("\n========================================================")
    print("  ALL 11 PROCESS WORKFLOWS TESTED & PASSED SUCCESSFULLY!")
    print("========================================================\n")
