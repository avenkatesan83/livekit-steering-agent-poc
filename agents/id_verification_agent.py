from livekit.agents import Agent, RunContext, function_tool

from agents.base_agent import BaseAgent
from agents.itss_steering_agent import ITSSSteeringAgent
from core.agent_instructions import ID_VERIFICATION_AGENT_INSTRUCTIONS


class IDVerificationAgent(BaseAgent):

    def __init__(self):
        super().__init__(instructions=ID_VERIFICATION_AGENT_INSTRUCTIONS)

    @function_tool
    async def transfer_to_itss_steering(
        self,
        context: RunContext,
        ani: str,
    ) -> Agent:
        context.userdata.ani = ani
        context.userdata.authenticated = True
        return ITSSSteeringAgent()