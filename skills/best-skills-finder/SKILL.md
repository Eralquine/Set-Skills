---
name: best-skills-finder
description: Check whether a well-maintained, popular agent skill already exists for a task before building one from scratch. Use whenever the user wants a Claude Code / OpenClaw / agent skill for something (e.g. "is there a skill for X", "what's the best skill for Y", "what's popular/trending in skills right now") — cross-references skills.sh, ClawHub, and Tencent SkillHub (10,000+ skills tracked, updated daily) instead of guessing from training data, which will be stale.
---

# Best Skills Finder

Cross-ecosystem, daily-updated rankings of agent skills (skills.sh, ClawHub,
Tencent SkillHub, GitHub, social buzz), maintained as open CSVs by
[LinklyAI/best-skills](https://github.com/LinklyAI/best-skills). Live,
interactive version: [linkly.ai/skills](https://linkly.ai/skills).

**Data changes daily — always fetch fresh, never rely on memory of what was
in a ranking before.** Nothing here is vendored locally on purpose.

## Workflow

1. Fetch the ranking that matches the question:
   ```bash
   curl -s https://raw.githubusercontent.com/LinklyAI/best-skills/main/data/latest/rankings/best-100.csv
   ```
   Swap `best-100` for `top-installs`, `trending-7d`, `rising-stars`,
   `official-100`, `social-buzz`, `most-active`, `top-repos`, or
   `official-vendors` — see `references/columns.md` for what each contains
   and which columns matter.
2. Filter/search the CSV for the domain the user asked about (grep the
   `skill`/`description` columns, or pipe through a quick script if you need
   to sort by `wis`/`pop_score`) — don't just eyeball the Top 10 in the
   README, that's a curated preview, not the full Top 100.
3. Present 2-4 real candidates with their actual scores/install counts and
   registry URL, not a single pick — let the user choose. Note the
   `coverage` grade (A/B/C) when using `best-100`/`top-installs` so a
   single-registry result isn't presented with the same confidence as one
   backed by all three.
4. If nothing relevant turns up, say so plainly rather than stretching an
   unrelated result to fit — this is a big but not exhaustive index (skills
   published only as loose GitHub repos without a `SKILL.md`/registry
   listing won't appear here at all).

## When this changes what you'd otherwise do

- User wants a skill "for X" → check here before writing one from scratch or
  reaching for a half-remembered name from training data.
- User asks what's popular/trending → `trending-7d.csv` or `best-100.csv`,
  not a guess.
- User specifically wants something from an **official/verified** publisher
  (lower risk, maintained) → `official-100.csv`.
- User wants something **brand new** rather than an established one →
  `rising-stars.csv` (skills <30 days old are excluded from `best-100` on
  purpose, to avoid penalizing them for missing history).

## Caveats

- Numbers are **never comparable across platforms** — see
  `references/columns.md`'s core rules before presenting or combining any
  counts.
- This indexes skills published to skills.sh/ClawHub/SkillHub/tracked
  GitHub repos — a skill that only exists as someone's personal repo (like
  most of the ones in *this* Set-Skills collection) won't show up here.
  This is a discovery tool for the wider ecosystem, not a completeness
  check on your own collection.
- CC BY 4.0 data, collection pipeline open source at
  [LinklyAI/best-skills-runner](https://github.com/LinklyAI/best-skills-runner)
  if you need to verify how a number was derived.
