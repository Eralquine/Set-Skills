---
name: scrapegraph-mcp
description: Extract structured data from web pages via natural-language prompts (no CSS selectors needed) using ScrapeGraphAI's hosted API — scrape, extract, search, multi-page crawl, JSON schema generation, and scheduled monitors. Use when the user wants "extract X from this page" described in plain language, needs scheduled change-monitoring on a page, or wants search results as structured data rather than raw HTML.
---

# ScrapeGraph MCP

Hosted API where you describe what to extract in plain language and an LLM
does the extraction — no CSS/XPath selectors to write or maintain. Different
tool for a different job than `scrapling-official`: reach for this when the
extraction logic itself should be prompt-driven (schema changes, ambiguous
targets, "get me whatever looks like a price") or when you need scheduled
monitoring; reach for `scrapling-official` when you need deterministic
selectors, stealth/anti-bot bypass, or a full crawl framework.

## Setup

Needs an API key from the [ScrapeGraph Dashboard](https://dashboard.scrapegraphai.com)
(paid service — check current pricing there). Simplest connection, the
hosted remote MCP endpoint:

```json
{"mcpServers": {"scrapegraph-mcp": {
  "url": "https://sgai-mcp-main.onrender.com",
  "headers": {"X-API-Key": "YOUR_API_KEY"}
}}}
```

(The older `https://mcp.scrapegraphai.com/mcp` endpoint is being deprecated
— use the one above for new setups.) Alternatively `npx -y @smithery/cli
install @ScrapeGraphAI/scrapegraph-mcp --client claude`, or clone+`pip
install -e .` to run it locally — see the repo's README for those paths.

## Tools

| Tool | Does |
|---|---|
| `scrape` | Fetch one page, `output_format`: markdown / html / screenshot / branding / links / images / summary |
| `extract` | `website_url` + `user_prompt` (plain language) → structured data; optional `output_schema` to pin the shape |
| `search` | Web search as structured results (`num_results` 1-20, `country_search`, `time_range`, optional `output_schema`) |
| `crawl_start` / `crawl_get_status` / `crawl_stop` / `crawl_resume` | Async multi-page crawl — start, poll `crawl_get_status` until `status: completed`, stop/resume as needed |
| `schema` | Generate or augment a JSON Schema from a prompt — build this before an `extract`/`crawl_start` call that needs a pinned shape |
| `monitor_create` / `monitor_list` / `monitor_get` / `monitor_pause` / `monitor_resume` / `monitor_delete` | Scheduled recurring scrape jobs with change detection |
| `monitor_activity` | Paginated tick history for a monitor: `createdAt`, `status`, `changed`, `elapsedMs`, `diffs` |
| `credits` / `history` | Account usage — check `credits` before a large `crawl_start` or bulk `search` run |

## Workflow

1. For a one-off extraction with a known target: `extract` directly with a
   clear `user_prompt`. Vague prompt → vague/unreliable extraction — be as
   specific as the user's request allows ("the price and currency", not
   "info about the product").
2. If the shape needs to be consistent across many pages or repeated runs,
   call `schema` first to generate an `output_schema`, then pass it to
   `extract`/`crawl_start`/`search` — don't leave the LLM to re-infer
   structure every call.
3. Multi-page work → `crawl_start`, then poll `crawl_get_status` (it's
   async — don't assume completion from the start call's response).
4. Recurring "let me know when this page changes" requests → `monitor_create`,
   not a crawl you re-run manually. Check `monitor_activity` for what
   actually changed rather than re-scraping to diff it yourself.
5. Check `credits` before a call that could be expensive (large crawl, high
   `num_results` search) — this is a paid, metered API.

## Source

[ScrapeGraphAI/scrapegraph-mcp](https://github.com/ScrapeGraphAI/scrapegraph-mcp)
(MIT), backed by the hosted [ScrapeGraphAI](https://scrapegraphai.com) API
(v2, `SGAI-APIKEY`/`X-API-Key` header). Not to be confused with the
`scrapegraphai` Python library (`pip install scrapegraphai`) — that's the
open-source local pipeline version; this skill covers the hosted MCP server.
