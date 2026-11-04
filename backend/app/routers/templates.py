import time
import secrets
from fastapi import APIRouter
from backend.app.config import DATA_DIR
from backend.app.core.storage import read_all_from_dir, write_json_atomic, delete_file
from backend.app.core.path_guard import safe_file_name

router = APIRouter(prefix="/api/templates", tags=["templates"])

DEFAULT_TERMS = {
    'id': 'default',
    'name': 'Standard Terms',
    'content': (
        "1. Payment is due within 15 days of invoice date unless otherwise agreed in writing.\n"
        "2. Interest @ 18% p.a. will be charged on overdue payments beyond the due date.\n"
        "3. The scope of work is limited to what is explicitly mentioned in the project proposal/agreement.\n"
        "4. All intellectual property and source code will be transferred to the client only upon receipt of full payment.\n"
        "5. We shall not be liable for any delays caused by incomplete or late submission of content, credentials, or approvals.\n"
        "6. Any change requests after project approval may attract additional charges and revised timelines.\n"
        "7. This invoice is subject to the jurisdiction of courts at the service provider's registered location.\n"
        "8. E. & O.E."
    )
}

@router.get("")
def get_templates():
    templates = read_all_from_dir("templates")
    if not templates:
        file_path = DATA_DIR / "templates" / "default.json"
        write_json_atomic(file_path, DEFAULT_TERMS)
        templates = [DEFAULT_TERMS]
    templates.sort(key=lambda t: str(t.get("name") or "").lower())
    return templates

@router.post("")
def save_template(tpl: dict):
    if not tpl.get("id"):
        tpl["id"] = f"tpl_{int(time.time() * 1000)}{secrets.token_hex(3)}"
    file_path = DATA_DIR / "templates" / f"{safe_file_name(tpl['id'])}.json"
    write_json_atomic(file_path, tpl)
    return {"success": True, "id": tpl["id"]}

@router.delete("/{template_id}")
def delete_template(template_id: str):
    file_path = DATA_DIR / "templates" / f"{safe_file_name(template_id)}.json"
    delete_file(file_path)
    return {"success": True}
