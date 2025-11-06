# Integrating into Applications

The code example below demonstrates how to integrate Group Sense as an adapter between a group chat system and an existing single-user AI assistant. The pattern shows key integration steps: setting up the concurrent reasoner with custom prompts, handling incoming group messages, processing triage decisions, and feeding assistant responses back into the shared conversation context. A complete running implementation using [Group Terminal](https://gradion-ai.github.io/group-terminal/) as a group chat system is available at [examples/chat/application.py](https://github.com/gradion-ai/group-sense/blob/main/examples/chat/application.py).

## Setup

```python
--8<-- "examples/chat/application.py:integration-setup"
```

## Message Handler

```python
--8<-- "examples/chat/application.py:integration-handler"
```
