# Basics

Group Sense processes messages through reasoners that analyze incoming group chat messages and decide whether to ignore them or delegate them to an AI assistant. Each message has a sender (the user who wrote it) and content. When a reasoner decides to delegate, it generates a self-contained query suitable for a single-user AI assistant and optionally specifies which user should receive the response.

All reasoners see the complete group chat context - every message from every user. The difference between reasoner types is how they maintain their internal reasoning state across messages.

## DefaultGroupReasoner

[`DefaultGroupReasoner`][group_sense.DefaultGroupReasoner] uses a single AI agent with shared reasoning state. All messages are processed through one conversation history, providing a unified perspective across all users.

```python
--8<-- "examples/basics/default_reasoner.py:basics-default-imports"

--8<-- "examples/basics/default_reasoner.py:basics-default"
```

The reasoner maintains state across `process()` calls, enabling context-aware decisions on subsequent message batches. A complete runnable example is available at [examples/basics/default_reasoner.py](https://github.com/gradion-ai/group-sense/blob/main/examples/basics/default_reasoner.py).

## ConcurrentGroupReasoner

[`ConcurrentGroupReasoner`][group_sense.ConcurrentGroupReasoner] creates a separate AI agent for each user, each maintaining its own independent reasoning state. While all agents see the complete group chat context, each maintains a separate conversation history. Messages from different users can be processed concurrently, while messages from the same user are processed sequentially.

```python
--8<-- "examples/basics/concurrent_reasoner.py:basics-concurrent-imports"

--8<-- "examples/basics/concurrent_reasoner.py:basics-concurrent"
```

Each user gets their own AI agent customized with their user ID via [`DefaultGroupReasonerFactory`][group_sense.DefaultGroupReasonerFactory]. While all agents see the same group chat messages, each maintains its own conversation history for reasoning. A complete runnable example is available at [examples/basics/concurrent_reasoner.py](https://github.com/gradion-ai/group-sense/blob/main/examples/basics/concurrent_reasoner.py).
