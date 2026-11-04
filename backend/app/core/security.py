import time
import hmac
import hashlib
import secrets
import re
from pathlib import Path
from backend.app.config import BASE_DIR, APP_DIR, META_PATH, LOCK_KEY

PIN_RE = re.compile(r'^(\d{6}|\d{8})$')

RESET_PIN_FILES = [
    BASE_DIR / 'RESET-PIN',
    BASE_DIR / 'RESET-PIN.txt',
    APP_DIR / 'RESET-PIN',
    APP_DIR / 'RESET-PIN.txt',
]

class PinRateLimiter:
    def __init__(self):
        self.wrong = 0
        self.until = 0

pin_limiter = PinRateLimiter()

def pin_hash(pin: str | int, salt: str) -> str:
    """Scrypt hash matching Node's crypto.scryptSync(String(pin), salt, 32).hex()."""
    pin_bytes = str(pin).encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    return hashlib.scrypt(pin_bytes, salt=salt_bytes, n=16384, r=8, p=1, dklen=32).hex()

def pin_matches(lock: dict, pin: str | int) -> bool:
    if not lock or not lock.get('salt') or not lock.get('hash'):
        return False
    pin_str = str(pin or '')
    if not PIN_RE.match(pin_str):
        return False
    calc = pin_hash(pin_str, lock['salt'])
    return hmac.compare_digest(calc, lock['hash'])

def generate_salt() -> str:
    return secrets.token_hex(16)
