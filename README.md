# Set-Skills

Colección personal de skills de Claude Code, juntadas aquí para poder instalarlas
de golpe en cualquier máquina (incluyendo el ROG) con un solo comando.

Este repo **no se usa como skill directamente** — es el punto de reunión. Cada
skill suelta vive en `skills/<nombre>/` con su propio `SKILL.md`, y `install.sh`
las copia a `~/.claude/skills` (o a un proyecto puntual) en la máquina donde lo
corras. Además soporta **plugins completos** de Claude Code (con agents,
commands y hooks propios) listados en `plugins.json`: para esos, `install.sh`
clona/actualiza el repo del plugin en `~/.claude-plugins/<nombre>` en vez de
copiar archivos sueltos, porque un plugin completo necesita que Claude Code lo
cargue como unidad. También soporta **project templates** listados en
`templates.json`: repos que no se instalan sino que se clonan frescos cada
vez que arrancas un proyecto nuevo de ese tipo (`install.sh new <template>
<destino>`), porque son el proyecto en sí (con su propio venv, node_modules,
config), no algo que se agregue a un proyecto existente. Y una cuarta
categoría, **self-installers** (`self-installers.json`): repos que se
instalan a sí mismos clonándose directo en `~/.claude/skills/<nombre>` y
corriendo su propio script de setup — `install.sh` los clona/actualiza ahí,
pero no corre el setup por ti (pueden necesitar dependencias como Bun que no
asumimos instaladas).

## Instalar todas las skills (uso normal en el ROG)

```sh
git clone https://github.com/Eralquine/set-skills.git ~/set-skills-src \
  && bash ~/set-skills-src/install.sh
```

Esto copia cada carpeta de `skills/` a `~/.claude/skills/`, quedando
disponibles en cualquier proyecto que abras en esa máquina, y fusiona los MCP
servers que esas skills requieran (ver `mcp-servers.json`) en tu
`~/.claude/.mcp.json` sin pisar lo que ya tengas configurado.

Si ya tienes el repo clonado y solo quieres actualizar:

```sh
cd ~/set-skills-src && git pull && bash install.sh
```

### Instalar solo una skill

```sh
bash install.sh plasmic-designer
```

### Instalar en un proyecto en vez de globalmente

```sh
bash install.sh --project /ruta/a/mi-proyecto
```

## Skills incluidas

