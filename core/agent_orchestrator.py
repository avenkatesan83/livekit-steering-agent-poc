from livekit.agents import (
    AgentSession,
    TurnHandlingOptions,
    inference,
)

from livekit.plugins import openai

from core.userdata import (
    UserData,
)


class AgentOrchestrator:

    @staticmethod
    def create_session():

        return AgentSession(
            userdata=UserData(),
            #Default to small model, when agent session is created.
            llm=inference.LLM(model="openai/gpt-4o-mini"),
            stt=inference.STT(
                model="deepgram/nova-3",
                language="multi",
            ),
            tts=inference.TTS(
                model="cartesia/sonic-3",
                voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
            ),
            # Explicit VAD anchors end-of-turn timing to wall clock. The default VAD derives it
            # from STT stream offsets, which double-count elapsed time after an agent handoff.
            vad=inference.VAD(model="silero", min_silence_duration=0.25),
            turn_handling=TurnHandlingOptions(
                turn_detection=inference.TurnDetector(),
                # Preemptive generation speculatively runs tools then discards the result,
                # so each skill handoff fired twice and the first reply was never spoken.
                preemptive_generation={"enabled": False},
            ),
        )
