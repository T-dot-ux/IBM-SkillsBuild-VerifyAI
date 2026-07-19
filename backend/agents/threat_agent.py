import asyncio
import json
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
from schemas.outputs import AgentReport, Indicator
from urllib.parse import urlparse
from google import genai
from pydantic import BaseModel, Field

class ThreatAssessment(BaseModel):
    confidence: float = Field(description="Confidence in the assessment (0-100)")
    reasoning: str = Field(description="Overall reasoning for the threat assessment")
    evidence_used: list[str] = Field(description="List of specific text snippets or findings used as evidence")
    indicators: list[dict] = Field(description="List of specific threat indicators found (e.g. {'id': 'BRAND_SPOOFING', 'severity': 'CRITICAL', 'description': '...'})")

class ThreatDetectionAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("ThreatDetectionAgent", message_bus)

    async def process_message(self, message: AgentMessage):
        if message.type == "ANALYZE_THREATS":
            job_id = message.job_id
            api_key = message.payload.get("gemini_api_key")
            info = message.payload.get("info", {})
            raw_text = info.get("raw_text", "").lower()
            metadata = info.get("metadata", {})
            
            print(f"[{self.name}] Analyzing threats for job {job_id}")
            
            if api_key and (raw_text or metadata.get("links")):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are an expert cybersecurity threat detection agent.
                    Analyze the following content and extracted metadata for phishing attempts, scams, malicious links, credential harvesting, and suspicious patterns.
                    
                    Raw Text:
                    {raw_text}
                    
                    Metadata (Links, QR Codes, Anomalies):
                    {json.dumps(metadata)}
                    
                    Return a JSON object containing a threat assessment. 
                    - severity must be one of: "CRITICAL", "HIGH", "MODERATE", "LOW", "NEUTRAL"
                    """
                    def call_gemini():
                        return client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config={
                                'response_mime_type': 'application/json',
                                'response_schema': ThreatAssessment,
                            },
                        )
                    loop = asyncio.get_running_loop()
                    response = await loop.run_in_executor(None, call_gemini)
                    
                    result = json.loads(response.text)
                    applied_indicators = []
                    for ind in result.get("indicators", []):
                        applied_indicators.append(Indicator(
                            id=ind.get("id", "UNKNOWN_THREAT"),
                            severity=ind.get("severity", "MODERATE"),
                            category="THREAT",
                            description=ind.get("description", "Potential threat detected")
                        ))
                        
                    report = AgentReport(
                        confidence=result.get("confidence", 85.0),
                        reasoning=result.get("reasoning", "Threat analysis complete"),
                        evidence_used=result.get("evidence_used", []),
                        applied_indicators=applied_indicators
                    )
                except Exception as e:
                    print(f"[{self.name}] Gemini API error: {e}, falling back to heuristics.")
                    report = self._heuristic_analysis(raw_text, metadata)
            else:
                report = self._heuristic_analysis(raw_text, metadata)
                
            if message.reply_to:
                await self.send_message(
                    recipient=message.reply_to,
                    msg_type="THREAT_ASSESSMENT_COMPLETE",
                    payload=report.model_dump(),
                    job_id=job_id,
                    reply_to=self.name
                )

    def _heuristic_analysis(self, raw_text: str, metadata: dict) -> AgentReport:
        applied_indicators = []
        evidence_used = []
        
        has_credential_harvesting = False
        for qr in metadata.get("qr_codes", []):
            if qr.startswith("http://") or qr.startswith("https://"):
                domain = urlparse(qr).netloc
                if any(bad_ext in domain for bad_ext in [".xyz", ".biz", ".top", ".info", ".win"]):
                    evidence_used.append(f"QR code points to suspicious domain: {domain}")
                    applied_indicators.append(Indicator(
                        id="SUSPICIOUS_QR_LINK",
                        severity="CRITICAL",
                        category="THREAT",
                        description=f"QR Code points to low reputation domain ({domain})"
                    ))
        
        for link in metadata.get("links", []):
            domain = urlparse(link).netloc.lower()
            brand_spoofs = ["paypa1", "amaz0n", "google-security", "verify-apple", "microsoft-support"]
            if any(spoof in domain for spoof in brand_spoofs):
                has_brand_spoofing = True
                evidence_used.append(f"Brand spoofing in URL: {domain}")
                applied_indicators.append(Indicator(
                    id="BRAND_SPOOFING",
                    severity="CRITICAL",
                    category="THREAT",
                    description=f"Domain {domain} attempts to imitate a known brand."
                ))
        
        fraud_keywords = {
            "security fee": ("UPFRONT_FEE", "CRITICAL", "Upfront fee request (job scam indicator)."),
            "deposit money": ("DEPOSIT_REQUEST", "CRITICAL", "Request for deposit or advance transfer.")
        }
        for kw, (ind_id, sev, desc) in fraud_keywords.items():
            if kw in raw_text:
                evidence_used.append(f"Text matches fraud pattern: '{kw}'")
                applied_indicators.append(Indicator(
                    id=ind_id, severity=sev, category="THREAT", description=desc
                ))
                
        return AgentReport(
            confidence=85.0,
            reasoning="Heuristic fallback threat analysis.",
            evidence_used=evidence_used,
            applied_indicators=applied_indicators
        )