| Skill | Qué hace | Requiere |
|---|---|---|
| [`plasmic-designer`](skills/plasmic-designer/SKILL.md) | Controla Plasmic Studio (editor visual) vía Chrome DevTools MCP para crear/editar componentes, páginas y layouts | MCP server `chrome-devtools` (se agrega solo al instalar), sesión iniciada en Plasmic Studio la primera vez |
| [`competitive-landscape`](skills/competitive-landscape/SKILL.md) | Mapea líderes del mercado SEO, temas de contenido ganadores, cobertura de keywords, backlinks y brechas estratégicas | Cuenta de OpenSEO ([openseo.so](https://openseo.so)) |
| [`competitor-analysis`](skills/competitor-analysis/SKILL.md) | Analiza el tráfico orgánico, keywords, contenido y backlinks de un competidor puntual | Cuenta de OpenSEO |
| [`keyword-clustering`](skills/keyword-clustering/SKILL.md) | Agrupa keywords por intención y las mapea a páginas existentes o propuestas | Cuenta de OpenSEO |
| [`keyword-research`](skills/keyword-research/SKILL.md) | Descubre oportunidades de keywords, evalúa métricas/SERPs y guarda/etiqueta términos | Cuenta de OpenSEO |
| [`link-prospecting`](skills/link-prospecting/SKILL.md) | Encuentra prospectos de link building, vías de contacto y redacta outreach | Cuenta de OpenSEO |
| [`local-seo`](skills/local-seo/SKILL.md) | Audita un Google Business Profile y compara visibilidad en Maps contra competidores locales | Cuenta de OpenSEO |
| [`seo-audit`](skills/seo-audit/SKILL.md) | Audita un sitio y entrega un reporte de una página con una sola acción prioritaria de la semana | Cuenta de OpenSEO |
| [`seo-coach`](skills/seo-coach/SKILL.md) | Modo coach de OpenSEO: explica workflows y recomienda siguientes pasos | Cuenta de OpenSEO |
| [`seo-project-setup`](skills/seo-project-setup/SKILL.md) | Llena el contexto compartido del proyecto (sitio, metas, competidores, páginas clave) y valida el MCP/Search Console | Cuenta de OpenSEO |
| [`api-finder`](skills/api-finder/SKILL.md) | Sugiere APIs públicas/gratis reales para lo que necesites (clima, animales, finanzas, geocoding, etc.) en vez de inventar endpoints | Ninguno — datos curados de [public-apis/public-apis](https://github.com/public-apis/public-apis) |
| [`graphify`](skills/graphify/SKILL.md) | Convierte cualquier carpeta (código, docs, PDFs, imágenes, video) en un grafo de conocimiento navegable: `graphify query "..."`, `graphify path A B`, `graphify explain "X"` | Se instala solo la primera vez (`uv tool install graphifyy` o `pip install graphifyy`); el análisis de código es local, pero el análisis semántico de docs/imágenes necesita una API key de LLM (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.) |
| [`nvidia-nim`](skills/nvidia-nim/SKILL.md) | Endpoints reales de NVIDIA NIM (build.nvidia.com) listos para usar sin re-descubrirlos cada vez: chat/LLM, embeddings, reranking, visión, generación de imágenes, TTS/ASR, biología (BioNeMo) — con specs OpenAPI completas incluidas y un grafo del catálogo de modelos (`references/graph/`, regenerable con `scripts/build_model_graph.py`) | API key `nvapi-...` gratis en [build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys) (1000 créditos gratis, 40 req/min) |
| [`omnivoice`](skills/omnivoice/SKILL.md) | TTS zero-shot multilingüe (600+ idiomas): clona una voz desde un audio de referencia de 3-10s, o diséñala por atributos (género, edad, tono, acento, dialecto) | Local — sin API key, pero necesita GPU (o Apple Silicon/Intel Arc) y PyTorch; descarga el modelo de Hugging Face la primera vez |
| [`penpot`](skills/penpot/SKILL.md) | Lee/edita archivos de diseño de Penpot (alternativa open-source a Figma): componentes, tokens, estilos, capas; exporta assets; diseño-a-código | MCP server oficial `@penpot/mcp` — modo remoto necesita cuenta Penpot + MCP key (Your account → Integrations → MCP Server); modo local no necesita nada |
| [`turso`](skills/turso/SKILL.md) | Consulta/modifica un archivo `.db` SQLite local en lenguaje natural (listar tablas, queries, inserts, cambios de schema) | Binario `tursodb` (se instala con un curl), sin auth — se registra por proyecto con `claude mcp add ... -- tursodb <db> --mcp` |
| [`codebase-memory-mcp`](skills/codebase-memory-mcp/SKILL.md) | Indexa un repo (162 lenguajes, tree-sitter) en un grafo de conocimiento persistente y local; consultas de arquitectura/dependencias en vez de re-grepear todo cada sesión | Binario nativo auto-instalable (self-configura Claude Code solo), o vía `npx`/`uvx` sin instalar nada — sin API key, todo local |
| [`scrapling-official`](skills/scrapling-official/SKILL.md) | Skill oficial (del autor) de Scrapling: scraping con bypass de anti-bot (Cloudflare Turnstile), browser stealth, framework de spiders con pause/resume, parser adaptativo que se auto-repara cuando el sitio cambia | `pip install "scrapling[all]"` + `scrapling install --force` (descarga browsers) — sin API key, todo local |
| [`agent-reach`](skills/agent-reach/SKILL.md) | Router de 15 plataformas de internet para investigación (YouTube, Twitter/X, Reddit, Bilibili, XiaoHongShu, GitHub, LinkedIn, RSS, etc.) con múltiples backends por plataforma y auto-detección de cuál está disponible | `pipx install` desde GitHub; 6 canales sin config, el resto necesita cookies/tokens **del propio usuario** (nunca hace login automático ni lee cookies del browser sin permiso) |
| [`scrapegraph-mcp`](skills/scrapegraph-mcp/SKILL.md) | Extrae datos de páginas web describiendo en lenguaje natural qué quieres (sin CSS selectors), con crawl multi-página async, generación de JSON Schema, y monitors programados que avisan cuando una página cambia | API key de pago en [dashboard.scrapegraphai.com](https://dashboard.scrapegraphai.com) — servicio hosteado, no local |
| [`best-skills-finder`](skills/best-skills-finder/SKILL.md) | Antes de armar una skill desde cero: busca si ya existe una buena en skills.sh/ClawHub/Tencent SkillHub (10,000+ skills, ranking actualizado a diario) — evita reinventar la rueda | Ninguno — datos abiertos (CSV) que se descargan en vivo de [LinklyAI/best-skills](https://github.com/LinklyAI/best-skills), nunca vendorizados (cambian a diario) |

**Top 10 del ranking `best-skills-finder`** (instaladas el 2026-09-12, vía sus repos oficiales):

| Skill | Qué hace | Fuente |
|---|---|---|
| [`find-skills`](skills/find-skills/SKILL.md) | Busca/instala skills desde la CLI oficial `npx skills` (skills.sh) | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| [`agent-browser`](skills/agent-browser/SKILL.md) | Automatización de browser vía CDP para agentes (Chrome/Chromium, apps Electron, Slack, Vercel Sandbox) — CLI Rust nativa, sin Playwright/Puppeteer | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) (`npm i -g agent-browser && agent-browser install`) |
| [`frontend-design`](skills/frontend-design/SKILL.md) | Guía de diseño visual intencional para UI nueva o rediseño — evita el look "default de IA" | [anthropics/skills](https://github.com/anthropics/skills) |
| [`grill-me`](skills/grill-me/SKILL.md) | Interrogatorio implacable para afilar un plan o diseño antes de implementarlo | [mattpocock/skills](https://github.com/mattpocock/skills) |
| [`azure-ai`](skills/azure-ai/SKILL.md) | Azure AI Search, Speech, OpenAI, Document Intelligence — búsqueda vectorial/híbrida, STT/TTS, OCR | [microsoft/azure-skills](https://github.com/microsoft/azure-skills) (necesita `az` CLI autenticado) |
| [`vercel-react-best-practices`](skills/vercel-react-best-practices/SKILL.md) | ~70 reglas de performance de React/Next.js de Vercel Engineering (rendering, bundling, async, server) | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) |
| [`web-design-guidelines`](skills/web-design-guidelines/SKILL.md) | Audita código de UI contra guías de accesibilidad/UX | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) |
| [`grill-with-docs`](skills/grill-with-docs/SKILL.md) | Como `grill-me`, pero además genera ADRs y glosario mientras interroga el plan | [mattpocock/skills](https://github.com/mattpocock/skills) |
| [`azure-compliance`](skills/azure-compliance/SKILL.md) | Auditorías de compliance/seguridad Azure con `azqr` + chequeo de expiración de Key Vault | [microsoft/azure-skills](https://github.com/microsoft/azure-skills) (necesita `az` CLI + `azqr`) |
| [`azure-storage`](skills/azure-storage/SKILL.md) | Blob/File/Queue/Table Storage y Data Lake — tiers de acceso, lifecycle management | [microsoft/azure-skills](https://github.com/microsoft/azure-skills) (necesita `az` CLI autenticado) |

Copiadas solo estas 10 (no los repos completos, que traen 30-80 skills más cada uno) — el ranking cambia a diario, así que si vuelves a correr `best-skills-finder` más adelante el top 10 puede ser distinto.

Las 9 skills de OpenSEO comparten el mismo MCP server hosteado (`openseo`,
`https://app.openseo.so/mcp`), agregado automáticamente por `install.sh`. La
primera vez que Claude use una herramienta de OpenSEO te va a pedir
autenticarte por OAuth con tu cuenta de [openseo.so](https://openseo.so). El
paquete de skills es gratis y open source, pero el uso del servidor hosteado
requiere cuenta y créditos (ver [openseo.so/pricing](https://openseo.so/pricing));
también se puede self-hostear (ver el [repo original](https://github.com/every-app/open-seo#self-hosting)).

### Demo: el catálogo de `api-finder` como grafo

Para probar `graphify` de una vez, convertimos las 1773 APIs de `api-finder`
en un grafo navegable — categoría → API → tipo de auth — en
`skills/api-finder/references/graph/`:

- `graph.html` — visor interactivo (D3, self-contained, ábrelo en cualquier navegador): filtra por categoría, busca por nombre, click en un nodo para ver URL/descripción/auth.
- `graph.json` — el grafo completo (1829 nodos, 3546 conexiones) para consultarlo por código.
- `GRAPH_REPORT.md` — resumen: categorías con más APIs, desglose por tipo de auth.

**Nota honesta:** el pipeline normal de `graphify` sobre un `.md` usa un LLM
para la pasada semántica (necesita `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.,
que no había disponible en esta sesión). Como los datos de `api-finder` ya
venían estructurados (categoría, auth, URL — nada que inferir), en vez de eso
construí el grafo directo desde `apis.json` con el mismo esquema de nodos/edges
que usa `graphify` (`EXTRACTED` en cada conexión, sin nada inferido). Si en tu
ROG tienes una API key de LLM configurada, puedes correr el pipeline real de
`graphify` sobre carpetas de docs/PDFs/imágenes y sí te va a hacer inferencia
semántica de verdad.

### Demo 2: el catálogo de modelos de `nvidia-nim` como grafo

Mismo patrón, aplicado a `nvidia-nim` en `skills/nvidia-nim/references/graph/`
— categoría → modelo → proveedor, generado por
`skills/nvidia-nim/scripts/build_model_graph.py`.

**Nota honesta (otra vez):** `build.nvidia.com`, `integrate.api.nvidia.com`
y `api.ngc.nvidia.com` están bloqueados por la política de egress de esta
sesión, así que no pude descargar el catálogo completo en vivo (100+
modelos). El grafo que subí es un **seed parcial de ~32 modelos** verificados
contra las specs OpenAPI reales de NVIDIA — no el catálogo completo. El
script hace ambas cosas: sin `NVIDIA_API_KEY` genera este seed; con la key
(y en una red que sí llegue a `integrate.api.nvidia.com`, como tu ROG) llama
`GET /v1/models` y genera el grafo real y completo. Corre
`NVIDIA_API_KEY=nvapi-... python3 scripts/build_model_graph.py` ahí para
reemplazar el seed por el catálogo de verdad.

## Plugins completos incluidos

| Plugin | Qué hace | Cómo se usa |
|---|---|---|
| [`pagokit`](https://github.com/hainrixz/agente-pagokit) | Agente que elige el proveedor de pagos correcto para tu proyecto y genera la integración completa (checkout, webhook autenticado, migración de DB, portal de cliente, reembolsos) con hooks que **bloquean** escrituras inseguras (secrets en texto plano, montos mal calculados, webhooks sin verificar) | `install.sh` lo clona en `~/.claude-plugins/pagokit`; para usarlo corre `claude --plugin-dir ~/.claude-plugins/pagokit` y luego `/pagokit:start` |
| [`firecrawl`](https://github.com/firecrawl/skills) | Catálogo oficial de Firecrawl (scraping/crawling/búsqueda web a markdown listo para LLM): ~17 skills — primitivas (`scrape`/`search`/`crawl`/`map`/`interact`/`agent`/`monitor`/`parse`/`download`) y guías de integración de API — más su MCP server propio | `install.sh` lo clona en `~/.claude-plugins/firecrawl`; corre `claude --plugin-dir ~/.claude-plugins/firecrawl`. Necesita `FIRECRAWL_API_KEY` (`fc-...` en [firecrawl.dev](https://firecrawl.dev)) para todo excepto scrape/search/parse básicos |
| [`cybersecurity-skills`](https://github.com/mukul975/anthropic-cybersecurity-skills) | 818 skills de seguridad en 34 dominios (DFIR, threat intel, cloud/container/OT security, red teaming, AI security), mapeadas a MITRE ATT&CK/ATLAS/D3FEND y NIST CSF/AI RMF. **No afiliado a Anthropic** pese al nombre — proyecto comunitario independiente, el propio README lo aclara | `install.sh` lo clona en `~/.claude-plugins/cybersecurity-skills`; corre `claude --plugin-dir ~/.claude-plugins/cybersecurity-skills`. Sin API key para la mayoría; algunas skills de amenaza/OSINT usan claves de terceros (VirusTotal, Shodan, etc.) que documentan en su propio SKILL.md |

`install.sh` clona cada plugin la primera vez y hace `git pull` en las
siguientes corridas, así que `git pull && bash install.sh` en el ROG también
actualiza los plugins.

## Project templates incluidos

| Template | Qué es | Cómo se usa |
|---|---|---|
| [`openmontage`](https://github.com/calesthio/OpenMontage) | Sistema de producción de video agéntico: describís el video en lenguaje natural y el agente investiga, escribe el guion, genera imágenes/video/música/narración, edita y renderiza (Remotion). 50+ skills propias (video gen con Veo/Kling/Seedance, TTS, música, ffmpeg, Three.js, etc.) | `bash install.sh new openmontage ~/proyectos/mi-video`, luego `cd` ahí y `make setup` (necesita Python 3.10+, FFmpeg, Node 18+) |
| [`daily-stock-analysis`](https://github.com/ZhuLinsen/daily_stock_analysis) | Analiza acciones diariamente (A-share/HK/US/JP/KR/TW) con IA: cotizaciones+noticias+fundamentales → dashboard de decisión (compra/venta, riesgos) → push a WeChat Work/Feishu/Telegram/Discord/email. CLI + API REST + web + desktop | `bash install.sh new daily-stock-analysis ~/proyectos/stocks`, `pip install -r requirements.txt`, configura `.env` (mínimo 1 API key de LLM + `STOCK_LIST`), `python main.py --schedule` o Docker/GitHub Actions para correrlo diario |
| [`omniroute`](https://github.com/diegosouzapw/OmniRoute) | Gateway de IA self-hosted: un endpoint OpenAI-compatible que rutea entre 356 proveedores (150+ tiers gratis, ~1.47B tokens/mes agregados), fallback automático, compresión de contexto, y MCP/A2A/REST/webhooks propios para que un agente controle el gateway mismo | `bash install.sh new omniroute ~/proyectos/mi-gateway`, luego `docker run -d -p 127.0.0.1:20128:20128 ... diegosouzapw/omniroute:latest` (o `npm install -g omniroute && omniroute setup`); apunta Claude Code al endpoint local o agrégalo como MCP server (`claude mcp add-server omniroute --type http --url http://localhost:20128/api/mcp/stream`) |

A diferencia de skills/plugins, esto **no se instala globalmente** — cada
`install.sh new` te da una copia fresca del template lista para un proyecto
nuevo. API keys de proveedores (FAL, ElevenLabs, etc.) se configuran en el
`.env` de esa copia, no en esta colección.

**Nota sobre `omniroute`:** el proyecto es transparente sobre el riesgo —
su propio README cataloga 13 de los 356 proveedores como "avoid" en su
"terms-risk catalog" porque agregar/redistribuir sus tiers gratis puede
violar los términos de esos proveedores específicos. La herramienta te deja
decidir cuáles usar (el dashboard lo muestra), pero la responsabilidad de
respetar los términos de cada proveedor es tuya, no de la herramienta.

## Self-installers incluidos

| Self-installer | Qué es | Cómo se usa |
|---|---|---|
| [`gstack`](https://github.com/garrytan/gstack) | 23 skills + 8 power tools de Garry Tan (YC) que arman un "equipo de ingeniería virtual" en Claude Code: `/office-hours`, `/plan-ceo-review`, `/review`, `/qa` (con browser real), `/cso` (auditoría OWASP+STRIDE), `/ship`, etc. | `install.sh` lo clona en `~/.claude/skills/gstack`; después corres tú `cd ~/.claude/skills/gstack && ./setup` (necesita Bun v1.0+, compila su propio binario de browser) |

A diferencia de las skills sueltas (que copiamos como contenido estático),
estos repos se clonan completos porque su propio script de instalación
necesita compilar binarios o generar configuración — `install.sh` los deja
clonados y actualizados, pero el `./setup` (o equivalente) lo corres tú,
porque puede necesitar dependencias que no asumimos instaladas.

## Qué se evaluó y se dejó fuera (y por qué)

Para que quede explícito por qué algunos repos que se pidieron agregar no
están arriba:

- **[bytedance/deer-flow](https://github.com/bytedance/deer-flow)** — es una
  aplicación completa auto-hosteada (backend LangGraph + frontend Next.js +
  DB propia + Docker Compose), no algo que se invoque desde dentro de Claude
  Code. Su única pieza agent-facing (`claude-to-deerflow`) es un shim HTTP
  que solo sirve si ya tienes la plataforma completa corriendo aparte —no
  vale la pena para esta colección.
- **[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl)** (el repo
  principal) — es el producto/API en sí, no algo que se copie a
  `~/.claude/skills`. Lo que sí vale la pena está en `firecrawl/skills`
  (arriba, como plugin).
`mukul975/anthropic-cybersecurity-skills` (818 skills) sí se agregó — ver la
tabla de plugins arriba. Confirmaste que quieres el catálogo completo,
incluyendo las skills dual-use de red-team/pentesting; cada una de esas trae
su propio aviso de "solo con autorización por escrito" en el `SKILL.md`, pero
eso no impone nada en tiempo de ejecución — la responsabilidad de solo
usarlas en engagements autorizados es tuya al invocarlas.

## Agregar una nueva skill, plugin, template o self-installer a esta colección

**Skill suelta** (solo un `SKILL.md` autocontenido):

1. Crea `skills/<nombre>/SKILL.md` (y cualquier `references/` que necesite).
2. Si necesita un MCP server, agrégalo en `mcp-servers.json` bajo la clave
   `<nombre>`.
3. Documéntala en la tabla de skills.

**Plugin completo** (trae agents/commands/hooks propios):

1. Agrégalo a `plugins.json`: `{"repo": "...", "description": "...", "entryCommand": "/algo"}`.
2. Documéntalo en la tabla de plugins.

**Project template** (un repo que se clona fresco por proyecto, no se instala):

1. Agrégalo a `templates.json`: `{"repo": "...", "description": "...", "setupCommand": "..."}`.
2. Documéntalo en la tabla de templates.

**Self-installer** (se clona directo en `~/.claude/skills/<nombre>` y corre su propio setup):

1. Agrégalo a `self-installers.json`: `{"repo": "...", "description": "...", "setupCommand": "..."}`.
2. Documéntalo en la tabla de self-installers.

Luego commit y push — el siguiente `git pull && install.sh` en el ROG lo recoge.
