from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.schema import VerificationJob, User
from api.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class HistoryItemResponse(BaseModel):
    id: str
    filename: str
    status: str
    document_type: str
    trust_score: Optional[float]
    confidence: Optional[float]
    summary: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[HistoryItemResponse])
def get_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetches all verification jobs associated with the currently authenticated user.
    Results are ordered by the most recent first.
    """
    jobs = (
        db.query(VerificationJob)
        .filter(VerificationJob.user_id == current_user.id)
        .order_by(VerificationJob.created_at.desc())
        .all()
    )
    return jobs
