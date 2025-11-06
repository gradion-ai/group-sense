from dataclasses import dataclass, field


@dataclass
class Attachment:
    """Metadata for media or documents attached to group chat messages.

    Attachments allow messages to reference external media files or
    documents that accompany the text content.

    Attributes:
        path: File path or URL to the attached resource.
        name: Display name of the attachment.
        media_type: MIME type of the attachment (e.g., 'image/png', 'application/pdf').
    """

    path: str
    name: str
    media_type: str


@dataclass
class Thread:
    """Reference to a group chat thread other than the current one.

    Threads allow messages to reference related discussions happening in
    other group chats, enabling cross-conversation context.

    Attributes:
        id: Unique identifier of the referenced thread.
        messages: List of messages from the referenced thread.
    """

    id: str
    messages: list["Message"]


@dataclass
class Message:
    """A message in a group chat conversation.

    Represents a single message exchanged in a group chat environment.
    Messages can optionally target specific recipients, reference other
    threads, and include attachments.

    Attributes:
        content: The text content of the message.
        sender: User ID of the message sender.
        receiver: Optional user ID of the intended recipient. When set,
            indicates the message is directed at a specific user (e.g.,
            via @mention).
        threads: List of referenced threads from other group chats. Used
            for cross-conversation context.
        attachments: List of media or document attachments accompanying
            the message.
    """

    content: str
    sender: str
    receiver: str | None = None
    threads: list[Thread] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)
