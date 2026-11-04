import time
import secrets
from fastapi import APIRouter
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

@router.get("")
def get_expenses():
    expenses = read_all_from_dir("expenses")
    expenses.sort(key=lambda e: str(e.get("date") or ""), reverse=True)
    return expenses

@router.post("")
def save_expense(expense: dict):
    if not expense.get("id"):
        expense["id"] = f"exp_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    file_path = DATA_DIR / "expenses" / f"{safe_file_name(expense['id'])}.json"
    write_json_atomic(file_path, expense)
    return {"success": True, "id": expense["id"]}

@router.delete("/{expense_id}")
def delete_expense(expense_id: str):
    file_path = DATA_DIR / "expenses" / f"{safe_file_name(expense_id)}.json"
    delete_file(file_path)
    return {"success": True}
