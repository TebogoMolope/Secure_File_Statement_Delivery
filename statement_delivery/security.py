import jwt
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

# Pull the secret key from an environment variable
SECRET_KEY = os.getenv("SECURE_STATEMENT_SECRET_KEY", "your-dev-secret-key-for-secure-statements")
ALGORITHM = "HS256"
# Default expiration time is 15 minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_download_token(filename: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a Secure Token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": filename}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_download_token(token: str) -> Optional[str]:
    """
    Verify a Secure Token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        filename: str = payload.get("sub")
        if filename is None:
            return None
        return filename
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None
