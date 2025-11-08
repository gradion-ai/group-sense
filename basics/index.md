# Basics

Group Sense processes messages through reasoners that analyze incoming group chat messages and decide whether to ignore them or delegate them to an AI assistant. Each message has a sender (the user who wrote it) and content. When a reasoner decides to delegate, it generates a self-contained query suitable for a single-user AI assistant and optionally specifies which user should receive the response.

Reasoners see the complete group chat context - every message from every user. The difference between reasoner types is how they maintain their internal reasoning state across messages.

## DefaultGroupReasoner

DefaultGroupReasoner uses a single reasoner agent with shared reasoning state. All messages are processed through one conversation history, providing a unified perspective across all users.

```python
from group_sense import Decision, DefaultGroupReasoner, Message


# Load system prompt from file
prompt_path = Path("examples", "prompts", "default", "fact_check.md")
system_prompt = prompt_path.read_text()

# Create reasoner
reasoner = DefaultGroupReasoner(system_prompt=system_prompt)

# Process group chat messages
logger.info("Processing first batch of messages...")
response = await reasoner.process(
    [
        Message(content="The meeting is tomorrow at 2pm.", sender="alice"),
        Message(content="Thanks for the reminder!", sender="charlie"),
    ]
)
logger.info(f"Decision: {response.decision}")
# Decision: IGNORE (no contradiction detected)

logger.info("\nProcessing message with contradiction...")
response = await reasoner.process(
    [
        Message(content="See you at 3pm tomorrow.", sender="bob"),
    ]
)
logger.info(f"Decision: {response.decision}")
if response.decision == Decision.DELEGATE:
    logger.info(f"Query: {response.query}")
    logger.info("Group dialogue transformed into self-contained verification query")
```

The reasoner maintains state across `process()` calls, enabling context-aware decisions on subsequent message batches. A complete runnable example is available at [examples/basics/default_reasoner.py](https://github.com/gradion-ai/group-sense/blob/main/examples/basics/default_reasoner.py).

## ConcurrentGroupReasoner

ConcurrentGroupReasoner creates a separate reasoner agent for each user, each maintaining its own independent reasoning state. While all reasoner agents see the complete group chat context, each maintains a separate conversation history. Messages from different users can be processed concurrently, while messages from the same user are processed sequentially.

```python
from group_sense import ConcurrentGroupReasoner, Decision, DefaultGroupReasonerFactory, Message


# Load system prompt template with {owner} placeholder
template_path = Path("examples", "prompts", "concurrent", "fact_check.md")
template = template_path.read_text()

# Create factory and reasoner
factory = DefaultGroupReasonerFactory(system_prompt_template=template)
reasoner = ConcurrentGroupReasoner(factory=factory)

# Earlier messages establishing context
logger.info("Processing alice's message establishing context...")
await reasoner.process(Message(content="The client meeting is on Thursday.", sender="alice"))

# Process new messages from different users concurrently
logger.info("\nProcessing messages from charlie and bob concurrently...")
f1 = reasoner.process(Message(content="Sounds good!", sender="charlie"))
f2 = reasoner.process(Message(content="I'll prepare slides for the Friday meeting.", sender="bob"))

response1 = await f1
logger.info(f"Charlie - Decision: {response1.decision}")

response2 = await f2
logger.info(f"Bob - Decision: {response2.decision}")
if response2.decision == Decision.DELEGATE:
    logger.info(f"Bob - Query: {response2.query}")
    logger.info("Bob's reasoner detects contradiction using full group context")
```

Each user gets their own reasoner agent customized with their user ID via DefaultGroupReasonerFactory. A complete runnable example is available at [examples/basics/concurrent_reasoner.py](https://github.com/gradion-ai/group-sense/blob/main/examples/basics/concurrent_reasoner.py).
