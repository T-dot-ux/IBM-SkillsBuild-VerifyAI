import asyncio
import logging
from copy import deepcopy
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable, Awaitable, Set
from schemas.messages import AgentMessage
from schemas.outputs import TimelineEvent
from agents.base_agent import BaseAgent

logger = logging.getLogger("verifyai.message_bus")


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------
Middleware = Callable[[AgentMessage], Awaitable[Optional[AgentMessage]]]


class DeadLetter:
    """Stores messages that could not be delivered."""

    def __init__(self):
        self.messages: List[AgentMessage] = []

    def add(self, message: AgentMessage, reason: str):
        logger.warning(
            "[DeadLetter] %s -> %s (%s): %s",
            message.sender, message.recipient, message.type, reason,
        )
        self.messages.append(message)

    def drain(self) -> List[AgentMessage]:
        """Return all dead letters and clear the queue."""
        out = list(self.messages)
        self.messages.clear()
        return out


# ---------------------------------------------------------------------------
# Job Tracker  – one per verification job flowing through the pipeline
# ---------------------------------------------------------------------------
class JobTracker:
    """Tracks the lifecycle of a single verification job."""

    def __init__(self, job_id: str, timeout: float = 120.0):
        self.job_id = job_id
        self.status: str = "PENDING"               # PENDING → RUNNING → COMPLETED / FAILED / TIMED_OUT
        self.timeline: List[TimelineEvent] = []     # Agent‑level events for the frontend animation
        self.future: asyncio.Future = asyncio.get_event_loop().create_future()
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.completed_at: Optional[str] = None
        self.timeout = timeout                      # seconds
        self._timeout_handle: Optional[asyncio.TimerHandle] = None

    # -- timeline helpers ---------------------------------------------------
    def record_event(self, agent: str, action: str):
        self.timeline.append(TimelineEvent(agent=agent, action=action))

    # -- state transitions --------------------------------------------------
    def mark_running(self):
        self.status = "RUNNING"

    def mark_completed(self, result: Any = None):
        if self.status in ("COMPLETED", "FAILED", "TIMED_OUT"):
            return
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self._cancel_timeout()
        if not self.future.done():
            self.future.set_result(result)

    def mark_failed(self, error: str = ""):
        if self.status in ("COMPLETED", "FAILED", "TIMED_OUT"):
            return
        self.status = "FAILED"
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self._cancel_timeout()
        if not self.future.done():
            self.future.set_exception(RuntimeError(error or "Job failed"))

    def mark_timed_out(self):
        if self.status in ("COMPLETED", "FAILED", "TIMED_OUT"):
            return
        self.status = "TIMED_OUT"
        self.completed_at = datetime.now(timezone.utc).isoformat()
        if not self.future.done():
            self.future.set_exception(TimeoutError(f"Job {self.job_id} timed out"))

    # -- timeout scheduling -------------------------------------------------
    def start_timeout(self, loop: asyncio.AbstractEventLoop):
        self._timeout_handle = loop.call_later(self.timeout, self._on_timeout)

    def _on_timeout(self):
        self.mark_timed_out()

    def _cancel_timeout(self):
        if self._timeout_handle is not None:
            self._timeout_handle.cancel()
            self._timeout_handle = None


