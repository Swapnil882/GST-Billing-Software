from fastapi import APIRouter, Request, Response, HTTPException, status, Query
from pathlib import Path
from backend.app.config import DATA_DIR, BILL_TRASH_DIR
from backend.app.core.storage import (
    read_all_from_dir,
    read_json,
    write_json_atomic,
    delete_file,
    invalidate_cache,
    find_credit_dependents,
)
from backend.app.core.path_guard import safe_file_name
from backend.app.core.audit import log_audit
from backend.app.db.session import SessionLocal, is_db_connected
from backend.app.db.models import InvoiceRecord

router = APIRouter(prefix="/api/bills", tags=["bills"])

@router.get("")
def get_bills(
    search: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = Query(None, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Query invoices. When PostgreSQL is connected, executes high-speed indexed SQL.
    Returns paginated items if limit is provided, or full list for backwards compatibility.
    """
    if is_db_connected() and SessionLocal:
        db = SessionLocal()
        try:
            query = db.query(InvoiceRecord)
            if search:
                s = f"%{search}%"
                query = query.filter(
                    (InvoiceRecord.invoice_number.ilike(s)) | (InvoiceRecord.client_name.ilike(s))
                )
            if status:
                query = query.filter(InvoiceRecord.status == status.lower())
            if start_date:
                query = query.filter(InvoiceRecord.invoice_date >= start_date)
            if end_date:
                query = query.filter(InvoiceRecord.invoice_date <= end_date)

            query = query.order_by(InvoiceRecord.invoice_date.desc())

            if limit is not None:
                total = query.count()
                records = query.offset(offset).limit(limit).all()
                return {
                    "items": [r.data for r in records],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "page": (offset // limit) + 1,
                    "pages": (total + limit - 1) // limit if limit > 0 else 1,
                }

            # Return raw list for backward compatibility with standard UI
            records = query.all()
            return [r.data for r in records]
        finally:
            db.close()

    # Fallback to local file storage if PostgreSQL is offline
    bills = read_all_from_dir("bills")
    if search:
        s = search.lower()
        bills = [
            b for b in bills
            if s in str(b.get("invoiceNumber", "")).lower() or s in str(b.get("clientName", "")).lower()
        ]
    if status:
        bills = [b for b in bills if b.get("status") == status.lower()]
    if start_date:
        bills = [b for b in bills if str(b.get("invoiceDate", "")) >= start_date]
    if end_date:
        bills = [b for b in bills if str(b.get("invoiceDate", "")) <= end_date]

    bills.sort(key=lambda b: str(b.get("invoiceDate") or ""), reverse=True)

    if limit is not None:
        total = len(bills)
        return {
            "items": bills[offset : offset + limit],
            "total": total,
            "limit": limit,
            "offset": offset,
            "page": (offset // limit) + 1,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    return bills

@router.post("")
def save_bill(bill: dict, request: Request, overwrite: str | None = None):
    if not bill or not bill.get("id"):
        raise HTTPException(status_code=400, detail={"error": "Bill must have an id"})
    
    file_name = f"{safe_file_name(bill['id'])}.json"
    file_path = DATA_DIR / "bills" / file_name
    client_ip = request.client.host if request.client else None
    
    existing_data = read_json(file_path) if file_path.exists() else None
    is_overwrite = overwrite in ("1", "true", True)
    
    if not is_overwrite and existing_data is not None:
        return Response(
            content='{"error":"A bill with this invoice number already exists","invoiceNumber":"' + str(bill["id"]) + '"}',
            status_code=409,
            media_type="application/json"
        )
        
    write_json_atomic(file_path, bill)

    # MCA Rule 3 Audit Trail Logging
    action = "UPDATE" if existing_data else "CREATE"
    client_name = bill.get("clientName") or bill.get("data", {}).get("client", {}).get("name", "Unknown Client")
    total_val = bill.get("totalAmount") or bill.get("data", {}).get("totals", {}).get("total", 0.0)
    summary = (
        f"Created invoice {bill['id']} for {client_name} (Total: ₹{total_val})"
        if action == "CREATE"
        else f"Updated invoice {bill['id']} (Status: {bill.get('status')})"
    )
    log_audit(
        entity_type="invoice",
        entity_id=bill["id"],
        action=action,
        change_summary=summary,
        previous_state=existing_data,
        new_state=bill,
        ip_address=client_ip,
    )

    return {"success": True}

@router.delete("/{bill_id:path}")
def delete_bill(bill_id: str, request: Request, force: str | None = None, permanent: str | None = None):
    file_name = f"{safe_file_name(bill_id)}.json"
    file_path = DATA_DIR / "bills" / file_name
    trash_path = BILL_TRASH_DIR / file_name
    client_ip = request.client.host if request.client else None

    if permanent in ("1", "true", True):
        target = file_path if file_path.exists() else (trash_path if trash_path.exists() else None)
        if target:
            existing_data = read_json(target)
            target.unlink()
            invalidate_cache("bills")
            log_audit(
                entity_type="invoice",
                entity_id=bill_id,
                action="PERMANENT_DELETE",
                change_summary=f"Permanently purged invoice {bill_id} from storage",
                previous_state=existing_data,
                ip_address=client_ip,
            )
        return {"success": True, "permanent": True}

    if not file_path.exists():
        return {"success": True}

    is_force = force in ("1", "true", True)
    if not is_force:
        dependents = find_credit_dependents(bill_id)
        if dependents:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "client-credit-dependency",
                    "message": "This bill was used as a client-credit source on another invoice.",
                    "dependents": dependents
                }
            )

    existing_data = read_json(file_path)
    BILL_TRASH_DIR.mkdir(parents=True, exist_ok=True)
    file_path.replace(trash_path)
    invalidate_cache("bills")

    log_audit(
        entity_type="invoice",
        entity_id=bill_id,
        action="SOFT_DELETE",
        change_summary=f"Soft deleted invoice {bill_id} to trash",
        previous_state=existing_data,
        ip_address=client_ip,
    )
    return {"success": True, "trashed": True}
