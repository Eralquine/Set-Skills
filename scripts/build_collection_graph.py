#!/usr/bin/env python3
"""
Build a category -> entry -> requirement/source graph of this whole
Set-Skills collection (skills + plugins + templates + self-installers).

Data is hardcoded below rather than parsed from the manifests, because the
useful dimensions here -- category, what it actually needs to run, which
org/person it's from -- aren't machine-readable in skills/plugins.json/etc.
(a SKILL.md description doesn't declare "category: seo"). Each entry was
classified by hand while adding it to the collection, so this is a curated
snapshot, not a live sync: re-run this after adding/removing entries.

Output (./collection-graph/): graph.json, graph.html (D3 viewer), GRAPH_REPORT.md
"""
import json
import os
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "..", "collection-graph")

# kind: skill | plugin | template | self-installer
# category: one label describing what domain it's for
# needs: list of requirement tags (an entry can have more than one)
# source: org/person it comes from
ENTRIES = [
    {"id": "plasmic-designer", "kind": "skill", "category": "design", "needs": ["mcp-server"], "source": "plasmicapp"},
    {"id": "competitive-landscape", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "competitor-analysis", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "keyword-clustering", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "keyword-research", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "link-prospecting", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "local-seo", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "seo-audit", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "seo-coach", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "seo-project-setup", "kind": "skill", "category": "seo", "needs": ["mcp-server", "cloud-account"], "source": "every-app"},
    {"id": "api-finder", "kind": "skill", "category": "api-discovery", "needs": ["no-requirement"], "source": "public-apis"},
    {"id": "graphify", "kind": "skill", "category": "knowledge-graph", "needs": ["cli-install"], "source": "Graphify-Labs"},
    {"id": "nvidia-nim", "kind": "skill", "category": "llm-api", "needs": ["api-key-free"], "source": "NVIDIA"},
    {"id": "omnivoice", "kind": "skill", "category": "voice-tts", "needs": ["gpu-required"], "source": "k2-fsa"},
    {"id": "penpot", "kind": "skill", "category": "design", "needs": ["mcp-server", "cloud-account"], "source": "penpot"},
    {"id": "turso", "kind": "skill", "category": "database", "needs": ["cli-install"], "source": "tursodatabase"},
    {"id": "codebase-memory-mcp", "kind": "skill", "category": "code-search-memory", "needs": ["mcp-server", "cli-install"], "source": "DeusData"},
    {"id": "scrapling-official", "kind": "skill", "category": "scraping-research", "needs": ["cli-install"], "source": "D4Vinci"},
    {"id": "agent-reach", "kind": "skill", "category": "scraping-research", "needs": ["cli-install", "user-cookies"], "source": "Panniantong"},
    {"id": "scrapegraph-mcp", "kind": "skill", "category": "scraping-research", "needs": ["mcp-server", "api-key-paid"], "source": "ScrapeGraphAI"},
    {"id": "best-skills-finder", "kind": "skill", "category": "skill-discovery", "needs": ["no-requirement"], "source": "LinklyAI"},
    {"id": "find-skills", "kind": "skill", "category": "skill-discovery", "needs": ["cli-install"], "source": "vercel-labs"},
    {"id": "agent-browser", "kind": "skill", "category": "browser-automation", "needs": ["cli-install"], "source": "vercel-labs"},
    {"id": "frontend-design", "kind": "skill", "category": "design", "needs": ["no-requirement"], "source": "anthropics"},
    {"id": "web-design-guidelines", "kind": "skill", "category": "design", "needs": ["no-requirement"], "source": "vercel-labs"},
    {"id": "grill-me", "kind": "skill", "category": "dev-productivity", "needs": ["no-requirement"], "source": "mattpocock"},
    {"id": "grill-with-docs", "kind": "skill", "category": "dev-productivity", "needs": ["no-requirement"], "source": "mattpocock"},
    {"id": "azure-ai", "kind": "skill", "category": "cloud-azure", "needs": ["cli-install", "cloud-account"], "source": "microsoft"},
    {"id": "azure-compliance", "kind": "skill", "category": "cloud-azure", "needs": ["cli-install", "cloud-account"], "source": "microsoft"},
    {"id": "azure-storage", "kind": "skill", "category": "cloud-azure", "needs": ["cli-install", "cloud-account"], "source": "microsoft"},
    {"id": "vercel-react-best-practices", "kind": "skill", "category": "react-frontend", "needs": ["no-requirement"], "source": "vercel-labs"},
    {"id": "pagokit", "kind": "plugin", "category": "payments", "needs": ["no-requirement"], "source": "hainrixz"},
    {"id": "firecrawl", "kind": "plugin", "category": "scraping-research", "needs": ["mcp-server", "api-key-free"], "source": "firecrawl"},
    {"id": "cybersecurity-skills", "kind": "plugin", "category": "security", "needs": ["no-requirement"], "source": "mukul975"},
    {"id": "openmontage", "kind": "template", "category": "video-production", "needs": ["api-key-paid"], "source": "calesthio"},
    {"id": "daily-stock-analysis", "kind": "template", "category": "finance", "needs": ["api-key-free"], "source": "ZhuLinsen"},
    {"id": "omniroute", "kind": "template", "category": "llm-api", "needs": ["no-requirement"], "source": "diegosouzapw"},
    {"id": "gstack", "kind": "self-installer", "category": "dev-productivity", "needs": ["cli-install"], "source": "garrytan"},
]

