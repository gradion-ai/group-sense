from group_sense.message import Attachment, Message, Thread
from group_sense.reasoner.prompt import (
    ATTACHMENT_TEMPLATE,
    THREADS_TEMPLATE,
    UPDATE_TEMPLATE,
    format_attachment,
    format_attachments,
    format_message,
    format_thread,
    format_threads,
    format_update,
    format_update_messages,
    unique_threads,
    user_prompt,
)


class TestFormatAttachment:
    def test_format_single_attachment(self):
        attachment = Attachment(path="/path/to/file.pdf", name="document.pdf", media_type="application/pdf")
        result = format_attachment(attachment)
        expected = ATTACHMENT_TEMPLATE.format(
            name="document.pdf", media_type="application/pdf", path="/path/to/file.pdf"
        )
        assert result == expected

    def test_format_image_attachment(self):
        attachment = Attachment(path="/path/to/image.png", name="photo.png", media_type="image/png")
        result = format_attachment(attachment)
        assert "photo.png" in result
        assert "image/png" in result
        assert "/path/to/image.png" in result


class TestFormatAttachments:
    def test_format_multiple_attachments(self):
        attachments = [
            Attachment(path="/path/to/file1.pdf", name="doc1.pdf", media_type="application/pdf"),
            Attachment(path="/path/to/file2.png", name="image.png", media_type="image/png"),
        ]
        result = format_attachments(attachments)
        assert "doc1.pdf" in result
        assert "image.png" in result
        assert result.count("<attachment") == 2

    def test_format_empty_attachments(self):
        result = format_attachments([])
        assert result == ""

    def test_format_single_attachment_in_list(self):
        attachments = [Attachment(path="/path/file.txt", name="file.txt", media_type="text/plain")]
        result = format_attachments(attachments)
        assert "file.txt" in result
        assert "text/plain" in result


class TestFormatMessage:
    def test_format_message_with_seq_nr(self):
        message = Message(content="Hello world", sender="user1", receiver="user2")
        result = format_message(message, seq_nr=0)
        assert 'seq_nr="0"' in result
        assert 'sender="user1"' in result
        assert 'receiver="user2"' in result
        assert "Hello world" in result
        assert "<message" in result

    def test_format_message_without_seq_nr(self):
        message = Message(content="Hello world", sender="user1", receiver="user2")
        result = format_message(message, seq_nr=None)
        assert "seq_nr" not in result
        assert 'sender="user1"' in result
        assert 'receiver="user2"' in result
        assert "Hello world" in result
        assert "<thread-message" in result

    def test_format_message_with_attachments(self):
        attachments = [Attachment(path="/path/to/file.pdf", name="doc.pdf", media_type="application/pdf")]
        message = Message(content="Check this out", sender="user1", receiver="user2", attachments=attachments)
        result = format_message(message, seq_nr=1)
        assert "doc.pdf" in result
        assert "Check this out" in result
        assert "<attachment" in result

    def test_format_message_without_receiver(self):
        message = Message(content="Broadcast message", sender="user1", receiver=None)
        result = format_message(message, seq_nr=0)
        assert 'receiver=""' in result
        assert "Broadcast message" in result

    def test_format_message_with_multiple_attachments(self):
        attachments = [
            Attachment(path="/path/1.pdf", name="1.pdf", media_type="application/pdf"),
            Attachment(path="/path/2.png", name="2.png", media_type="image/png"),
        ]
        message = Message(content="Multiple files", sender="user1", receiver="user2", attachments=attachments)
        result = format_message(message, seq_nr=5)
        assert "1.pdf" in result
        assert "2.png" in result
        assert "Multiple files" in result


