import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from examples.utils import configure_logging
from group_sense import (
    DefaultGroupReasoner,
    Message,
)

logger = logging.getLogger(__name__)


async def main():
    template_path = Path("examples", "prompts", "default" "fact_check.md")
    reasoner = DefaultGroupReasoner(system_prompt=template_path.read_text())

    message_1 = Message(content="The meeting is tomorrow at 2pm.", sender="user1")
    message_2 = Message(content="I'll be there.", sender="user2")
    message_3 = Message(content="It is at 3pm.", sender="user3")

    response = await reasoner.process([message_1, message_2])
    logger.debug(f"Reasoner response: {response}")

    response = await reasoner.process([message_3])
    logger.debug(f"Reasoner response: {response}")


if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    asyncio.run(main())
