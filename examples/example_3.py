"""Tutorial 3: Concurrent Processing for Multiple Users

This example demonstrates the ConcurrentGroupReasoner which maintains separate
conversation contexts for each sender. Messages from different senders are processed
concurrently, while messages from the same sender are processed sequentially to
preserve conversation order.

For a full reference prompt, see: examples/prompts/concurrent/general_assist.md
"""

import asyncio
import logging

from dotenv import load_dotenv

from examples.utils import configure_logging

# --8<-- [start:example-3-imports]
from group_sense import ConcurrentGroupReasoner, Decision, DefaultGroupReasonerFactory, Message

# --8<-- [end:example-3-imports]

logger = logging.getLogger(__name__)


async def main():
    # --8<-- [start:example-3]
    # Template with {owner} placeholder for per-sender customization
    template = (
        "You are assisting {owner} in a group chat. "
        "Delegate when {owner} asks questions or continues conversations with the system. "
        "Make delegate queries self-contained. Ignore everything else."
    )

    factory = DefaultGroupReasonerFactory(system_prompt_template=template)
    reasoner = ConcurrentGroupReasoner(factory=factory)

    # Process alice's first message
    # Expected: DELEGATE with query "What's the weather like in Vienna today?"
    logger.info("Processing alice's first message...")
    f1 = reasoner.process(Message(content="What's the weather like in Vienna today?", sender="alice"))
    response1 = await f1
    logger.info(f"Alice message 1 - Decision: {response1.decision}")
    if response1.decision == Decision.DELEGATE:
        logger.info(f"  Query: {response1.query}")

    # Add AI response back to the shared context
    logger.info("Adding system response to shared context...")
    reasoner.append(Message(content="It's sunny in Vienna today.", sender="system"))
    logger.info("System message added - available to all user contexts")

    # Process bob and alice's messages concurrently
    # Bob expected: IGNORE (casual statement)
    # Alice expected: DELEGATE with self-contained query "What's the weather like in Vienna tomorrow?"
    logger.info("\nProcessing bob and alice's messages concurrently...")
    f2 = reasoner.process(Message(content="I'm feeling good!", sender="bob"))
    f3 = reasoner.process(Message(content="and tomorrow?", sender="alice"))

    response2 = await f2
    logger.info(f"Bob message - Decision: {response2.decision}")
    if response2.decision == Decision.DELEGATE:
        logger.info(f"  Query: {response2.query}")

    response3 = await f3
    logger.info(f"Alice message 2 - Decision: {response3.decision}")
    if response3.decision == Decision.DELEGATE:
        logger.info(f"  Query: {response3.query}")
        logger.info("  Notice: Follow-up to both alice's first message AND the system response!")
    # --8<-- [end:example-3]


if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    asyncio.run(main())
