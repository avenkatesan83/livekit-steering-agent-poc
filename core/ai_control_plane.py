import logging

from livekit.agents import (
    inference,
)

logger = logging.getLogger(__name__)

class AIControlPlane:
    """
    Central location for:
    - Model Routing
    - Cost Optimization
    - Failover
    """

    @staticmethod
    def select_model(user_message: str) -> str:

        if not user_message:
            return "openai/gpt-4o-mini"

        text = user_message.strip().lower()
        word_count = len(text.split())

        # Fast path
        if word_count <= 15:
            return "openai/gpt-4o-mini"

        # Medium complexity
        if word_count <= 35:
            return "openai/gpt-4.1-mini"

        # Complex reasoning
        return "openai/gpt-4.1"

    @staticmethod
    def get_llm(user_message: str = ""):

        model = AIControlPlane.select_model(
            user_message
        )

        logger.info(f"[AI-CONTROL-PLANE] USER_MESSAGE={user_message}")

        logger.info(
            f"[AI-CONTROL-PLANE] MODEL={model}"
        )

        return inference.LLM(
            model=model
        )