NEED_LABELS = {
    "no-requirement": "No requirement (local/free)",
    "mcp-server": "MCP server",
    "api-key-free": "API key (free tier)",
    "api-key-paid": "API key (paid)",
    "cli-install": "Self-installing CLI",
    "gpu-required": "GPU required",
    "cloud-account": "Cloud account (OAuth/login)",
    "user-cookies": "User's own login cookies",
}

KIND_LABELS = {
    "skill": "skills/",
    "plugin": "plugins.json",
    "template": "templates.json",
    "self-installer": "self-installers.json",
}


def main():
    nodes = {}
    edges = []

    def add_node(node_id, label, ntype, **attrs):
        if node_id not in nodes:
            nodes[node_id] = {"id": node_id, "label": label, "type": ntype, **attrs}
        return node_id

    for e in ENTRIES:
        cat_id = add_node(f"cat:{e['category']}", e["category"], "category")
        entry_id = add_node(f"entry:{e['id']}", e["id"], "entry", kind=e["kind"], kindLabel=KIND_LABELS[e["kind"]])
        src_id = add_node(f"source:{e['source']}", e["source"], "source")

        edges.append({"source": cat_id, "target": entry_id, "relation": "contains", "confidence": "EXTRACTED"})
        edges.append({"source": entry_id, "target": src_id, "relation": "from", "confidence": "EXTRACTED"})
        for need in e["needs"]:
            need_id = add_node(f"need:{need}", NEED_LABELS[need], "requirement")
            edges.append({"source": entry_id, "target": need_id, "relation": "needs", "confidence": "EXTRACTED"})

    graph = {
        "meta": {"source": "Set-Skills collection, hand-classified", "node_count": len(nodes), "edge_count": len(edges)},
        "nodes": list(nodes.values()),
        "edges": edges,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "graph.json"), "w") as f:
        json.dump(graph, f, ensure_ascii=False, indent=1)

    cat_counts = Counter(e["category"] for e in ENTRIES)
    kind_counts = Counter(e["kind"] for e in ENTRIES)
    need_counts = Counter(n for e in ENTRIES for n in e["needs"])
    source_counts = Counter(e["source"] for e in ENTRIES)

    lines = ["# Set-Skills Collection Graph Report\n\n"]
    lines.append(f"{len(ENTRIES)} entries: " + ", ".join(f"{v} {k}" for k, v in kind_counts.most_common()) + ".\n\n")
    lines.append("## By category\n\n| Category | Entries |\n|---|---|\n")
    for cat, count in cat_counts.most_common():
        lines.append(f"| {cat} | {count} |\n")
    lines.append("\n## By requirement\n\n| Requirement | Entries |\n|---|---|\n")
    for need, count in need_counts.most_common():
        lines.append(f"| {NEED_LABELS[need]} | {count} |\n")
    lines.append("\n## By source\n\n| Source | Entries |\n|---|---|\n")
    for src, count in source_counts.most_common():
        lines.append(f"| {src} | {count} |\n")
    lines.append(
        "\n## Suggested questions\n\n"
        "- \"¿Qué tengo instalado que no necesita ninguna cuenta ni API key?\" -> filtrar por `no-requirement`\n"
        "- \"¿Qué toca scraping/investigación web?\" -> categoría `scraping-research`\n"
        "- \"¿Cuántas skills vienen del mismo repo/vendor?\" -> nodos de tipo `source`\n"
        "- Abre `graph.html` y filtra por categoría o requisito para explorar visualmente.\n"
    )
    with open(os.path.join(OUT_DIR, "GRAPH_REPORT.md"), "w") as f:
        f.writelines(lines)

    write_graph_html(graph)
    print(f"Wrote {OUT_DIR}/graph.json, graph.html, GRAPH_REPORT.md ({len(nodes)} nodes, {len(edges)} edges).")


