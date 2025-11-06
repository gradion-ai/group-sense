import logging
from typing import Any

from pydantic_ai import Agent, NativeOutput
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from pydantic_ai.models import Model
from pydantic_ai.models.google import GoogleModelSettings
from pydantic_ai.settings import ModelSettings
from pydantic_core import to_jsonable_python

from group_sense.message import Message
from group_sense.reasoner.base import GroupReasoner, GroupReasonerFactory, Response
from group_sense.reasoner.prompt import user_prompt

logger = logging.getLogger(__name__)


class DefaultGroupReasoner(GroupReasoner):
    """Sequential group chat message processor with single shared context.

    Processes group chat messages incrementally using a single AI agent that
    maintains conversation history across all
    [`process()`][group_sense.reasoner.base.GroupReasoner.process] calls.
    Suitable for scenarios where all messages are processed from a unified
    perspective without per-sender context separation.

    The reasoner uses an AI agent to decide whether each message increment
    should be ignored or delegated to downstream systems with a generated query.

    Example:
        ```python
        reasoner = DefaultGroupReasoner(system_prompt="...")
        response = await reasoner.process([message1, message2])
        if response.decision == Decision.DELEGATE:
            print(f"Query: {response.query}")
        ```
    """

    def __init__(
        self,
        system_prompt: str,
        model: str | Model | None = None,
        model_settings: ModelSettings | None = None,
    ):
        """Initialize the reasoner with a system prompt and optional model configuration.

        Args:
            system_prompt: System prompt that defines the reasoner's behavior and
                decision-making criteria. Should not contain an {owner} placeholder.
            model: Optional AI model to use. Defaults to "gemini-2.5-flash".
                Can be a model name string or a pydantic-ai Model instance.
            model_settings: Optional model-specific settings. Defaults to
                GoogleModelSettings with thinking enabled.
        """
        super().__init__()
        self._history: list[ModelMessage] = []
        self._processed: int = 0
        self._agent = Agent(
            system_prompt=system_prompt,
            output_type=NativeOutput(Response),
            model=model or "gemini-2.5-flash",
            model_settings=model_settings
            or GoogleModelSettings(
                google_thinking_config={
                    "thinking_budget": -1,
                    "include_thoughts": True,
                }
            ),
        )

    @property
    def processed(self) -> int:
        return self._processed

    async def process(self, updates: list[Message]) -> Response:
        """Process a message increment and decide whether to delegate.

        Analyzes new messages in the context of the entire conversation history
        maintained by this reasoner. Each call adds to the conversation history,
        making subsequent calls aware of previous messages and decisions.

        Args:
            updates: List of new messages to process as an increment. Must not
                be empty. Represents messages that arrived since the last
                [`process()`][group_sense.reasoner.base.GroupReasoner.process] call.

        Returns:
            Response containing the triage decision (IGNORE or DELEGATE) and
                optional delegation parameters (query and receiver).

        Raises:
            ValueError: If updates is empty.
        """
        if not updates:
            raise ValueError("Updates must not be empty")

        reasoner_prompt = user_prompt(updates, self._processed)
        logger.debug(f"Reasoner prompt:\n{reasoner_prompt}")
        result = await self._agent.run(reasoner_prompt, message_history=self._history)
        self._history = result.all_messages()
        self._processed += len(updates)
        return result.output

    def get_serialized(self) -> dict[str, Any]:
        """Serialize the reasoner's state for persistence.

        Captures the conversation history and message count for later
        restoration via
        [`set_serialized()`][group_sense.reasoner.default.DefaultGroupReasoner.set_serialized].
        Used by applications to persist reasoner state across restarts or for
        debugging purposes.

        Returns:
            Dictionary containing serialized conversation history and processed
                message count.
        """
        return {
            "agent": to_jsonable_python(self._history, bytes_mode="base64"),
            "processed": self._processed,
        }

    def set_serialized(self, state: dict[str, Any]):
        """Restore the reasoner's state from serialized data.

        Reconstructs the conversation history and message count from previously
        serialized state. Used by applications to restore reasoner state after
        restarts or for debugging purposes.

        Args:
            state: Dictionary containing serialized state from
                [`get_serialized()`][group_sense.reasoner.default.DefaultGroupReasoner.get_serialized].
                Must include 'agent' (conversation history) and 'processed'
                (message count) keys.
        """
        self._history = ModelMessagesTypeAdapter.validate_python(state["agent"])
        self._processed = state["processed"]


class DefaultGroupReasonerFactory(GroupReasonerFactory):
    """Factory for creating DefaultGroupReasoner instances with owner-specific prompts.

    Creates reasoner instances by substituting the {owner} placeholder in a
    system prompt template. Used primarily by
    [`ConcurrentGroupReasoner`][group_sense.reasoner.concurrent.ConcurrentGroupReasoner]
    to create per-sender reasoner instances, where each sender gets their own
    reasoner customized with their user ID.

    Example:
        ```python
        template = "You are assisting {owner} in a group chat..."
        factory = DefaultGroupReasonerFactory(system_prompt_template=template)
        reasoner = factory.create_group_reasoner(owner="user123")
        ```
    """

    def __init__(self, system_prompt_template: str):
        """Initialize the factory with a system prompt template.

        Args:
            system_prompt_template: Template string containing an {owner}
                placeholder that will be replaced with the actual owner ID
                when creating reasoner instances.

        Raises:
            ValueError: If the template does not contain an {owner} placeholder.
        """
        if "{owner}" not in system_prompt_template:
            raise ValueError("System prompt template must contain an {owner} placeholder")

        self._system_prompt_template = system_prompt_template

    def create_group_reasoner(self, owner: str, **kwargs: Any) -> GroupReasoner:
        """Create a DefaultGroupReasoner instance for the specified owner.

        Substitutes the {owner} placeholder in the template with the provided
        owner ID and creates a new reasoner instance.

        Args:
            owner: User ID to substitute into the {owner} placeholder.
            **kwargs: Additional keyword arguments passed to DefaultGroupReasoner
                constructor (e.g., model, model_settings).

        Returns:
            A new DefaultGroupReasoner instance configured with the owner-specific
                system prompt.
        """
        system_prompt = self._system_prompt_template.format(owner=owner)
        return DefaultGroupReasoner(system_prompt=system_prompt, **kwargs)
