# Ranking CSV columns

All fetched fresh at `https://raw.githubusercontent.com/LinklyAI/best-skills/main/data/latest/rankings/<name>.csv`.
Every ranking preserves raw per-platform numbers alongside any composite score — never invent a summed cross-platform total, the source explicitly avoids that (see Core rules below).

| File | What it ranks | Key columns beyond the shared id columns |
|---|---|---|
| `best-100.csv` | Overall "worth installing" | `wis` (0-100 composite score), `popularity`, `momentum`, `buzz`, `maintenance`, `trust`, `coverage` (A/B/C = how many registries have install data), `anomaly` |
| `top-installs.csv` | Raw install/download counts | `installs_skillssh`, `downloads_clawhub`, `downloads_skillhub_cn` — side by side, never summed |
| `trending-7d.csv` | 7-day growth | `installs`, weekly `Δ%` |
| `rising-stars.csv` | New skills (<30 days old) gaining traction, kept separate so they aren't penalized for missing history | `first_seen_days`, `pop_score` |
| `official-100.csv` | Official/verified-publisher skills only | `verified_by` (which registry verified them), `pop_score` |
| `official-vendors.csv` | Vendors/publishers, not individual skills | `skills_count`, `total_installs_or_downloads`, `featured_skill` |
| `social-buzz.csv` | Social mention volume (X/HN/Bluesky/GitHub, 7-day window) | `x_mentions_7d`, `hn_hits_7d`, `bsky_hits_7d`, `gh_mentions_7d`, `buzz_score`, `buzz_shared` (true = name collides with another skill, mentions may not be attributable) |
| `most-active.csv` | Recent maintenance activity | `last_update`, `versions_clawhub`, `freshness_score` |
| `top-repos.csv` | GitHub repos (not individual skills — a repo can bundle many) | `stars`, `stars_1d`, `skills_tracked`, `topics` |

Shared id columns on most files: `rank`, `skill`, `platform` (skills.sh / clawhub / skillhub-cn), `vendor`, `url` (the skill's page on its origin registry, empty if none exists), `match` (`single` = one source only, `upstream`/`upstream-unresolved` = cross-platform join evidence).

## Core rules (from the source's methodology — respect these when presenting results)

- **Never sum numbers across platforms.** skills.sh, ClawHub, and Tencent SkillHub count different, non-overlapping things (different ecosystems/regions/dedup rules). Report them side by side, or use the pre-computed percentile composite (`wis`, `pop_score`) — never add `installs_skillssh + downloads_clawhub` yourself.
- **Repo stars (`top-repos.csv`) never rank individual skills** — a monorepo with 14 skills shares one star count.
- **`coverage: C`** on `best-100`/`top-installs` means data from only one registry — say so rather than presenting a `C`-coverage entry with the same confidence as an `A`.
- Empty cells in `best-100.csv` (e.g. blank `maintenance`) mean "not measured, neutral prior 0.3 was used" — not zero.
- Full methodology (weights, known limitations, why some skills are excluded from `social-buzz`): fetch `https://raw.githubusercontent.com/LinklyAI/best-skills/main/docs/methodology.md` if a claim needs to be precise.
