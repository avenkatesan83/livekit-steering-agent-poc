## ITSS Steering Agent (Hop 1)

This project is the LiveKit voice steering agent only.

It owns:

- caller greeting, authentication, and context collection
- intent or capability discovery
- a vendor-neutral skill handoff containing ANI, caller identity, authentication state, and session ID

It does not contain A2A routing, skill registry logic, or Dialogflow CX integration. Those belong in separate Hop 2 and Hop 3 projects.

This project does not implement or start the A2A gateway. It only consumes an already-running external FastAPI service.

Set `A2A_GATEWAY_URL` to that service URL. The steering agent posts A2A message envelopes to `POST {A2A_GATEWAY_URL}/message:send`.
Set `A2A_GATEWAY_TIMEOUT_SECONDS` when required; its default is 35 seconds to cover Hop 2's 30-second downstream timeout.
