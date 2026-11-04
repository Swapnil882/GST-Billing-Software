from fastapi import APIRouter, HTTPException
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name

router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.get("")
def get_clients():
    return read_all_from_dir("clients")

@router.post("")
def save_client(client: dict):
    if not client or not client.get("id"):
        raise HTTPException(status_code=400, detail={"error": "Client must have an id"})
    file_path = DATA_DIR / "clients" / f"{safe_file_name(client['id'])}.json"
    write_json_atomic(file_path, client)
    return {"success": True}

@router.delete("/{client_id}")
def delete_client(client_id: str):
    file_path = DATA_DIR / "clients" / f"{safe_file_name(client_id)}.json"
    delete_file(file_path)
    return {"success": True}
