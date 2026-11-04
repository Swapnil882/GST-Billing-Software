import time
import secrets
from fastapi import APIRouter, HTTPException
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name, is_path_inside

router = APIRouter(tags=["purchases"])
PURCHASES_DIR = DATA_DIR / "purchases"
PO_DIR = DATA_DIR / "purchase-orders"

def validate_purchase_payments(p: dict) -> str:
    payments = p.get("payments")
    if payments is None:
        return ""
    if not isinstance(payments, list):
        return "Invalid payments"
    total_paid = 0.0
    for x in payments:
        if not isinstance(x, dict):
            return "Invalid payment"
        try:
            amt = float(x.get("amount") or 0.0)
            if amt <= 0:
                return "Enter an amount more than 0"
            if amt > 1e11:
                return "The amount is too large"
            total_paid += amt
        except (ValueError, TypeError):
            return "Enter an amount more than 0"
        if not x.get("date"):
            return "Enter the payment date"
            
    total_bill = float(p.get("totalAmount") or 0.0)
    tds = float(p.get("tdsAmount") or 0.0)
    owed = max(0.0, total_bill - tds)
    if total_paid > owed + 1.0:
        return f"Payments of {total_paid:.2f} are more than the {owed:.2f} this bill comes to"
    return ""

@router.get("/api/purchases")
def get_purchases():
    purchases = read_all_from_dir("purchases")
    purchases.sort(key=lambda p: str(p.get("date") or ""), reverse=True)
    return purchases

@router.post("/api/purchases")
def save_purchase(purchase: dict):
    if not isinstance(purchase, dict):
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
    problem = validate_purchase_payments(purchase)
    if problem:
        raise HTTPException(status_code=400, detail={"error": problem, "code": "bad-request"})
        
    if not purchase.get("id"):
        purchase["id"] = f"pur_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    file_path = PURCHASES_DIR / f"{safe_file_name(purchase['id'])}.json"
    write_json_atomic(file_path, purchase)
    return {"success": True, "id": purchase["id"]}

@router.delete("/api/purchases/{purchase_id}")
def delete_purchase(purchase_id: str):
    file_path = PURCHASES_DIR / f"{safe_file_name(purchase_id)}.json"
    delete_file(file_path)
    return {"success": True}

@router.get("/api/purchase-orders")
def get_purchase_orders():
    orders = read_all_from_dir("purchase-orders")
    orders.sort(key=lambda o: (str(o.get("date") or ""), str(o.get("poNumber") or "")), reverse=True)
    return orders

@router.post("/api/purchase-orders")
def save_purchase_order(order: dict):
    if not isinstance(order, dict):
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
    if not order.get("id"):
        order["id"] = f"po_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    file_path = PO_DIR / f"{safe_file_name(order['id'])}.json"
    if not is_path_inside(file_path, PO_DIR):
        raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
    write_json_atomic(file_path, order)
    return {"success": True, "id": order["id"]}
