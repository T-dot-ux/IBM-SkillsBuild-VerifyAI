from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from models.database import engine, Base
from api import verify, auth, chat, history

# Agent imports
from agents.message_bus import MessageBus
from agents.master_agent import MasterAgent
from agents.input_agent import InputIntelligenceAgent
from agents.threat_agent import ThreatDetectionAgent
from agents.source_agent import SourceCredibilityAgent
from agents.evidence_agent import EvidenceVerificationAgent
from agents.decision_agent import DecisionAgent
from agents.report_agent import ReportGenerationAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Message Bus and Agents
    bus = MessageBus()
    app.state.bus = bus
    
    agents = [
        MasterAgent(bus),
        InputIntelligenceAgent(bus),
        ThreatDetectionAgent(bus),
        SourceCredibilityAgent(bus),
        EvidenceVerificationAgent(bus),
        DecisionAgent(bus),
        ReportGenerationAgent(bus)
    ]
    
    tasks = [asyncio.create_task(agent.run()) for agent in agents]
    
    yield
    
    # Shutdown
    await bus.shutdown()
    for task in tasks:
        task.cancel()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VerifyAI API",
    description="Backend API for Digital Trust Copilot",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verify.router, prefix="/api/verify", tags=["verification"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

@app.get("/")
async def root():
    return {"message": "VerifyAI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
