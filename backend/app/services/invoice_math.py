import calendar
import datetime
from typing import Any
from backend.app.config import META_PATH
from backend.app.core.storage import read_json, write_json_atomic

DEFAULT_NUMBER_SETTINGS = {
    'format': 'branded',
    'brandPrefix': '',
    'separator': '/',
    'showFinYear': True,
    'startNumber': 1,
    'padDigits': 4
}

def get_financial_year_start(d: datetime.date | None = None) -> int:
    if d is None:
        d = datetime.date.today()
    return d.year if d.month >= 4 else d.year - 1

def get_financial_year_label(d: datetime.date | None = None) -> str:
    y = get_financial_year_start(d)
    return f"{y}-{str(y + 1)[-2:]}"

def business_key_of(profile: dict | None) -> str:
    if not profile:
        return ""
    gstin = str(profile.get('gstin') or '').strip().upper()
    if gstin:
        return gstin
    name = str(profile.get('businessName') or '').strip().lower()
    name = ' '.join(name.split())
    return f"NAME:{name}" if name else ""

def number_series_for(shared: dict | None, series_map: dict | None, business_key: str) -> dict:
    base = {**DEFAULT_NUMBER_SETTINGS, **(shared or {})}
    own = series_map.get(business_key) if (business_key and series_map) else None
    if own:
        return {**base, **own, 'own': True}
    return {**base, 'own': False}

def counter_key_for(type_prefix: str, series: dict, business_key: str) -> str:
    if series.get('own') and business_key:
        return f"counter_{type_prefix}@{business_key}"
    return f"counter_{type_prefix}"

def next_counter_value(current: Any, start: Any = 1) -> int:
    try:
        last = max(0, int(current))
    except (ValueError, TypeError):
        last = 0
    try:
        from_val = min(1_000_000, max(1, int(start)))
    except (ValueError, TypeError):
        from_val = 1
    return max(from_val, last + 1)

def start_for(invoice_type: str | None, number_settings: dict | None) -> int:
    if (invoice_type or 'tax-invoice') == 'tax-invoice':
        return int((number_settings or {}).get('startNumber') or 1)
    return 1

def format_doc_number(settings: dict | None, type_prefix: str, next_val: int, explicit_prefix: bool = False, fy_label: str = '') -> str:
    s = {**DEFAULT_NUMBER_SETTINGS, **(settings or {})}
    brand = str(s.get('brandPrefix') or '').strip()
    if explicit_prefix:
        pfx = type_prefix
    else:
        if brand:
            pfx = brand if type_prefix == 'INV' else f"{brand}-{type_prefix}"
        else:
            pfx = type_prefix
            
    sep = s.get('separator') or '/'
    pad = int(s.get('padDigits') or 4)
    padded = str(next_val).zfill(pad)
    
    fy = fy_label
    if s.get('fyStyle') == 'short' and fy:
        # 2026-27 -> 26-27
        if len(fy) >= 7 and fy[4] == '-':
            fy = fy[2:]
            
    if s.get('showFinYear') and fy:
        return f"{pfx}{sep}{fy}{sep}{padded}"
    return f"{pfx}{sep}{padded}"

def get_next_invoice_number(prefix: str, invoice_type: str = 'tax-invoice', business_key: str = '') -> str:
    """Atomic generation of next document number in series, updating meta.json."""
    meta = read_json(META_PATH, {})
    series_settings = meta.get('invoiceNumberSettings') or {}
    series_map = meta.get('invoiceNumberSeries') or {}
    series = number_series_for(series_settings, series_map, business_key)
    
    key = counter_key_for(prefix, series, business_key)
    start_num = start_for(invoice_type, series)
    next_val = next_counter_value(meta.get(key), start_num)
    meta[key] = next_val
    write_json_atomic(META_PATH, meta)
    
    fy_label = get_financial_year_label()
    return format_doc_number(series, prefix, next_val, fy_label=fy_label)

def advance_date(date_str: str, frequency: str, interval: int = 1, anchor_day: int | None = None) -> str:
    """Advance ISO YYYY-MM-DD date based on recurrence frequency and interval."""
    try:
        parts = [int(p) for p in date_str.split('-')[:3]]
        curr = datetime.date(parts[0], parts[1], parts[2])
    except Exception:
        return date_str
        
    n = max(1, int(interval or 1))
    if frequency == 'weekly':
        return (curr + datetime.timedelta(days=7 * n)).isoformat()
        
    months = 3 * n if frequency == 'quarterly' else (12 * n if frequency == 'yearly' else n)
    day = min(31, max(1, anchor_day or curr.day))
    
    total_months = (curr.year * 12 + curr.month - 1) + months
    new_year = total_months // 12
    new_month = (total_months % 12) + 1
    max_days = calendar.monthrange(new_year, new_month)[1]
    target_day = min(day, max_days)
    
    return datetime.date(new_year, new_month, target_day).isoformat()
