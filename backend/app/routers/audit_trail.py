import io
import csv
import json
from datetime import datetime
from fastapi import APIRouter, Response, Query
from backend.app.config import DATA_DIR
from backend.app.core.audit import AUDIT_LOG_FILE
from backend.app.db.session import SessionLocal, is_db_connected
from backend.app.db.models import AuditLogRecord

router = APIRouter(prefix="/api/audit-trail", tags=["audit-trail"])

@router.get("")
def get_audit_trail(
    entity_type: str | None = None,
    entity_id: str | None = None,
    action: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Retrieve MCA Rule 3 compliant audit trail logs with filtering & pagination.
    """
    if is_db_connected() and SessionLocal:
        db = SessionLocal()
        try:
            query = db.query(AuditLogRecord)
            if entity_type:
                query = query.filter(AuditLogRecord.entity_type == entity_type.lower())
            if entity_id:
                query = query.filter(AuditLogRecord.entity_id == entity_id)
            if action:
                query = query.filter(AuditLogRecord.action == action.upper())

            total = query.count()
            records = (
                query.order_by(AuditLogRecord.timestamp.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            items = [
                {
                    "id": r.id,
                    "timestamp": r.timestamp.isoformat() + "Z",
                    "entityType": r.entity_type,
                    "entityId": r.entity_id,
                    "action": r.action,
                    "userIdentifier": r.user_identifier,
                    "ipAddress": r.ip_address,
                    "changeSummary": r.change_summary,
                    "hasPreviousState": bool(r.previous_state),
                    "hasNewState": bool(r.new_state),
                }
                for r in records
            ]
            return {
                "items": items,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        finally:
            db.close()

    # Fallback to local jsonl file if PostgreSQL is offline
    logs = []
    if AUDIT_LOG_FILE.exists():
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry = json.loads(line)
                        if entity_type and entry.get("entity_type") != entity_type.lower():
                            continue
                        if entity_id and entry.get("entity_id") != entity_id:
                            continue
                        if action and entry.get("action") != action.upper():
                            continue
                        logs.append(entry)
        except Exception:
            pass

    logs.reverse()
    total = len(logs)
    sliced = logs[offset : offset + limit]
    return {
        "items": sliced,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@router.get("/export")
def export_audit_csv(
    entity_type: str | None = None,
    entity_id: str | None = None,
    action: str | None = None,
):
    """
    Export unalterable MCA audit trail as CSV for statutory audit & tax assessment.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Timestamp (UTC)",
        "Entity Type",
        "Entity ID",
        "Action Performed",
        "User / System",
        "IP Address",
        "Change Summary",
    ])

    if is_db_connected() and SessionLocal:
        db = SessionLocal()
        try:
            query = db.query(AuditLogRecord)
            if entity_type:
                query = query.filter(AuditLogRecord.entity_type == entity_type.lower())
            if entity_id:
                query = query.filter(AuditLogRecord.entity_id == entity_id)
            if action:
                query = query.filter(AuditLogRecord.action == action.upper())

            for r in query.order_by(AuditLogRecord.timestamp.desc()).all():
                writer.writerow([
                    r.timestamp.isoformat() + "Z",
                    r.entity_type,
                    r.entity_id,
                    r.action,
                    r.user_identifier,
                    r.ip_address or "-",
                    r.change_summary or "-",
                ])
        finally:
            db.close()
    else:
        # File fallback
        if AUDIT_LOG_FILE.exists():
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        writer.writerow([
                            entry.get("timestamp", ""),
                            entry.get("entity_type", ""),
                            entry.get("entity_id", ""),
                            entry.get("action", ""),
                            entry.get("user_identifier", ""),
                            entry.get("ip_address", "-"),
                            entry.get("change_summary", "-"),
                        ])

    csv_data = output.getvalue()
    filename = f"MCA_Audit_Trail_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
