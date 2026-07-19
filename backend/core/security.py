import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt
from cryptography.fernet import Fernet
import base64

# Secret keys (In production, these MUST be in .env)
# Using a static fallback for the capstone demo.
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-capstone-key-do-not-use-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

# For API Key encryption
# Fernet requires a 32 url-safe base64-encoded byte key.
FERNET_KEY = os.getenv("FERNET_KEY", base64.urlsafe_b64encode(b"0123456789abcdef0123456789abcdef"))
fernet = Fernet(FERNET_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. Password Hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# 2. JWT Generation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# 3. API Key Encryption (Fernet)
def encrypt_api_key(plain_api_key: str) -> str:
    if not plain_api_key:
        return None
    return fernet.encrypt(plain_api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: str) -> str:
    if not encrypted_api_key:
        return None
    return fernet.decrypt(encrypted_api_key.encode()).decode()