def write_graph_html(graph):
    graph_json = json.dumps(graph, ensure_ascii=False)
    n_entries = len([n for n in graph["nodes"] if n["type"] == "entry"])
    n_cats = len([n for n in graph["nodes"] if n["type"] == "category"])
    html_doc = HTML_TEMPLATE.replace("__GRAPH_JSON__", graph_json)
    html_doc = html_doc.replace("__ENTRY_COUNT__", str(n_entries))
    html_doc = html_doc.replace("__CAT_COUNT__", str(n_cats))
    with open(os.path.join(OUT_DIR, "graph.html"), "w") as f:
        f.write(html_doc)


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Set-Skills Collection Graph</title>
<style>
  :root { color-scheme: light dark; }
  html, body { margin: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0b0e14; color: #e6e6e6; }
  #app { display: flex; height: 100%; }
  #sidebar { width: 340px; flex-shrink: 0; padding: 16px; box-sizing: border-box; overflow-y: auto; background: #11151d; border-right: 1px solid #232a36; }
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
    <h1>Set-Skills Collection Graph</h1>
    <div class="sub">__ENTRY_COUNT__ entradas · __CAT_COUNT__ categorías</div>
    <label for="modeFilter">Vista</label>
    <select id="modeFilter">
      <option value="category">Por categoría</option>
      <option value="need">Por requisito</option>
    </select>
    <label for="valueFilter">Filtro</label>
    <select id="valueFilter"></select>
    <label for="search">Buscar entrada</label>
    <input type="text" id="search" placeholder="ej. azure, scraping, seo...">
    <div id="legend">
      <div class="legend-item"><span class="dot" style="background:#ffb454"></span> Categoría</div>
      <div class="legend-item"><span class="dot" style="background:#6cb6ff"></span> Skill/plugin/template</div>
      <div class="legend-item"><span class="dot" style="background:#7ee787"></span> Fuente (repo/org)</div>
      <div class="legend-item"><span class="dot" style="background:#f97583"></span> Requisito</div>
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
document.getElementById('stats').textContent = `${allNodes.length} nodos · ${allEdges.length} conexiones`;

const modeSelect = document.getElementById('modeFilter');
const valueSelect = document.getElementById('valueFilter');
const detail = document.getElementById('detail');
const svg = d3.select('svg');
const g = svg.append('g');
svg.call(d3.zoom().scaleExtent([0.1, 6]).on('zoom', (ev) => g.attr('transform', ev.transform)));
let simulation;

function color(type) {
  return type === 'category' ? '#ffb454' : type === 'source' ? '#7ee787' : type === 'requirement' ? '#f97583' : '#6cb6ff';
}
function radius(type) { return type === 'entry' ? 6 : 9; }

function populateValueSelect() {
  const type = modeSelect.value === 'category' ? 'category' : 'requirement';
  const opts = allNodes.filter(n => n.type === type).map(n => n.label).sort();
  valueSelect.innerHTML = '<option value="__all__">Todas</option>' + opts.map(o => `<option value="${o}">${o}</option>`).join('');
}

function showDetail(n) {
  if (n.type === 'entry') {
    detail.innerHTML = `<b>${n.label}</b><br>${n.kindLabel || n.kind}`;
  } else {
    detail.innerHTML = `<b>${n.label}</b><br><span class="placeholder">${n.type}</span>`;
  }
}

function render() {
  g.selectAll('*').remove();
  const mode = modeSelect.value;
  const value = valueSelect.value;
  const wantType = mode === 'category' ? 'category' : 'requirement';

  let nodes, edges;
  if (value === '__all__') {
    nodes = allNodes; edges = allEdges;
  } else {
    const pivot = allNodes.find(n => n.type === wantType && n.label === value);
    const entryIds = new Set(allEdges.filter(e => (e.source === pivot.id || e.target === pivot.id)).map(e => e.source === pivot.id ? e.target : e.source));
    const relEdges = allEdges.filter(e => entryIds.has(e.source) || entryIds.has(e.target));
    const otherIds = new Set(relEdges.flatMap(e => [e.source, e.target]));
    otherIds.add(pivot.id);
    nodes = allNodes.filter(n => otherIds.has(n.id));
    edges = relEdges;
  }

  const width = svg.node().clientWidth, height = svg.node().clientHeight;
  const link = g.append('g').selectAll('line').data(edges).join('line').attr('class', 'link');
  const node = g.append('g').selectAll('g').data(nodes).join('g').attr('class', 'node')
    .call(d3.drag()
      .on('start', (ev, d) => { if (!ev.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
      .on('end', (ev, d) => { if (!ev.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));
  node.append('circle').attr('r', d => radius(d.type)).attr('fill', d => color(d.type)).on('click', (ev, d) => showDetail(d));
  node.append('text').attr('dx', d => radius(d.type) + 3).attr('dy', 3).text(d => d.label);
  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(55).strength(0.35))
    .force('charge', d3.forceManyBody().strength(-70))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide(d => radius(d.type) + 4))
    .on('tick', () => {
      link.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
}

modeSelect.addEventListener('change', () => { populateValueSelect(); render(); });
valueSelect.addEventListener('change', render);
document.getElementById('search').addEventListener('input', (ev) => {
  const q = ev.target.value.trim().toLowerCase();
  g.selectAll('.node circle').attr('opacity', d => !q || d.label.toLowerCase().includes(q) ? 1 : 0.15);
});

populateValueSelect();
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
