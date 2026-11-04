from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Integer, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class InvoiceRecord(Base):
    __tablename__ = "invoices"

    id = Column(String(128), primary_key=True, index=True)
    invoice_number = Column(String(128), index=True, nullable=False)
    client_name = Column(String(255), index=True)
    invoice_date = Column(String(32), index=True)
    invoice_type = Column(String(64), default="tax-invoice")
    status = Column(String(32), index=True, default="unpaid")
    currency = Column(String(16), default="INR")
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClientRecord(Base):
    __tablename__ = "clients"

    id = Column(String(128), primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    gstin = Column(String(64), index=True)
    state = Column(String(64))
    pan = Column(String(32))
    phone = Column(String(32))
    email = Column(String(128))
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductRecord(Base):
    __tablename__ = "products"

    id = Column(String(128), primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    hsn = Column(String(32), index=True)
    unit = Column(String(32), default="PCS")
    price = Column(Float, default=0.0)
    tax_rate = Column(Float, default=18.0)
    stock = Column(Float, default=0.0)
    is_service = Column(Boolean, default=False)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExpenseRecord(Base):
    __tablename__ = "expenses"

    id = Column(String(128), primary_key=True, index=True)
    date = Column(String(32), index=True)
    category = Column(String(128), index=True)
    amount = Column(Float, default=0.0)
    mode = Column(String(64), default="cash")
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PurchaseRecord(Base):
    __tablename__ = "purchases"

    id = Column(String(128), primary_key=True, index=True)
    bill_number = Column(String(128), index=True)
    supplier_name = Column(String(255), index=True)
    date = Column(String(32))
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    status = Column(String(32), default="unpaid")
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CashBookRecord(Base):
    __tablename__ = "cash_book"

    id = Column(String(128), primary_key=True, index=True)
    date = Column(String(32), index=True)
    type = Column(String(16), index=True)  # 'in' or 'out'
    category = Column(String(128))
    amount = Column(Float, default=0.0)
    party_name = Column(String(255))
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProfileRecord(Base):
    __tablename__ = "business_profile"

    id = Column(String(64), primary_key=True, default="default")
    business_name = Column(String(255))
    gstin = Column(String(64))
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RecurringRecord(Base):
    __tablename__ = "recurring_templates"

    id = Column(String(128), primary_key=True, index=True)
    client_name = Column(String(255))
    frequency = Column(String(32))
    next_date = Column(String(32))
    active = Column(Boolean, default=True)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductionRecord(Base):
    __tablename__ = "productions"

    id = Column(String(128), primary_key=True, index=True)
    date = Column(String(32))
    product_id = Column(String(128))
    quantity = Column(Float, default=1.0)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLogRecord(Base):
    """
    MCA Audit Trail (Rule 3(1) of Companies Accounts Rules 2014 / 2023 amendment).
    Immutable ledger of all financial and master record modifications.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(64), index=True, nullable=False)  # invoice, client, product, expense, purchase, cash_book, profile
    entity_id = Column(String(128), index=True, nullable=False)
    action = Column(String(32), index=True, nullable=False)       # CREATE, UPDATE, CANCEL, SOFT_DELETE, RESTORE, PERMANENT_DELETE
    user_identifier = Column(String(128), default="system")
    ip_address = Column(String(64), nullable=True)
    change_summary = Column(Text, nullable=True)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
