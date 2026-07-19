import asyncio
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
from schemas.outputs import FinalDecision

class MasterAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("MasterAgent", message_bus)
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        # Stores collected data for each job

    async def process_message(self, message: AgentMessage):
        job_id = message.job_id
        msg_type = message.type
        payload = message.payload

        if msg_type == "START_JOB":
            print(f"[MasterAgent] Starting job {job_id}")
            self.active_jobs[job_id] = {
                "input_data": payload.get("data"),
                "status": "PROCESSING",
                "gemini_api_key": payload.get("gemini_api_key"),
                "extracted_info": None,
                "threat_assessment": None,
                "source_credibility": None,
                "evidence": None,
                "decision": None
            }
            # Step 1: Delegate to Input Agent
            await self.send_message(
                recipient="InputIntelligenceAgent",
                msg_type="EXTRACT_INFO",
                payload={"data": payload.get("data"), "gemini_api_key": payload.get("gemini_api_key")},
                job_id=job_id,
                reply_to="MasterAgent"
            )

        elif msg_type == "INFO_EXTRACTED":
            print(f"[MasterAgent] Info extracted for job {job_id}")
            self.active_jobs[job_id]["extracted_info"] = payload
            
            # Step 2: Parallel Dispatch to Threat and Source Agents
            await self.send_message(
                recipient="ThreatDetectionAgent",
                msg_type="ANALYZE_THREATS",
                payload={"info": payload, "gemini_api_key": self.active_jobs[job_id].get("gemini_api_key")},
                job_id=job_id,
                reply_to="MasterAgent"
            )
            await self.send_message(
                recipient="SourceCredibilityAgent",
                msg_type="ANALYZE_SOURCE",
                payload={"info": payload, "gemini_api_key": self.active_jobs[job_id].get("gemini_api_key")},
                job_id=job_id,
                reply_to="MasterAgent"
            )

        elif msg_type == "THREAT_ASSESSMENT_COMPLETE":
            self.active_jobs[job_id]["threat_assessment"] = payload
            await self.check_evidence_phase(job_id)

        elif msg_type == "SOURCE_CREDIBILITY_COMPLETE":
            self.active_jobs[job_id]["source_credibility"] = payload
            await self.check_evidence_phase(job_id)

        elif msg_type == "EVIDENCE_COLLECTED":
            self.active_jobs[job_id]["evidence"] = payload
            
            job_data = self.active_jobs[job_id]
            reports_for_validation = {
                "ThreatAgent": job_data["threat_assessment"],
                "SourceAgent": job_data["source_credibility"],
                "EvidenceAgent": job_data["evidence"]
            }
            
            from core.governance import ValidationEngine
            from schemas.outputs import AgentReport
            
            parsed_reports = {}
            for name, r_data in reports_for_validation.items():
                if r_data:
                    parsed_reports[name] = AgentReport(**r_data)
                    
            is_valid, reason = ValidationEngine.validate_context(parsed_reports)
            
            if not is_valid:
                print(f"[MasterAgent] Validation failed for job {job_id}: {reason}. Routing to Consensus.")
                await self.send_message(
                    recipient="ConsensusAgent",
                    msg_type="RESOLVE_CONFLICT",
                    payload={"reports": reports_for_validation, "gemini_api_key": job_data.get("gemini_api_key")},
                    job_id=job_id,
                    reply_to="MasterAgent"
                )
            else:
                await self.send_message(
                    recipient="DecisionAgent",
                    msg_type="MAKE_DECISION",
                    payload={
                        "reports": reports_for_validation,
                        "gemini_api_key": job_data.get("gemini_api_key")
                    },
                    job_id=job_id,
                    reply_to="MasterAgent"
                )

        elif msg_type == "CONSENSUS_COMPLETE":
            resolved = payload.get("resolved_report")
            self.active_jobs[job_id]["threat_assessment"] = None
            self.active_jobs[job_id]["source_credibility"] = None
            self.active_jobs[job_id]["evidence"] = resolved
            
            job_data = self.active_jobs[job_id]
            await self.send_message(
                recipient="DecisionAgent",
                msg_type="MAKE_DECISION",
                payload={
                    "reports": {"ConsensusAgent": resolved},
                    "gemini_api_key": job_data.get("gemini_api_key")
                },
                job_id=job_id,
                reply_to="MasterAgent"
            )

        elif msg_type == "DECISION_COMPLETE":
            self.active_jobs[job_id]["decision"] = payload
            # Step 5: Report Generation
            await self.send_message(
                recipient="ReportGenerationAgent",
                msg_type="GENERATE_REPORT",
                payload=payload,
                job_id=job_id,
                reply_to="MasterAgent"
            )

        elif msg_type == "REPORT_GENERATED":
            self.active_jobs[job_id]["report"] = payload
            self.active_jobs[job_id]["status"] = "COMPLETED"
            print(f"[MasterAgent] Job {job_id} COMPLETED. Reports generated at {payload.get('json_path')}")
            
    async def check_evidence_phase(self, job_id: str):
        job = self.active_jobs[job_id]
        if job["threat_assessment"] is not None and job["source_credibility"] is not None:
            # Step 3: Dispatch to Evidence Agent now that context is gathered
            await self.send_message(
                recipient="EvidenceVerificationAgent",
                msg_type="GATHER_EVIDENCE",
                payload={
                    "info": job["extracted_info"],
                    "threat": job["threat_assessment"],
                    "source": job["source_credibility"],
                    "gemini_api_key": job.get("gemini_api_key")
                },
                job_id=job_id,
                reply_to="MasterAgent"
            )

