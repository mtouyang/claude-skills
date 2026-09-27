---
name: docs-for-humans
description: Rewrite manuals, SOPs, runbooks, and step-by-step operating docs into a shape a human can actually follow — a routing table first, copy-paste command blocks, a bold budget, design rationale moved to an appendix, and (for Chinese) full-width punctuation. Supports English and Traditional Chinese (zh-TW). Use when writing or rewriting an operational doc a person will follow step by step, or when the user says a document is hard to read, too dense, or confusing. 中文觸發：文件看不懂、太密、讀不下去、改寫手冊、寫 SOP、寫給人看。
license: MIT
---

# Docs for humans

## What this fixes

Operating docs are rarely hard to read because they lack detail. They are hard to read because **"what to do now" and "why it is this way" are glued into the same sentence.**

The reader arrives with a task and wants the next command. The author wrote defensively, trying to block every future misunderstanding. When both live in one paragraph, the person following the steps must read every justification, and the skeptic cannot find where the reasons are.

This skill separates the two. It does not delete either side.

Do not use it for docs written for agents, for ADRs, research reports, or specs. Those readers are not following steps, so the split is different.

## Pick the language module first

Decide the document's language from its prose (ignore code blocks), then read the matching module before writing:

- English → `${CLAUDE_SKILL_DIR}/lang/en.md`
- Traditional Chinese → `${CLAUDE_SKILL_DIR}/lang/zh-TW.md`

Rules 1–4 below apply to every language. The module adds the language-specific rules (rule 5 for both, rule 6 for Chinese) and names any extra checks. For a language without a module, apply rules 1–4 only and say so in the change summary.

## Core rules

### 1. Open with a routing table, not a concept

The first heading must not be "what problem this solves". People arrive with a task, not curiosity.

The first block is a table: **why you are here → which section → how long it takes**. One row per reason a reader might open the doc. Under the table, one line: "Not sure which one you need? Start with X."

### 2. Give the full command sequence first

Any procedure longer than two steps starts with one copy-pasteable code block listing every command, each followed by a comment saying what you should see. The step-by-step explanation comes after.

Test: the reader should not have to read five sections to discover that it is "really just five commands".

### 3. Bold only what breaks things if ignored

This is the most effective rule and the easiest to erode. In the original, bold usually means "this is important", so it is everywhere and means nothing.

After the rewrite, the bold count must be at most a quarter of the original's, and you report both numbers. Every remaining bold must answer: if the reader ignores this, what breaks? If you cannot answer, remove the bold.

### 4. Move design rationale to an appendix, leave an anchor

Pull every "why it is shaped like this" passage into one appendix at the end, numbered C1, C2, … In the body, leave one line in place: `Reason: see C3`.

Decide each passage with one question: does this reason change what the reader does right now?

- Yes → keep it in place. Example: why you must not skip the backup, because it affects whether they will be tempted to skip it.
- No, it only explains history or trade-offs → move it. Example: how this step broke in the past.

Moving is not deleting. If you delete something, say so explicitly.

You may move a reason to another file (an ADR, another doc) only if that file already exists and already contains the content. Check each one with grep before you claim the move. A "moved to the ADR" line whose target does not exist is a deletion disguised as a move.

## Procedure

1. **Read the whole original.** The routing table must cover every reason to open the doc, which you cannot know from one section.
2. **Inventory the facts:** measured numbers, exit codes, commit hashes, dates, paths. This list is how you prove later that nothing was lost.
3. **Inventory the reasons.** Search for rationale phrases (the language module lists them) and apply rule 4's test to each.
4. **Check the project glossary, if there is one.** If the project keeps a glossary (for example a `CONTEXT.md`), collect its avoided terms and grep the rewrite afterwards to confirm none appear.
5. **Write,** applying all rules together.
6. **Verify.** All of these, none optional:
   - `python3 ${CLAUDE_SKILL_DIR}/scripts/doc_stats.py --baseline <original> <rewrite>` exits 0: no broken relative links, bold within a quarter of the original. It prints both bold counts and both line counts for the summary.
   - Every item on the fact list is found in the rewrite with grep.
   - Whatever extra check the language module names (for Chinese, the punctuation check) exits 0.
7. **Append a change summary** at the end of the draft: what each rule changed, bold before → after, what moved where, line count before → after. This section is an audit tool for the reviewer and is removed when the draft is finalised.

## Three things to say honestly

1. **This usually makes the doc longer, not shorter.** The routing table, the command block, the split sentences, and the appendix headings are all new. What the reader gains is only needing the first third; the total length grows. Report the real line counts from `doc_stats.py`, never a guess like "a quarter shorter".
2. **Every number in the summary is counted, never estimated.** Use the script output.
3. **The "moved to" table is verified item by item before it is shown.** See rule 4.

## Draft and final

The draft and the final doc are two files. When finalising, do all four:

1. Remove the "this is a draft" note at the top.
2. Remove the change summary at the end.
3. Recompute every relative link. The draft and the final file usually sit in different directories.
4. Rerun `doc_stats.py` on the final file and the language module's checks.

Make the replacements with a script that asserts each one took effect, not with a blind search-and-replace.
