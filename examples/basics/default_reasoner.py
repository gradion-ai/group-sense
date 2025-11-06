"""Example: DefaultGroupReasoner

Demonstrates fact-checking with DefaultGroupReasoner. The reasoner maintains
state across all users and detects contradictions in group chat messages.
"""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from examples.utils import configure_logging

# --8<-- [start:basics-default-imports]
from group_sense import Decision, DefaultGroupReasoner, Message

# --8<-- [end:basics-default-imports]

logger = logging.getLogger(__name__)


async def main():
    # --8<-- [start:basics-default]
    # Load system prompt from file
    prompt_path = Path("examples", "prompts", "default", "fact_check.md")
    system_prompt = prompt_path.read_text()

    # Create reasoner
    reasoner = DefaultGroupReasoner(system_prompt=system_prompt)

    # Process group chat messages
    logger.info("Processing first batch of messages...")
    response = await reasoner.process(
        [
            Message(content="The meeting is tomorrow at 2pm.", sender="alice"),
            Message(content="Thanks for the reminder!", sender="charlie"),
        ]
    )
    logger.info(f"Decision: {response.decision}")
    # Decision: IGNORE (no contradiction detected)

    logger.info("\nProcessing message with contradiction...")
    response = await reasoner.process(
        [
            Message(content="See you at 3pm tomorrow.", sender="bob"),
        ]
    )
    logger.info(f"Decision: {response.decision}")
    if response.decision == Decision.DELEGATE:
        logger.info(f"Query: {response.query}")
        logger.info("Group dialogue transformed into self-contained verification query")
    # --8<-- [end:basics-default]


if __name__ == "__main__":
    load_dotenv()
    configure_logging(level=logging.INFO)
    asyncio.run(main())
