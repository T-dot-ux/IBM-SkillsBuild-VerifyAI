import asyncio
import json
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
from schemas.outputs import AgentReport, Indicator
from google import genai
from pydantic import BaseModel, Field

class ConsensusResolution(BaseModel):
    confidence: float = Field(description="Confidence in the resolution (0-100)")
    reasoning: str = Field(description="Explanation of how the conflict was resolved")
    resolved_indicators: list[dict] = Field(description="List of indicators that remain valid after conflict resolution")

class ConsensusAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("ConsensusAgent", message_bus)

    async def process_message(self, message: AgentMessage):
        if message.type == "RESOLVE_CONFLICT":
            job_id = message.job_id
            payload = message.payload
            
            print(f"[{self.name}] Resolving conflicting reports for job {job_id}")
            
            reports = payload.get("reports", {})
            api_key = payload.get("gemini_api_key")
            
            if api_key:
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are a Consensus Resolution agent for a digital trust platform.
                    The specialized agents have returned conflicting reports about a document/link, triggering a validation failure.
                    Analyze the conflicting indicators below and determine the ground truth.
                    
                    Conflicting Reports:
                    {json.dumps(reports)}
                    
                    Rules:
                    1. If a CRITICAL or HIGH threat is identified (e.g. phishing link, brand spoofing), it almost always overrides any POSITIVE source credibility or evidence.
                    2. Retain all non-conflicting indicators.
                    3. Filter out any POSITIVE indicators that are invalidated by the threat (e.g., if a phishing page has 'verified contact info', the contact info is part of the scam and should be discarded).
                    
                    Return a JSON object containing the resolved assessment.
                    - resolved_indicators must include the 'id', 'severity', 'category', and 'description' for each indicator.
                    """
                    def call_gemini():
                        return client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config={
                                'response_mime_type': 'application/json',
                                'response_schema': ConsensusResolution,
                            },
                        )
                    loop = asyncio.get_running_loop()
                    response = await loop.run_in_executor(None, call_gemini)
                    
                    result = json.loads(response.text)
                    applied_indicators = []
                    for ind in result.get("resolved_indicators", []):
                        applied_indicators.append(Indicator(
                            id=ind.get("id", "UNKNOWN"),
                            severity=ind.get("severity", "NEUTRAL"),
                            category="CONSENSUS",
                            description=ind.get("description", "Resolved indicator")
                        ))
                        
                    report = AgentReport(
                        confidence=result.get("confidence", 85.0),
                        reasoning=result.get("reasoning", "Conflict resolved via AI consensus."),
                        applied_indicators=applied_indicators
                    )
                except Exception as e:
                    print(f"[{self.name}] Gemini API error: {e}, falling back to heuristics.")
                    report = self._heuristic_analysis(reports)
            else:
                report = self._heuristic_analysis(reports)
                
            if message.reply_to:
                await self.send_message(
                    recipient=message.reply_to,
                    msg_type="CONSENSUS_COMPLETE",
                    payload={"resolved_report": report.model_dump()},
                    job_id=job_id,
                    reply_to=self.name
                )
                
    def _heuristic_analysis(self, reports: dict) -> AgentReport:
        # Heuristic resolution: CRITICAL threats override POSITIVE evidence.
        applied_indicators = []
        has_critical = False
        
        # Collect all
        for agent_name, report_data in reports.items():
            for ind in report_data.get("applied_indicators", []):
                if ind.get("severity") == "CRITICAL":
                    has_critical = True
                applied_indicators.append(ind)
                
        # Filter
        resolved = []
        for ind in applied_indicators:
            if has_critical and ind.get("severity") == "POSITIVE":
                continue # Discard positive if critical threat exists
            resolved.append(Indicator(**ind))
            
        return AgentReport(
            confidence=80.0,
            reasoning="Conflict resolved by prioritizing risk indicators over positive claims.",
            applied_indicators=resolved
        )
