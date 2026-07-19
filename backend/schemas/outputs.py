from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime, timezone

class Indicator(BaseModel):
    id: str
    severity: Literal["CRITICAL", "HIGH", "MODERATE", "LOW", "POSITIVE", "NEUTRAL"]
    category: Literal["THREAT", "SOURCE", "EVIDENCE", "TECH", "CONSENSUS"]
    description: str

class AgentReport(BaseModel):
    confidence: float = Field(..., ge=0.0, le=100.0)
    reasoning: str
    evidence_used: List[str] = []
    applied_indicators: List[Indicator] = []

class TimelineEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent: str
    action: str

class VerdictInfo(BaseModel):
    level: Literal["VERIFIED", "SAFE", "CAUTION", "SUSPICIOUS", "HIGH RISK", "FRAUDULENT", "INVALID"]
    mascot_state: str
    color: str
    recommended_action: str

class FinalDecision(BaseModel):
    final_trust_score: float
    confidence_meter: float
    verdict: VerdictInfo
    trust_breakdown: Dict[str, float]
    reasoning_tree: List[Dict[str, Any]]

class ExtractedData(BaseModel):
    raw_text: str = ""
    metadata: Dict[str, Any] = {}
    parsed_urls: List[str] = []

class InvestigationContext(BaseModel):
    job_id: str
    timeline: List[TimelineEvent] = []
    extracted_data: ExtractedData = Field(default_factory=ExtractedData)
    agent_reports: Dict[str, AgentReport] = {}
    final_decision: Optional[FinalDecision] = None
    status: str = "PROCESSING" # "PROCESSING", "COMPLETE", "FAILED"

class APIResponse(BaseModel):
    job_id: str
    final_trust_score: float
    confidence_meter: float
    verdict: VerdictInfo
    trust_breakdown: Dict[str, float]
    reasoning_tree: List[Dict[str, Any]]
    agent_timeline: List[TimelineEvent]
