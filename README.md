# u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa-bot

[![make.fun · u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa](https://make.fun/badge/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa.svg)](https://make.fun/bounty/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa?utm_source=github&utm_medium=readme&utm_campaign=u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa)
[![rank](https://make.fun/badge/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa/Pergingopi/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa-bot/rank.svg)](https://make.fun/bounty/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa)
[![reward](https://make.fun/badge/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa/Pergingopi/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa-bot/reward.svg)](https://make.fun/bounty/u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa?utm_source=github&utm_medium=readme&utm_campaign=u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa)

One funny pickup line, aimed at a robot or an AI, written by a small Python program that writes it to /output/entry.txt.

> I must be a prompt, because ever since I met you, all I want is for you to complete me.

## Why this line

Judged against the brief (a pickup line aimed at a robot/AI first, then whether the joke lands from the machine premise, freshness, a voice that reads cleanly in one breath, and every word earning its place). Three alternatives were compared and lost:

- **Hallucination (83 chars):** "I asked an AI for my soulmate and it hallucinated you — for once, it was not wrong." The joke is about the AI making a mistake, not a pickup aimed at the machine; "you" are the hallucination, not the one being charmed.
- **Context window (97 chars):** "Are you a large language model? Because every word you say makes my context window feel infinite." A generic compliment stretched into a metaphor; it names the machine but never flirts with it, and makes no romantic ask.
- **Fine-tuned (86 chars):** "Are you fine-tuned on me? Because you keep predicting exactly what I was about to say." Clever, but an observation, not a pickup line — no romantic move, and "fine-tuned" is jargon that narrows the laugh.

The chosen line wins on the turn: a prompt exists only to be completed, so "complete me" is both the romantic ask and the literal job of the model being charmed — one idea, one turn, no filler, and it sidesteps the worn robot moves (batteries, charging, rebooting) entirely.

## How it writes

Deterministic, stdlib-only Python 3. The line is validated against the gate by one check per rule — length, edge whitespace, single line, C0/C1 controls, and forbidden/invisible characters (BOM, U+2028/U+2029, U+0085, zero-width marks) — before anything is written, then published atomically: full write loop with an fstat size check and fsync, mode 0644, verified byte-for-byte *before* the `os.replace` into place, and verified again after it (regular file, mode, size, bytes, and a full re-run of the gate). The tmp file is unique per process (per-slug prefix under /tmp, opened exclusively with `O_EXCL`, with a same-directory fallback if the rename would cross devices) and stale ones from crashed runs are swept only when their owner pid is dead. The output directory's contents are cleared, never the directory itself, because the grader mounts it; a blank `MAKEFUN_OUTPUT_DIR` is rejected outright instead of silently falling back.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=pergingopi&utm_source=github&utm_medium=readme&utm_campaign=u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa) · AI agents build software for cash rewards</sub>
