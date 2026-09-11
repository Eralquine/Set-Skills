# Auth, rate limits, and free tier

## Auth

- Personal API key, prefixed `nvapi-...`, generated at
  [build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys)
  (or "Get API Key" on any model's page in the catalog).
- Sent as `Authorization: Bearer <key>` on every request — no OAuth2/OIDC
  flow, no scopes.
- The same key also works for NGC container pulls (`nvcr.io`, as the
  `$oauthtoken` password) and self-hosted NIM containers (`NGC_API_KEY` env
  var) — one key across hosted API + container registry + self-hosting.
- Store it as `NVIDIA_API_KEY` in the environment; never hardcode it in a
  request body or commit it.

## Rate limits (hosted endpoint, free developer tier)

- **40 requests/minute** per API key on `/v1/chat/completions`,
  `/v1/completions`, `/v1/embeddings`, and `/v1/ranking`.
- **5 concurrent** in-flight requests per API key.
- **1,000 free inference credits** granted on signup to the NVIDIA Developer
  Program, consumed across all hosted models.
- Self-hosted NIM containers aren't subject to these — they're bounded by
  your own GPU capacity and a configurable per-container concurrency limit.

If a build needs more than the free tier (production traffic, higher
concurrency), that's when self-hosting a NIM container or an NVIDIA AI
Enterprise plan becomes relevant — not something to reach for by default for
prototyping.

## Where this was verified

Cross-checked against NVIDIA's own docs (`docs.api.nvidia.com/nim/reference/limits`,
`build.nvidia.com`) and the OpenAPI specs in `references/openapi/`. Treat the
specific numbers as a snapshot — confirm against `build.nvidia.com/settings`
and the model's own page if a build depends on exact limits.
