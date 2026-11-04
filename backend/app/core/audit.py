import json
import logging
from datetime import datetime
from pathlib import Path
from backend.app.config import DATA_DIR
from backend.app.db.session import SessionLocal, is_db_connected
from backend.app.db.models import AuditLogRecord

logger = logging.getLogger("uvicorn.error")
AUDIT_LOG_FILE = DATA_DIR / "audit_trail.jsonl"

def log_audit(
    entity_type: str,
    entity_id: str,
    action: str,
    change_summary: str | None = None,
    previous_state: dict | None = None,
    new_state: dict | None = None,
    user_identifier: str = "system",
    ip_address: str | None = None,
):
    """
    MCA Audit Trail Logger (Rule 3(1) of Companies Accounts Rules 2014 / 2023 amendment).
    Records every financial/master change into both PostgreSQL audit_logs and local audit_trail.jsonl.
    """
    now = datetime.utcnow()
    iso_time = now.isoformat() + "Z"

    # 1. Append to local immutable jsonl file
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "timestamp": iso_time,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "action": action.upper(),
            "user_identifier": user_identifier,
            "ip_address": ip_address,
            "change_summary": change_summary,
            "previous_state": previous_state,
            "new_state": new_state,
        }
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"[Audit] Failed to append to audit log file: {e}")

    # 2. Record in PostgreSQL if connected
    if is_db_connected() and SessionLocal:
        try:
            db = SessionLocal()
            try:
                record = AuditLogRecord(
                    entity_type=entity_type,
                    entity_id=str(entity_id),
                    action=action.upper(),
                    user_identifier=user_identifier,
                    ip_address=ip_address,
                    change_summary=change_summary,
                    previous_state=previous_state,
                    new_state=new_state,
                    timestamp=now,
                )
                db.add(record)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"[Audit] Failed to commit audit record to DB: {e}")
