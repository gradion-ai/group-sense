## group_sense.Decision

Bases: `Enum`

Decision outcome for message triage.

Determines whether messages should be processed by the downstream application or ignored by the triage system.

### DELEGATE

```python
DELEGATE = 'delegate'
```

### IGNORE

```python
IGNORE = 'ignore'
```

## group_sense.Response

Bases: `BaseModel`

Triage decision response for group chat messages.

Encapsulates the triage decision and optional delegation parameters for processing messages from the group chat environment.

Fields:

- `decision` (`Decision`)
- `query` (`str | None`)
- `receiver` (`str | None`)

### decision

```python
decision: Decision
```

### query

```python
query: str | None = None
```

First-person query for the downstream application, formulated as if written by a single user. Required when decision is DELEGATE. Should be self-contained with all necessary context. Example: 'Can you help me understand how async/await works in Python?'

### receiver

```python
receiver: str | None = None
```

User ID of the intended recipient who should receive the downstream application's response. Required when decision is DELEGATE.

## group_sense.GroupReasoner

Bases: `ABC`

Abstract protocol for incremental group chat message processing.

Defines the interface for reasoners that process group chat messages incrementally, maintaining conversation context across multiple calls. Each process() call represents a conversation turn that adds to the reasoner's history.

Implementations decide whether message increments should be ignored or delegated to downstream AI systems for processing.

### processed

```python
processed: int
```

Number of messages processed so far by this reasoner.

### process

```python
process(updates: list[Message]) -> Response
```

Process a message increment and decide whether to delegate.

Analyzes new messages in the context of the entire conversation history and decides whether to ignore them or generate a query for downstream AI processing.

Parameters:

| Name      | Type            | Description                                                                                                                         | Default    |
| --------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `updates` | `list[Message]` | List of new messages to process as an increment. Must not be empty. Represents messages that arrived since the last process() call. | *required* |

Returns:

| Type       | Description                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------ |
| `Response` | Response containing the triage decision and optional delegation parameters (query and receiver). |

Raises:

| Type         | Description          |
| ------------ | -------------------- |
| `ValueError` | If updates is empty. |

## group_sense.GroupReasonerFactory

Bases: `ABC`

Abstract factory protocol for creating GroupReasoner instances.

Defines the interface for factories that create reasoner instances customized for specific owners. Used primarily by ConcurrentGroupReasoner to create per-sender reasoner instances.

### create_group_reasoner

```python
create_group_reasoner(owner: str) -> GroupReasoner
```

Create a new GroupReasoner instance for the specified owner.

Parameters:

| Name    | Type  | Description                                                                                          | Default    |
| ------- | ----- | ---------------------------------------------------------------------------------------------------- | ---------- |
| `owner` | `str` | User ID of the reasoner instance owner. The reasoner will be customized for this user's perspective. | *required* |

Returns:

| Type            | Description                                            |
| --------------- | ------------------------------------------------------ |
| `GroupReasoner` | A new GroupReasoner instance configured for the owner. |

## group_sense.DefaultGroupReasoner

```python
DefaultGroupReasoner(system_prompt: str, model: str | Model | None = None, model_settings: ModelSettings | None = None)
```

Bases: `GroupReasoner`

Sequential group chat message processor with single shared context.

Processes group chat messages incrementally using a single reasoner agent that maintains conversation history across all process() calls. Suitable for scenarios where all messages are processed from a unified perspective without per-sender context separation.

The reasoner uses an agent to decide whether each message increment should be ignored or delegated to downstream systems with a generated query.

Example

```python
reasoner = DefaultGroupReasoner(system_prompt="...")
response = await reasoner.process([message1, message2])
if response.decision == Decision.DELEGATE:
    print(f"Query: {response.query}")
```

Initialize the reasoner with a system prompt and optional model configuration.

Parameters:

