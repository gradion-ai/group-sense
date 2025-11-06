import argparse
import asyncio
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from examples.utils import configure_logging
from group_sense import (
    ConcurrentGroupReasoner,
    Decision,
    DefaultGroupReasoner,
    DefaultGroupReasonerFactory,
    Message,
    Response,
)


def load_system_prompt(prompt_path: Path) -> str:
    with open(prompt_path) as f:
        return f.read()


def load_chat(chat_path: Path) -> list[Message]:
    with open(chat_path / "chat.json") as f:
        conversation_data = json.load(f)
    return [Message(**msg) for msg in conversation_data]


def print_message(index: int, msg: Message) -> None:
    sender_info = f"{msg.sender} -> {msg.receiver}" if msg.receiver else msg.sender
    print(f"\nMessage {index} ({sender_info}):")
    print(f"  {msg.content}")


def print_response(response: Response) -> None:
    if response.decision == Decision.DELEGATE:
        print(f"\n{'=' * 80}")
        if response.query:
            print("<downstream-query>")
            print(f"{response.query}")
            print("</downstream-query>")
        if response.receiver:
            print("<response-receiver>")
            print(f"{response.receiver}")
            print("</response-receiver>")
        print(f"{'=' * 80}")


async def run_default_reasoner(chat_dir: Path, prompt_file: Path, batch_size: int = 1):
    system_prompt = load_system_prompt(prompt_file)

    if "{owner}" in system_prompt:
        raise ValueError("System prompt of default group reasoner must not contain an {owner} placeholder")

    reasoner = DefaultGroupReasoner(system_prompt=system_prompt)
    messages = load_chat(chat_dir)

    for i in range(0, len(messages), batch_size):
        batch = messages[i : i + batch_size]

        for j, msg in enumerate(batch):
            print_message(i + j, msg)

        response = await reasoner.process(batch)
        print_response(response)


async def run_concurrent_reasoner(chat_dir: Path, prompt_file: Path):
    system_prompt_template = load_system_prompt(prompt_file)

    factory = DefaultGroupReasonerFactory(system_prompt_template=system_prompt_template)
    reasoner = ConcurrentGroupReasoner(factory=factory)
    messages = load_chat(chat_dir)

    for i, msg in enumerate(messages):
        print_message(i, msg)

        if msg.sender == "system":
            reasoner.append(msg)
            continue

        response = await reasoner.process(msg)
        print_response(response)


async def main(args):
    if args.concurrent:
        await run_concurrent_reasoner(args.data_dir, args.prompt_file)
    else:
        await run_default_reasoner(args.data_dir, args.prompt_file, args.batch_size)


if __name__ == "__main__":
    load_dotenv()
    configure_logging(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Run reasoner on example data")
    parser.add_argument("--data-dir", type=Path, required=True, help="Path to example data directory")
    parser.add_argument("--prompt-file", type=Path, required=True, help="Path to reasoner system prompt")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for default group reasoner")
    parser.add_argument("--concurrent", action="store_true", help="Use concurrent group reasoner")

    asyncio.run(main(args=parser.parse_args()))
