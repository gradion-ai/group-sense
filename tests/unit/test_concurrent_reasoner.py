import asyncio

import pytest

from group_sense.message import Message
from group_sense.reasoner.base import Decision, GroupReasoner, GroupReasonerFactory, Response
from group_sense.reasoner.concurrent import ConcurrentGroupReasoner


class MockGroupReasoner(GroupReasoner):
    """Mock reasoner for testing."""

    def __init__(self, processed: int = 0, response: Response | None = None):
        self._processed = processed
        self._response = response or Response(decision=Decision.IGNORE)
        self.process_calls: list[list[Message]] = []

    @property
    def processed(self) -> int:
        return self._processed

    async def process(self, updates: list[Message]) -> Response:
        self.process_calls.append(updates)
        self._processed += len(updates)
        await asyncio.sleep(0.01)  # Simulate async work
        return self._response


class MockGroupReasonerFactory(GroupReasonerFactory):
    """Mock factory for testing."""

    def __init__(self):
        self.created_reasoners: dict[str, MockGroupReasoner] = {}
        self.create_calls: list[tuple[str, dict]] = []

    def create_group_reasoner(self, owner: str, **kwargs) -> GroupReasoner:
        self.create_calls.append((owner, kwargs))
        if owner not in self.created_reasoners:
            reasoner = MockGroupReasoner()
            self.created_reasoners[owner] = reasoner
        return self.created_reasoners[owner]


@pytest.fixture
def concurrent_reasoner():
    """Fixture that creates a ConcurrentGroupReasoner with a MockGroupReasonerFactory."""
    factory = MockGroupReasonerFactory()
    return ConcurrentGroupReasoner(factory)


