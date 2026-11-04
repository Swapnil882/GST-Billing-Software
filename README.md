# GST Billing Software

Modern, high-performance, offline-first GST invoice & billing software for India. Built with **FastAPI (Python 3.11)** on the backend, **React 19 + Vite 7** on the frontend, and backed by dual **PostgreSQL** & local atomic JSON storage.

---

## Project Structure

```
GST-Billing-Software/
│
├── backend/                  # FastAPI Python Backend
│   ├── app/                  # Main application package
│   │   ├── core/             # Storage, security (Scrypt), path guard, audit logger
│   │   ├── db/               # PostgreSQL SQLAlchemy models, session & sync
│   │   ├── routers/          # 21 modular API routers (bills, clients, audit_trail, etc.)
│   │   ├── schemas/          # Pydantic validation models
│   │   ├── services/         # Invoice math, recurring engine, backup rotation
│   │   ├── config.py         # App configuration & .env loader
│   │   └── main.py           # FastAPI entrypoint, CORS, static SPA mount
│   ├── scripts/              # Database initialization & demo seeding scripts
│   ├── tests/                # Comprehensive test suites (API, processes, PostgreSQL)
│   └── run.py                # Backend Uvicorn runner
│
├── frontend/                 # React 19 Frontend (Vite 7)
│   ├── public/               # Static assets, PWA manifest, offline OCR WASM
│   ├── src/                  # React source code (components, hooks, store, utils)
│   ├── dist/                 # Production compiled SPA bundle
│   ├── index.html            # SPA entry HTML
│   ├── vite.config.js        # Vite configuration & PWA workbox caching
│   └── package.json          # Frontend dependencies
│
├── docs/                     # Comprehensive Documentation & Reports
│   ├── ARCHITECTURE.md       # Full architecture specification
│   ├── CHANGELOG.md          # Release history & feature changelog
│   ├── USER_GUIDE.md         # End-user operational guide
│   └── ...                   # Tax guides, release checklists, and audits
│
├── data/                     # Local Storage Data (Atomic JSON & Backups)
│   ├── bills/                # Invoices
│   ├── clients/              # Customer directory
│   ├── products/             # Inventory catalog
│   ├── backups/              # Automated daily snapshot archives
│   └── audit_trail.jsonl     # Local immutable MCA audit log
│
├── Saved Invoices/           # PDF Invoice Archive
│
├── .env                      # Active environment & database settings
├── .env.example              # Environment configuration template
├── run.py                    # Unified single-command launcher
└── run.bat                   # Windows one-click launcher
```

---

## Running the Application

You can run the application either in **Independent Development Mode** (Frontend & Backend running separately in their own terminal windows) or in **Unified Production Mode** (single command).

### Mode A: Running Frontend & Backend Separately (Recommended for Development)

Run Frontend and Backend in separate terminal windows for instant hot-reloading:

#### 1. Start FastAPI Backend:
- **Windows**: Double-click `run-backend.bat`
- **Or Terminal**:
  ```powershell
  python backend/run.py
  ```
  *Backend listens on [http://127.0.0.1:47371](http://127.0.0.1:47371) (Interactive Swagger Docs at [http://127.0.0.1:47371/docs](http://127.0.0.1:47371/docs)) and streams live request logs.*

#### 2. Start React Frontend (Vite Dev Server):
- **Windows**: Double-click `run-frontend.bat`
- **Or Terminal**:
  ```powershell
  cd frontend
  npm run dev
  ```
  *Frontend runs on [http://localhost:5173](http://localhost:5173) with instant Hot Module Replacement (HMR) and automatically proxies all `/api` requests to the FastAPI backend.*

---

### Mode B: Running Unified Full-Stack (Single Command)

To run the complete production stack in a single terminal:
- **Windows**: Double-click `run.bat`
- **Or Terminal**:
  ```powershell
  python run.py
  ```
  *This automatically verifies the frontend build, starts the FastAPI server, and serves both the React application and API on [http://127.0.0.1:47371](http://127.0.0.1:47371).*

---

## Features

- **GST Compliance**: Real-time CGST, SGST, IGST, UTGST, and Cess calculation.
- **Statutory Audit Trail**: MCA Rule 3(1) compliant unalterable edit logs with CSV export.
- **Dual Database Architecture**: High-speed PostgreSQL integration with automatic local offline fallback.
- **Hardware-Resistant Security**: Scrypt PIN hashing with automated lockout protection.
- **Client-Side OCR**: Offline document & receipt scanning using WASM Tesseract.
- **Multi-Currency & Reports**: Supports 22 global currencies, GSTR-1/3B JSON exports, GSTR-2B reconciliation, and e-Way bill format.
