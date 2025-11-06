import logging
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field

from group_sense.message import Message

logger = logging.getLogger(__name__)


class Decision(Enum):
    """Decision outcome for message triage.

    Determines whether messages should be processed by the downstream
    application or ignored by the triage system.
    """

    IGNORE = "ignore"
    DELEGATE = "delegate"


class Response(BaseModel):
    """Triage decision response for group chat messages.

    Encapsulates the triage decision and optional delegation parameters
    for processing messages from the group chat environment.
    """

    decision: Decision

    query: str | None = Field(
        default=None,
        description=(
            "First-person query for the downstream application, formulated as if "
            "written by a single user. Required when decision is DELEGATE. Should "
            "be self-contained with all necessary context. Example: 'Can you help "
            "me understand how async/await works in Python?'"
        ),
    )

    receiver: str | None = Field(
        default=None,
        description=(
            "User ID of the intended recipient who should receive the downstream "
            "application's response. Required when decision is DELEGATE."
        ),
    )


class GroupReasoner(ABC):
    """Abstract protocol for incremental group chat message processing.

    Defines the interface for reasoners that process group chat messages
    incrementally, maintaining conversation context across multiple calls.
    Each [`process()`][group_sense.reasoner.base.GroupReasoner.process] call
    represents a conversation turn that adds to the reasoner's history.

    Implementations decide whether message increments should be ignored or
    delegated to downstream AI systems for processing.
    """

    @property
    @abstractmethod
    def processed(self) -> int:
        """Number of messages processed so far by this reasoner."""
        ...

    @abstractmethod
    async def process(self, updates: list[Message]) -> Response:
        """Process a message increment and decide whether to delegate.

        Analyzes new messages in the context of the entire conversation history
        and decides whether to ignore them or generate a query for downstream
        AI processing.

        Args:
            updates: List of new messages to process as an increment. Must not
                be empty. Represents messages that arrived since the last
                [`process()`][group_sense.reasoner.base.GroupReasoner.process] call.

        Returns:
            Response containing the triage decision and optional delegation
                parameters (query and receiver).

        Raises:
            ValueError: If updates is empty.
        """
        ...


class GroupReasonerFactory(ABC):
    """Abstract factory protocol for creating GroupReasoner instances.

    Defines the interface for factories that create reasoner instances
    customized for specific owners. Used primarily by
    [`ConcurrentGroupReasoner`][group_sense.reasoner.concurrent.ConcurrentGroupReasoner]
    to create per-sender reasoner instances.
    """

    @abstractmethod
    def create_group_reasoner(self, owner: str) -> GroupReasoner:
        """Create a new GroupReasoner instance for the specified owner.

        Args:
            owner: User ID of the reasoner instance owner. The reasoner will
                be customized for this user's perspective.

        Returns:
            A new GroupReasoner instance configured for the owner.
        """
        ...
