import asyncio
import json
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
from schemas.outputs import AgentReport, Indicator
from urllib.parse import urlparse
from google import genai
from pydantic import BaseModel, Field

class SourceAssessment(BaseModel):
    confidence: float = Field(description="Confidence in the assessment (0-100)")
    reasoning: str = Field(description="Overall reasoning for the source assessment")
    evidence_used: list[str] = Field(description="List of specific text snippets or findings used as evidence")
    indicators: list[dict] = Field(description="List of specific indicators found (e.g. {'id': 'KNOWN_TRUSTED_DOMAIN', 'severity': 'POSITIVE', 'description': '...'})")

class SourceCredibilityAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("SourceCredibilityAgent", message_bus)

    async def process_message(self, message: AgentMessage):
        if message.type == "ANALYZE_SOURCE":
            job_id = message.job_id
            payload = message.payload
            
            print(f"[{self.name}] Analyzing source credibility for job {job_id}")
            
            info = payload.get("info", {})
            metadata = info.get("metadata", {})
            api_key = payload.get("gemini_api_key")
            
            links = metadata.get("links", [])
            qr_codes = metadata.get("qr_codes", [])
            all_urls = links + [qr for qr in qr_codes if qr.startswith("http")]
            
            if not all_urls:
                report = AgentReport(
                    confidence=10.0,
                    reasoning="No source URLs found to evaluate.",
                    applied_indicators=[Indicator(
                        id="NO_SOURCE_INFO", severity="NEUTRAL", category="SOURCE",
                        description="Could not identify any source domains or links."
                    )]
                )
                if message.reply_to:
                    await self.send_message(
                        recipient=message.reply_to,
                        msg_type="SOURCE_CREDIBILITY_COMPLETE",
                        payload=report.model_dump(),
                        job_id=job_id,
                        reply_to=self.name
                    )
                return

            if api_key:
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are an expert domain and source credibility agent.
                    Analyze the following list of URLs for reputation, TLD trustworthiness, and typical usage in spam or fraud.
                    
                    URLs:
                    {json.dumps(all_urls)}
                    
                    Return a JSON object containing a source assessment.
                    - severity must be one of: "CRITICAL", "HIGH", "MODERATE", "LOW", "POSITIVE", "NEUTRAL"
                    """
                    def call_gemini():
                        return client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config={
                                'response_mime_type': 'application/json',
                                'response_schema': SourceAssessment,
                            },
                        )
                    loop = asyncio.get_running_loop()
                    response = await loop.run_in_executor(None, call_gemini)
                    
                    result = json.loads(response.text)
                    applied_indicators = []
                    for ind in result.get("indicators", []):
                        applied_indicators.append(Indicator(
                            id=ind.get("id", "UNKNOWN_SOURCE_IND"),
                            severity=ind.get("severity", "NEUTRAL"),
                            category="SOURCE",
                            description=ind.get("description", "Source indicator")
                        ))
                        
                    report = AgentReport(
                        confidence=result.get("confidence", 85.0),
                        reasoning=result.get("reasoning", "Source credibility analysis complete"),
                        evidence_used=result.get("evidence_used", []),
                        applied_indicators=applied_indicators
                    )
                except Exception as e:
                    print(f"[{self.name}] Gemini API error: {e}, falling back to heuristics.")
                    report = self._heuristic_analysis(all_urls)
            else:
                report = self._heuristic_analysis(all_urls)
                
            if message.reply_to:
                await self.send_message(
                    recipient=message.reply_to,
                    msg_type="SOURCE_CREDIBILITY_COMPLETE",
                    payload=report.model_dump(),
                    job_id=job_id,
                    reply_to=self.name
                )
                
    def _heuristic_analysis(self, all_urls: list) -> AgentReport:
        applied_indicators = []
        evidence_used = []
        
        trusted_tlds = [".gov", ".edu", ".mil"]
        spam_tlds = [".xyz", ".top", ".biz", ".win", ".stream"]
        
        for url in all_urls:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if not parsed.scheme == "https":
                evidence_used.append(f"Insecure connection: {url}")
                applied_indicators.append(Indicator(
                    id="INSECURE_HTTP", severity="HIGH", category="SOURCE",
                    description="Domain uses insecure HTTP connection."
                ))
                
            if any(domain.endswith(t) for t in trusted_tlds):
                evidence_used.append(f"Trusted TLD found: {domain}")
                applied_indicators.append(Indicator(
                    id="TRUSTED_TLD", severity="POSITIVE", category="SOURCE",
                    description="Domain uses a highly trusted TLD."
                ))
            
            if any(domain.endswith(t) for t in spam_tlds):
                evidence_used.append(f"Spam TLD found: {domain}")
                applied_indicators.append(Indicator(
                    id="SPAM_TLD", severity="HIGH", category="SOURCE",
                    description="Domain uses a TLD often associated with spam/fraud."
                ))
                
        return AgentReport(
            confidence=85.0,
            reasoning="Heuristic fallback source analysis.",
            evidence_used=evidence_used,
            applied_indicators=applied_indicators
        )
