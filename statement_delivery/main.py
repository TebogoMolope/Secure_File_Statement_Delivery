from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
import os

# Import our custom modules
try:
    from security import create_download_token, verify_download_token, ACCESS_TOKEN_EXPIRE_MINUTES
    from storage import save_statement, get_statement_path, list_statements, setup_storage
except ImportError:
    from .security import create_download_token, verify_download_token, ACCESS_TOKEN_EXPIRE_MINUTES
    from .storage import save_statement, get_statement_path, list_statements, setup_storage

app = FastAPI(title="Secure File Statement Delivery API")

# Ensure storage is ready
@app.on_event("startup")
async def startup_event():
    setup_storage()

@app.post("/upload", status_code=201)
async def upload_statement(file: UploadFile = File(...)):
    """
    Upload a Statement
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    content = await file.read()
    save_statement(file.filename, content)
    return {"message": f"Statement '{file.filename}' uploaded successfully."}

@app.get("/link/{filename}")
async def generate_link(filename: str):
    """
    Generate a Secure Link
    """
    path = get_statement_path(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Statement not found.")
    
    token = create_download_token(filename)
    # In a real-world application, this would be a complete URL like:
    # https://api.example.com/download/{token}
    return {"download_token": token, "expires_in": f"{ACCESS_TOKEN_EXPIRE_MINUTES} minutes"}

@app.get("/download/{token}")
async def download_statement(token: str):
    """
    Download a Statement
    """
    filename = verify_download_token(token)
    if not filename:
        raise HTTPException(status_code=401, detail="Invalid or expired download link.")
    
    path = get_statement_path(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Statement file no longer exists.")
    
    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=filename
    )

@app.get("/statements", response_model=List[str])
async def list_available_statements():
    """
    List Statements
    """
    return list_statements()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
