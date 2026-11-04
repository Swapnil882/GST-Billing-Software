# Free GST Billing Software — Frontend (React 19 + Vite 7)

Offline-first Progressive Web App (PWA) for GST Invoicing and Billing.

## Architecture

```
frontend/
├── public/                 # Static assets copied directly to dist/
│   ├── icons/              # App launcher and PWA icons
│   ├── tesseract/          # Offline Tesseract OCR worker & WASM assets
│   ├── boot-guard.js       # Stale offline service worker protection
│   ├── favicon.svg         # App favicon
│   └── sw-reload.js        # Service worker lifecycle reload helper
├── src/
│   ├── components/         # React UI views, modals, cards, and reports
│   │   ├── Dashboard.jsx   # Invoices list, metrics, status filters
│   │   ├── InvoiceGenerator.jsx # Interactive invoice editor & calculations
│   │   ├── InvoicePreview.jsx   # Live split-view PDF preview
│   │   ├── GSTReturns.jsx       # GSTR-1, GSTR-3B, GSTR-2B reconciliation
│   │   ├── SettingsView.jsx     # Business profile, accounts, backup/restore
│   │   ├── ... (and other modular components)
│   ├── services/           # External browser-side services (Google Drive)
│   ├── utils/              # Pure domain utility modules
│   ├── App.jsx             # Root layout, navigation router, Ctrl+K palette
│   ├── main.jsx            # Application bootstrap, PWA registration
│   ├── store.js            # API client wrapper for /api/* backend calls
│   ├── utils.js            # Core Indian GST math, round-off, numbers to words
│   └── index.css           # Global CSS variables, themes, dark mode
├── index.html              # Single Page Application HTML entry point
├── package.json            # Client dependencies and npm scripts
└── vite.config.js          # Vite 7 build config, PWA manifest, proxy rules
```

## Running the Frontend

### Development Mode (with Hot Module Replacement):
```powershell
npm.cmd --prefix frontend run dev
```
* Runs on `http://localhost:5173` and automatically proxies all `/api/*` calls to the FastAPI backend.

### Production Build:
```powershell
npm.cmd --prefix frontend run build
```
* Compiles optimized chunks into `frontend/dist/`.

### Linting & Tests:
```powershell
npm.cmd --prefix frontend run test
```