| Name             | Type            | Description                                                                                                                 | Default                                                                                  |
| ---------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `system_prompt`  | `str`           | System prompt that defines the reasoner's behavior and decision-making criteria. Should not contain an {owner} placeholder. | *required*                                                                               |
| `model`          | \`str           | Model                                                                                                                       | None\`                                                                                   |
| `model_settings` | \`ModelSettings | None\`                                                                                                                      | Optional model-specific settings. Defaults to GoogleModelSettings with thinking enabled. |

### get_serialized

```python
get_serialized() -> dict[str, Any]
```

Serialize the reasoner's state for persistence.

Captures the conversation history and message count for later restoration via set_serialized(). Used by applications to persist reasoner state across restarts or for debugging purposes.

Returns:

| Type             | Description                                                                        |
| ---------------- | ---------------------------------------------------------------------------------- |
| `dict[str, Any]` | Dictionary containing serialized conversation history and processed message count. |

### process

```python
process(updates: list[Message]) -> Response
```

Process a message increment and decide whether to delegate.

Analyzes new messages in the context of the entire conversation history maintained by this reasoner. Each call adds to the conversation history, making subsequent calls aware of previous messages and decisions.

Parameters:

| Name      | Type            | Description                                                                                                                         | Default    |
| --------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `updates` | `list[Message]` | List of new messages to process as an increment. Must not be empty. Represents messages that arrived since the last process() call. | *required* |

Returns:

| Type       | Description                                                                                                           |
| ---------- | --------------------------------------------------------------------------------------------------------------------- |
| `Response` | Response containing the triage decision (IGNORE or DELEGATE) and optional delegation parameters (query and receiver). |

Raises:

| Type         | Description          |
| ------------ | -------------------- |
| `ValueError` | If updates is empty. |

### set_serialized

```python
set_serialized(state: dict[str, Any])
```

Restore the reasoner's state from serialized data.

Reconstructs the conversation history and message count from previously serialized state. Used by applications to restore reasoner state after restarts or for debugging purposes.

Parameters:

| Name    | Type             | Description                                                                                                                                     | Default    |
| ------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `state` | `dict[str, Any]` | Dictionary containing serialized state from get_serialized(). Must include 'agent' (conversation history) and 'processed' (message count) keys. | *required* |

## group_sense.DefaultGroupReasonerFactory

```python
DefaultGroupReasonerFactory(system_prompt_template: str)
```

Bases: `GroupReasonerFactory`

Factory for creating DefaultGroupReasoner instances with owner-specific prompts.

Creates reasoner instances by substituting the {owner} placeholder in a system prompt template. Used primarily by ConcurrentGroupReasoner to create per-sender reasoner instances, where each sender gets their own reasoner customized with their user ID.

Example

```python
template = "You are assisting {owner} in a group chat..."
factory = DefaultGroupReasonerFactory(system_prompt_template=template)
reasoner = factory.create_group_reasoner(owner="user123")
```

Initialize the factory with a system prompt template.

Parameters:

| Name                     | Type  | Description                                                                                                                        | Default    |
| ------------------------ | ----- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `system_prompt_template` | `str` | Template string containing an {owner} placeholder that will be replaced with the actual owner ID when creating reasoner instances. | *required* |

Raises:

| Type         | Description                                              |
| ------------ | -------------------------------------------------------- |
| `ValueError` | If the template does not contain an {owner} placeholder. |

### create_group_reasoner

```python
create_group_reasoner(owner: str, **kwargs: Any) -> GroupReasoner
```

Create a DefaultGroupReasoner instance for the specified owner.

Substitutes the {owner} placeholder in the template with the provided owner ID and creates a new reasoner instance.

Parameters:

| Name       | Type  | Description                                                                                            | Default    |
| ---------- | ----- | ------------------------------------------------------------------------------------------------------ | ---------- |
| `owner`    | `str` | User ID to substitute into the {owner} placeholder.                                                    | *required* |
| `**kwargs` | `Any` | Additional keyword arguments passed to DefaultGroupReasoner constructor (e.g., model, model_settings). | `{}`       |

Returns:

| Type            | Description                                                                           |
| --------------- | ------------------------------------------------------------------------------------- |
| `GroupReasoner` | A new DefaultGroupReasoner instance configured with the owner-specific system prompt. |

## group_sense.ConcurrentGroupReasoner

```python
ConcurrentGroupReasoner(factory: GroupReasonerFactory)
```

Concurrent group chat processor with per-sender reasoner instances.

Manages multiple reasoner instances (one per sender) that process messages concurrently. Maintains a shared list of all group chat messages that all reasoner instances can see, accessible via the messages property.

Each sender gets their own reasoner instance with independent conversation context, but all instances see the same shared group chat messages. A reasoner instance is triggered only when its owner sends a message. Sequential execution per sender prevents concurrent state corruption to a single reasoner instance.

The process() method returns a Future to allow callers to control message ordering: calling process() in the order messages arrive from the group chat ensures messages are stored internally in that same order.

Example

```python
factory = DefaultGroupReasonerFactory(system_prompt_template="...")
reasoner = ConcurrentGroupReasoner(factory=factory)

# Process messages concurrently
future1 = reasoner.process(Message(content="Hi", sender="alice"))
future2 = reasoner.process(Message(content="Hello", sender="bob"))

# Await responses
response1 = await future1
response2 = await future2

# Add AI response to context without triggering reasoning
reasoner.append(Message(content="How can I help?", sender="system"))
```

Initialize the concurrent reasoner with a factory.

Parameters:

| Name      | Type                   | Description                                                                                                                | Default    |
| --------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `factory` | `GroupReasonerFactory` | Factory used to create per-sender reasoner instances. Each unique sender gets their own reasoner created via this factory. | *required* |

### messages

```python
messages: list[Message]
```

The shared list of all group chat messages stored internally.

### append

```python
append(message: Message)
```

Add a message to the shared group chat context without triggering reasoning.

Adds the message to the internally stored group chat message list that all reasoner instances share, without initiating a reasoning process. Typically used for AI-generated responses to prevent infinite reasoning loops while ensuring all reasoners see these messages.

Parameters:

| Name      | Type      | Description                                                                                                             | Default    |
| --------- | --------- | ----------------------------------------------------------------------------------------------------------------------- | ---------- |
| `message` | `Message` | Message to add to the shared group chat context. Typically messages with sender="system" or other AI-generated content. | *required* |

### process

```python
process(message: Message) -> Future[Response]
```

Process a message and return a Future for the reasoning result.

Adds the message to the shared group chat message list and triggers the sender's reasoner instance. Returns a Future to allow the caller to control message ordering: calling process() in the order messages arrive from the group chat ensures they are stored internally in that same order.

Processing happens asynchronously. Messages from different senders can be processed concurrently, while messages from the same sender are processed sequentially to prevent concurrent state corruption to that sender's reasoner instance.

Parameters:

| Name      | Type      | Description                                                                                | Default    |
| --------- | --------- | ------------------------------------------------------------------------------------------ | ---------- |
| `message` | `Message` | User message to process. The sender field determines which reasoner instance is triggered. | *required* |

Returns:

| Type               | Description                                                                                                                                                      |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Future[Response]` | Future that will resolve to a Response containing the triage decision and optional delegation parameters. Use await or asyncio utilities to retrieve the result. |

Example

```python
# Store messages internally in arrival order, process concurrently
f1 = reasoner.process(msg1)  # from alice
f2 = reasoner.process(msg2)  # from bob
f3 = reasoner.process(msg3)  # from alice

# Messages stored internally as: msg1, msg2, msg3
# Processing: msg1 and msg2 run concurrently, msg3 waits for msg1
```
