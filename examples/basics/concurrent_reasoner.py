"""Example: ConcurrentGroupReasoner

Demonstrates concurrent processing with per-user reasoner instances.
Each user gets their own reasoner that maintains independent state while
seeing all group chat messages.
"""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from examples.utils import configure_logging

# --8<-- [start:basics-concurrent-imports]
from group_sense import ConcurrentGroupReasoner, Decision, DefaultGroupReasonerFactory, Message

# --8<-- [end:basics-concurrent-imports]

logger = logging.getLogger(__name__)


async def main():
    # --8<-- [start:basics-concurrent]
    # Load system prompt template with {owner} placeholder
    template_path = Path("examples", "prompts", "concurrent", "fact_check.md")
    template = template_path.read_text()

    # Create factory and reasoner
    factory = DefaultGroupReasonerFactory(system_prompt_template=template)
    reasoner = ConcurrentGroupReasoner(factory=factory)

    # Earlier messages establishing context
    logger.info("Processing alice's message establishing context...")
    await reasoner.process(Message(content="The client meeting is on Thursday.", sender="alice"))

    # Process new messages from different users concurrently
    logger.info("\nProcessing messages from charlie and bob concurrently...")
    f1 = reasoner.process(Message(content="Sounds good!", sender="charlie"))
    f2 = reasoner.process(Message(content="I'll prepare slides for the Friday meeting.", sender="bob"))

    response1 = await f1
    logger.info(f"Charlie - Decision: {response1.decision}")

    response2 = await f2
    logger.info(f"Bob - Decision: {response2.decision}")
    if response2.decision == Decision.DELEGATE:
        logger.info(f"Bob - Query: {response2.query}")
        logger.info("Bob's reasoner detects contradiction using full group context")
    # --8<-- [end:basics-concurrent]


if __name__ == "__main__":
    load_dotenv()
    configure_logging(level=logging.INFO)
    asyncio.run(main())
