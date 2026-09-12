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
| [`nvidia-nim`](skills/nvidia-nim/SKILL.md) | Endpoints reales de NVIDIA NIM (build.nvidia.com) listos para usar sin re-descubrirlos cada vez: chat/LLM, embeddings, reranking, visión, generación de imágenes, TTS/ASR, biología (BioNeMo) — con specs OpenAPI completas incluidas | API key `nvapi-...` gratis en [build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys) (1000 créditos gratis, 40 req/min) |
| [`omnivoice`](skills/omnivoice/SKILL.md) | TTS zero-shot multilingüe (600+ idiomas): clona una voz desde un audio de referencia de 3-10s, o diséñala por atributos (género, edad, tono, acento, dialecto) | Local — sin API key, pero necesita GPU (o Apple Silicon/Intel Arc) y PyTorch; descarga el modelo de Hugging Face la primera vez |
| [`penpot`](skills/penpot/SKILL.md) | Lee/edita archivos de diseño de Penpot (alternativa open-source a Figma): componentes, tokens, estilos, capas; exporta assets; diseño-a-código | MCP server oficial `@penpot/mcp` — modo remoto necesita cuenta Penpot + MCP key (Your account → Integrations → MCP Server); modo local no necesita nada |
| [`turso`](skills/turso/SKILL.md) | Consulta/modifica un archivo `.db` SQLite local en lenguaje natural (listar tablas, queries, inserts, cambios de schema) | Binario `tursodb` (se instala con un curl), sin auth — se registra por proyecto con `claude mcp add ... -- tursodb <db> --mcp` |
| [`codebase-memory-mcp`](skills/codebase-memory-mcp/SKILL.md) | Indexa un repo (162 lenguajes, tree-sitter) en un grafo de conocimiento persistente y local; consultas de arquitectura/dependencias en vez de re-grepear todo cada sesión | Binario nativo auto-instalable (self-configura Claude Code solo), o vía `npx`/`uvx` sin instalar nada — sin API key, todo local |

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

A diferencia de skills/plugins, esto **no se instala globalmente** — cada
`install.sh new` te da una copia fresca del template lista para un proyecto
nuevo. API keys de proveedores (FAL, ElevenLabs, etc.) se configuran en el
`.env` de esa copia, no en esta colección.

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
