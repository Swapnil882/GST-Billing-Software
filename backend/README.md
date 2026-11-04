# Free GST Billing Software — Backend (FastAPI)

Fast, secure, and offline-first Python backend for Free GST Billing Software.

## Architecture

```
backend/
├── app/
│   ├── core/               # Low-level utilities
│   │   ├── logging_util.py # Sensitive PII/GSTIN error redaction & log rotation
│   │   ├── path_guard.py   # Path traversal protection & file name sanitization
│   │   ├── security.py     # Scrypt PIN password hashing matching Node format
│   │   └── storage.py      # Atomic JSON writes (temp+rename), 5s dir cache TTL
│   ├── routers/            # Modular FastAPI APIRouters (REST endpoints)
│   │   ├── bills.py        # Invoices CRUD, 409 duplicate check, credit lock
│   │   ├── profile.py      # Company profile & multi-business profiles
│   │   ├── clients.py      # Client directory
│   │   ├── products.py     # Product & inventory catalog
│   │   ├── productions.py  # Manufacturing BOM assembly & atomic stock rollback
│   │   ├── purchases.py    # Purchase bills & Purchase Orders (PO)
│   │   ├── cash_book.py    # Cash Book Money In / Money Out
│   │   ├── receipts.py     # Payment receipt vouchers
│   │   ├── recurring.py    # Recurring invoice templates & auto-fire
│   │   ├── templates.py    # Standard terms & conditions templates
│   │   ├── meta.py         # Counters & document number series
│   │   ├── prefs.py        # Local browser preferences server mirror
│   │   ├── lock.py         # PIN security lock gate
│   │   ├── pdf.py          # PDF storage & CANCELLED watermark stamping
│   │   ├── backups.py      # Daily backup, retention pruning, transactional restore
│   │   ├── trash.py        # Soft-delete invoice trash bin
│   │   ├── export_import.py# Full JSON backup export & selective import
│   │   ├── system.py       # Health check, version, errors log
│   │   └── control_panel.py# Desktop system integration & paths
│   ├── schemas/            # Pydantic models for validation and OpenAPI schemas
│   ├── services/           # Domain background business logic
│   │   ├── backup_service.py   # Daily backup & 30-day trash purge
│   │   ├── invoice_math.py     # Counter generation, date advance & FY labels
│   │   └── recurring_engine.py # Auto-fire loop for due recurring invoices
│   ├── config.py           # Paths, constants, port discovery
│   └── main.py             # FastAPI entry, lifespan events, CORS, SPA mount
├── tests/                  # Automated integration tests
│   ├── test_api.py         # REST endpoint smoke tests
│   └── test_all_processes.py # Full 11-process workflow test suite
├── requirements.txt        # Python package dependencies
└── run.py                  # Standalone Uvicorn runner with port auto-scan
```

## Running the Backend

```powershell
python backend/run.py
```
* Interactive API Documentation (Swagger UI): `http://127.0.0.1:47371/docs`
* Health Check: `http://127.0.0.1:47371/api/health`

## Running Tests

```powershell
python backend/tests/test_all_processes.py
```
