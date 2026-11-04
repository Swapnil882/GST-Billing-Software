import time
import secrets
from fastapi import APIRouter
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("")
def get_products():
    products = read_all_from_dir("products")
    products.sort(key=lambda p: str(p.get("name") or "").lower())
    return products

@router.post("")
def save_product(product: dict):
    if not product.get("id"):
        product["id"] = f"prod_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    if product.get("kind") == "service" and "stock" in product:
        del product["stock"]
        
    file_path = DATA_DIR / "products" / f"{safe_file_name(product['id'])}.json"
    write_json_atomic(file_path, product)
    return {"success": True, "id": product["id"]}

@router.delete("/{product_id}")
def delete_product(product_id: str):
    file_path = DATA_DIR / "products" / f"{safe_file_name(product_id)}.json"
    delete_file(file_path)
    return {"success": True}
