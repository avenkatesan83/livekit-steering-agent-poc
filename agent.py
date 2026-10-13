from dotenv import load_dotenv

import logging

from livekit.agents import (
    AgentServer,
    JobContext,
    WorkerOptions,
    cli,
    room_io,
)

from livekit.plugins import ai_coustics

from core.agent_orchestrator import (
    AgentOrchestrator,
)

from agents.id_verification_agent import IDVerificationAgent

load_dotenv(".env.local")

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

server = AgentServer()


@server.rtc_session(
    agent_name="itss-steering-agent"
)
async def entrypoint(
    ctx: JobContext,
):

    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    await ctx.connect()

    logger.info("ITSS Steering Agent Started")

    session = (
        AgentOrchestrator.create_session()
    )
    session.userdata.session_id = ctx.room.name

    await session.start(
        agent=IDVerificationAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=
                ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_S
                ),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Begin the identity verification greeting."
    )


if __name__ == "__main__":

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="itss-steering-agent",
        )
    )