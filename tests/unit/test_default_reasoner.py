import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from group_sense.message import Message
from group_sense.reasoner.base import Decision, Response
from group_sense.reasoner.default import DefaultGroupReasoner


class TestableDefaultGroupReasoner(DefaultGroupReasoner):
    """Test subclass that allows configuring output_type for testing."""

    def __init__(self, system_prompt: str, model: TestModel):
        super().__init__(system_prompt=system_prompt, model=model)
        self._agent = Agent(
            system_prompt=system_prompt,
            output_type=Response,  # Use Response directly, not NativeOutput
            model=model,
        )


@pytest.fixture
def reasoner():
    """Fixture that creates a TestableDefaultGroupReasoner with IGNORE decision."""
    model = TestModel(custom_output_args=Response(decision=Decision.IGNORE))
    return TestableDefaultGroupReasoner(
        system_prompt="You are a helpful assistant for {owner}",
        model=model,
    )


class TestDefaultGroupReasoner:
    @pytest.mark.asyncio
    async def test_process_with_delegate_decision(self):
        expected_response = Response(
            decision=Decision.DELEGATE,
            query="Can you help me with Python async/await?",
            receiver="user123",
        )
        model = TestModel(custom_output_args=expected_response)
        reasoner = TestableDefaultGroupReasoner(
            system_prompt="You are a helpful assistant for {owner}",
            model=model,
        )

        messages = [Message(content="How does async work?", sender="user123", receiver="bot")]
        result = await reasoner.process(messages)

        assert result.decision == Decision.DELEGATE
        assert result.query == "Can you help me with Python async/await?"
        assert result.receiver == "user123"

    @pytest.mark.asyncio
    async def test_process_with_ignore_decision(self):
        expected_response = Response(decision=Decision.IGNORE)
        model = TestModel(custom_output_args=expected_response)
        reasoner = TestableDefaultGroupReasoner(
            system_prompt="You are a helpful assistant for {owner}",
            model=model,
        )

        messages = [Message(content="Just chatting", sender="user456", receiver="user789")]
        result = await reasoner.process(messages)

        assert result.decision == Decision.IGNORE
        assert result.query is None
        assert result.receiver is None

    @pytest.mark.asyncio
    async def test_processed_counter_starts_at_zero(self, reasoner):
        assert reasoner.processed == 0

    @pytest.mark.asyncio
    async def test_processed_counter_increments(self, reasoner):
        messages = [Message(content="First", sender="user1", receiver="bot")]
        await reasoner.process(messages)

        assert reasoner.processed == 1

    @pytest.mark.asyncio
    async def test_processed_counter_with_multiple_messages(self, reasoner):
        messages = [
            Message(content="First", sender="user1", receiver="bot"),
            Message(content="Second", sender="user2", receiver="bot"),
            Message(content="Third", sender="user3", receiver="bot"),
        ]
        await reasoner.process(messages)

        assert reasoner.processed == 3

    @pytest.mark.asyncio
    async def test_empty_updates_raises_value_error(self, reasoner):
        with pytest.raises(ValueError, match="Updates must not be empty"):
            await reasoner.process([])

    @pytest.mark.asyncio
    async def test_multiple_sequential_calls(self, reasoner):
        messages1 = [Message(content="First batch", sender="user1", receiver="bot")]
        await reasoner.process(messages1)
        assert reasoner.processed == 1

        messages2 = [
            Message(content="Second batch 1", sender="user2", receiver="bot"),
            Message(content="Second batch 2", sender="user3", receiver="bot"),
        ]
        await reasoner.process(messages2)
        assert reasoner.processed == 3

        messages3 = [Message(content="Third batch", sender="user4", receiver="bot")]
        await reasoner.process(messages3)
        assert reasoner.processed == 4

    @pytest.mark.asyncio
    async def test_message_history_maintained(self, reasoner):
        assert len(reasoner._history) == 0

        messages1 = [Message(content="First", sender="user1", receiver="bot")]
        await reasoner.process(messages1)
        history_length_after_first = len(reasoner._history)
        assert history_length_after_first > 0

        messages2 = [Message(content="Second", sender="user2", receiver="bot")]
        await reasoner.process(messages2)
        assert len(reasoner._history) > history_length_after_first
