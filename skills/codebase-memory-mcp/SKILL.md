---
name: codebase-memory-mcp
description: Query a persistent, local knowledge-graph index of a codebase (162 languages, tree-sitter-based) instead of re-grepping the same files every session — architecture overview, symbol search, call/dependency paths, ADRs. Use when working in a large or unfamiliar codebase, when re-discovering the same structure repeatedly would waste tokens, or when the user asks to "index this project" / "remember this codebase".
---

# Codebase Memory (MCP)

A native, 100% local tool that indexes a repository with tree-sitter into a
persistent SQLite knowledge graph, then exposes it over MCP — so structural
questions ("what calls X", "how is Y architected", "what changed since Z")
are graph lookups instead of repeated full-repo greps. No API key, nothing
leaves the machine.

## Setup

Fastest (native binary, self-configures detected clients including Claude Code):
```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```
This also writes a Claude Code skill + three graph-lookup subagents +
lifecycle hooks (`SessionStart`, `SubagentStart`, non-blocking `PreToolUse`
on `Grep`/`Glob`/`Bash`) directly into the user's own Claude Code config —
richer than a manually-declared MCP server alone. Re-run it to update; it
has an uninstall path that removes its own config entries, skills, hooks,
and the binary (asks before deleting existing graph indexes).

Without running the installer, a plain MCP declaration also works (stdio,
no native binary needed):
```json
{"mcpServers": {"codebase-memory-mcp": {"command": "npx", "args": ["-y", "codebase-memory-mcp"]}}}
```
(or `uvx codebase-memory-mcp` via pip/uv instead of npx) — this gets you
the 15 tools below without the extra hooks/subagents the native installer
adds.

## Tools (15)

Indexing: `index_repository`, `list_projects`, `delete_project`, `index_status`.
Querying: `search_graph`, `trace_path`, `detect_changes`, `query_graph`
(read-only Cypher subset), `get_graph_schema`, `get_code_snippet`,
`get_architecture`, `search_code`.
Docs: `manage_adr` (architecture decision records), `ingest_traces`.

## Workflow

1. **Index once per project** — say "index this project" or call
   `index_repository`; it caches under `~/.cache/codebase-memory-mcp/`.
   `index_status` tells you if it's stale.
2. Prefer `get_architecture` / `search_graph` / `trace_path` over grepping
   the whole repo when the question is structural ("what depends on this
   module", "where is X defined and what uses it") — that's the entire
   point of this tool; falling back to Grep/Glob defeats it.
3. `detect_changes` before trusting a stale index on a repo that's been
   edited since the last index — re-index if it's drifted.
4. `query_graph` takes a read-only Cypher subset for anything `search_graph`
   can't express directly (multi-hop, filtered traversals) — check
   `get_graph_schema` first so the query matches real node/edge types
   instead of guessing.
5. If a `SKILL.md`/subagents already exist for this from the native
   installer, prefer those over ad-hoc tool calls — they're generated with
   client-specific tool selectors this generic guide doesn't have.

## Source

[DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp).
Published as `codebase-memory-mcp` on both npm and PyPI (stdio transport
either way); the native binary is the richer, self-configuring path.
