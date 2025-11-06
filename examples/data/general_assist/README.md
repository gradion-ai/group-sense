# General group chat assistance example

Run with concurrent reasoner:

```bash
python examples/reasoner.py \
  --data-dir examples/data/general_assist \
  --prompt-file examples/prompts/concurrent/general_assist.md \
  --concurrent
```

[chat.json](chat.json) is a test conversation with **15 messages** (incl. system responses). Below is a summary of the messages that trigger a delegate decision defined in the [system prompt](../../prompts/general_assist.md). Message indices are 0-based.

**Message 4 - Condition A (Information Request)**
- user_2 asks: "Does anyone know how to implement binary search in Python?"
- Receiver: null (broadcast)

**Message 6 - Condition B (Follow-up to System)**
- user_2 follows up on system's response (message 5)

**Message 9 - Condition C (Deferred Question)**
- user_1 replies to user_4 saying they can't answer
- Delegates user_4's original question from message 8

All other messages: **ignore** (chit-chat or direct user-to-user messages)
