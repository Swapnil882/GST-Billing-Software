import os
import io
import math
import shutil
import datetime
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from pypdf import PdfReader, PdfWriter
from backend.app.config import BASE_DIR, INVOICES_DIR, PDF_ORIGINALS_DIR, DATA_DIR
from backend.app.core.path_guard import safe_path_segment, is_path_inside
from backend.app.core.logging_util import log_error

router = APIRouter(tags=["pdf"])
TRASH_DIR = BASE_DIR / "Trash"

def find_saved_pdfs(file_name: str, client_name: str | None = None) -> list[Path]:
    safe_client = safe_path_segment(client_name, "General")
    safe_name = safe_path_segment(file_name, "Untitled.pdf")
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
        
    out = []
    client_dir = INVOICES_DIR / safe_client
    if is_path_inside(client_dir, INVOICES_DIR) and client_dir.is_dir():
        for month_entry in client_dir.iterdir():
            if month_entry.is_dir():
                target = month_entry / safe_name
                if is_path_inside(target, INVOICES_DIR) and target.is_file():
                    out.append(target)
                    
    flat = INVOICES_DIR / safe_name
    if is_path_inside(flat, INVOICES_DIR) and flat.is_file():
        out.append(flat)
    return out

def create_watermark_page(width: float, height: float, text: str = "CANCELLED") -> bytes:
    size = min(width, height) / 6.5
    angle = 30
    rad = math.radians(angle)
    w = 0.65 * size * len(text)
    x = width / 2 - (w / 2) * math.cos(rad) + (size / 3) * math.sin(rad)
    y = height / 2 - (w / 2) * math.sin(rad) - (size / 3) * math.cos(rad)
    
    stream = f"""q
/GS1 gs
0.86 0.15 0.15 rg
BT
/F1 {size:.2f} Tf
{math.cos(rad):.4f} {math.sin(rad):.4f} {-math.sin(rad):.4f} {math.cos(rad):.4f} {x:.2f} {y:.2f} Tm
({text}) Tj
ET
Q"""
    raw = f"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 {width} {height}] /Contents 6 0 R>> endobj
4 0 obj <</Font <</F1 5 0 R>> /ExtGState <</GS1 <</ca 0.28 /CA 0.28>>>>>> endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>> endobj
6 0 obj <</Length {len(stream.encode('ascii'))}>>
stream
{stream}
endstream
endobj
xref
0 7
0000000000 65535 f 
trailer <</Size 7 /Root 1 0 R>>
startxref
0
%%EOF"""
    return raw.encode('ascii')

def stamp_cancelled_pdf(pdf_bytes: bytes) -> bytes:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        box = page.mediabox
        width = float(box.width)
        height = float(box.height)
        watermark_pdf = create_watermark_page(width, height, "CANCELLED")
        stamp_reader = PdfReader(io.BytesIO(watermark_pdf))
        page.merge_page(stamp_reader.pages[0])
        writer.add_page(page)
    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue()

@router.post("/api/save-pdf")
async def save_pdf(request: Request, name: str | None = None, client: str | None = None, month: str | None = None):
    body = await request.body()
    now = datetime.datetime.now()
    default_month = now.strftime("%B %Y")
    
    safe_client = safe_path_segment(client, "General")
    safe_month = safe_path_segment(month, default_month)
    safe_name = safe_path_segment(name or f"invoice-{int(now.timestamp() * 1000)}.pdf")
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
        
    folder_path = INVOICES_DIR / safe_client / safe_month
    file_path = folder_path / safe_name
    if not is_path_inside(file_path, INVOICES_DIR):
        raise HTTPException(status_code=400, detail={"error": "Invalid path", "code": "invalid-path"})
        
    folder_path.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(body)
        
    # Remove any existing original kept for undo
    rel_under_invoices = file_path.relative_to(INVOICES_DIR)
    kept_original = PDF_ORIGINALS_DIR / rel_under_invoices
    if is_path_inside(kept_original, PDF_ORIGINALS_DIR) and kept_original.exists():
        try:
            kept_original.unlink()
        except Exception:
            pass
            
    rel_path = file_path.relative_to(BASE_DIR).as_posix()
    return {"saved": True, "relPath": rel_path}

@router.post("/api/saved-pdf/cancel-mark")
def cancel_mark_pdf(payload: dict):
    file_name = payload.get("fileName")
    client_name = payload.get("clientName")
    cancelled = payload.get("cancelled")
    
    if not file_name or not isinstance(cancelled, bool):
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
        
    updated = 0
    failed = 0
    for target in find_saved_pdfs(file_name, client_name):
        rel = target.relative_to(INVOICES_DIR)
        original = PDF_ORIGINALS_DIR / rel
        if not is_path_inside(original, PDF_ORIGINALS_DIR):
            continue
        try:
            if cancelled:
                if not original.exists():
                    original.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, original)
                with open(original, "rb") as f:
                    orig_bytes = f.read()
                stamped = stamp_cancelled_pdf(orig_bytes)
                with open(target, "wb") as f:
                    f.write(stamped)
                updated += 1
            elif original.exists():
                shutil.copy2(original, target)
                original.unlink()
                updated += 1
        except Exception as e:
            failed += 1
            log_error(f"Cancel mark failed for {target}: {e}", "pdf")
    return {"updated": updated, "failed": failed}

@router.post("/api/trash-pdf")
def trash_pdf(payload: dict):
    file_name = payload.get("fileName")
    client_name = payload.get("clientName")
    if not file_name:
        raise HTTPException(status_code=400, detail={"error": "Invalid request", "code": "bad-request"})
        
    safe_client = safe_path_segment(client_name, "General")
    safe_name = safe_path_segment(file_name, "Untitled.pdf")
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
        
    TRASH_DIR.mkdir(parents=True, exist_ok=True)
    found = False
    
    client_dir = INVOICES_DIR / safe_client
    if is_path_inside(client_dir, INVOICES_DIR) and client_dir.is_dir():
        for month_dir in client_dir.iterdir():
            if month_dir.is_dir():
                target = month_dir / safe_name
                if is_path_inside(target, INVOICES_DIR) and target.is_file():
                    trash_path = TRASH_DIR / safe_client / month_dir.name
                    trash_path.mkdir(parents=True, exist_ok=True)
                    trash_file = trash_path / safe_name
                    if is_path_inside(trash_file, TRASH_DIR):
                        try:
                            target.replace(trash_file)
                        except Exception:
                            shutil.copy2(target, trash_file)
                            target.unlink()
                        found = True
                        break
                        
    if not found:
        flat_path = INVOICES_DIR / safe_name
        if is_path_inside(flat_path, INVOICES_DIR) and flat_path.is_file():
            trash_path = TRASH_DIR / safe_client
            trash_path.mkdir(parents=True, exist_ok=True)
            trash_file = trash_path / safe_name
            if is_path_inside(trash_file, TRASH_DIR):
                try:
                    flat_path.replace(trash_file)
                except Exception:
                    shutil.copy2(flat_path, trash_file)
                    flat_path.unlink()
                found = True
    return {"trashed": found}
