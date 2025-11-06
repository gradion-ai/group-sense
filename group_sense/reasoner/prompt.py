from group_sense.message import Attachment, Message, Thread

UPDATE_TEMPLATE = """<update>
{messages}
</update>"""


UPDATE_MESSAGE_TEMPLATE = """<message seq_nr="{seq_nr}" sender="{sender}" receiver="{receiver}">
{content}
</message>"""


ATTACHMENT_TEMPLATE = """<attachment name="{name}" media_type="{media_type}">
{path}
</attachment>"""


THREADS_TEMPLATE = """<threads>
{threads}
</threads>"""


THREAD_TEMPLATE = """<thread id="{thread_id}">
{messages}
</thread>"""


THREAD_MESSAGE_TEMPLATE = """<thread-message sender="{sender}" receiver="{receiver}">
{content}
</thread-message>"""


def user_prompt(messages: list[Message], start_seq_nr: int) -> str:
    prompt = []

    if threads := unique_threads(messages):
        prompt.append(format_threads(threads))

    prompt.append(format_update(messages, start_seq_nr))
    return "\n\n".join(prompt)


def format_update(messages: list[Message], start_seq_nr: int) -> str:
    return UPDATE_TEMPLATE.format(messages=format_update_messages(messages, start_seq_nr))


def format_update_messages(messages: list[Message], start_seq_nr: int) -> str:
    return "\n".join([format_message(message, seq_nr) for seq_nr, message in enumerate(messages, start_seq_nr)])


def format_attachments(attachments: list[Attachment]) -> str:
    return "\n".join(format_attachment(attachment) for attachment in attachments)


def format_attachment(attachment: Attachment) -> str:
    return ATTACHMENT_TEMPLATE.format(
        name=attachment.name,
        media_type=attachment.media_type,
        path=attachment.path,
    )


def format_threads(threads: list[Thread]) -> str:
    formatted_threads = [format_thread(thread) for thread in threads]
    return THREADS_TEMPLATE.format(threads="\n".join(formatted_threads))


def format_thread(thread: Thread) -> str:
    formatted_messages = [format_message(message) for message in thread.messages]
    return THREAD_TEMPLATE.format(thread_id=thread.id, messages="\n".join(formatted_messages))


def unique_threads(messages: list[Message]) -> list[Thread]:
    thread_ids = set()
    threads = []
    for message in messages:
        for thread in message.threads:
            if thread.id not in thread_ids:
                thread_ids.add(thread.id)
                threads.append(thread)

    return threads


def format_message(message: Message, seq_nr: int | None = None) -> str:
    content_parts = []

    if message.attachments:
        content_parts.append(format_attachments(message.attachments))

    content_parts.append(message.content)
    content = "\n".join(content_parts)

    if seq_nr is None:
        message_template = THREAD_MESSAGE_TEMPLATE
    else:
        message_template = UPDATE_MESSAGE_TEMPLATE

    return message_template.format(
        seq_nr=seq_nr,
        sender=message.sender,
        receiver=message.receiver or "",
        content=content,
    )


def example():
    attachments = [
        Attachment(path="/path/to/image.png", name="image.png", media_type="image/png"),
        Attachment(path="/path/to/doc.pdf", name="document.pdf", media_type="application/pdf"),
    ]

    thread_messages_1 = [
        Message(content="Question 1", sender="user1", receiver="system"),
        Message(content="Answer 1", sender="system", receiver="user1"),
    ]
    thread_1 = Thread(id="thread-123", messages=thread_messages_1)

    thread_messages_2 = [
        Message(content="Question 2", sender="user1", receiver="system"),
        Message(content="Answer 2", sender="system", receiver="user1", threads=[thread_1]),
    ]
    thread_2 = Thread(id="thread-456", messages=thread_messages_2)

    messages = [
        Message(content="Question 3?", sender="user1", receiver="user2", attachments=attachments, threads=[thread_1]),
        Message(content="Another statement", sender="user2", receiver=""),
        Message(content="Answer 3", sender="system", receiver="user1", threads=[thread_2, thread_1]),
    ]

    print(user_prompt(messages, start_seq_nr=0))


if __name__ == "__main__":
    example()
