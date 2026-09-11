---
name: penpot
description: Drive Penpot (open-source Figma-alternative design tool) design files via its official MCP server — inspect/create/restyle components, tokens, pages and layers, export assets, and translate a design into HTML/CSS. Use whenever the user has a Penpot file open and wants to design, audit, or hand off to code, or asks about Penpot MCP.
---

# Penpot MCP

Penpot's official MCP server bridges an AI client to a Penpot design file
open in the browser, so you can read and modify components, styles, tokens,
pages, and layers in natural language — both design work and design-to-code.

## Architecture (matters for troubleshooting)

Three pieces, all must be connected:
1. **MCP server** — receives your tool calls, forwards them to Penpot.
2. **MCP plugin inside Penpot** — runs in the browser tab with the file
   open; must be explicitly connected (**File → MCP Server → Connect**) for
   the server to see anything. It always operates on the *currently focused
   page* — if the user switches pages/tabs, the context follows.
3. **This client** (Claude Code) — connects to the server via URL (+ MCP
   key for remote mode).

If a tool call fails or returns nothing, the first thing to check is
whether the Penpot plugin is actually connected to the right file/page —
not just whether the MCP server itself is reachable.

## Setup

**Remote (hosted, simplest):**
1. In Penpot: **Your account → Integrations → MCP Server** → enable, generate an MCP key (shown once — user must save it), copy the server URL (already includes the key as `userToken`).
2. Connect a client: `npx -y add-mcp -g -n penpot <URL>` (recommended by Penpot), or add it manually as a remote MCP server per the client's own docs.
3. In Penpot, open the file and **File → MCP Server → Connect**.

**Local mode** (self-hosted Penpot, no account/key needed): server URL is `http://localhost:4401/mcp` (streamable) or `http://localhost:4401/sse` (legacy SSE).

## Tools

- `execute_code` — run code against Penpot's JS Plugin API (the general-purpose tool; most design/dev tasks route through this).
- `high_level_overview` — summarize the current file/page structure before making changes.
- `penpot_api_info` — look up the Plugin API surface (methods/types) instead of guessing.
- `export_shape` — export a shape/asset. Local mode can write to a local path; **remote mode cannot** (no filesystem access) — only in-band export.
- `import_image` — **local mode only**, not available remotely.

## Workflow

1. `high_level_overview` before any change — know the file's actual structure (components, styles, tokens, pages) rather than assuming.
2. For anything beyond a trivial one-off, use `penpot_api_info` to confirm the right method/property before calling `execute_code` — the Plugin API has specific shapes for tokens vs. styles vs. component variants.
3. **This is a live, shared design file** — MCP write operations (create/rename/move/delete/restyle) apply immediately to whatever the user has open:
   - Start with read-only calls to verify you're looking at the right page/file.
   - Describe the intended change before applying it, especially anything that could cascade (renaming a widely-used component, restyling a shared token).
   - Prefer small, reversible steps over "refactor the whole file" in one call.
4. Design-to-code: read tokens/styles via `high_level_overview` + `penpot_api_info` first, then generate HTML/CSS that maps to them — don't hardcode values Penpot already expresses as a token.
5. Remote mode has a smaller tool surface than local (no filesystem-touching tools) — if a task needs `import_image` or a local-path `export_shape`, that's a local-mode-only task; say so rather than trying to work around it in remote mode.

## Source

[penpot/penpot](https://github.com/penpot/penpot) (MPL-2.0). MCP docs:
[help.penpot.app/mcp](https://help.penpot.app/mcp/),
[penpot.app/penpot-mcp-server](https://penpot.app/penpot-mcp-server). MCP
server package: `@penpot/mcp` on npm (used via `npx -y add-mcp`, not run
directly by hand under normal setup).
