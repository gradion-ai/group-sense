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

    Processes group chat messages incrementally using a single reasoner agent that
    maintains conversation history across all
    [`process()`][group_sense.reasoner.base.GroupReasoner.process] calls.
    Suitable for scenarios where all messages are processed from a unified
    perspective without per-sender context separation.

    The reasoner uses an agent to decide whether each message increment
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
            model: Optional AI model to use. Defaults to "google-gla:gemini-3.6-flash".
                Can be a model name string or a pydantic-ai Model instance.
            model_settings: Optional model-specific settings. Defaults to
                GoogleModelSettings with thinking enabled.
        """
        super().__init__()
        self._history: list[ModelMessage] = []
        self._new_messages: list[Any] = []
        self._processed: int = 0
        self._agent = Agent(
            system_prompt=system_prompt,
            output_type=NativeOutput(Response),
            model=model or "google-gla:gemini-3.6-flash",
            model_settings=model_settings
            or GoogleModelSettings(
                google_thinking_config={
                    "thinking_level": "high",
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
        self._new_messages = to_jsonable_python(result.new_messages(), bytes_mode="base64")
        self._history = result.all_messages()
        self._processed += len(updates)

        response = result.output
        if response.receiver == "":
            response.receiver = None
        return response

    def get_new_messages(self) -> list[dict[str, Any]]:
        """Return new data since last save for incremental persistence.

        Returns an entry containing the new messages from the last
        [`process()`][group_sense.reasoner.default.DefaultGroupReasoner.process]
        call along with the cumulative processed count. Clears the internal
        new messages buffer after returning.

        Returns:
            List containing a single entry with 'messages' (new conversation
                messages) and 'processed' (cumulative message count), or empty
                list if no new messages.
        """
        if not self._new_messages:
            return []
        result = [{"messages": self._new_messages, "processed": self._processed}]
        self._new_messages = []
        return result

    def set_serialized(self, lines: list[dict[str, Any]]):
        """Restore the reasoner's state from JSONL lines.

        Reconstructs the conversation history by concatenating messages from
        all entries. Uses the processed count from the last entry.

        Args:
            lines: List of entries, each containing 'messages' (conversation
                messages) and 'processed' (cumulative message count).
        """
        if not lines:
            return
        all_messages: list[Any] = []
        for line in lines:
            all_messages.extend(line["messages"])
        self._history = ModelMessagesTypeAdapter.validate_python(all_messages)
        self._processed = lines[-1]["processed"]
        self._new_messages = []


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
