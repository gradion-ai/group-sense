import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from examples.utils import configure_logging
from group_sense import (
    ConcurrentGroupReasoner,
    DefaultGroupReasonerFactory,
    Message,
)

logger = logging.getLogger(__name__)


async def main():
    template_path = Path("examples", "prompts", "concurrent", "general_assist.md")

    factory = DefaultGroupReasonerFactory(system_prompt_template=template_path.read_text())
    reasoner = ConcurrentGroupReasoner(factory=factory)

    future_1 = reasoner.process(Message(content="What is the weather like in Vienna?", sender="user1"))
    future_2 = reasoner.process(Message(content="I'm feeling good!", sender="user2"))
    future_3 = reasoner.process(Message(content="and in Berlin?", sender="user1"))

    for future in asyncio.as_completed([future_1, future_2, future_3]):
        logger.debug(f"Reasoner response: {await future}")


if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    asyncio.run(main())
