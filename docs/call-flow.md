# Call Flow

```mermaid
sequenceDiagram
    participant C as Caller
    participant L as LiveKit
    participant H1 as Hop 1 Steering
    participant H2 as Hop 2 Router
    participant H3 as Hop 3 DFCX Adapter
    participant CX as Dialogflow CX

    C->>L: Join voice session
    L->>H1: Start agent job
    H1->>C: Greeting and identity prompt
    C->>H1: Employee or contractor ID and confirmation
    H1->>H1: Store ANI, identity, authenticated=true
    H1->>C: Ask what IT help is needed
    C->>H1: Request in natural language
    H1->>C: "Let me look into that for you."
    H1->>H2: A2A handoff(session, context, utterance)
    H2->>H2: Validate, select capability, create task
    H2->>H3: Skill task
    H3->>CX: Detect intent with mapped context
    CX-->>H3: Match, page, response messages
    H3-->>H2: Structured skill artifact
    H2-->>H1: Task state and response
    alt Successful response
        H1->>C: Speak responseMessages text
    else Queue transfer requested
        H1->>C: Speak closing line
        H1->>L: Shut down job for contact-center transfer
    else Failure or timeout
        H1->>C: Safe unavailable message
    end
```

## Important behavior

1. Hop 1 sends the original request and does not pre-classify or shorten it.
2. The gateway can return HTTP 200 while the task state is failed; Hop 1 checks `status.state` and the structured response.
3. The caller hears a filler line during the multi-second downstream round trip.
4. A successful skill response is spoken exactly as returned.
5. Internal error text is logged and traced but is not read aloud.
6. Queue-transfer responses cause Hop 1 to play the closing line fully before shutting down.