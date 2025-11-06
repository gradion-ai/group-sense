# Examples

The following examples demonstrate different engagement patterns using simplified system prompts. For more elaborate prompts with detailed instructions, as used in [Basics](../basics/), see [examples/prompts/](https://github.com/gradion-ai/group-sense/tree/main/examples/prompts/).

## Answer Assistance

In group conversations, users sometimes cannot answer questions addressed to them. The reasoner detects this pattern and delegates the original question to the AI, setting the receiver to the original questioner. A complete runnable example is available at [examples/example_1.py](https://github.com/gradion-ai/group-sense/blob/main/examples/example_1.py).

```python
from group_sense import Decision, DefaultGroupReasoner, Message


# Short prompt for delegation when users can't answer
system_prompt = (
    "Delegate when a user indicates they can't answer a question "
    "addressed to them. Transform to first-person query and set receiver to the question "
    "sender. Ignore everything else."
)

# Create the reasoner with the system prompt
reasoner = DefaultGroupReasoner(system_prompt=system_prompt)

# Process alice's question to bob - should be ignored
logger.info("Processing alice's question to bob...")
response1 = await reasoner.process(
    [
        Message(
            content="We need to add rate limiting to our API. Do you know how to implement that?",
            sender="alice",
            receiver="bob",
        ),
    ]
)
logger.info(f"Decision: {response1.decision}")

# bob can't answer - should be delegated
logger.info("Processing bob's message...")
response2 = await reasoner.process(
    [
        Message(content="I'm not sure, let me check.", sender="bob"),
    ]
)
logger.info(f"Decision: {response2.decision}")

if response2.decision == Decision.DELEGATE:
    logger.info(f"Query: {response2.query}")
    logger.info(f"Respond to: {response2.receiver}")
    logger.info("The AI will research and respond to alice!")
else:
    logger.info("No delegation triggered")
```

This example uses DefaultGroupReasoner to process messages and make delegation decisions based on the configured system prompt. The Message class represents individual chat messages, and Decision is an enum indicating whether to delegate or ignore.

## Fact Checking

When participants provide conflicting information about facts, dates, or events, the reasoner detects the contradiction and generates verification queries without requiring explicit user requests. A complete runnable example is available at [examples/example_2.py](https://github.com/gradion-ai/group-sense/blob/main/examples/example_2.py).

```python
from group_sense import Decision, DefaultGroupReasoner, Message


# Short custom prompt for fact-checking engagement
system_prompt = (
    "Delegate when you detect contradictory information "
    "about facts, dates, or events. Generate a query asking for verification. "
    "Ignore everything else. Always set receiver to null."
)

# Create the reasoner with the fact-checking prompt
reasoner = DefaultGroupReasoner(system_prompt=system_prompt)

# Process messages with contradictory information
logger.info("Processing messages with contradictory meeting times...")
response = await reasoner.process(
    [
        Message(content="The meeting is tomorrow at 2pm.", sender="alice"),
        Message(content="Thank you for the reminder, I'll be there.", sender="charlie"),
        Message(content="I'll be there too, see you at 3pm.", sender="bob"),
    ]
)

# Check the decision and display results
logger.info(f"Decision: {response.decision}")

if response.decision == Decision.DELEGATE:
    logger.info(f"Query generated: {response.query}")
    logger.info(f"Send to: {response.receiver}")
    logger.info("The reasoner detected a contradiction and wants verification!")
else:
    logger.info("No delegation - no contradiction detected")
```

This example demonstrates how DefaultGroupReasoner can proactively identify patterns in group conversations and generate verification queries without explicit requests from users.

## General Assistance

Provides assistance by handling direct questions and follow-up queries. Uses ConcurrentGroupReasoner so that reasoning runs for different users concurrently. This example is similar to direct assistant usage, but the reasoner handles all group context complexity: transforming group conversations into self-contained queries and managing per-user reasoning state. A complete runnable example is available at [examples/example_3.py](https://github.com/gradion-ai/group-sense/blob/main/examples/example_3.py).

```python
from group_sense import ConcurrentGroupReasoner, Decision, DefaultGroupReasonerFactory, Message


# Template with {owner} placeholder for per-sender customization
template = (
    "You are assisting {owner} in a group chat. "
    "Delegate when {owner} asks questions or continues conversations with the system. "
    "Make delegate queries self-contained. Ignore everything else."
)

factory = DefaultGroupReasonerFactory(system_prompt_template=template)
reasoner = ConcurrentGroupReasoner(factory=factory)

# Process alice's first message
# Expected: DELEGATE with query "What's the weather like in Vienna today?"
logger.info("Processing alice's first message...")
f1 = reasoner.process(Message(content="What's the weather like in Vienna today?", sender="alice"))
response1 = await f1
logger.info(f"Alice message 1 - Decision: {response1.decision}")
if response1.decision == Decision.DELEGATE:
    logger.info(f"  Query: {response1.query}")

# Add AI response back to the shared context
logger.info("Adding system response to shared context...")
reasoner.append(Message(content="It's sunny in Vienna today.", sender="system"))
logger.info("System message added - available to all user contexts")

# Process bob and alice's messages concurrently
# Bob expected: IGNORE (casual statement)
# Alice expected: DELEGATE with self-contained query "What's the weather like in Vienna tomorrow?"
logger.info("\nProcessing bob and alice's messages concurrently...")
f2 = reasoner.process(Message(content="I'm feeling good!", sender="bob"))
f3 = reasoner.process(Message(content="and tomorrow?", sender="alice"))

response2 = await f2
logger.info(f"Bob message - Decision: {response2.decision}")
if response2.decision == Decision.DELEGATE:
    logger.info(f"  Query: {response2.query}")

response3 = await f3
logger.info(f"Alice message 2 - Decision: {response3.decision}")
if response3.decision == Decision.DELEGATE:
    logger.info(f"  Query: {response3.query}")
    logger.info("  Notice: Follow-up to both alice's first message AND the system response!")
```

This example uses ConcurrentGroupReasoner with DefaultGroupReasonerFactory to create per-user reasoning instances. Each user gets their own reasoner customized via the `{owner}` placeholder in the system prompt template.
