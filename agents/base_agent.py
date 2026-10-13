import logging

from livekit.agents import Agent

from core.ai_control_plane import (
    AIControlPlane,
)

logger = logging.getLogger(__name__)


class BaseAgent(Agent):
    """
    Shared base class for all agents.

    Responsibilities:
    - Capture user input
    - Invoke AI Control Plane
    - Dynamically switch model
    - Provide common logging
    """

    async def on_user_turn_completed(
        self,
        turn_ctx,
        new_message,
    ):

        try:

            user_text = str(
                new_message.content
            )

            logger.info(
                "================================================="
            )

            logger.info(
                f"AGENT={self.__class__.__name__}"
            )

            logger.info(
                f"USER_INPUT={user_text}"
            )

            selected_model = (
                AIControlPlane.select_model(
                    user_text
                )
            )

            logger.info(
                f"SELECTED_MODEL={selected_model}"
            )

            #
            # Dynamically update model
            # for next AI turn
            #

            self.session.llm.update_options(
                model=selected_model
            )

            logger.info(
                f"ACTIVE_MODEL={self.session.llm.model}"
            )

            logger.info(
                "================================================="
            )

        except Exception:

            logger.exception(
                "AI_CONTROL_PLANE_ERROR"
            )

        return await super().on_user_turn_completed(
            turn_ctx,
            new_message,
        )