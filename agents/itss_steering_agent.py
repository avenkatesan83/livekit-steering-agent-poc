import logging

from livekit.agents import Agent, RunContext, function_tool

from agents.base_agent import BaseAgent
from agents.finish_queue_agent import FinishQueueAgent, is_queue_transfer
from core.agent_instructions import ITSS_STEERING_AGENT_INSTRUCTIONS
from core.a2a_client import A2AGatewayClient

logger = logging.getLogger(__name__)


class ITSSSteeringAgent(BaseAgent):

    def __init__(self):
        super().__init__(instructions=ITSS_STEERING_AGENT_INSTRUCTIONS)

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Ask the caller how the IT Service Desk can help.",
        )

    def _build_handoff(self, utterance: str) -> dict[str, object]:
        userdata = self.session.userdata
        return {
            "handoff_version": "1",
            "source": "itss-steering-agent",
            "session_id": userdata.session_id,
            # Fixed routing capability; the skill agent classifies the actual intent from utterance.
            "capability": "it service desk",
            "utterance": utterance,
            "user_context": {
                "ani": userdata.ani,
                "caller_name": userdata.caller_name,
                "authenticated": userdata.authenticated,
            },
        }

    @function_tool
    async def prepare_skill_handoff(
        self,
        context: RunContext,
        utterance: str,
    ) -> dict[str, object] | Agent:
        utterance = utterance.strip()
        if not utterance:
            raise ValueError("The caller's request text is required for handoff")

        context.userdata.intent = utterance
        handoff = self._build_handoff(utterance)
        # Flat scalars only: the OTel exporter drops dict-valued log attributes.
        logger.info(
            "SKILL_HANDOFF_READY",
            extra={
                "lk_session_id": context.userdata.session_id,
                "capability": handoff["capability"],
                "utterance": utterance,
            },
        )

        # Keeps the caller engaged across the multi-second downstream round trip.
        self.session.say("Let me look into that for you.")

        try:
            result = await A2AGatewayClient().route(handoff)
        except Exception:
            logger.exception(
                "SKILL_HANDOFF_FAILED",
                extra={"lk_session_id": context.userdata.session_id, "utterance": utterance},
            )
            return {
                "succeeded": False,
                "caller_response_text": None,
                "error": "The skill service could not be reached.",
            }

        logger.info(
            "SKILL_HANDOFF_RESULT",
            extra={
                "lk_session_id": context.userdata.session_id,
                "task_id": result.get("task_id"),
                "state": result.get("state"),
                "succeeded": bool(result.get("succeeded")),
                "dfcx_session": result.get("dfcx_session"),
                "intent": result.get("intent"),
                "caller_response_text": result.get("caller_response_text"),
                "error": result.get("error"),
            },
        )

        if not result.get("succeeded"):
            return result

        caller_response_text = result.get("caller_response_text")
        if is_queue_transfer(caller_response_text):
            return FinishQueueAgent(str(caller_response_text))

        return result
