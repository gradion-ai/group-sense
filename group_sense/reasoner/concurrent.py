from asyncio import Future, Lock, create_task

from group_sense.message import Message
from group_sense.reasoner.base import GroupReasoner, GroupReasonerFactory, Response


class ConcurrentGroupReasoner:
    """Concurrent group chat processor with per-sender reasoner instances.

    Manages multiple reasoner instances (one per sender) that process messages
    concurrently. Maintains a shared list of all group chat messages that all
    reasoner instances can see, accessible via the messages property.

    Each sender gets their own reasoner instance with independent conversation
    context, but all instances see the same shared group chat messages. A
    reasoner instance is triggered only when its owner sends a message.
    Sequential execution per sender prevents concurrent state corruption to
    a single reasoner instance.

    The process() method returns a Future to allow callers to control message
    ordering: calling process() in the order messages arrive from the group
    chat ensures messages are stored internally in that same order.

    Example:
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
    """

    def __init__(self, factory: GroupReasonerFactory):
        """Initialize the concurrent reasoner with a factory.

        Args:
            factory: Factory used to create per-sender reasoner instances.
                Each unique sender gets their own reasoner created via this
                factory.
        """
        self._factory = factory
        self._messages: list[Message] = []
        self._reasoner: dict[str, tuple[GroupReasoner, Lock]] = {}

    @property
    def messages(self) -> list[Message]:
        """The shared list of all group chat messages stored internally."""
        return self._messages

    def append(self, message: Message):
        """Add a message to the shared group chat context without triggering reasoning.

        Adds the message to the internally stored group chat message list that
        all reasoner instances share, without initiating a reasoning process.
        Typically used for AI-generated responses to prevent infinite reasoning
        loops while ensuring all reasoners see these messages.

        Args:
            message: Message to add to the shared group chat context. Typically
                messages with sender="system" or other AI-generated content.
        """
        self._messages.append(message)

    def process(self, message: Message) -> Future[Response]:
        """Process a message and return a Future for the reasoning result.

        Adds the message to the shared group chat message list and triggers the
        sender's reasoner instance. Returns a Future to allow the caller to
        control message ordering: calling
        [`process()`][group_sense.reasoner.concurrent.ConcurrentGroupReasoner.process]
        in the order messages arrive from the group chat ensures they are stored
        internally in that same order.

        Processing happens asynchronously. Messages from different senders can be
        processed concurrently, while messages from the same sender are processed
        sequentially to prevent concurrent state corruption to that sender's
        reasoner instance.

        Args:
            message: User message to process. The sender field determines which
                reasoner instance is triggered.

        Returns:
            Future that will resolve to a Response containing the triage decision
                and optional delegation parameters. Use await or asyncio utilities
                to retrieve the result.

        Example:
            ```python
            # Store messages internally in arrival order, process concurrently
            f1 = reasoner.process(msg1)  # from alice
            f2 = reasoner.process(msg2)  # from bob
            f3 = reasoner.process(msg3)  # from alice

            # Messages stored internally as: msg1, msg2, msg3
            # Processing: msg1 and msg2 run concurrently, msg3 waits for msg1
            ```
        """
        self._messages.append(message)
        reasoner, lock = self._get_reasoner(message.sender)
        return create_task(self._run(self._messages.copy(), reasoner, lock))

    async def _run(self, messages: list[Message], reasoner: GroupReasoner, lock: Lock) -> Response:
        async with lock:
            updates = messages[reasoner.processed :]
            return await reasoner.process(updates)

    def _get_reasoner(self, sender: str) -> tuple[GroupReasoner, Lock]:
        if sender in self._reasoner:
            reasoner, lock = self._reasoner[sender]
        else:
            reasoner, lock = self._factory.create_group_reasoner(owner=sender), Lock()
            self._reasoner[sender] = (reasoner, lock)
        return reasoner, lock