class TestFormatThread:
    def test_format_single_message_thread(self):
        messages = [Message(content="Question", sender="user1", receiver="system")]
        thread = Thread(id="thread-123", messages=messages)
        result = format_thread(thread)
        assert 'id="thread-123"' in result
        assert "Question" in result
        assert "<thread-message" in result

    def test_format_multi_message_thread(self):
        messages = [
            Message(content="Question", sender="user1", receiver="system"),
            Message(content="Answer", sender="system", receiver="user1"),
        ]
        thread = Thread(id="thread-456", messages=messages)
        result = format_thread(thread)
        assert 'id="thread-456"' in result
        assert "Question" in result
        assert "Answer" in result
        assert result.count("<thread-message") == 2

    def test_format_empty_thread(self):
        thread = Thread(id="thread-empty", messages=[])
        result = format_thread(thread)
        assert 'id="thread-empty"' in result
        assert "<thread" in result


class TestFormatThreads:
    def test_format_single_thread(self):
        messages = [Message(content="Test", sender="user1", receiver="system")]
        threads = [Thread(id="thread-1", messages=messages)]
        result = format_threads(threads)
        assert "<threads>" in result
        assert "</threads>" in result
        assert 'id="thread-1"' in result

    def test_format_multiple_threads(self):
        thread1 = Thread(id="thread-1", messages=[Message(content="Q1", sender="user1", receiver="system")])
        thread2 = Thread(id="thread-2", messages=[Message(content="Q2", sender="user2", receiver="system")])
        result = format_threads([thread1, thread2])
        assert 'id="thread-1"' in result
        assert 'id="thread-2"' in result
        assert "Q1" in result
        assert "Q2" in result

    def test_format_empty_threads(self):
        result = format_threads([])
        expected = THREADS_TEMPLATE.format(threads="")
        assert result == expected


class TestUniqueThreads:
    def test_no_threads(self):
        messages = [Message(content="Test", sender="user1", receiver="user2")]
        result = unique_threads(messages)
        assert result == []

    def test_single_unique_thread(self):
        thread = Thread(id="thread-1", messages=[])
        messages = [
            Message(content="Test1", sender="user1", receiver="user2", threads=[thread]),
            Message(content="Test2", sender="user2", receiver="user1", threads=[thread]),
        ]
        result = unique_threads(messages)
        assert len(result) == 1
        assert result[0].id == "thread-1"

    def test_multiple_unique_threads(self):
        thread1 = Thread(id="thread-1", messages=[])
        thread2 = Thread(id="thread-2", messages=[])
        messages = [
            Message(content="Test1", sender="user1", receiver="user2", threads=[thread1]),
            Message(content="Test2", sender="user2", receiver="user1", threads=[thread2]),
        ]
        result = unique_threads(messages)
        assert len(result) == 2
        assert {t.id for t in result} == {"thread-1", "thread-2"}

    def test_duplicate_threads(self):
        thread = Thread(id="thread-1", messages=[])
        messages = [
            Message(content="Test1", sender="user1", receiver="user2", threads=[thread]),
            Message(content="Test2", sender="user2", receiver="user1", threads=[thread]),
            Message(content="Test3", sender="user1", receiver="user2", threads=[thread]),
        ]
        result = unique_threads(messages)
        assert len(result) == 1
        assert result[0].id == "thread-1"

    def test_multiple_threads_per_message(self):
        thread1 = Thread(id="thread-1", messages=[])
        thread2 = Thread(id="thread-2", messages=[])
        messages = [Message(content="Test", sender="user1", receiver="user2", threads=[thread1, thread2])]
        result = unique_threads(messages)
        assert len(result) == 2
        assert {t.id for t in result} == {"thread-1", "thread-2"}

    def test_preserves_order(self):
        thread1 = Thread(id="thread-1", messages=[])
        thread2 = Thread(id="thread-2", messages=[])
        thread3 = Thread(id="thread-3", messages=[])
        messages = [
            Message(content="Test1", sender="user1", receiver="user2", threads=[thread1]),
            Message(content="Test2", sender="user2", receiver="user1", threads=[thread2, thread3]),
        ]
        result = unique_threads(messages)
        assert len(result) == 3
        assert [t.id for t in result] == ["thread-1", "thread-2", "thread-3"]


