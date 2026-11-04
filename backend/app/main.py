import os
import sys
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import (
    ensure_directories,
    FRONTEND_DIST,
    PORT_FILE,
    DEFAULT_PORT
)
from backend.app.services.recurring_engine import process_due_recurring
from backend.app.services.backup_service import run_daily_backup, purge_old_trash

# Routers
from backend.app.routers import (
    bills,
    profile,
    clients,
    products,
    templates,
    expenses,
    purchases,
    productions,
    cash_book,
    receipts,
    recurring,
    meta,
    prefs,
    lock,
    pdf,
    backups,
    trash,
    export_import,
    system,
    control_panel,
    audit_trail,
)

async def background_scheduler():
    """Background loop for daily backup, trash purge, and recurring invoice firing."""
    await asyncio.sleep(3)
    try:
        await process_due_recurring()
    except Exception:
        pass
    try:
        run_daily_backup()
    except Exception:
        pass
    try:
        purge_old_trash()
    except Exception:
        pass

    while True:
        await asyncio.sleep(3600)  # Hourly check
        try:
            await process_due_recurring()
        except Exception:
            pass
        try:
            run_daily_backup()
        except Exception:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ensure_directories()
    try:
        from backend.app.db.session import init_db, is_db_connected
        from backend.app.db.sync_service import sync_all_json_to_db
        if is_db_connected():
            init_db()
            sync_all_json_to_db()
    except Exception as e:
        print(f"[DB] Startup DB note: {e}")
    task = asyncio.create_task(background_scheduler())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(
    title="Free GST Billing Software API",
    version="1.10.83",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None
)

# CORS Middleware (locked down to localhost and 127.0.0.1)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register all API routers
app.include_router(bills.router)
app.include_router(profile.router)
app.include_router(clients.router)
app.include_router(products.router)
app.include_router(templates.router)
app.include_router(expenses.router)
app.include_router(purchases.router)
app.include_router(productions.router)
app.include_router(cash_book.router)
app.include_router(receipts.router)
app.include_router(recurring.router)
app.include_router(meta.router)
app.include_router(prefs.router)
app.include_router(lock.router)
app.include_router(pdf.router)
app.include_router(backups.router)
app.include_router(trash.router)
app.include_router(export_import.router)
app.include_router(system.router)
app.include_router(control_panel.router)
app.include_router(audit_trail.router)

# Mount frontend static files if dist exists
if FRONTEND_DIST.is_dir():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        
    tesseract_dir = FRONTEND_DIST / "tesseract"
    if tesseract_dir.is_dir():
        app.mount("/tesseract", StaticFiles(directory=str(tesseract_dir)), name="tesseract")

    icons_dir = FRONTEND_DIST / "icons"
    if icons_dir.is_dir():
        app.mount("/icons", StaticFiles(directory=str(icons_dir)), name="icons")

PLACEHOLDER_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Free GST Billing Software — building…</title>
<meta http-equiv="refresh" content="3">
<style>
  body { font-family: -apple-system, Segoe UI, Inter, sans-serif; max-width: 560px;
         margin: 6rem auto; padding: 2rem; color: #1e293b; line-height: 1.55; }
  h1 { color: #1e40af; margin: 0 0 0.5rem; }
  code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
  .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid #cbd5e1;
             border-top-color: #1e40af; border-radius: 50%; animation: spin 1s linear infinite;
             vertical-align: middle; margin-right: 6px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .muted { color: #64748b; font-size: 0.9em; }
  .box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.85rem 1rem; border-radius: 8px; margin-top: 1rem; }
</style></head>
<body>
  <h1>Free GST Billing Software (FastAPI Backend)</h1>
  <p><span class="spinner"></span> The frontend is not built yet or still building. This page refreshes every 3 seconds.</p>
  <div class="box">
    <p style="margin:0 0 0.5rem"><strong>Build the frontend:</strong></p>
    <p style="margin:0.5rem 0 0"><code>cd frontend && npm run build</code></p>
    <p class="muted" style="margin:0.5rem 0 0">…then reload this page.</p>
  </div>
</body></html>"""

@app.get("/{full_path:path}", response_class=Response)
async def serve_spa(request: Request, full_path: str):
    # Reject unknown API paths with JSON 404
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail={"error": "No such endpoint"})

    # Check for direct files in dist (e.g. favicon.svg, manifest.webmanifest, sw.js)
    if FRONTEND_DIST.is_dir():
        target_file = FRONTEND_DIST / full_path
        if full_path and target_file.is_file():
            return FileResponse(target_file)
            
        index_file = FRONTEND_DIST / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)

    return HTMLResponse(content=PLACEHOLDER_HTML, status_code=503)
