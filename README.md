# Secure File Statement Delivery System

This project provides a secure system to store customer account statements as PDF files and deliver them via secure, time-limited download links using Python, FastAPI, and JWT.

## System Architecture

The system consists of three main components:

1.  **Security Module (`security.py`)**: Uses JSON Web Tokens (JWT) to generate and verify secure download links. Each token is tied to a specific file and has a configurable expiration time (defaulting to 15 minutes).
2.  **Storage Module (`storage.py`)**: Manages the persistent storage of PDF statements. It handles file operations like saving, retrieving the full path, and listing available files.
3.  **FastAPI Application (`main.py`)**: Provides a RESTful API with endpoints for:
    *   **Admin/Internal**: Uploading statements and listing existing files.
    *   **Customer/Integration**: Generating a secure download link for a specific file and downloading the file using a valid token.

## Security Model

*   **Time-limited Links**: Download links are generated using JWTs with an `exp` (expiration) claim. Once the time limit is reached, the token becomes invalid, and the file can no longer be downloaded using that link.
*   **File Isolation**: The token includes the `sub` (subject) claim, which identifies the specific file permitted for download. Users cannot use a valid token for one file to download another.
*   **Path Traversal Prevention**: All input filenames are sanitized using `os.path.basename` to ensure that file operations are restricted to the designated storage directory.
*   **Secret-based Signing**: Tokens are signed using the `HS256` algorithm with a server-side secret key. For production, the secret key is retrieved from the `SECURE_STATEMENT_SECRET_KEY` environment variable.

## Setup and Installation

### Prerequisites

*   Python 3.12+
*   `pip` (Python package installer)

### Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r statement_delivery/requirements.txt
    ```

## Usage

### Running the API Server

You can start the FastAPI server using `uvicorn`:

```bash
uvicorn statement_delivery.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can also explore the interactive API documentation at `http://127.0.0.1:8000/docs`.

### API Endpoints

*   **Upload a Statement**:
    *   `POST /upload`
    *   Example using `curl`:
        ```bash
        curl -X POST -F "file=@/path/to/statement.pdf" http://127.0.0.1:8000/upload
        ```

*   **Generate a Secure Link**:
    *   `GET /link/{filename}`
    *   Example: `GET http://127.0.0.1:8000/link/statement.pdf`
    *   Returns: `{"download_token": "your-jwt-token", "expires_in": "15 minutes"}`

*   **Download a Statement**:
    *   `GET /download/{token}`
    *   Example: `GET http://127.0.0.1:8000/download/your-jwt-token`

*   **List Statements**:
    *   `GET /statements`

## Testing

To run the automated tests, execute the following command:

```bash
pytest statement_delivery/test_main.py
```

These tests verify the full lifecycle of a statement: upload, link generation, and secure download (including validation of expired tokens).
