import asyncio
import enum
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from schemas.messages import AgentMessage
from schemas.outputs import FinalDecision
from core.logger import get_agent_logger

class AgentState(str, enum.Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    WAITING_FOR_INFO = "WAITING_FOR_INFO"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class BaseAgent(ABC):
    def __init__(self, name: str, message_bus: Any):
        self.name = name
        self.message_bus = message_bus
        self.logger = get_agent_logger(name)
        self.state = AgentState.IDLE
        self.inbox = asyncio.Queue()
    
    async def run(self):
        """Main event loop for the agent."""
        while True:
            self.state = AgentState.IDLE
            msg: AgentMessage = await self.inbox.get()
            self.state = AgentState.RUNNING
            try:
                await self.process_message(msg)
            except Exception as e:
                print(f"[{self.name}] Error processing message: {e}")
                self.state = AgentState.FAILED
            finally:
                self.inbox.task_done()
                if self.state == AgentState.RUNNING:
                    self.state = AgentState.COMPLETED

    @abstractmethod
    async def process_message(self, message: AgentMessage):
        """Process incoming messages. Must be implemented by subclasses."""
        pass
    
    async def send_message(self, recipient: str, msg_type: str, payload: Dict[str, Any], job_id: str, reply_to: Optional[str] = None):
        """Helper to send a message via the message bus."""
        msg = AgentMessage(
            sender=self.name,
            recipient=recipient,
            type=msg_type,
            payload=payload,
            job_id=job_id,
            reply_to=reply_to
        )
        await self.message_bus.publish(msg)
