# ITSS Steering Agent Documentation

Hop 1 is the LiveKit voice steering agent. It authenticates the caller, gathers the request, and sends one vendor-neutral handoff to the external Hop 2 gateway.

## Documents

- [Configuration](configuration.md): runtime settings, dependencies, and deployment notes.
- [Master Architecture](architecture.md): the combined Hop 1, Hop 2, and Hop 3 design, including the DFCX skill agent.
- [Call Flow](call-flow.md): request and response sequence for a caller interaction.
- [Voice AI Pipeline](voice-ai-pipeline.md): audio, turn detection, model, handoff, and response behavior.

## Hops

1. **Hop 1 - LiveKit Steering Agent:** voice ingress, identity verification, context collection, and handoff.
2. **Hop 2 - A2A Router:** capability registry, policy, task state, and skill routing.
3. **Hop 3 - DFCX Skill Agent Adapter:** A2A server, Dialogflow CX session management, intent execution, and normalized response.