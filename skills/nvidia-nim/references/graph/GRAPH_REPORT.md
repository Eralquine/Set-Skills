# NVIDIA NIM Model Graph Report

Source: seed list (no API key), 32 models.

**This is a partial, hand-verified seed list (~32 models), not the full NVIDIA catalog (100+ models as of this writing).** Set `NVIDIA_API_KEY` and re-run `scripts/build_model_graph.py` on a network that can reach `integrate.api.nvidia.com` (this sandbox's egress policy blocks that domain) to get the real, current, full catalog.

## Models per category

| Category | Models |
|---|---|
| chat | 22 |
| embeddings | 3 |
| image-generation | 3 |
| reranking | 2 |
| tts | 1 |
| asr | 1 |

## Models per provider

| Provider | Models |
|---|---|
| nvidia | 9 |
| meta | 5 |
| mistralai | 3 |
| google | 3 |
| microsoft | 2 |
| deepseek-ai | 2 |
| qwen | 2 |
| bytedance | 1 |
| abacusai | 1 |
| ibm | 1 |
| baai | 1 |
| black-forest-labs | 1 |
| stabilityai | 1 |

## Suggested questions

- "¿Qué modelos de chat tiene NVIDIA propios (`nvidia/...`)?"
- "¿Cuáles son rápidos para edge/mobile?" (mirar `use_case`)
- Abre `graph.html` y filtra por categoría para explorar visualmente.
