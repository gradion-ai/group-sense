## Commands

### Default reasoner

```bash
python examples/reasoner.py \
 --data-dir examples/data/fact_check \
 --prompt-file examples/prompts/default/fact_check.md
p
ython examples/reasoner.py \
 --data-dir examples/data/topic_change \
 --prompt-file examples/prompts/default/topic_change.md \
 --batch-size=3
```

### Concurrent reasoner

```bash
python examples/reasoner.py \
 --data-dir examples/data/general_assist \
 --prompt-file examples/prompts/concurrent/general_assist.md \
 --concurrent

python examples/reasoner.py \
 --data-dir examples/data/fact_check \
 --prompt-file examples/prompts/concurrent/fact_check.md \
 --concurrent
```
