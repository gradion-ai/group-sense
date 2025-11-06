# Topic Change Detection Example

Run with default reasoner:

```bash
python examples/reasoner.py \
  --data-dir examples/data/topic_change \
  --prompt-file examples/prompts/default/topic_change.md \
  --batch-size=3
```

[chat.json](chat.json) is a test conversation with **36 messages** covering **5 distinct topics**:

## Topics Breakdown (0-based message indices):

1. **Weekend Activities** (messages 0-3): 4 messages
   - Casual conversation about weekend plans

2. **Q4 Project Deadline** (messages 4-12): 9 messages
   - Discussion about project status, frontend work, API integration, and testing schedule

3. **Lunch Ordering** (messages 13-19): 7 messages
   - Coordinating food delivery from a taco place

4. **Code Review/Authentication PR** (messages 20-32): 13 messages
   - Technical discussion about JWT authentication refactor, token refresh issues, and testing

5. **Office Renovation** (messages 33-35): 3 messages
   - Brief chat about new coffee bar being installed

## Conversation Features:

- Natural topic transitions with clear semantic shifts
- Mix of general group messages (`receiver: null`) and direct replies (e.g., `"receiver": "user_4"`)
- Varying topic lengths (from 3 to 13 messages)
