import asyncio
import json
import re
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
from schemas.outputs import AgentReport, Indicator
from google import genai
from pydantic import BaseModel, Field

class EvidenceAssessment(BaseModel):
    confidence: float = Field(description="Confidence in the assessment (0-100)")
    reasoning: str = Field(description="Overall reasoning for the evidence assessment")
    evidence_used: list[str] = Field(description="List of specific text snippets or findings used as evidence")
    indicators: list[dict] = Field(description="List of specific indicators found (e.g. {'id': 'VERIFIED_FACT', 'severity': 'POSITIVE', 'description': '...'})")

class EvidenceVerificationAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("EvidenceVerificationAgent", message_bus)

    async def process_message(self, message: AgentMessage):
        if message.type == "GATHER_EVIDENCE":
            job_id = message.job_id
            payload = message.payload
            
            print(f"[{self.name}] Gathering evidence for job {job_id}")
            
            info = payload.get("info", {})
            raw_text = info.get("raw_text", "")
            api_key = payload.get("gemini_api_key")
            
            if api_key and raw_text:
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are an expert fact-checking and evidence verification agent.
                    Analyze the following text. Extract any claims, facts, numbers, dates, or contact info and verify them for internal consistency, logical sense, and common scam tropes.
                    
                    Text:
                    {raw_text}
                    
                    Return a JSON object containing an evidence assessment.
                    - severity must be one of: "CRITICAL", "HIGH", "MODERATE", "LOW", "POSITIVE", "NEUTRAL"
                    """
                    def call_gemini():
                        return client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config={
                                'response_mime_type': 'application/json',
                                'response_schema': EvidenceAssessment,
                            },
                        )
                    loop = asyncio.get_running_loop()
                    response = await loop.run_in_executor(None, call_gemini)
                    
                    result = json.loads(response.text)
                    applied_indicators = []
                    for ind in result.get("indicators", []):
                        applied_indicators.append(Indicator(
                            id=ind.get("id", "UNKNOWN_EVIDENCE_IND"),
                            severity=ind.get("severity", "NEUTRAL"),
                            category="EVIDENCE",
                            description=ind.get("description", "Evidence indicator")
                        ))
                        
                    report = AgentReport(
                        confidence=result.get("confidence", 85.0),
                        reasoning=result.get("reasoning", "Evidence analysis complete"),
                        evidence_used=result.get("evidence_used", []),
                        applied_indicators=applied_indicators
                    )
                except Exception as e:
                    print(f"[{self.name}] Gemini API error: {e}, falling back to heuristics.")
                    report = self._heuristic_analysis(raw_text)
            else:
                report = self._heuristic_analysis(raw_text)
            
            if message.reply_to:
                await self.send_message(
                    recipient=message.reply_to,
                    msg_type="EVIDENCE_COLLECTED",
                    payload=report.model_dump(),
                    job_id=job_id,
                    reply_to=self.name
                )
                
    def _heuristic_analysis(self, raw_text: str) -> AgentReport:
        applied_indicators = []
        evidence_used = []
        
        if len(raw_text) > 1000:
            evidence_used.append("Document contains substantial text to evaluate.")
            applied_indicators.append(Indicator(
                id="SUBSTANTIAL_TEXT", severity="POSITIVE", category="EVIDENCE",
                description="Sufficient text length for detailed analysis."
            ))
        elif len(raw_text) < 50:
            evidence_used.append("Document contains very little text.")
            applied_indicators.append(Indicator(
                id="SPARSE_TEXT", severity="LOW", category="EVIDENCE",
                description="Very sparse textual evidence."
            ))
            
        has_numbers = bool(re.search(r'\d+', raw_text))
        has_emails = bool(re.search(r'[\w\.-]+@[\w\.-]+', raw_text))
        
        if has_numbers or has_emails:
            evidence_used.append("Verifiable facts (numbers, contact info) found in text.")
            applied_indicators.append(Indicator(
                id="VERIFIABLE_FACTS", severity="POSITIVE", category="EVIDENCE",
                description="Contains structured contact info or numerical data."
            ))
        else:
            evidence_used.append("Lacks specific verifiable facts.")
            
        confidence = 85.0
        if len(raw_text) < 10:
            confidence -= 40.0
            
        return AgentReport(
            confidence=confidence,
            reasoning="Cross-referenced text structure and density to gauge evidence quality.",
            evidence_used=evidence_used,
            applied_indicators=applied_indicators
        )
