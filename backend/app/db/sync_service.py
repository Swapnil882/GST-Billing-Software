import logging
from sqlalchemy.orm import Session
from backend.app.config import DATA_DIR, PROFILE_PATH
from backend.app.core.storage import read_all_from_dir, read_json
from .session import SessionLocal, is_db_connected
from .models import (
    InvoiceRecord,
    ClientRecord,
    ProductRecord,
    ExpenseRecord,
    PurchaseRecord,
    CashBookRecord,
    ProfileRecord,
    RecurringRecord,
    ProductionRecord,
)

logger = logging.getLogger("uvicorn.error")

def sync_record(db: Session, model_class, record_id: str, fields: dict):
    """Upsert a single record into the database."""
    try:
        existing = db.query(model_class).filter(model_class.id == record_id).first()
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
        else:
            new_item = model_class(id=record_id, **fields)
            db.add(new_item)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[DB Sync] Error syncing {model_class.__tablename__} {record_id}: {e}")

def delete_record(db: Session, model_class, record_id: str):
    """Remove a record from the database."""
    try:
        existing = db.query(model_class).filter(model_class.id == record_id).first()
        if existing:
            db.delete(existing)
            db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[DB Sync] Error deleting {model_class.__tablename__} {record_id}: {e}")

def mirror_write_to_db(dir_name: str, file_stem: str, data: dict):
    """Mirror a single JSON write into PostgreSQL in real time."""
    if not is_db_connected() or not SessionLocal or not isinstance(data, dict):
        return
    try:
        db: Session = SessionLocal()
        try:
            if dir_name == "bills":
                bid = data.get("id") or data.get("invoiceNumber", file_stem)
                sync_record(db, InvoiceRecord, bid, {
                    "invoice_number": data.get("invoiceNumber", bid),
                    "client_name": data.get("clientName", ""),
                    "invoice_date": data.get("invoiceDate", ""),
                    "invoice_type": data.get("invoiceType", "tax-invoice"),
                    "status": data.get("status", "unpaid"),
                    "currency": data.get("currency", "INR"),
                    "total_amount": float(data.get("totalAmount") or 0.0),
                    "paid_amount": float(data.get("paidAmount") or 0.0),
                    "data": data,
                })
            elif dir_name == "clients":
                cid = data.get("id", file_stem)
                sync_record(db, ClientRecord, cid, {
                    "name": data.get("name", ""),
                    "gstin": data.get("gstin", ""),
                    "state": data.get("state", ""),
                    "pan": data.get("pan", ""),
                    "phone": data.get("phone", ""),
                    "email": data.get("email", ""),
                    "data": data,
                })
            elif dir_name == "products":
                pid = data.get("id", file_stem)
                sync_record(db, ProductRecord, pid, {
                    "name": data.get("name", ""),
                    "hsn": data.get("hsn", ""),
                    "unit": data.get("unit", "PCS"),
                    "price": float(data.get("price") or 0.0),
                    "tax_rate": float(data.get("taxRate") or 18.0),
                    "stock": float(data.get("stock") or 0.0),
                    "is_service": bool(data.get("isService")),
                    "data": data,
                })
            elif dir_name == "expenses":
                eid = data.get("id", file_stem)
                sync_record(db, ExpenseRecord, eid, {
                    "date": data.get("date", ""),
                    "category": data.get("category", ""),
                    "amount": float(data.get("amount") or 0.0),
                    "mode": data.get("mode", "cash"),
                    "data": data,
                })
            elif dir_name == "purchases":
                puid = data.get("id", file_stem)
                sync_record(db, PurchaseRecord, puid, {
                    "bill_number": data.get("billNumber", ""),
                    "supplier_name": data.get("supplierName", ""),
                    "date": data.get("date", ""),
                    "total_amount": float(data.get("totalAmount") or 0.0),
                    "paid_amount": float(data.get("paidAmount") or 0.0),
                    "status": data.get("status", "unpaid"),
                    "data": data,
                })
            elif dir_name == "cash-book":
                cbid = data.get("id", file_stem)
                sync_record(db, CashBookRecord, cbid, {
                    "date": data.get("date", ""),
                    "type": data.get("type", "in"),
                    "category": data.get("category", ""),
                    "amount": float(data.get("amount") or 0.0),
                    "party_name": data.get("partyName", ""),
                    "data": data,
                })
            elif dir_name == "recurring":
                rid = data.get("id", file_stem)
                sync_record(db, RecurringRecord, rid, {
                    "client_name": data.get("clientName", ""),
                    "frequency": data.get("frequency", ""),
                    "next_date": data.get("nextDate", ""),
                    "active": bool(data.get("active", True)),
                    "data": data,
                })
            elif dir_name == "productions":
                prid = data.get("id", file_stem)
                sync_record(db, ProductionRecord, prid, {
                    "date": data.get("date", ""),
                    "product_id": data.get("productId", ""),
                    "quantity": float(data.get("quantity") or 1.0),
                    "data": data,
                })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[DB Sync] Real-time write sync error: {e}")

def mirror_delete_from_db(dir_name: str, file_stem: str):
    """Mirror a single JSON deletion into PostgreSQL in real time."""
    if not is_db_connected() or not SessionLocal:
        return
    model_map = {
        "bills": InvoiceRecord,
        "clients": ClientRecord,
        "products": ProductRecord,
        "expenses": ExpenseRecord,
        "purchases": PurchaseRecord,
        "cash-book": CashBookRecord,
        "recurring": RecurringRecord,
        "productions": ProductionRecord,
    }
    model_cls = model_map.get(dir_name)
    if not model_cls:
        return
    try:
        db: Session = SessionLocal()
        try:
            delete_record(db, model_cls, file_stem)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[DB Sync] Real-time delete sync error: {e}")

