---
name: turso
description: Query and manage a local SQLite/Turso database file through natural language via the tursodb CLI's built-in MCP mode. Use whenever the user wants to inspect, query, or modify a local .db/.sqlite file, or asks about Turso/libSQL. Local-only, no auth, no cloud account needed.
---

# Turso Database (tursodb)

Turso Database is a Rust rewrite of SQLite (replaces libSQL as the project's
direction), file-compatible with regular SQLite `.db` files. Its CLI,
`tursodb`, has a built-in MCP server mode — no separate MCP server package,
no auth, no cloud account: it just points at a local file.

## Setup

Install once:
```bash
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/tursodatabase/turso/releases/latest/download/turso_cli-installer.sh | sh
```

Register the MCP server **per database** (the db path is part of the
command, so this is project-specific — there's no single global config):
```bash
claude mcp add my-database -- tursodb ./path/to/your.db --mcp
```
Restart Claude Code to activate. Repeat with a different name/path for each
database the user wants access to (`claude mcp add analytics-db -- tursodb
/path/to/analytics.db --mcp`).

If the user doesn't have a `.db` file yet: `tursodb` with no args opens a
transient in-memory shell; `.open filename.db` inside it (or
`tursodb newfile.db` directly) creates a persistent one.

## Tools

Nine tools, all scoped to the one database file the server was pointed at:
`open_database`, `current_database`, `list_tables`, `describe_table`,
`execute_query` (read-only SELECT), `insert_data`, `update_data`,
`delete_data`, `schema_change`.

## Workflow

1. `current_database` / `list_tables` / `describe_table` before writing a
   query — don't assume a schema, read it.
2. Use `execute_query` for SELECTs; use `insert_data`/`update_data`/
   `delete_data`/`schema_change` for writes rather than trying to smuggle
   DML into `execute_query` (it's read-only by design).
3. Since the server is bound to one file at setup time, "wrong database"
   symptoms usually mean the wrong `claude mcp add` was registered, not a
   query bug — check which MCP server name is actually in use.
4. This is a local file on disk — schema changes and deletes are immediate
   and there's no built-in undo. For anything destructive on data the user
   cares about, confirm intent first (same caution as any other DB work).

## Source

[tursodatabase/turso](https://github.com/tursodatabase/turso) (MIT). No
separate MCP server repo exists — MCP mode is a flag on the CLI binary
itself.
