import asyncio
from typing import Dict, Any
import json
import os
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage

class ReportGenerationAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("ReportGenerationAgent", message_bus)

    async def process_message(self, message: AgentMessage):
        if message.type == "GENERATE_REPORT":
            job_id = message.job_id
            decision_payload = message.payload
            
            self.logger.info("Generating evidence-based report.", extra={"job_id": job_id})
            
            api_key = decision_payload.get("gemini_api_key")
            final_decision = decision_payload.get("decision", decision_payload)
            
            summary = "Verification completed."
            recommendation = final_decision.get("verdict", {}).get("recommended_action", "")
            
            if api_key:
                try:
                    from google import genai
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are a Report Generation Agent.
                    Given the following Final Decision and Reasoning Tree, write a single concise paragraph (max 3 sentences) summarizing WHY this verdict was reached.
                    Focus strictly on the evidence and indicators found. Do NOT invent new facts.
                    
                    Data:
                    {json.dumps(final_decision)}
                    """
                    def call_gemini():
                        return client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                    loop = asyncio.get_running_loop()
                    response = await loop.run_in_executor(None, call_gemini)
                    summary = response.text.strip()
                except Exception as e:
                    self.logger.error(f"Failed to generate summary: {e}")
                    summary = "Automated summary generation failed. Please review the reasoning tree."
            else:
                summary = "Verification complete. Review the reasoning tree for details."
                
            if "verdict" not in final_decision:
                final_decision["verdict"] = {}
                
            final_decision["summary"] = summary
                
            report_dir = "reports"
            os.makedirs(report_dir, exist_ok=True)
            
            json_path = os.path.join(report_dir, f"{job_id}_report.json")
            with open(json_path, "w") as f:
                json.dump(final_decision, f, indent=4)
                
            if message.reply_to:
                await self.send_message(
                    recipient=message.reply_to,
                    msg_type="REPORT_GENERATED",
                    payload={"json_path": json_path, "summary": summary, "recommendation": recommendation},
                    job_id=job_id,
                    reply_to=self.name
                )
