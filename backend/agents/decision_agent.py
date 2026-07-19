import asyncio
import json
import statistics
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
from schemas.outputs import FinalDecision, VerdictInfo, AgentReport, InvestigationContext, TimelineEvent
from utils.config import settings

class DecisionAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("DecisionAgent", message_bus)

    async def process_message(self, message: AgentMessage):
        if message.type == "MAKE_DECISION":
            job_id = message.job_id
            payload = message.payload
            
            print(f"[{self.name}] Making AI-powered consensus decision for job {job_id}")
            
            reports_data = payload.get("reports", {})
            
            from schemas.outputs import AgentReport
            from core.governance import DecisionEngine
            
            parsed_reports = {}
            for name, r_data in reports_data.items():
                if r_data:
                    parsed_reports[name] = AgentReport(**r_data)
                    
            decision_dict = DecisionEngine.compute_decision(parsed_reports)
            
            from schemas.outputs import FinalDecision
            final_decision = FinalDecision(**decision_dict)
            
            if message.reply_to:
                await self.send_message(
                    recipient=message.reply_to,
                    msg_type="DECISION_COMPLETE",
                    payload=final_decision.model_dump(),
                    job_id=job_id,
                    reply_to=self.name
                )