def sync_all_json_to_db() -> dict:
    """Reads all current JSON files in data/ and mirrors them into PostgreSQL."""
    if not is_db_connected() or not SessionLocal:
        return {"synced": False, "reason": "PostgreSQL not connected"}

    db: Session = SessionLocal()
    counts = {
        "profile": 0,
        "bills": 0,
        "clients": 0,
        "products": 0,
        "expenses": 0,
        "purchases": 0,
        "cash_book": 0,
        "recurring": 0,
        "productions": 0,
    }

    try:
        # 1. Profile
        if PROFILE_PATH.exists():
            prof = read_json(PROFILE_PATH)
            if prof:
                sync_record(db, ProfileRecord, "default", {
                    "business_name": prof.get("businessName", ""),
                    "gstin": prof.get("gstin", ""),
                    "data": prof,
                })
                counts["profile"] += 1

        # 2. Invoices / Bills
        for b in read_all_from_dir("bills"):
            bid = b.get("id") or b.get("invoiceNumber")
            if bid:
                sync_record(db, InvoiceRecord, bid, {
                    "invoice_number": b.get("invoiceNumber", bid),
                    "client_name": b.get("clientName", ""),
                    "invoice_date": b.get("invoiceDate", ""),
                    "invoice_type": b.get("invoiceType", "tax-invoice"),
                    "status": b.get("status", "unpaid"),
                    "currency": b.get("currency", "INR"),
                    "total_amount": float(b.get("totalAmount") or 0.0),
                    "paid_amount": float(b.get("paidAmount") or 0.0),
                    "data": b,
                })
                counts["bills"] += 1

        # 3. Clients
        for c in read_all_from_dir("clients"):
            cid = c.get("id")
            if cid:
                sync_record(db, ClientRecord, cid, {
                    "name": c.get("name", ""),
                    "gstin": c.get("gstin", ""),
                    "state": c.get("state", ""),
                    "pan": c.get("pan", ""),
                    "phone": c.get("phone", ""),
                    "email": c.get("email", ""),
                    "data": c,
                })
                counts["clients"] += 1

        # 4. Products
        for p in read_all_from_dir("products"):
            pid = p.get("id")
            if pid:
                sync_record(db, ProductRecord, pid, {
                    "name": p.get("name", ""),
                    "hsn": p.get("hsn", ""),
                    "unit": p.get("unit", "PCS"),
                    "price": float(p.get("price") or 0.0),
                    "tax_rate": float(p.get("taxRate") or 18.0),
                    "stock": float(p.get("stock") or 0.0),
                    "is_service": bool(p.get("isService")),
                    "data": p,
                })
                counts["products"] += 1

        # 5. Expenses
        for ex in read_all_from_dir("expenses"):
            eid = ex.get("id")
            if eid:
                sync_record(db, ExpenseRecord, eid, {
                    "date": ex.get("date", ""),
                    "category": ex.get("category", ""),
                    "amount": float(ex.get("amount") or 0.0),
                    "mode": ex.get("mode", "cash"),
                    "data": ex,
                })
                counts["expenses"] += 1

        # 6. Purchases
        for pu in read_all_from_dir("purchases"):
            puid = pu.get("id")
            if puid:
                sync_record(db, PurchaseRecord, puid, {
                    "bill_number": pu.get("billNumber", ""),
                    "supplier_name": pu.get("supplierName", ""),
                    "date": pu.get("date", ""),
                    "total_amount": float(pu.get("totalAmount") or 0.0),
                    "paid_amount": float(pu.get("paidAmount") or 0.0),
                    "status": pu.get("status", "unpaid"),
                    "data": pu,
                })
                counts["purchases"] += 1

        # 7. Cash Book
        for cb in read_all_from_dir("cash-book"):
            cbid = cb.get("id")
            if cbid:
                sync_record(db, CashBookRecord, cbid, {
                    "date": cb.get("date", ""),
                    "type": cb.get("type", "in"),
                    "category": cb.get("category", ""),
                    "amount": float(cb.get("amount") or 0.0),
                    "party_name": cb.get("partyName", ""),
                    "data": cb,
                })
                counts["cash_book"] += 1

        # 8. Recurring
        for r in read_all_from_dir("recurring"):
            rid = r.get("id")
            if rid:
                sync_record(db, RecurringRecord, rid, {
                    "client_name": r.get("clientName", ""),
                    "frequency": r.get("frequency", ""),
                    "next_date": r.get("nextDate", ""),
                    "active": bool(r.get("active", True)),
                    "data": r,
                })
                counts["recurring"] += 1

        # 9. Productions
        for pr in read_all_from_dir("productions"):
            prid = pr.get("id")
            if prid:
                sync_record(db, ProductionRecord, prid, {
                    "date": pr.get("date", ""),
                    "product_id": pr.get("productId", ""),
                    "quantity": float(pr.get("quantity") or 1.0),
                    "data": pr,
                })
                counts["productions"] += 1

        logger.info(f"[DB Sync] Successfully mirrored data to PostgreSQL: {counts}")
        return {"synced": True, "counts": counts}
    finally:
        db.close()
