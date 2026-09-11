# NVIDIA NIM hosted endpoints (build.nvidia.com)

Base URL: `https://integrate.api.nvidia.com` (self-hosted NIM containers use
`http://localhost:8000` with the same paths). Every endpoint below is
OpenAI-compatible in transport (`Authorization: Bearer <key>`, JSON in/out)
even where the payload shape is NVIDIA-specific — see the notes.

Full OpenAPI specs (real request/response schemas, all fields, enums, error
codes) are in `references/openapi/`, one file per category — read the
relevant one before writing a request body instead of guessing fields.

| Category | Endpoint | Spec file | Notes |
|---|---|---|---|
| Chat / LLM | `POST /v1/chat/completions` | `nvidia-nim-chat-api-openapi.yml` | Standard OpenAI chat schema. Streaming via SSE (`stream: true`), tool/function calling, JSON mode, and image inputs in `messages` on VLM models (same endpoint as vision). 100+ models: Llama, Mistral/Mixtral, Nemotron, DeepSeek, Qwen, Phi, Gemma, Granite, etc. |
| Text completion | `POST /v1/completions` | `nvidia-nim-completions-api-openapi.yml` | Legacy single-turn completion, OpenAI-compatible. |
| Vision / VLM | `POST /v1/chat/completions` | `nvidia-nim-vision-api-openapi.yml` | Same endpoint as chat — pass an image (URL or base64 data URI) inside a message's content array on a VLM model. |
| Embeddings | `POST /v1/embeddings` | `nvidia-nim-embeddings-api-openapi.yml` | **Not plain OpenAI-compatible**: NV-EmbedQA-style models require `input_type: "query"` or `"passage"` (asymmetric retrieval) or results are poor. Also takes `truncate` (`NONE`/`START`/`END`) and optional `dimensions` for Matryoshka models. |
| Reranking | `POST /v1/ranking` | `nvidia-nim-reranking-api-openapi.yml` | **Not OpenAI-shaped at all** — body is `{model, query: {text}, passages: [{text}, ...]}`, Cohere-rerank-style, not a flat list of strings. |
| Image generation | `POST /v1/genai/{publisher}/{model}` | `nvidia-nim-images-api-openapi.yml` | Path-parameterized by publisher+model (e.g. `black-forest-labs/flux.1-schnell`, `stabilityai/sdxl-turbo`, `nvidia/edify-image`). Request schema varies by model family — check the model's own doc page before assuming SDXL-style params work on FLUX. |
| Text-to-speech | `POST /v1/audio/speech` | `nvidia-nim-tts-api-openapi.yml` | Riva TTS NIMs (Magpie-TTS, FastPitch). `{model, input, voice, response_format: mp3\|wav\|opus\|flac, speed}`. Returns raw audio bytes, not JSON. |
| Speech-to-text | `POST /v1/audio/transcriptions` | `nvidia-nim-asr-api-openapi.yml` | Riva ASR NIMs (Parakeet, Canary). `multipart/form-data`: `file`, `model`, `language` (default `en-US`), `response_format: json\|text\|srt\|vtt`. |
| Biology (BioNeMo) | `POST /v1/biology/nvidia/alphafold2/predict-structure-from-sequence`<br>`POST /v1/biology/mit/diffdock`<br>`POST /v1/biology/nvidia/molmim/generate` | `nvidia-nim-biology-api-openapi.yml` | Protein structure prediction (AlphaFold2/ESMFold/OpenFold), molecular docking (DiffDock), molecule generation (MolMIM). Each model has its own task-specific payload — read the spec per model, don't assume a shared shape. |
| Model catalog | `GET /v1/models`, `GET /v1/models/{model_id}` | `nvidia-nim-models-api-openapi.yml` | **The live source of truth for what's actually deployed/available right now** — the model catalog changes often; don't trust a hardcoded list (including the example model names in this skill) over what this endpoint returns. |
| Health / metrics | `GET /v1/health/live`, `GET /v1/health/ready`, `GET /v1/metrics` | `nvidia-nim-health-api-openapi.yml` | Mainly relevant for self-hosted NIM containers (liveness/readiness probes), Prometheus-style metrics. |

## Example model IDs seen in the specs (verify against `/v1/models` — catalog moves)

- Chat/LLM: `meta/llama-3.1-*`, `mistralai/mixtral-8x22b-instruct-v0.1`, `nvidia/nemotron-*`, `deepseek-ai/*`, `qwen/*`, `microsoft/phi-*`, `google/gemma-*`, `ibm/granite-*`
- Embeddings: `nvidia/llama-3.2-nv-embedqa-1b-v2`, `nvidia/nv-embedqa-e5-v5`, `baai/bge-m3`
- Reranking: `nvidia/llama-3.2-nv-rerankqa-1b-v2`, `nvidia/nv-rerankqa-mistral-4b-v3`
- TTS: `nvidia/magpie-tts`
- ASR: `nvidia/parakeet-ctc-1.1b-asr`
- Image gen: `black-forest-labs/flux.1-schnell`, `stabilityai/sdxl-turbo`, `nvidia/edify-image`

## Minimal working examples

Chat completion:

```bash
curl https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Say hi in one word."}],
    "stream": false
  }'
```

Embeddings (note `input_type`):

```bash
curl https://integrate.api.nvidia.com/v1/embeddings \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/nv-embedqa-e5-v5",
    "input": ["What is NIM?"],
    "input_type": "query"
  }'
```

Reranking (nested query/passages, not a flat array):

```bash
curl https://integrate.api.nvidia.com/v1/ranking \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/nv-rerankqa-mistral-4b-v3",
    "query": {"text": "What is NIM?"},
    "passages": [{"text": "NIM is..."}, {"text": "Unrelated text."}]
  }'
```

Because the transport is OpenAI-compatible for chat/completions/embeddings,
the OpenAI SDK works by just swapping `base_url` and `api_key`:

```python
from openai import OpenAI
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
resp = client.chat.completions.create(model="meta/llama-3.1-8b-instruct", messages=[...])
```
