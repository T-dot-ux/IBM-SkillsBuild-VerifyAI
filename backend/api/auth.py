from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import SessionLocal
from models.schema import User
from core.security import create_access_token, decode_token, encrypt_api_key
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import google.generativeai as genai

router = APIRouter()

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AuthRequest(BaseModel):
    username: str
    gemini_api_key: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/login", response_model=Token)
async def login(request: AuthRequest, db: Session = Depends(get_db)):
    if not request.username or not request.gemini_api_key:
        raise HTTPException(status_code=400, detail="Username and API Key are required.")
        
    # Verify the API key by trying to configure and list models
    try:
        genai.configure(api_key=request.gemini_api_key)
        # Just a quick check to see if the key is valid
        list(genai.list_models())
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Gemini API Key: {str(e)}")

    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        user = User(username=request.username)
        db.add(user)
        
    user.encrypted_gemini_key = encrypt_api_key(request.gemini_api_key)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "has_api_key": current_user.encrypted_gemini_key is not None
    }
