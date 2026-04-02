import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
import time
import os
import shutil

# Import our FastAPI app and custom modules
from .main import app
from .security import create_download_token, SECRET_KEY, ALGORITHM
import jwt

client = TestClient(app)

# Ensure a clean slate for storage during tests
TEST_STORAGE_DIR = "statement_delivery/storage"

@pytest.fixture(autouse=True)
def clean_storage():
    """
    Clean Storage
    """
    if os.path.exists(TEST_STORAGE_DIR):
        shutil.rmtree(TEST_STORAGE_DIR)
    os.makedirs(TEST_STORAGE_DIR)
    yield
    # No cleanup after test so we can inspect if needed (or uncomment to cleanup)
    # shutil.rmtree(TEST_STORAGE_DIR)

def test_upload_statement():
    """
    Test Upload Statement
    """
    filename = "test_statement.pdf"
    content = b"%PDF-1.4 dummy pdf content"
    
    response = client.post(
        "/upload",
        files={"file": (filename, content, "application/pdf")}
    )
    
    assert response.status_code == 201
    assert filename in response.json()["message"]
    assert os.path.exists(os.path.join(TEST_STORAGE_DIR, filename))

def test_upload_invalid_file_type():
    """
    Test Upload Invalid File Type
    """
    filename = "test.txt"
    content = b"not a pdf"
    
    response = client.post(
        "/upload",
        files={"file": (filename, content, "text/plain")}
    )
    
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]

def test_generate_and_download_statement():
    """
    Test Generate and Download Statement
    """
    # 1. Upload
    filename = "download_test.pdf"
    content = b"%PDF-1.4 dummy content"
    client.post("/upload", files={"file": (filename, content, "application/pdf")})
    
    # 2. Generate link
    response = client.get(f"/link/{filename}")
    assert response.status_code == 200
    token = response.json()["download_token"]
    
    # 3. Download using token
    download_response = client.get(f"/download/{token}")
    assert download_response.status_code == 200
    assert download_response.content == content
    assert download_response.headers["content-type"] == "application/pdf"

def test_download_with_invalid_token():
    """
    Test Download With Invalid Token
    """
    invalid_token = "invalid.token.string"
    
    response = client.get(f"/download/{invalid_token}")
    
    assert response.status_code == 401
    assert "Invalid or expired" in response.json()["detail"]

def test_download_with_expired_token():
    """
    Test Download With Expired Token
    """
    filename = "expired_test.pdf"
    content = b"%PDF-1.4 expired"
    client.post("/upload", files={"file": (filename, content, "application/pdf")})
    
    # Create an already expired token (using security.py's logic directly for the test)
    # or use create_download_token with a negative timedelta
    expired_token = create_download_token(filename, expires_delta=timedelta(minutes=-5))
    
    response = client.get(f"/download/{expired_token}")
    
    assert response.status_code == 401
    assert "Invalid or expired" in response.json()["detail"]

def test_list_statements():
    """
    Test List Statements
    """
    # Upload two files
    client.post("/upload", files={"file": ("file1.pdf", b"%PDF-1.4 1", "application/pdf")})
    client.post("/upload", files={"file": ("file2.pdf", b"%PDF-1.4 2", "application/pdf")})
    
    response = client.get("/statements")
    
    assert response.status_code == 200
    statements = response.json()
    assert "file1.pdf" in statements
    assert "file2.pdf" in statements
    assert len(statements) == 2

def test_path_traversal_prevention():
    """
    Test Path Traversal Prevention
    """
    # Attempt to upload with a traversal filename (non-PDF)
    traversal_filename = "../malicious.txt"
    content = b"malicious content"
    
    # The application should fail because it's not a PDF, even if sanitized to 'malicious.txt'
    response = client.post(
        "/upload",
        files={"file": (traversal_filename, content, "application/pdf")}
    )
    
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]
    
    # Re-run with .pdf but traversal path
    traversal_pdf = "../malicious.pdf"
    response = client.post(
        "/upload",
        files={"file": (traversal_pdf, content, "application/pdf")}
    )
    assert response.status_code == 201
    assert "malicious.pdf" in response.json()["message"]
    
    # Verify it's NOT in the parent directory but IN the storage directory
    assert not os.path.exists("statement_delivery/malicious.pdf")
    assert os.path.exists("statement_delivery/storage/malicious.pdf")
