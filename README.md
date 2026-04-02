# Secure File Statement Delivery System

This project provides a secure system to store customer account statements as PDF files and deliver them via secure, time-limited download links using Python, FastAPI, and JWT.

## Setup and Installation

### Prerequisites

* Python 3.12+
* `pip` (Python package installer)

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

The API will be available at `http://127.0.0.1:8000`.

### Docker

#### Build the Image:
```bash
docker build -t secure-statement-delivery .
```

#### Run the Container:
```bash
docker run -p 8000:8000 secure-statement-delivery
```

## Testing

To run the automated tests, execute the following command:

```bash
pytest --import-mode=importlib statement_delivery/test_main.py
```
