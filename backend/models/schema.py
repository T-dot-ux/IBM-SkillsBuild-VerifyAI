from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from models.database import Base

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    SCANNING = "SCANNING"
    EXTRACTING = "EXTRACTING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentCategory(str, enum.Enum):
    JOB_OFFER = "JOB_OFFER"
    CERTIFICATE = "CERTIFICATE"
    PAYMENT_PROOF = "PAYMENT_PROOF"
    LEGAL_DOCUMENT = "LEGAL_DOCUMENT"
    NEWS_MEDIA = "NEWS_MEDIA"
    UNKNOWN = "UNKNOWN"

class EvidenceType(str, enum.Enum):
    RED_FLAG = "RED_FLAG"
    POSITIVE_INDICATOR = "POSITIVE_INDICATOR"
    METADATA = "METADATA"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    encrypted_gemini_key = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    jobs = relationship("VerificationJob", back_populates="user", cascade="all, delete-orphan")

class VerificationJob(Base):
    __tablename__ = "verification_jobs"

    id = Column(String, primary_key=True, index=True) # UUID string
    filename = Column(String, index=True)
    original_url = Column(String, nullable=True) # Cloudinary or S3 URL
    
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    document_type = Column(Enum(DocumentCategory), default=DocumentCategory.UNKNOWN)
    
    trust_score = Column(Float, nullable=True) # 0 to 100
    confidence = Column(Float, nullable=True) # 0 to 1
    
    summary = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    investigation_context_blob = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="jobs")
    evidence = relationship("VerificationEvidence", back_populates="job", cascade="all, delete-orphan")

class VerificationEvidence(Base):
    __tablename__ = "verification_evidence"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("verification_jobs.id"))
    
    evidence_type = Column(Enum(EvidenceType))
    description = Column(Text)
    severity_or_confidence = Column(Float, nullable=True) # E.g. severity for red flags
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("VerificationJob", back_populates="evidence")

