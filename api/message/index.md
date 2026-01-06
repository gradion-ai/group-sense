## group_sense.Message

```
Message(content: str, sender: str, receiver: str | None = None, threads: list[Thread] = list(), attachments: list[Attachment] = list())
```

A message in a group chat conversation.

Represents a single message exchanged in a group chat environment. Messages can optionally target specific recipients, reference other threads, and include attachments.

Attributes:

| Name          | Type               | Description                                                                             |
| ------------- | ------------------ | --------------------------------------------------------------------------------------- |
| `content`     | `str`              | The text content of the message.                                                        |
| `sender`      | `str`              | User ID of the message sender.                                                          |
| `receiver`    | \`str              | None\`                                                                                  |
| `threads`     | `list[Thread]`     | List of referenced threads from other group chats. Used for cross-conversation context. |
| `attachments` | `list[Attachment]` | List of media or document attachments accompanying the message.                         |

## group_sense.Attachment

```
Attachment(path: str, name: str, media_type: str)
```

Metadata for media or documents attached to group chat messages.

Attachments allow messages to reference external media files or documents that accompany the text content.

Attributes:

| Name         | Type  | Description                                                         |
| ------------ | ----- | ------------------------------------------------------------------- |
| `path`       | `str` | File path or URL to the attached resource.                          |
| `name`       | `str` | Display name of the attachment.                                     |
| `media_type` | `str` | MIME type of the attachment (e.g., 'image/png', 'application/pdf'). |

## group_sense.Thread

```
Thread(id: str, messages: list[Message])
```

Reference to a group chat thread other than the current one.

Threads allow messages to reference related discussions happening in other group chats, enabling cross-conversation context.

Attributes:

| Name       | Type            | Description                                  |
| ---------- | --------------- | -------------------------------------------- |
| `id`       | `str`           | Unique identifier of the referenced thread.  |
| `messages` | `list[Message]` | List of messages from the referenced thread. |
