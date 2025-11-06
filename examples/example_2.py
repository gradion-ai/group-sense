"""Tutorial 2: Fact-Checking

This example demonstrates how the reasoner can monitor conversations and
delegate when it detects contradictory information, without requiring a
direct request from users.

For a full reference prompt, see: examples/prompts/default/fact_check.md
"""

import asyncio
import logging

from dotenv import load_dotenv

from examples.utils import configure_logging

# --8<-- [start:example-2-imports]
from group_sense import Decision, DefaultGroupReasoner, Message

# --8<-- [end:example-2-imports]

logger = logging.getLogger(__name__)


async def main():
    # --8<-- [start:example-2]
    # Short custom prompt for fact-checking engagement
    system_prompt = (
        "Delegate when you detect contradictory information "
        "about facts, dates, or events. Generate a query asking for verification. "
        "Ignore everything else. Always set receiver to null."
    )

    # Create the reasoner with the fact-checking prompt
    reasoner = DefaultGroupReasoner(system_prompt=system_prompt)

    # Process messages with contradictory information
    logger.info("Processing messages with contradictory meeting times...")
    response = await reasoner.process(
        [
            Message(content="The meeting is tomorrow at 2pm.", sender="alice"),
            Message(content="Thank you for the reminder, I'll be there.", sender="charlie"),
            Message(content="I'll be there too, see you at 3pm.", sender="bob"),
        ]
    )

    # Check the decision and display results
    logger.info(f"Decision: {response.decision}")

    if response.decision == Decision.DELEGATE:
        logger.info(f"Query generated: {response.query}")
        logger.info(f"Send to: {response.receiver}")
        logger.info("The reasoner detected a contradiction and wants verification!")
    else:
        logger.info("No delegation - no contradiction detected")
    # --8<-- [end:example-2]


if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    asyncio.run(main())