# ---------------------------------------------------------------------------
# MessageBus
# ---------------------------------------------------------------------------
class MessageBus:
    """
    Central nervous system for the VerifyAI multi‑agent pipeline.

    Responsibilities
    ─────────────────
    • Agent registry & pub/sub routing
    • Per‑job lifecycle tracking (start → complete/fail/timeout)
    • Timeline recording for the frontend agent animation
    • Dead‑letter queue for undeliverable messages
    • Middleware pipeline (logging, metrics, transforms)
    • Graceful shutdown with queue draining
    """

    def __init__(self, default_job_timeout: float = 120.0):
        # -- Agent registry --------------------------------------------------
        self.agents: Dict[str, BaseAgent] = {}
        self.subscribers: Dict[str, List[BaseAgent]] = {}

        # -- Message history & dead letters -----------------------------------
        self.history: List[AgentMessage] = []
        self.dead_letters = DeadLetter()

        # -- Job tracking -----------------------------------------------------
        self.jobs: Dict[str, JobTracker] = {}
        self.default_job_timeout = default_job_timeout

        # -- Middleware -------------------------------------------------------
        self._middleware: List[Middleware] = []

        # -- Internal bookkeeping ---------------------------------------------
        self._agent_tasks: List[asyncio.Task] = []
        self._running = False

    # ======================================================================
    # Agent Registration
    # ======================================================================
    def register(self, agent: BaseAgent):
        """Register an agent with the message bus."""
        self.agents[agent.name] = agent
        logger.info("[MessageBus] Registered agent: %s", agent.name)

    def unregister(self, agent_name: str):
        """Remove an agent from the bus."""
        self.agents.pop(agent_name, None)
        for subs in self.subscribers.values():
            subs[:] = [a for a in subs if a.name != agent_name]
        logger.info("[MessageBus] Unregistered agent: %s", agent_name)

    # ======================================================================
    # Pub / Sub
    # ======================================================================
    def subscribe(self, msg_type: str, agent: BaseAgent):
        """Subscribe an agent to a specific message type."""
        if msg_type not in self.subscribers:
            self.subscribers[msg_type] = []
        if agent not in self.subscribers[msg_type]:
            self.subscribers[msg_type].append(agent)

    def unsubscribe(self, msg_type: str, agent: BaseAgent):
        """Remove an agent from a subscription."""
        if msg_type in self.subscribers:
            self.subscribers[msg_type] = [
                a for a in self.subscribers[msg_type] if a.name != agent.name
            ]

    # ======================================================================
    # Middleware
    # ======================================================================
    def use(self, middleware: Middleware):
        """
        Add an async middleware function that runs before every publish.

        The middleware receives the message and should return:
        • the (possibly modified) message to continue routing, or
        • ``None`` to silently drop the message.
        """
        self._middleware.append(middleware)

    async def _run_middleware(self, message: AgentMessage) -> Optional[AgentMessage]:
        current = message
        for mw in self._middleware:
            result = await mw(current)
            if result is None:
                logger.debug("[Middleware] Message %s dropped", current.message_id)
                return None
            current = result
        return current

    # ======================================================================
    # Publishing / Routing
    # ======================================================================
    async def publish(self, message: AgentMessage):
        """Route a message to its recipient or subscribers."""

        # -- Run middleware pipeline -----------------------------------------
        message = await self._run_middleware(message)
        if message is None:
            return

        # -- Record in history -----------------------------------------------
        self.history.append(message)

        # -- Record in job timeline ------------------------------------------
        job_id = message.job_id
        if job_id and job_id in self.jobs:
            tracker = self.jobs[job_id]
            tracker.record_event(
                agent=message.sender,
                action=f"Sent {message.type} -> {message.recipient or 'broadcast'}",
            )

        logger.info(
            "[MessageBus] Routing %s from %s → %s (job=%s)",
            message.type, message.sender,
            message.recipient or "broadcast", job_id,
        )

        delivered = False

        # -- Direct routing --------------------------------------------------
        if message.recipient and message.recipient in self.agents:
            await self.agents[message.recipient].inbox.put(message)
            delivered = True

        # -- Broadcast to topic subscribers ----------------------------------
        elif message.type in self.subscribers:
            targets = self.subscribers[message.type]
            for agent in targets:
                # Deliver a shallow copy so subscribers can't interfere
                await agent.inbox.put(message)
            delivered = bool(targets)

        # -- Dead‑letter if no consumer found --------------------------------
        if not delivered:
            if message.recipient:
                self.dead_letters.add(
                    message,
                    reason=f"Recipient '{message.recipient}' not registered",
                )
            else:
                self.dead_letters.add(
                    message,
                    reason=f"No subscribers for message type '{message.type}'",
                )

    async def request(
        self,
        message: AgentMessage,
        timeout: float = 30.0,
    ) -> AgentMessage:
        """
        Send a message and wait for a reply (request / reply pattern).

        Blocks until a message with ``reply_to == message.message_id`` arrives
        in the sender's inbox, or raises ``asyncio.TimeoutError``.
        """
        sender_agent = self.agents.get(message.sender)
        if sender_agent is None:
            raise ValueError(f"Sender agent '{message.sender}' is not registered")

        await self.publish(message)

        # Poll the sender's inbox for a reply
        async def _wait():
            while True:
                reply: AgentMessage = await sender_agent.inbox.get()
                if reply.reply_to == message.message_id:
                    return reply
                # Put back messages that don't match
                await sender_agent.inbox.put(reply)
                await asyncio.sleep(0.05)

        return await asyncio.wait_for(_wait(), timeout=timeout)

    # ======================================================================
    # Job Lifecycle
    # ======================================================================
    def create_job(self, job_id: str, timeout: Optional[float] = None) -> JobTracker:
        """
        Create a tracked job.  Returns a ``JobTracker`` whose ``.future``
        can be awaited by the API layer instead of polling.
        """
        t = timeout or self.default_job_timeout
        tracker = JobTracker(job_id, timeout=t)
        self.jobs[job_id] = tracker
        tracker.mark_running()
        tracker.start_timeout(asyncio.get_event_loop())
        logger.info("[MessageBus] Job %s created (timeout=%.0fs)", job_id, t)
        return tracker

    def complete_job(self, job_id: str, result: Any = None):
        """Mark a job as successfully completed and resolve its future."""
        tracker = self.jobs.get(job_id)
        if tracker:
            tracker.mark_completed(result)
            logger.info("[MessageBus] Job %s completed", job_id)

    def fail_job(self, job_id: str, error: str = ""):
        """Mark a job as failed and reject its future."""
        tracker = self.jobs.get(job_id)
        if tracker:
            tracker.mark_failed(error)
            logger.warning("[MessageBus] Job %s failed: %s", job_id, error)

    def get_job_timeline(self, job_id: str) -> List[TimelineEvent]:
        """Return the recorded timeline for a job."""
        tracker = self.jobs.get(job_id)
        return tracker.timeline if tracker else []

    def get_job_status(self, job_id: str) -> Optional[str]:
        """Return the current status string for a job."""
        tracker = self.jobs.get(job_id)
        return tracker.status if tracker else None

    # ======================================================================
    # Startup / Shutdown
    # ======================================================================
    async def start_all(self) -> List[asyncio.Task]:
        """Start all registered agents as background tasks."""
        self._running = True
        self._agent_tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(agent.run(), name=f"agent-{agent.name}")
            self._agent_tasks.append(task)
        logger.info(
            "[MessageBus] Started %d agents: %s",
            len(self._agent_tasks),
            ", ".join(a.name for a in self.agents.values()),
        )
        return self._agent_tasks

    async def shutdown(self, timeout: float = 10.0):
        """
        Gracefully shut down the bus:
        1. Stop accepting new messages.
        2. Wait for agent inbox queues to drain (up to ``timeout`` seconds).
        3. Cancel remaining agent tasks.
        """
        self._running = False
        logger.info("[MessageBus] Initiating graceful shutdown…")

        # Give agents time to finish processing
        try:
            await asyncio.wait_for(self._drain_queues(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("[MessageBus] Queue drain timed out after %.0fs", timeout)

        # Cancel all agent tasks
        for task in self._agent_tasks:
            task.cancel()

        # Suppress CancelledError from tasks
        await asyncio.gather(*self._agent_tasks, return_exceptions=True)
        self._agent_tasks.clear()

        # Time‑out any still‑pending jobs
        for tracker in self.jobs.values():
            if tracker.status == "RUNNING":
                tracker.mark_timed_out()

        logger.info("[MessageBus] Shutdown complete.")

    async def _drain_queues(self):
        """Wait until every agent's inbox is empty."""
        while any(not agent.inbox.empty() for agent in self.agents.values()):
            await asyncio.sleep(0.1)

    # ======================================================================
    # Introspection / Debug
    # ======================================================================
    def get_agent_states(self) -> Dict[str, str]:
        """Snapshot of every agent's current state."""
        return {name: agent.state.value for name, agent in self.agents.items()}

    def get_message_count(self) -> int:
        """Total number of messages routed through the bus."""
        return len(self.history)

    def get_pending_messages(self) -> Dict[str, int]:
        """Number of unprocessed messages per agent inbox."""
        return {name: agent.inbox.qsize() for name, agent in self.agents.items()}

    def get_stats(self) -> Dict[str, Any]:
        """Return a comprehensive diagnostic snapshot."""
        return {
            "total_messages_routed": self.get_message_count(),
            "dead_letter_count": len(self.dead_letters.messages),
            "registered_agents": list(self.agents.keys()),
            "agent_states": self.get_agent_states(),
            "pending_messages": self.get_pending_messages(),
            "active_jobs": {
                jid: {
                    "status": t.status,
                    "events": len(t.timeline),
                    "created_at": t.created_at,
                    "completed_at": t.completed_at,
                }
                for jid, t in self.jobs.items()
            },
            "subscriptions": {
                msg_type: [a.name for a in agents]
                for msg_type, agents in self.subscribers.items()
            },
        }

    def __repr__(self) -> str:
        return (
            f"<MessageBus agents={len(self.agents)} "
            f"jobs={len(self.jobs)} "
            f"messages={len(self.history)}>"
        )
