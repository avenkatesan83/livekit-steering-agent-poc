# Configuration

## Hop 1 environment

Load these values through `.env.local`, the process environment, or the deployment secret manager. Do not commit credentials.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `A2A_GATEWAY_URL` | No | `https://a2a-gateway-service-331552655001.us-east1.run.app` | Hop 2 base URL. The client calls `/message:send`. |
| `A2A_GATEWAY_TIMEOUT_SECONDS` | No | `35` | HTTP timeout. This covers the Hop 2 downstream timeout of about 30 seconds. |
| `A2A_API_KEY` | No | unset | Optional `x-api-key` sent to Hop 2 when configured. |

LiveKit and provider credentials are supplied by the LiveKit runtime and provider integrations. The current session is configured with:

- LLM: `openai/gpt-4o-mini` initially, with per-turn model selection in the AI control plane.
- STT: `deepgram/nova-3`, multilingual mode.
- TTS: `cartesia/sonic-3`, voice `9626c31c-bec5-4cca-baa8-f8ba9e84c8bc`.
- VAD: Silero with `min_silence_duration=0.25` seconds.
- Turn detector: LiveKit inference turn detector.
- Preemptive generation: disabled to prevent duplicate handoffs.

## Handoff contract

Hop 1 posts an A2A envelope with `A2A-Version: 1.0` and `Content-Type: application/a2a+json`:

```json
{
  "message": {
    "messageId": "<session_id>-handoff",
    "role": "ROLE_USER",
    "contextId": "<session_id>",
    "parts": [{
      "data": {
        "handoff_version": "1",
        "source": "itss-steering-agent",
        "session_id": "<session_id>",
        "capability": "it service desk",
        "utterance": "<caller's words>",
        "user_context": {
          "ani": "<ANI>",
          "caller_name": "<name>",
          "authenticated": true
        }
      },
      "mediaType": "application/json"
    }]
  },
  "configuration": {
    "acceptedOutputModes": ["application/json"],
    "returnImmediately": false
  }
}
```

Hop 1 reads the task state and the first structured artifact. A successful response supplies `responseMessages[].text.text[]`; failure details are read from `status.message.parts[].text` and are not spoken directly to the caller.

## Run and deploy

```powershell
uv sync
uv run agent.py dev
```

The container starts with `uv run agent.py start`. Hop 2 and Hop 3 are separate services; Hop 1 must not contain Dialogflow CX credentials or create Dialogflow sessions.