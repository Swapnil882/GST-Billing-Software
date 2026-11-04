import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "version" in data
    assert "uptimeSec" in data

def test_version():
    res = client.get("/api/version")
    assert res.status_code == 200
    assert "current" in res.json()

def test_profile():
    res = client.get("/api/profile")
    assert res.status_code == 200
    assert "businessName" in res.json()

def test_meta_counter():
    # Set
    res = client.post("/api/meta/testCounter", json={"value": 10})
    assert res.status_code == 200
    
    # Get
    res = client.get("/api/meta/testCounter")
    assert res.status_code == 200
    assert res.json()["value"] == 10
    
    # Increment
    res = client.post("/api/meta/testCounter/increment", json={"start": 1})
    assert res.status_code == 200
    assert res.json()["value"] == 11

def test_clients_crud():
    test_client = {"id": "test_client_001", "name": "Test Client Corp", "state": "Delhi"}
    res = client.post("/api/clients", json=test_client)
    assert res.status_code == 200
    
    res = client.get("/api/clients")
    assert res.status_code == 200
    found = any(c.get("id") == "test_client_001" for c in res.json())
    assert found is True
    
    # Clean up
    res = client.delete("/api/clients/test_client_001")
    assert res.status_code == 200

def test_products_crud():
    test_prod = {"id": "test_prod_001", "name": "Test Widget", "price": 250, "stock": 50}
    res = client.post("/api/products", json=test_prod)
    assert res.status_code == 200
    
    res = client.get("/api/products")
    assert res.status_code == 200
    found = any(p.get("id") == "test_prod_001" for p in res.json())
    assert found is True
    
    # Clean up
    res = client.delete("/api/products/test_prod_001")
    assert res.status_code == 200

def test_bills_crud_and_conflict():
    bill = {
        "id": "INV-TEST-001",
        "clientName": "Test Client",
        "invoiceNumber": "INV-TEST-001",
        "invoiceDate": "2026-11-04",
        "totalAmount": 1000.0,
        "status": "unpaid"
    }
    # Initial save
    res = client.post("/api/bills", json=bill)
    assert res.status_code == 200
    
    # Duplicate save without overwrite -> 409
    res = client.post("/api/bills", json=bill)
    assert res.status_code == 409
    
    # Duplicate save with overwrite -> 200
    res = client.post("/api/bills?overwrite=1", json=bill)
    assert res.status_code == 200
    
    # Soft delete
    res = client.delete("/api/bills/INV-TEST-001")
    assert res.status_code == 200
    assert res.json().get("trashed") is True
    
    # Clean from trash
    res = client.delete("/api/trash/INV-TEST-001")
    assert res.status_code == 200

def test_local_prefs():
    res = client.get("/api/local-prefs")
    assert res.status_code == 200
    assert "value" in res.json()
    
    res = client.post("/api/local-prefs", json={"set": {"test_pref": "hello"}, "remove": []})
    assert res.status_code == 200
    
    res = client.get("/api/local-prefs")
    assert res.json()["value"].get("test_pref") == "hello"
    
    # Clean up
    client.post("/api/local-prefs", json={"set": {}, "remove": ["test_pref"]})

def test_export():
    res = client.get("/api/export")
    assert res.status_code == 200
    data = res.json()
    assert "bills" in data
    assert "profile" in data
    assert "clients" in data
    assert "products" in data
    assert "meta" in data

def test_status_and_supporters():
    # /api/status alias
    res = client.get("/api/status")
    assert res.status_code == 200
    assert res.json()["ok"] is True

    # /api/supporters
    res = client.get("/api/supporters")
    assert res.status_code == 200
    data = res.json()
    assert "supporters" in data
    assert "goal" in data

def test_control_panel():
    res = client.get("/api/control-panel/status")
    assert res.status_code == 200
    assert "dataFolder" in res.json()

    res = client.post("/api/control-panel/backup")
    assert res.status_code == 200
    assert res.json()["ok"] is True

def test_spa_serving():
    res = client.get("/")
    assert res.status_code == 200
    # Should serve frontend/dist/index.html
    assert "<!doctype html>" in res.text.lower()

if __name__ == "__main__":
    print("Running API tests...")
    test_health()
    test_version()
    test_profile()
    test_status_and_supporters()
    test_control_panel()
    test_meta_counter()
    test_clients_crud()
    test_products_crud()
    test_bills_crud_and_conflict()
    test_local_prefs()
    test_export()
    test_spa_serving()
    print("ALL API TESTS PASSED SUCCESSFULLY! [OK]")
