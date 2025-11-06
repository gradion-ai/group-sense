# Examples

The following examples demonstrate different engagement patterns using simplified system prompts. For more elaborate prompts with detailed instructions, as used in [Basics](basics.md), see [examples/prompts/](https://github.com/gradion-ai/group-sense/tree/main/examples/prompts/).

## Answer Assistance

In group conversations, users sometimes cannot answer questions addressed to them. The reasoner detects this pattern and delegates the original question to the AI, setting the receiver to the original questioner. A complete runnable example is available at [examples/example_1.py](https://github.com/gradion-ai/group-sense/blob/main/examples/example_1.py).

```python
--8<-- "examples/example_1.py:example-1-imports"

--8<-- "examples/example_1.py:example-1"
```

This example uses [`DefaultGroupReasoner`][group_sense.DefaultGroupReasoner] to process messages and make delegation decisions based on the configured system prompt. The [`Message`][group_sense.Message] class represents individual chat messages, and [`Decision`][group_sense.Decision] is an enum indicating whether to delegate or ignore.

## Fact Checking

When participants provide conflicting information about facts, dates, or events, the reasoner detects the contradiction and generates verification queries without requiring explicit user requests. A complete runnable example is available at [examples/example_2.py](https://github.com/gradion-ai/group-sense/blob/main/examples/example_2.py).

```python
--8<-- "examples/example_2.py:example-2-imports"

--8<-- "examples/example_2.py:example-2"
```

This example demonstrates how [`DefaultGroupReasoner`][group_sense.DefaultGroupReasoner] can proactively identify patterns in group conversations and generate verification queries without explicit requests from users.

## General Assistance

Provides assistance by handling direct questions and follow-up queries. Uses [`ConcurrentGroupReasoner`][group_sense.ConcurrentGroupReasoner] so that reasoning runs for different users concurrently. This example is similar to direct assistant usage, but the reasoner handles all group context complexity: transforming group conversations into self-contained queries and managing per-user reasoning state. A complete runnable example is available at [examples/example_3.py](https://github.com/gradion-ai/group-sense/blob/main/examples/example_3.py).

```python
--8<-- "examples/example_3.py:example-3-imports"

--8<-- "examples/example_3.py:example-3"
```

This example uses [`ConcurrentGroupReasoner`][group_sense.ConcurrentGroupReasoner] with [`DefaultGroupReasonerFactory`][group_sense.DefaultGroupReasonerFactory] to create per-user reasoning instances. Each user gets their own reasoner customized via the `{owner}` placeholder in the system prompt template.
