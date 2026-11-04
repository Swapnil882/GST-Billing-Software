import os
import re
import urllib.parse
from pathlib import Path

def safe_file_name(val) -> str:
    """Safe filename from ID by replacing forbidden filename characters."""
    if val is None:
        return "untitled"
    return re.sub(r'[/\\:*?"<>|]', '_', str(val))

def safe_path_segment(user_input, fallback: str = "Untitled") -> str:
    """
    Path-traversal-safe user-string -> single path segment.
    Strips path separators, drive letters, control characters, and ..
    """
    if user_input is None:
        return fallback
    try:
        s = urllib.parse.unquote(str(user_input))
    except Exception:
        s = str(user_input)
    
    # Strip reserved/control characters
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', s)
    # Squash .. and ...
    s = re.sub(r'\.{2,}', '-', s)
    # Trim leading/trailing dot and whitespace
    s = s.strip('. ')
    # Cap length
    s = s[:120]
    return s if s else fallback

def is_path_inside(resolved: str | Path, root: str | Path) -> bool:
    """Enforce that resolved path lives strictly inside root directory."""
    resolved_path = Path(resolved).resolve()
    root_path = Path(root).resolve()
    
    if os.name == 'nt':
        r_str = str(root_path).lower()
        p_str = str(resolved_path).lower()
    else:
        r_str = str(root_path)
        p_str = str(resolved_path)
        
    sep = os.sep
    return p_str == r_str or p_str.startswith(r_str + sep)
