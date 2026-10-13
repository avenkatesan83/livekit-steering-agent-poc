import logging

from livekit.agents import get_job_context

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Phrases a skill agent uses to announce a warm handoff to the contact center queue.
QUEUE_TRANSFER_MARKERS = (
    "transfer to an agent",
    "transfer you to an agent",
    "transfer to a live agent",
    "transferring you to an agent",
)


def is_queue_transfer(caller_response_text: str | None) -> bool:
    if not caller_response_text:
        return False
    normalized = " ".join(caller_response_text.lower().split())
    return any(marker in normalized for marker in QUEUE_TRANSFER_MARKERS)


class FinishQueueAgent(BaseAgent):
    """Speaks the skill's closing line, then ends the session so the queue can take the call."""

    def __init__(self, closing_text: str):
        super().__init__(
            instructions="Say nothing further. The call is being handed to the contact center queue."
        )
        self._closing_text = closing_text

    async def on_enter(self):
        ctx = get_job_context()
        logger.info(
            "QUEUE_TRANSFER_STARTED",
            extra={"lk_session_id": ctx.room.name, "closing_text": self._closing_text},
        )
        try:
            await self.session.say(self._closing_text).wait_for_playout()
        finally:
            logger.info("QUEUE_TRANSFER_COMPLETED", extra={"lk_session_id": ctx.room.name})
            ctx.shutdown(reason="transferred_to_contact_center_queue")
