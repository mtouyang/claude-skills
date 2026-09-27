# English module

Core rules 1–4 come from `SKILL.md`. English docs add the rule below.

## Rule 5: Break asides out into their own sentences

An em dash (—) or a parenthetical in mid-sentence makes the reader hold the main clause in memory, walk around the aside, and pick the thread up again. In a procedure, that costs attention the reader needs for the task.

Split it into two sentences. Keep a dash or parenthesis only for a short, genuine interjection that does not carry an instruction or a condition.

Before:

> Stop the writer service — the restore will fail if anything holds a connection (see the note on pooled clients below) — then run the restore.

After:

> Stop the writer service. The restore fails if anything still holds a connection. Then run the restore.

## Rationale phrases to search for

For step 3 of the procedure:

```bash
grep -niE "\bwhy\b|because|this is intentional|the reason|historically|used to|we chose" <original>
```

## Extra checks

None beyond `doc_stats.py`. English has no punctuation-width problem, so rule 6 does not apply.