class TestFormatUpdate:
    def test_format_single_message_update(self):
        messages = [Message(content="Hello", sender="user1", receiver="user2")]
        result = format_update(messages, start_seq_nr=0)
        expected = UPDATE_TEMPLATE.format(messages=format_update_messages(messages, 0))
        assert result == expected
        assert "Hello" in result

    def test_format_multiple_messages_update(self):
        messages = [
            Message(content="First", sender="user1", receiver="user2"),
            Message(content="Second", sender="user2", receiver="user1"),
        ]
        result = format_update(messages, start_seq_nr=5)
        assert "First" in result
        assert "Second" in result
        assert 'seq_nr="5"' in result
        assert 'seq_nr="6"' in result


class TestFormatUpdateMessages:
    def test_format_with_start_seq_nr_zero(self):
        messages = [
            Message(content="First", sender="user1", receiver="user2"),
            Message(content="Second", sender="user2", receiver="user1"),
        ]
        result = format_update_messages(messages, start_seq_nr=0)
        assert 'seq_nr="0"' in result
        assert 'seq_nr="1"' in result
        assert "First" in result
        assert "Second" in result

    def test_format_with_custom_start_seq_nr(self):
        messages = [Message(content="Test", sender="user1", receiver="user2")]
        result = format_update_messages(messages, start_seq_nr=10)
        assert 'seq_nr="10"' in result

    def test_format_empty_messages(self):
        result = format_update_messages([], start_seq_nr=0)
        assert result == ""


class TestUserPrompt:
    def test_messages_only(self):
        messages = [Message(content="Hello", sender="user1", receiver="user2")]
        result = user_prompt(messages, start_seq_nr=0)
        assert "Hello" in result
        assert "<update>" in result
        assert "<threads>" not in result

    def test_messages_with_threads(self):
        thread = Thread(id="thread-1", messages=[Message(content="Previous", sender="user1", receiver="system")])
        messages = [Message(content="Current", sender="user1", receiver="user2", threads=[thread])]
        result = user_prompt(messages, start_seq_nr=0)
        assert "Current" in result
        assert "Previous" in result
        assert "<threads>" in result
        assert "<update>" in result

    def test_multiple_messages_with_duplicate_threads(self):
        thread = Thread(id="thread-1", messages=[Message(content="Thread msg", sender="user1", receiver="system")])
        messages = [
            Message(content="Msg1", sender="user1", receiver="user2", threads=[thread]),
            Message(content="Msg2", sender="user2", receiver="user1", threads=[thread]),
        ]
        result = user_prompt(messages, start_seq_nr=0)
        assert "Msg1" in result
        assert "Msg2" in result
        assert "Thread msg" in result
        assert result.count('id="thread-1"') == 1

    def test_complex_scenario_with_attachments_and_threads(self):
        attachment = Attachment(path="/path/file.pdf", name="file.pdf", media_type="application/pdf")
        thread_msg = Message(content="Thread content", sender="user1", receiver="system")
        thread = Thread(id="thread-xyz", messages=[thread_msg])
        messages = [
            Message(
                content="Main message", sender="user1", receiver="user2", attachments=[attachment], threads=[thread]
            )
        ]
        result = user_prompt(messages, start_seq_nr=0)
        assert "Main message" in result
        assert "file.pdf" in result
        assert "Thread content" in result
        assert "<threads>" in result
        assert "<update>" in result

    def test_custom_start_seq_nr(self):
        messages = [
            Message(content="First", sender="user1", receiver="user2"),
            Message(content="Second", sender="user2", receiver="user1"),
        ]
        result = user_prompt(messages, start_seq_nr=100)
        assert 'seq_nr="100"' in result
        assert 'seq_nr="101"' in result
