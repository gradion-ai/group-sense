# Contradiction detection example

Run with concurrent reasoner:

```bash
python examples/reasoner.py \
  --data-dir examples/data/fact_check \
  --prompt-file examples/prompts/concurrent/fact_check.md \
  --concurrent
```

[chat.json](chat.json) is a test conversation with **13 messages** covering **2 contradictions**:

## Contradictions (0-based message indices):

**1. Direct Contradiction - Meeting Time (Messages 2 & 7):**
- Message 2: user_3 says "the team meeting is scheduled for 2pm tomorrow"
- Message 7: user_4 says "the team meeting tomorrow is at 3pm, not 2pm"

**2. Subtle Contradiction - Deadline (Messages 3 & 10):**
- Message 3: user_1 says "the client proposal deadline is next Friday, March 15th"
- Message 10: user_3 casually mentions "Need to finish my part for the March 22nd deadline"

The second contradiction is now less explicit - user_3 doesn't acknowledge the discrepancy, just mentions a different date in passing.
