from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from models.database import get_db, SessionLocal
from models.schema import (
    VerificationJob, JobStatus, EvidenceType,
    VerificationEvidence, DocumentCategory, User
)
from api.auth import get_current_user
from core.security import decrypt_api_key
from agents.message_bus import MessageBus
from agents.master_agent import MasterAgent
from agents.input_agent import InputIntelligenceAgent
from agents.threat_agent import ThreatDetectionAgent
from agents.source_agent import SourceCredibilityAgent
from agents.evidence_agent import EvidenceVerificationAgent
from agents.consensus_agent import ConsensusAgent
from agents.decision_agent import DecisionAgent
from agents.report_agent import ReportGenerationAgent
from agents.learning_agent import LearningAgent
from schemas.messages import AgentMessage
from schemas.outputs import InvestigationContext
import uuid
import os
import asyncio
import json

router = APIRouter()

async def process_verification_task(job_id: str, file_path: str, api_key: str = None):
    db = SessionLocal()
    bus = None
    try:
        job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.ANALYZING
        db.commit()

        # Initialize Message Bus and Agents
        bus = MessageBus(default_job_timeout=120.0)
        master = MasterAgent(bus)
        input_agent = InputIntelligenceAgent(bus)
        threat_agent = ThreatDetectionAgent(bus)
        source_agent = SourceCredibilityAgent(bus)
        evidence_agent = EvidenceVerificationAgent(bus)
        consensus_agent = ConsensusAgent(bus)
        decision_agent = DecisionAgent(bus)
        report_agent = ReportGenerationAgent(bus)
        learning_agent = LearningAgent(bus)

        # Subscribe the learning agent to broadcast events it cares about
        bus.subscribe("DECISION_COMPLETE", learning_agent)
        bus.subscribe("INPUT_PARSED", learning_agent)

        for agent in [master, input_agent, threat_agent, source_agent, evidence_agent, consensus_agent, decision_agent, report_agent, learning_agent]:
            bus.register(agent)

        await bus.start_all()

        # Create a tracked job so we can await its future
        tracker = bus.create_job(job_id, timeout=60.0)

        # Start the job
        await bus.publish(AgentMessage(
            sender="API",
            recipient="MasterAgent",
            type="START_JOB",
            payload={"data": f"File path: {file_path}", "gemini_api_key": api_key},
            job_id=job_id
        ))

        # Wait for the MasterAgent to signal completion (via polling for now,
        # since MasterAgent doesn't call bus.complete_job yet — will be
        # upgraded once MasterAgent is wired to the tracker).
        for _ in range(120):
            await asyncio.sleep(0.5)
            if job_id in master.active_jobs and master.active_jobs[job_id].get("status") == "COMPLETED":
                bus.complete_job(job_id)
                break

        if bus.get_job_status(job_id) == "COMPLETED":
            final_decision = master.active_jobs[job_id].get("decision", {})

            job.trust_score = final_decision.get("final_trust_score", 0.0)
            job.confidence = final_decision.get("confidence_meter", 0.0)

            verdict_info = final_decision.get("verdict", {})
            job.summary = final_decision.get("summary", "COMPLETED")
            job.recommendation = verdict_info.get("recommended_action", "")
            job.status = JobStatus.COMPLETED

            # Collect the timeline recorded by the message bus
            timeline = bus.get_job_timeline(job_id)

            # Serialize full InvestigationContext
            context = InvestigationContext(
                job_id=job_id,
                timeline=timeline,
                extracted_data=master.active_jobs[job_id].get("extracted_info", {}),
                agent_reports={
                    "threat": master.active_jobs[job_id].get("threat_assessment", {}),
                    "source": master.active_jobs[job_id].get("source_credibility", {}),
                    "evidence": master.active_jobs[job_id].get("evidence", {})
                },
                final_decision=final_decision,
                status="COMPLETED"
            )
            job.investigation_context_blob = context.model_dump_json()

            # Save Evidence (Reasoning Tree mapping)
            for leaf in final_decision.get("reasoning_tree", []):
                db.add(VerificationEvidence(
                    job_id=job.id,
                    evidence_type=EvidenceType.RED_FLAG if leaf.get("impact") in ["CRITICAL", "HIGH"] else EvidenceType.METADATA,
                    description=f"[{leaf.get('agent')}] {leaf.get('finding')}",
                    severity_or_confidence=1.0 if leaf.get("impact") == "CRITICAL" else 0.5,
                ))
            db.commit()
        else:
            bus.fail_job(job_id, "Agent pipeline timed out")
            job.status = JobStatus.FAILED
            job.summary = "Agent pipeline timed out."
            db.commit()

    except Exception as e:
        db.rollback()
        job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.summary = f"Unexpected pipeline error: {e}"
            db.commit()
        print(f"[verify] Unexpected task error for job {job_id}: {e}")
    finally:
        if bus:
            await bus.shutdown(timeout=5.0)
        db.close()


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job_id = str(uuid.uuid4())
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    job = VerificationJob(
        id=job_id,
        filename=file.filename,
        original_url=file_path,
        status=JobStatus.PENDING,
        user_id=current_user.id
    )
    db.add(job)
    db.commit()

    api_key = None
    if current_user.encrypted_gemini_key:
        try:
            api_key = decrypt_api_key(current_user.encrypted_gemini_key)
        except Exception as e:
            print(f"[verify] Decryption of API key failed: {e}")

    background_tasks.add_task(process_verification_task, job.id, file_path, api_key)

    return {"job_id": job.id, "status": job.status}


@router.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VerificationJob).filter(VerificationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # If completed, serve the exact APIResponse contract
    if job.status == JobStatus.COMPLETED and job.investigation_context_blob:
        try:
            context = json.loads(job.investigation_context_blob)
            decision = context.get("final_decision", {})
            return {
                "job_id": job.id,
                "status": job.status,
                "trust_score": decision.get("final_trust_score", 0.0), # For frontend backwards compatibility
                "confidence": decision.get("confidence_meter", 0.0), # For frontend backwards compatibility
                "summary": decision.get("summary", "Verification complete."),
                "recommendation": decision.get("verdict", {}).get("recommended_action", ""),
                "final_trust_score": decision.get("final_trust_score", 0.0),
                "confidence_meter": decision.get("confidence_meter", 0.0),
                "verdict": decision.get("verdict", {}),
                "trust_breakdown": decision.get("trust_breakdown", {}),
                "reasoning_tree": decision.get("reasoning_tree", []),
                "agent_timeline": context.get("timeline", [])
            }
        except Exception as e:
            print(f"Error parsing blob: {e}")
            pass

    # Fallback for pending / failed or old jobs
    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "document_type": job.document_type,
        "trust_score": job.trust_score,
        "confidence": job.confidence,
        "summary": job.summary,
        "recommendation": job.recommendation
    }
