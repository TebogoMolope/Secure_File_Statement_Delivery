import os
import shutil
from pathlib import Path
from typing import Optional

# Storage directory for PDF statements
STORAGE_DIR = Path("statement_delivery/storage")

def setup_storage():
    """
    Setup Storage
    """
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize Filename
    """
    return os.path.basename(filename)

def save_statement(filename: str, content: bytes) -> str:
    """
    Save Statement
    """
    setup_storage()
    # Sanitize the filename to prevent directory traversal
    safe_filename = sanitize_filename(filename)
    file_path = STORAGE_DIR / safe_filename
    with open(file_path, "wb") as f:
        f.write(content)
    return str(file_path)

def get_statement_path(filename: str) -> Optional[Path]:
    """
    Get Statement Path
    """
    # Sanitize the filename to prevent directory traversal
    safe_filename = sanitize_filename(filename)
    file_path = STORAGE_DIR / safe_filename
    if file_path.exists() and file_path.is_file():
        return file_path
    return None

def list_statements() -> list[str]:
    """
    List Statements
    """
    if not STORAGE_DIR.exists():
        return []
    return [f.name for f in STORAGE_DIR.glob("*.pdf")]
