import re
import datetime
from pathlib import Path
from backend.app.config import ERRORS_LOG

REDACTIONS = [
    (re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', re.IGNORECASE), '[email]'),
    (re.compile(r'\b[A-Za-z0-9._-]{2,}@[A-Za-z]{2,}\b(?!:)', re.IGNORECASE), '[upi-id]'),
    (re.compile(r'\b\d{2}[A-Za-z]{5}\d{4}[A-Za-z][A-Za-z0-9]Z[A-Za-z0-9]\b', re.IGNORECASE), '[gstin]'),
    (re.compile(r'\b[A-Za-z]{5}\d{4}[A-Za-z]\b', re.IGNORECASE), '[pan]'),
    (re.compile(r'\b[A-Za-z]{4}0[A-Za-z0-9]{6}\b', re.IGNORECASE), '[ifsc]'),
    (re.compile(r'(?:\+91[\s-]?|\b0)?\b[6-9]\d{4}[\s-]?\d{5}\b'), '[phone]'),
    (re.compile(r'([\\/](?:Users|home)[\\/])[^\\/\s]+', re.IGNORECASE), r'\1[user]'),
]

NUM_REGEX = re.compile(r'(\.m?jsx?:\d+:\d+)|\b\d{6,}\b')

def redact(text: str) -> str:
    """Redacts sensitive PII and account info from error strings."""
    s = str(text or '')
    for regex, replacement in REDACTIONS:
        s = regex.sub(replacement, s)
    s = NUM_REGEX.sub(lambda m: m.group(1) if m.group(1) else '[number]', s)
    return s

def rotate_errors_if_large(max_bytes: int = 512 * 1024, keep_bytes: int = 256 * 1024):
    """Keep errors.log bounded so a looping error doesn't fill the disk."""
    if not ERRORS_LOG.exists():
        return
    try:
        size = ERRORS_LOG.stat().st_size
        if size > max_bytes:
            with open(ERRORS_LOG, 'rb') as f:
                f.seek(size - keep_bytes)
                tail = f.read()
            lines = tail.split(b'\n', 1)
            tail = lines[1] if len(lines) > 1 else lines[0]
            with open(ERRORS_LOG, 'wb') as f:
                f.write(tail)
    except Exception:
        pass

def log_error(msg: str, context: str = "api"):
    """Append a redacted, timestamped line to errors.log."""
    try:
        rotate_errors_if_large()
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        clean = redact(msg).replace('\r', ' ').replace('\n', ' ')
        with open(ERRORS_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] [{context}] {clean}\n")
    except Exception:
        pass
