#!/usr/bin/env python3
"""
Build a category -> model -> provider graph of the NVIDIA NIM catalog.

Live mode (recommended): set NVIDIA_API_KEY and run this on a network that
can reach integrate.api.nvidia.com (this sandbox's egress policy blocks it,
so it was never run live from here — try it on your own machine). It calls
GET /v1/models and builds the graph from the real, current catalog.

Offline/seed mode (no key, or network blocked): falls back to a small,
hand-verified list of ~32 real model IDs pulled from NVIDIA's own OpenAPI
specs (see ../endpoints.md) and a public NIM model-listing script's static
metadata table. This is NOT the full catalog (NVIDIA lists 100+ models) --
it's a labeled-as-partial starter so the graph exists and is useful before
you have a key.

Output (references/graph/): graph.json, graph.html (D3 viewer), GRAPH_REPORT.md
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_DIR = os.path.join(SCRIPT_DIR, "..", "references", "graph")

# Known-real model IDs, verified from NVIDIA's OpenAPI specs (../endpoints.md)
# plus a public model-listing script's static metadata table. Used only when
# no live API access is available. Category is assigned by known endpoint,
# not guessed from the name.
SEED_MODELS = [
    # Chat / LLM (POST /v1/chat/completions)
    {"model": "meta/llama-3.1-8b-instruct", "category": "chat", "use_case": "Fast general-purpose chat"},
    {"model": "meta/llama-3.1-70b-instruct", "category": "chat", "use_case": "Complex reasoning, high quality"},
    {"model": "meta/llama-3.2-1b-instruct", "category": "chat", "use_case": "Edge devices, ultra-low latency"},
    {"model": "meta/llama-3.2-3b-instruct", "category": "chat", "use_case": "Mobile, low-resource"},
    {"model": "meta/llama-3.3-70b-instruct", "category": "chat", "use_case": "Latest Llama, optimized"},
    {"model": "mistralai/mistral-7b-instruct-v0.3", "category": "chat", "use_case": "Efficient general purpose"},
    {"model": "mistralai/mixtral-8x7b-instruct", "category": "chat", "use_case": "Balanced MoE performance"},
    {"model": "mistralai/mixtral-8x22b-instruct-v0.1", "category": "chat", "use_case": "High-end MoE reasoning"},
    {"model": "microsoft/phi-4-mini-instruct", "category": "chat", "use_case": "Compact, efficient"},
    {"model": "microsoft/phi-4-mini-flash-reasoning", "category": "chat", "use_case": "Fast reasoning tasks"},
    {"model": "google/gemma-7b", "category": "chat", "use_case": "Base model for fine-tuning"},
    {"model": "google/gemma-2-2b-it", "category": "chat", "use_case": "Lightweight chat"},
    {"model": "google/codegemma-7b", "category": "chat", "use_case": "Code generation"},
    {"model": "nvidia/nemotron-mini-4b-instruct", "category": "chat", "use_case": "Compact instruction following"},
    {"model": "nvidia/llama-3.1-nemotron-nano-8b-v1", "category": "chat", "use_case": "Optimized Llama variant"},
    {"model": "deepseek-ai/deepseek-v4-flash", "category": "chat", "use_case": "Fast inference"},
    {"model": "deepseek-ai/deepseek-v4-pro", "category": "chat", "use_case": "High quality"},
    {"model": "qwen/qwen2.5-coder-7b-instruct", "category": "chat", "use_case": "Code generation"},
    {"model": "qwen/qwen3-coder-480b-a35b-instruct", "category": "chat", "use_case": "Advanced coding"},
    {"model": "bytedance/seed-oss-36b-instruct", "category": "chat", "use_case": "Open source large model"},
    {"model": "abacusai/dracarys-llama-3.1-70b-instruct", "category": "chat", "use_case": "Enhanced Llama variant"},
    {"model": "ibm/granite-3.0-8b-instruct", "category": "chat", "use_case": "Enterprise general purpose"},
    # Embeddings (POST /v1/embeddings)
    {"model": "nvidia/llama-3.2-nv-embedqa-1b-v2", "category": "embeddings", "use_case": "Asymmetric retrieval (query/passage)"},
    {"model": "nvidia/nv-embedqa-e5-v5", "category": "embeddings", "use_case": "Asymmetric retrieval (query/passage)"},
    {"model": "baai/bge-m3", "category": "embeddings", "use_case": "Multilingual embeddings"},
    # Reranking (POST /v1/ranking)
    {"model": "nvidia/llama-3.2-nv-rerankqa-1b-v2", "category": "reranking", "use_case": "RAG result reranking"},
    {"model": "nvidia/nv-rerankqa-mistral-4b-v3", "category": "reranking", "use_case": "RAG result reranking"},
    # Text-to-speech (POST /v1/audio/speech)
    {"model": "nvidia/magpie-tts", "category": "tts", "use_case": "Speech synthesis (Riva)"},
    # Speech-to-text (POST /v1/audio/transcriptions)
    {"model": "nvidia/parakeet-ctc-1.1b-asr", "category": "asr", "use_case": "Speech transcription (Riva)"},
    # Image generation (POST /v1/genai/{publisher}/{model})
    {"model": "black-forest-labs/flux.1-schnell", "category": "image-generation", "use_case": "Fast image generation"},
    {"model": "stabilityai/sdxl-turbo", "category": "image-generation", "use_case": "Fast image generation"},
    {"model": "nvidia/edify-image", "category": "image-generation", "use_case": "High-fidelity image generation"},
]


def fetch_live_models(api_key):
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data.get("data", [])


def guess_category(model_id):
    name = model_id.lower()
    if "embed" in name:
        return "embeddings"
    if "rerank" in name:
        return "reranking"
    if "tts" in name or "magpie" in name:
        return "tts"
    if "asr" in name or "parakeet" in name or "canary" in name:
        return "asr"
    if any(k in name for k in ("flux", "sdxl", "edify", "stable-diffusion")):
        return "image-generation"
    if any(k in name for k in ("vlm", "vision", "vl-")):
        return "vision"
    if "biology" in name or "alphafold" in name or "diffdock" in name or "molmim" in name:
        return "biology"
    return "chat"


def build_from_live(models_raw):
    out = []
    for m in models_raw:
        model_id = m.get("id", "")
        if not model_id:
            continue
        out.append({"model": model_id, "category": guess_category(model_id), "use_case": ""})
    return out


def main():
    api_key = os.environ.get("NVIDIA_API_KEY")
    source_note = ""
    if api_key:
        try:
            print("Fetching live catalog from https://integrate.api.nvidia.com/v1/models ...")
            models = build_from_live(fetch_live_models(api_key))
            source_note = f"live /v1/models fetch, {len(models)} models"
            print(f"Got {len(models)} models from the live API.")
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"Live fetch failed ({e}); falling back to the seed list.", file=sys.stderr)
            models = SEED_MODELS
            source_note = f"seed list (live fetch failed), {len(models)} models"
    else:
        print("NVIDIA_API_KEY not set; using the seed list (partial, ~32 known models).")
        print("Set NVIDIA_API_KEY and re-run for the full, current catalog.")
        models = SEED_MODELS
        source_note = f"seed list (no API key), {len(models)} models"

    nodes = {}
    edges = []

    def add_node(node_id, label, ntype, **attrs):
        if node_id not in nodes:
            nodes[node_id] = {"id": node_id, "label": label, "type": ntype, **attrs}
        return node_id

    for m in models:
        provider = m["model"].split("/")[0] if "/" in m["model"] else "unknown"
        cat_id = add_node(f"cat:{m['category']}", m["category"], "category")
        prov_id = add_node(f"provider:{provider}", provider, "provider")
        model_id = add_node(
            f"model:{m['model']}", m["model"], "model",
            use_case=m.get("use_case", ""),
        )
        edges.append({"source": cat_id, "target": model_id, "relation": "contains", "confidence": "EXTRACTED"})
        edges.append({"source": model_id, "target": prov_id, "relation": "published_by", "confidence": "EXTRACTED"})

    graph = {
        "meta": {
            "source": f"NVIDIA NIM catalog ({source_note})",
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        "nodes": list(nodes.values()),
        "edges": edges,
    }

    os.makedirs(GRAPH_DIR, exist_ok=True)
    with open(os.path.join(GRAPH_DIR, "graph.json"), "w") as f:
        json.dump(graph, f, ensure_ascii=False, indent=1)

    # GRAPH_REPORT.md
    from collections import Counter
    cat_counts = Counter(m["category"] for m in models)
    provider_counts = Counter(m["model"].split("/")[0] for m in models)

    lines = ["# NVIDIA NIM Model Graph Report\n\n"]
    lines.append(f"Source: {source_note}.\n\n")
    if not api_key:
        lines.append(
            "**This is a partial, hand-verified seed list (~32 models), not the "
            "full NVIDIA catalog (100+ models as of this writing).** Set "
            "`NVIDIA_API_KEY` and re-run `scripts/build_model_graph.py` on a "
            "network that can reach `integrate.api.nvidia.com` (this sandbox's "
            "egress policy blocks that domain) to get the real, current, full "
            "catalog.\n\n"
        )
    lines.append("## Models per category\n\n| Category | Models |\n|---|---|\n")
    for cat, count in cat_counts.most_common():
        lines.append(f"| {cat} | {count} |\n")
    lines.append("\n## Models per provider\n\n| Provider | Models |\n|---|---|\n")
    for prov, count in provider_counts.most_common():
        lines.append(f"| {prov} | {count} |\n")
    lines.append(
        "\n## Suggested questions\n\n"
        "- \"¿Qué modelos de chat tiene NVIDIA propios (`nvidia/...`)?\"\n"
        "- \"¿Cuáles son rápidos para edge/mobile?\" (mirar `use_case`)\n"
        "- Abre `graph.html` y filtra por categoría para explorar visualmente.\n"
    )
    with open(os.path.join(GRAPH_DIR, "GRAPH_REPORT.md"), "w") as f:
        f.writelines(lines)

    write_graph_html(graph)

    print(f"Wrote {GRAPH_DIR}/graph.json, graph.html, GRAPH_REPORT.md ({len(nodes)} nodes, {len(edges)} edges).")


def write_graph_html(graph):
    graph_json = json.dumps(graph, ensure_ascii=False)
    n_models = len([n for n in graph["nodes"] if n["type"] == "model"])
    n_cats = len([n for n in graph["nodes"] if n["type"] == "category"])
    html_doc = HTML_TEMPLATE.replace("__GRAPH_JSON__", graph_json)
    html_doc = html_doc.replace("__MODEL_COUNT__", str(n_models))
    html_doc = html_doc.replace("__CAT_COUNT__", str(n_cats))
    with open(os.path.join(GRAPH_DIR, "graph.html"), "w") as f:
        f.write(html_doc)


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>NVIDIA NIM Model Graph</title>
<style>
  :root { color-scheme: light dark; }
  html, body { margin: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0b0e14; color: #e6e6e6; }
  #app { display: flex; height: 100%; }
  #sidebar { width: 320px; flex-shrink: 0; padding: 16px; box-sizing: border-box; overflow-y: auto; background: #11151d; border-right: 1px solid #232a36; }
  #canvas-wrap { flex: 1; position: relative; }
  h1 { font-size: 15px; margin: 0 0 4px; }
  .sub { font-size: 12px; color: #8b93a3; margin-bottom: 16px; }
  label { font-size: 12px; color: #8b93a3; display: block; margin: 12px 0 4px; }
  select, input[type=text] { width: 100%; box-sizing: border-box; padding: 6px 8px; background: #1a2029; border: 1px solid #2a3140; color: #e6e6e6; border-radius: 6px; font-size: 13px; }
  #legend { margin-top: 16px; font-size: 12px; }
  .legend-item { display: flex; align-items: center; gap: 6px; margin: 4px 0; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  #detail { margin-top: 16px; padding-top: 16px; border-top: 1px solid #232a36; font-size: 13px; line-height: 1.5; }
  #detail .placeholder { color: #5a6270; font-size: 12px; }
  #stats { font-size: 11px; color: #5a6270; margin-top: 16px; }
  svg { width: 100%; height: 100%; display: block; }
  .link { stroke: #2a3140; stroke-width: 1px; }
  .node circle { stroke: #0b0e14; stroke-width: 1px; cursor: pointer; }
  .node text { font-size: 9px; fill: #aab2c0; pointer-events: none; }
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <h1>NVIDIA NIM Model Graph</h1>
    <div class="sub">__MODEL_COUNT__ modelos · __CAT_COUNT__ categorías</div>
    <label for="catFilter">Categoría</label>
    <select id="catFilter"></select>
    <label for="search">Buscar modelo</label>
    <input type="text" id="search" placeholder="ej. llama, embed, tts...">
    <div id="legend">
      <div class="legend-item"><span class="dot" style="background:#ffb454"></span> Categoría</div>
      <div class="legend-item"><span class="dot" style="background:#6cb6ff"></span> Modelo</div>
      <div class="legend-item"><span class="dot" style="background:#7ee787"></span> Proveedor</div>
    </div>
    <div id="detail"><div class="placeholder">Click un nodo para ver detalles.</div></div>
    <div id="stats"></div>
  </div>
  <div id="canvas-wrap"><svg></svg></div>
</div>
<script id="graph-data" type="application/json">__GRAPH_JSON__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
const graph = JSON.parse(document.getElementById('graph-data').textContent);
const allNodes = graph.nodes, allEdges = graph.edges;
const catCounts = {};
allNodes.forEach(n => { if (n.type === 'category') catCounts[n.label] = 0; });
allEdges.forEach(e => {
  const s = allNodes.find(n => n.id === e.source);
  if (s && s.type === 'category') catCounts[s.label] = (catCounts[s.label] || 0) + 1;
});
document.getElementById('stats').textContent = `${allNodes.length} nodos · ${allEdges.length} conexiones`;
const catSelect = document.getElementById('catFilter');
const cats = Object.keys(catCounts).sort((a,b) => catCounts[b]-catCounts[a]);
catSelect.innerHTML = '<option value="__all__">Todas</option>' + cats.map(c => `<option value="${c}">${c} (${catCounts[c]})</option>`).join('');
catSelect.value = '__all__';
const svg = d3.select('svg');
const g = svg.append('g');
svg.call(d3.zoom().scaleExtent([0.1, 6]).on('zoom', (ev) => g.attr('transform', ev.transform)));
const detail = document.getElementById('detail');
let simulation;
function color(type) { return type === 'category' ? '#ffb454' : type === 'provider' ? '#7ee787' : '#6cb6ff'; }
function radius(type) { return type === 'category' ? 10 : type === 'provider' ? 7 : 5; }
function showDetail(n) {
  if (n.type === 'model') {
    detail.innerHTML = `<b>${n.label}</b><br>${n.use_case || ''}`;
  } else {
    detail.innerHTML = `<b>${n.label}</b><br><span class="placeholder">${n.type}</span>`;
  }
}
function render(categoryLabel) {
  g.selectAll('*').remove();
  let nodes, edges;
  if (categoryLabel === '__all__') { nodes = allNodes; edges = allEdges; }
  else {
    const catNode = allNodes.find(n => n.type === 'category' && n.label === categoryLabel);
    const modelIds = new Set(allEdges.filter(e => e.source === catNode.id).map(e => e.target));
    const provEdges = allEdges.filter(e => modelIds.has(e.source));
    const provIds = new Set(provEdges.map(e => e.target));
    const nodeIds = new Set([catNode.id, ...modelIds, ...provIds]);
    nodes = allNodes.filter(n => nodeIds.has(n.id));
    edges = [...allEdges.filter(e => e.source === catNode.id), ...provEdges];
  }
  const width = svg.node().clientWidth, height = svg.node().clientHeight;
  const link = g.append('g').selectAll('line').data(edges).join('line').attr('class', 'link');
  const node = g.append('g').selectAll('g').data(nodes).join('g').attr('class', 'node')
    .call(d3.drag()
      .on('start', (ev, d) => { if (!ev.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
      .on('end', (ev, d) => { if (!ev.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));
  node.append('circle').attr('r', d => radius(d.type)).attr('fill', d => color(d.type)).on('click', (ev, d) => showDetail(d));
  node.append('text').attr('dx', d => radius(d.type) + 3).attr('dy', 3).text(d => d.type !== 'model' ? d.label : '');
  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(50).strength(0.3))
    .force('charge', d3.forceManyBody().strength(-60))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide(d => radius(d.type) + 3))
    .on('tick', () => {
      link.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
}
catSelect.addEventListener('change', () => render(catSelect.value));
document.getElementById('search').addEventListener('input', (ev) => {
  const q = ev.target.value.trim().toLowerCase();
  g.selectAll('.node circle').attr('opacity', d => !q || d.label.toLowerCase().includes(q) ? 1 : 0.15);
});
render('__all__');
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
