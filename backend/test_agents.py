import asyncio
import json
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

async def main():
    bus = MessageBus(default_job_timeout=60.0)
    master = MasterAgent(bus)
    input_agent = InputIntelligenceAgent(bus)
    threat_agent = ThreatDetectionAgent(bus)
    source_agent = SourceCredibilityAgent(bus)
    evidence_agent = EvidenceVerificationAgent(bus)
    consensus_agent = ConsensusAgent(bus)
    decision_agent = DecisionAgent(bus)
    report_agent = ReportGenerationAgent(bus)
    learning_agent = LearningAgent(bus)

    # Subscribe learning agent to broadcast events
    bus.subscribe("DECISION_COMPLETE", learning_agent)
    bus.subscribe("INPUT_PARSED", learning_agent)

    for agent in [master, input_agent, threat_agent, source_agent, evidence_agent, consensus_agent, decision_agent, report_agent, learning_agent]:
        bus.register(agent)

    await bus.start_all()
    job_id = "test-job-12345"

    # Create a tracked job
    tracker = bus.create_job(job_id, timeout=30.0)

    test_payload = {
        "data": "This is a test document containing a malicious link: http://paypa1-security-update.xyz. You must pay a security fee immediately.",
        "gemini_api_key": None
    }

    print("Submitting test job...")
    await bus.publish(AgentMessage(
        sender="TestScript",
        recipient="MasterAgent",
        type="START_JOB",
        payload=test_payload,
        job_id=job_id
    ))

    # Wait for completion via polling (until MasterAgent is upgraded to call bus.complete_job)
    for _ in range(60):
        await asyncio.sleep(0.5)
        if job_id in master.active_jobs and master.active_jobs[job_id].get("status") == "COMPLETED":
            bus.complete_job(job_id)
            break

    if bus.get_job_status(job_id) == "COMPLETED":
        decision = master.active_jobs[job_id].get("decision", {})
        print("\n--- FINAL DECISION ---\n")
        print(json.dumps(decision, indent=4))

        # Print the timeline
        timeline = bus.get_job_timeline(job_id)
        print("\n--- AGENT TIMELINE ---\n")
        for event in timeline:
            print(f"  [{event.timestamp}] {event.agent}: {event.action}")

        # Print bus stats
        print("\n--- BUS STATS ---\n")
        print(json.dumps(bus.get_stats(), indent=2, default=str))
    else:
        status = bus.get_job_status(job_id)
        print(f"Job ended with status: {status}")

    # Graceful shutdown
    await bus.shutdown(timeout=5.0)

if __name__ == "__main__":
    asyncio.run(main())