class TestConcurrentGroupReasoner:
    def test_initial_state_empty(self, concurrent_reasoner):
        assert concurrent_reasoner.messages == []
        assert len(concurrent_reasoner._reasoner) == 0

    def test_append_adds_message(self, concurrent_reasoner):
        message = Message(content="Hello", sender="user1", receiver="user2")

        concurrent_reasoner.append(message)

        assert len(concurrent_reasoner.messages) == 1
        assert concurrent_reasoner.messages[0] == message

    def test_append_accumulates_messages(self, concurrent_reasoner):
        msg1 = Message(content="First", sender="user1", receiver="user2")
        msg2 = Message(content="Second", sender="user2", receiver="user1")

        concurrent_reasoner.append(msg1)
        concurrent_reasoner.append(msg2)

        assert len(concurrent_reasoner.messages) == 2
        assert concurrent_reasoner.messages[0] == msg1
        assert concurrent_reasoner.messages[1] == msg2

    @pytest.mark.asyncio
    async def test_process_appends_message(self, concurrent_reasoner):
        message = Message(content="Test", sender="user1", receiver="user2")

        future = concurrent_reasoner.process(message)
        await future

        assert len(concurrent_reasoner.messages) == 1
        assert concurrent_reasoner.messages[0] == message

    @pytest.mark.asyncio
    async def test_process_creates_reasoner_for_new_sender(self, concurrent_reasoner):
        message = Message(content="Test", sender="user1", receiver="user2")

        future = concurrent_reasoner.process(message)
        await future

        assert len(concurrent_reasoner._factory.create_calls) == 1
        assert concurrent_reasoner._factory.create_calls[0][0] == "user1"
        assert "user1" in concurrent_reasoner._reasoner

    @pytest.mark.asyncio
    async def test_process_reuses_reasoner_for_same_sender(self, concurrent_reasoner):
        msg1 = Message(content="First", sender="user1", receiver="user2")
        msg2 = Message(content="Second", sender="user1", receiver="user2")

        future1 = concurrent_reasoner.process(msg1)
        await future1
        future2 = concurrent_reasoner.process(msg2)
        await future2

        assert len(concurrent_reasoner._factory.create_calls) == 1
        assert concurrent_reasoner._factory.create_calls[0][0] == "user1"

    @pytest.mark.asyncio
    async def test_process_creates_different_reasoners_for_different_senders(self, concurrent_reasoner):
        msg1 = Message(content="First", sender="user1", receiver="user2")
        msg2 = Message(content="Second", sender="user2", receiver="user1")

        future1 = concurrent_reasoner.process(msg1)
        future2 = concurrent_reasoner.process(msg2)
        await asyncio.gather(future1, future2)

        assert len(concurrent_reasoner._factory.create_calls) == 2
        assert concurrent_reasoner._factory.create_calls[0][0] == "user1"
        assert concurrent_reasoner._factory.create_calls[1][0] == "user2"
        assert "user1" in concurrent_reasoner._reasoner
        assert "user2" in concurrent_reasoner._reasoner
        assert concurrent_reasoner._reasoner["user1"][0] is not concurrent_reasoner._reasoner["user2"][0]

    @pytest.mark.asyncio
    async def test_process_returns_future_that_resolves_to_response(self, concurrent_reasoner):
        expected_response = Response(decision=Decision.DELEGATE, query="Test query", receiver="user2")
        concurrent_reasoner._factory.created_reasoners["user1"] = MockGroupReasoner(response=expected_response)

        message = Message(content="Test", sender="user1", receiver="user2")
        future = concurrent_reasoner.process(message)
        result = await future

        assert isinstance(result, Response)
        assert result.decision == Decision.DELEGATE
        assert result.query == "Test query"

    @pytest.mark.asyncio
    async def test_process_passes_all_messages_on_first_call(self, concurrent_reasoner):
        msg1 = Message(content="Pre-existing", sender="user1", receiver="user2")
        msg2 = Message(content="New", sender="user1", receiver="user2")

        concurrent_reasoner.append(msg1)
        future = concurrent_reasoner.process(msg2)
        await future

        mock_reasoner = concurrent_reasoner._factory.created_reasoners["user1"]
        assert len(mock_reasoner.process_calls) == 1
        assert len(mock_reasoner.process_calls[0]) == 2
        assert mock_reasoner.process_calls[0][0] == msg1
        assert mock_reasoner.process_calls[0][1] == msg2

    @pytest.mark.asyncio
    async def test_process_passes_only_new_messages_after_first_call(self, concurrent_reasoner):
        msg1 = Message(content="First", sender="user1", receiver="user2")
        msg2 = Message(content="Second", sender="user1", receiver="user2")
        msg3 = Message(content="Third", sender="user1", receiver="user2")

        future1 = concurrent_reasoner.process(msg1)
        await future1

        future2 = concurrent_reasoner.process(msg2)
        await future2

        future3 = concurrent_reasoner.process(msg3)
        await future3

        mock_reasoner = concurrent_reasoner._factory.created_reasoners["user1"]
        assert len(mock_reasoner.process_calls) == 3
        assert len(mock_reasoner.process_calls[0]) == 1
        assert mock_reasoner.process_calls[0][0] == msg1
        assert len(mock_reasoner.process_calls[1]) == 1
        assert mock_reasoner.process_calls[1][0] == msg2
        assert len(mock_reasoner.process_calls[2]) == 1
        assert mock_reasoner.process_calls[2][0] == msg3

    @pytest.mark.asyncio
    async def test_process_uses_reasoner_processed_count_for_slicing(self, concurrent_reasoner):
        # Pre-populate with messages and create reasoner with processed count
        msg1 = Message(content="Old1", sender="user1", receiver="user2")
        msg2 = Message(content="Old2", sender="user1", receiver="user2")
        msg3 = Message(content="New", sender="user1", receiver="user2")

        concurrent_reasoner.append(msg1)
        concurrent_reasoner.append(msg2)

        # Manually create reasoner with processed=2
        mock_reasoner = MockGroupReasoner(processed=2)
        lock = asyncio.Lock()
        concurrent_reasoner._reasoner["user1"] = (mock_reasoner, lock)

        future = concurrent_reasoner.process(msg3)
        await future

        # Should only pass the new message (index 2 onward)
        assert len(mock_reasoner.process_calls) == 1
        assert len(mock_reasoner.process_calls[0]) == 1
        assert mock_reasoner.process_calls[0][0] == msg3

    @pytest.mark.asyncio
    async def test_concurrent_calls_for_same_sender_are_serialized(self, concurrent_reasoner):
        # Track execution order
        execution_order = []

        class TrackingMockReasoner(MockGroupReasoner):
            async def process(self, updates: list[Message]) -> Response:
                execution_order.append(f"start-{updates[0].content}")
                await asyncio.sleep(0.05)  # Longer delay to ensure overlap if not locked
                execution_order.append(f"end-{updates[0].content}")
                return await super().process(updates)

        concurrent_reasoner._factory.created_reasoners["user1"] = TrackingMockReasoner()

        msg1 = Message(content="First", sender="user1", receiver="user2")
        msg2 = Message(content="Second", sender="user1", receiver="user2")

        # Start both concurrently
        future1 = concurrent_reasoner.process(msg1)
        future2 = concurrent_reasoner.process(msg2)
        await asyncio.gather(future1, future2)

        # Verify serialized execution (no interleaving)
        first = ["start-First", "end-First"]
        second = ["start-Second", "end-Second"]
        assert execution_order == first + second or second + first

    @pytest.mark.asyncio
    async def test_concurrent_calls_for_different_senders_run_in_parallel(self, concurrent_reasoner):
        # Track execution order
        execution_order = []

        class TrackingMockReasoner(MockGroupReasoner):
            def __init__(self, name: str):
                super().__init__()
                self.name = name

            async def process(self, updates: list[Message]) -> Response:
                execution_order.append(f"start-{self.name}")
                await asyncio.sleep(0.05)
                execution_order.append(f"end-{self.name}")
                return await super().process(updates)

        concurrent_reasoner._factory.created_reasoners["user1"] = TrackingMockReasoner("user1")
        concurrent_reasoner._factory.created_reasoners["user2"] = TrackingMockReasoner("user2")

        msg1 = Message(content="From user1", sender="user1", receiver="user2")
        msg2 = Message(content="From user2", sender="user2", receiver="user1")

        # Start both concurrently
        future1 = concurrent_reasoner.process(msg1)
        future2 = concurrent_reasoner.process(msg2)
        await asyncio.gather(future1, future2)

        # Verify parallel execution (should see interleaving)
        # Both should start before the other ends
        start1_idx = execution_order.index("start-user1")
        start2_idx = execution_order.index("start-user2")
        end1_idx = execution_order.index("end-user1")
        end2_idx = execution_order.index("end-user2")

        # Both must start before the other ends (indicating parallel execution)
        assert start1_idx < end2_idx and start2_idx < end1_idx

    @pytest.mark.asyncio
    async def test_interleaved_messages_from_multiple_senders(self, concurrent_reasoner):
        messages = [
            Message(content="User1-1", sender="user1", receiver="user2"),
            Message(content="User2-1", sender="user2", receiver="user1"),
            Message(content="User1-2", sender="user1", receiver="user2"),
            Message(content="User2-2", sender="user2", receiver="user1"),
        ]

        futures = [concurrent_reasoner.process(msg) for msg in messages]
        await asyncio.gather(*futures)

        # Verify both reasoners were created and invoked
        assert "user1" in concurrent_reasoner._factory.created_reasoners
        assert "user2" in concurrent_reasoner._factory.created_reasoners

        user1_reasoner = concurrent_reasoner._factory.created_reasoners["user1"]
        user2_reasoner = concurrent_reasoner._factory.created_reasoners["user2"]

        # Both reasoners should have been called
        assert len(user1_reasoner.process_calls) > 0
        assert len(user2_reasoner.process_calls) > 0

        # Each reasoner sees ALL messages from the group (not just their sender's messages)
        # User1 reasoner was triggered twice (by user1's messages)
        assert len(user1_reasoner.process_calls) == 2
        # User2 reasoner was triggered twice (by user2's messages)
        assert len(user2_reasoner.process_calls) == 2

    @pytest.mark.asyncio
    async def test_lock_is_created_per_reasoner(self, concurrent_reasoner):
        msg1 = Message(content="Test", sender="user1", receiver="user2")
        msg2 = Message(content="Test", sender="user2", receiver="user1")

        future1 = concurrent_reasoner.process(msg1)
        future2 = concurrent_reasoner.process(msg2)
        await asyncio.gather(future1, future2)

        # Each reasoner should have its own lock
        user1_reasoner, user1_lock = concurrent_reasoner._reasoner["user1"]
        user2_reasoner, user2_lock = concurrent_reasoner._reasoner["user2"]

        assert isinstance(user1_lock, asyncio.Lock)
        assert isinstance(user2_lock, asyncio.Lock)
        assert user1_lock is not user2_lock

    @pytest.mark.asyncio
    async def test_messages_property_returns_copy_of_list(self, concurrent_reasoner):
        msg1 = Message(content="First", sender="user1", receiver="user2")

        concurrent_reasoner.append(msg1)
        messages = concurrent_reasoner.messages

        # Verify it's the same list object (based on implementation)
        assert messages is concurrent_reasoner._messages

    @pytest.mark.asyncio
    async def test_process_with_pre_existing_messages_and_append(self, concurrent_reasoner):
        msg1 = Message(content="Pre-1", sender="user1", receiver="user2")
        msg2 = Message(content="Pre-2", sender="user1", receiver="user2")
        msg3 = Message(content="New", sender="user1", receiver="user2")

        concurrent_reasoner.append(msg1)
        concurrent_reasoner.append(msg2)

        future = concurrent_reasoner.process(msg3)
        await future

        assert len(concurrent_reasoner.messages) == 3
        mock_reasoner = concurrent_reasoner._factory.created_reasoners["user1"]
        # First process call should get all 3 messages
        assert len(mock_reasoner.process_calls[0]) == 3
