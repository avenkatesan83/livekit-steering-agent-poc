import os
from typing import Any

import httpx

_FAILED_STATES = {"TASK_STATE_FAILED", "TASK_STATE_REJECTED", "TASK_STATE_CANCELED"}


def skill_result(task: dict[str, Any]) -> dict[str, Any]:
    """The skill agent's payload carried in the first structured artifact part."""
    for artifact in task.get("artifacts") or []:
        if not isinstance(artifact, dict):
            continue
        for part in artifact.get("parts") or []:
            if isinstance(part, dict) and isinstance(part.get("data"), dict):
                return part["data"]
    return {}


def caller_response_text(task: dict[str, Any]) -> str | None:
    messages = skill_result(task).get("responseMessages")
    if not isinstance(messages, list):
        return None
    for message in messages:
        if not isinstance(message, dict):
            continue
        text = message.get("text")
        if not isinstance(text, dict):
            continue
        values = text.get("text")
        if isinstance(values, list):
            reply = " ".join(value for value in values if isinstance(value, str))
            if reply:
                return reply
    return None


def status_message_text(task: dict[str, Any]) -> str | None:
    status = task.get("status")
    if not isinstance(status, dict):
        return None
    message = status.get("message")
    if not isinstance(message, dict):
        return None
    parts = message.get("parts")
    if not isinstance(parts, list):
        return None
    texts = [
        part["text"]
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ]
    return " ".join(texts) or None


class A2AGatewayClient:
    def __init__(self, base_url: str | None = None):
        self._base_url = (
            base_url
            or os.getenv(
                "A2A_GATEWAY_URL",
                "https://a2a-gateway-service-331552655001.us-east1.run.app",
            )
        ).rstrip("/")
        self._timeout = float(os.getenv("A2A_GATEWAY_TIMEOUT_SECONDS", "35"))
        self._api_key = os.getenv("A2A_API_KEY")

    async def route(self, handoff: dict[str, object]) -> dict[str, object]:
        session_id = str(handoff["session_id"])
        headers = {
            "A2A-Version": "1.0",
            "Content-Type": "application/a2a+json",
        }
        if self._api_key:
            headers["x-api-key"] = self._api_key

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/message:send",
                headers=headers,
                json={
                    "message": {
                        "messageId": f"{session_id}-handoff",
                        "role": "ROLE_USER",
                        "contextId": session_id,
                        "parts": [
                            {
                                "data": handoff,
                                "mediaType": "application/json",
                            }
                        ],
                    },
                    "configuration": {
                        "acceptedOutputModes": ["application/json"],
                        "returnImmediately": False,
                    },
                },
            )
            response.raise_for_status()
            task = response.json()
            state = task.get("status", {}).get("state")
            reply = caller_response_text(task)
            result = skill_result(task)
            match = result.get("match") or {}
            return {
                "task_id": task.get("id"),
                "context_id": task.get("contextId"),
                "state": state,
                "succeeded": bool(reply) and state not in _FAILED_STATES,
                "caller_response_text": reply,
                "dfcx_session": result.get("dfcxSession"),
                "intent": (match.get("intent") or {}).get("displayName"),
                "error": None if reply else status_message_text(task),
            }