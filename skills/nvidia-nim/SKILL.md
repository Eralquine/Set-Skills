---
name: nvidia-nim
description: Use NVIDIA's hosted NIM API (build.nvidia.com / integrate.api.nvidia.com) instead of re-discovering it from scratch — chat/LLM, embeddings, reranking, vision, image generation, TTS/ASR, and BioNeMo biology models, all OpenAI-transport-compatible behind one API key. Use whenever the user wants to call an NVIDIA-hosted model, build a tool/integration on top of NVIDIA's inference API, or asks "how do I use build.nvidia.com" / "NVIDIA NIM" / "nvapi key".
---

# NVIDIA NIM (build.nvidia.com)

NVIDIA NIM is a catalog of GPU-accelerated inference microservices exposed
behind OpenAI-compatible REST endpoints — one API key, one base URL
(`https://integrate.api.nvidia.com`), 100+ models across chat/LLM,
embeddings, reranking, vision, image generation, speech, and biology
(BioNeMo). The same paths work self-hosted (NIM containers) by pointing at
`http://localhost:8000` instead.

This skill exists so building against NVIDIA's API doesn't mean re-reading
docs each time: real endpoint paths, request shapes, and OpenAPI specs are
in `references/`, sourced from NVIDIA's own docs and OpenAPI specs (not
guessed).

## Workflow

1. **Check `references/endpoints.md` first** — it maps every category
   (chat, embeddings, reranking, images, TTS, ASR, biology, models, health)
   to its exact path, quirks, and a minimal working example. Most of what
   you need is there without opening the full spec.
2. **Read the matching file in `references/openapi/`** before writing a
   request body for a category you haven't used yet in this session — some
   of these are *not* plain OpenAI-shaped (embeddings needs `input_type`;
   reranking takes nested `query`/`passages` objects, not flat arrays) and
   guessing the shape wastes a round trip.
3. **Auth**: needs `NVIDIA_API_KEY` (an `nvapi-...` key from
   [build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys))
   sent as `Authorization: Bearer $NVIDIA_API_KEY`. See
   `references/auth-and-limits.md` for rate limits and the free tier.
4. **Model IDs drift** — the catalog changes. `references/endpoints.md` has
   example model IDs seen in the specs, but before depending on one, confirm
   it's still live with `GET /v1/models` (or the model's page on
   build.nvidia.com) rather than assuming the example is current.
   `references/graph/` has a browsable category → model → provider graph
   built from `scripts/build_model_graph.py` — regenerate it with
   `NVIDIA_API_KEY=... python3 scripts/build_model_graph.py` for the full,
   current catalog (it falls back to a ~32-model hand-verified seed list
   without a key — see the graph's own report for which mode produced it).
   No API key handy but need the catalog anyway? `scripts/scrape_model_catalog.py`
   uses the `scrapling-official` skill to browse `build.nvidia.com/models`
   directly and capture the page's own internal API calls (more reliable
   than scraping rendered HTML) — see that script's docstring.
5. For chat/completions/embeddings, the transport is OpenAI-compatible
   enough that the official `openai` SDK works unmodified — just change
   `base_url` to `https://integrate.api.nvidia.com/v1` and `api_key` to the
   NVIDIA key. Don't reach for a bespoke HTTP client unless the endpoint
   needs it (images, TTS/ASR, biology do — see `endpoints.md`).

## What NOT to do

- Don't invent endpoint paths or parameter names — every real one is in
  `references/`. If something the user wants isn't covered there, say so and
  check the model's own page on build.nvidia.com rather than guessing.
- Don't assume free-tier limits or pricing are current for a
  production-sizing decision — point the user at build.nvidia.com/settings
  and the model's pricing page for anything that has to be exact.
- Don't treat `/v1/embeddings` or `/v1/ranking` as literally OpenAI's
  schema — they aren't (see `endpoints.md`).

## Source

Endpoint paths and schemas verified against NVIDIA's own docs
(`docs.api.nvidia.com`, `build.nvidia.com`) and the OpenAPI specs published
in [api-evangelist/nvidia-nim](https://github.com/api-evangelist/nvidia-nim)
(an independent third-party profile of NVIDIA's public API surface, not an
NVIDIA repo). Re-verify against `build.nvidia.com` if something looks stale
— this is a snapshot, not a live sync.
