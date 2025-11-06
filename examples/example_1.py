"""Tutorial 1: Deferred Questions

This example demonstrates the DefaultGroupReasoner handling "deferred questions" -
when a user cannot answer a question addressed to them, the reasoner delegates
to the AI assistant.

For a full reference prompt, see: examples/prompts/default/general_assist.md
"""

import asyncio
import logging

from dotenv import load_dotenv

from examples.utils import configure_logging

# --8<-- [start:example-1-imports]
from group_sense import Decision, DefaultGroupReasoner, Message

# --8<-- [end:example-1-imports]

logger = logging.getLogger(__name__)


async def main():
    # --8<-- [start:example-1]
    # Short prompt for delegation when users can't answer
    system_prompt = (
        "Delegate when a user indicates they can't answer a question "
        "addressed to them. Transform to first-person query and set receiver to the question "
        "sender. Ignore everything else."
    )

    # Create the reasoner with the system prompt
    reasoner = DefaultGroupReasoner(system_prompt=system_prompt)

    # Process alice's question to bob - should be ignored
    logger.info("Processing alice's question to bob...")
    response1 = await reasoner.process(
        [
            Message(
                content="We need to add rate limiting to our API. Do you know how to implement that?",
                sender="alice",
                receiver="bob",
            ),
        ]
    )
    logger.info(f"Decision: {response1.decision}")

    # bob can't answer - should be delegated
    logger.info("Processing bob's message...")
    response2 = await reasoner.process(
        [
            Message(content="I'm not sure, let me check.", sender="bob"),
        ]
    )
    logger.info(f"Decision: {response2.decision}")

    if response2.decision == Decision.DELEGATE:
        logger.info(f"Query: {response2.query}")
        logger.info(f"Respond to: {response2.receiver}")
        logger.info("The AI will research and respond to alice!")
    else:
        logger.info("No delegation triggered")
    # --8<-- [end:example-1]


if __name__ == "__main__":
    load_dotenv()
    configure_logging(level=logging.INFO)
    asyncio.run(main())
