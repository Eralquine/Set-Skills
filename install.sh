#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
MCP_MANIFEST="$SCRIPT_DIR/mcp-servers.json"
PLUGINS_MANIFEST="$SCRIPT_DIR/plugins.json"
TEMPLATES_MANIFEST="$SCRIPT_DIR/templates.json"
SELF_INSTALLERS_MANIFEST="$SCRIPT_DIR/self-installers.json"

SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
MCP_CONFIG="${CLAUDE_MCP_CONFIG:-$HOME/.claude/.mcp.json}"
PLUGINS_DIR="${CLAUDE_PLUGINS_DIR:-$HOME/.claude-plugins}"

usage() {
  cat <<'EOF'
Uso: install.sh [--project <ruta>] [nombre1 nombre2 ...]
     install.sh new <template> <destino>

Sin argumentos: instala todas las skills sueltas en ~/.claude/skills, clona/
actualiza todos los plugins completos en ~/.claude-plugins, y clona/actualiza
los self-installers (self-installers.json) directo en ~/.claude/skills/<nombre>
(quedan pendientes de que corras tú su propio setup — necesitan dependencias
propias como Bun que no asumimos instaladas).

  --project <ruta>   Instala las skills en <ruta>/.claude/skills en vez de ~/.claude/skills
  nombre1 nombre2 ...   Instala/clona solo esas skills, plugins o self-installers (por nombre)
  new <template> <destino>   Clona un project template (templates.json) fresco en <destino>
                              (no toca ~/.claude/skills ni ~/.claude-plugins — son proyectos
                              completos que se clonan una vez por cada nuevo proyecto)

Variables de entorno:
  CLAUDE_SKILLS_DIR   Sobrescribe el destino de las skills sueltas
  CLAUDE_MCP_CONFIG   Sobrescribe la ruta del .mcp.json a fusionar
  CLAUDE_PLUGINS_DIR  Sobrescribe el destino de los plugins completos
EOF
}

if [[ "${1:-}" == "new" ]]; then
  template="${2:?Uso: install.sh new <template> <destino>}"
  dest="${3:?Uso: install.sh new <template> <destino>}"
  if [[ ! -f "$TEMPLATES_MANIFEST" ]] || ! command -v node >/dev/null 2>&1; then
    echo "No encuentro $TEMPLATES_MANIFEST o falta node." >&2
    exit 1
  fi
  repo=$(node -e '
    const m = require(process.argv[1]);
    if (!m[process.argv[2]]) process.exit(1);
    console.log(m[process.argv[2]].repo);
  ' "$TEMPLATES_MANIFEST" "$template") || { echo "Template '$template' no existe en templates.json." >&2; exit 1; }
  setupCmd=$(node -e '
    const m = require(process.argv[1]);
    console.log(m[process.argv[2]].setupCommand || "");
  ' "$TEMPLATES_MANIFEST" "$template")
  if [[ -e "$dest" ]]; then
    echo "El destino '$dest' ya existe — elige otra carpeta para no pisar nada." >&2
    exit 1
  fi
  echo "↓ Clonando template '$template' en $dest"
  git clone "$repo" "$dest"
  echo ""
  echo "Listo. Siguiente paso:"
  echo "  cd \"$dest\""
  [[ -n "$setupCmd" ]] && echo "  $setupCmd"
  exit 0
fi

SELECTED=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      SKILLS_DIR="$2/.claude/skills"
      MCP_CONFIG="$2/.claude/.mcp.json"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      SELECTED+=("$1")
      shift
      ;;
  esac
done

if [[ ! -d "$SKILLS_SRC" ]]; then
  echo "No encuentro $SKILLS_SRC — corre este script desde el repo clonado." >&2
  exit 1
fi

mkdir -p "$SKILLS_DIR"

INSTALLED=()
for dir in "$SKILLS_SRC"/*/; do
  name="$(basename "$dir")"
  if [[ ${#SELECTED[@]} -gt 0 ]]; then
    match=0
    for s in "${SELECTED[@]}"; do
      [[ "$s" == "$name" ]] && match=1
    done
    [[ $match -eq 0 ]] && continue
  fi
  rm -rf "$SKILLS_DIR/$name"
  cp -r "$dir" "$SKILLS_DIR/$name"
  INSTALLED+=("$name")
  echo "✔ Instalada: $name -> $SKILLS_DIR/$name"
done

if [[ ${#INSTALLED[@]} -eq 0 ]]; then
  echo "(Ninguna skill suelta coincide con lo pedido; revisando plugins completos...)" >&2
fi

if [[ ${#INSTALLED[@]} -gt 0 ]] && [[ -f "$MCP_MANIFEST" ]] && command -v node >/dev/null 2>&1; then
  mkdir -p "$(dirname "$MCP_CONFIG")"
  NAMES_JSON=$(printf '%s\n' "${INSTALLED[@]}" | node -e '
    const names = require("fs").readFileSync(0, "utf8").trim().split("\n").filter(Boolean);
    process.stdout.write(JSON.stringify(names));
  ')
  node - "$MCP_MANIFEST" "$MCP_CONFIG" "$NAMES_JSON" <<'NODE'
    const fs = require("fs");
    const [, , manifestPath, configPath, namesJson] = process.argv;
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    const names = JSON.parse(namesJson);
    let config = { mcpServers: {} };
    if (fs.existsSync(configPath)) {
      try {
        config = JSON.parse(fs.readFileSync(configPath, "utf8"));
      } catch {
        console.error(`Aviso: ${configPath} no es JSON válido, no se toca.`);
        process.exit(0);
      }
    }
    config.mcpServers = config.mcpServers || {};
    let added = [];
    for (const name of names) {
      const servers = manifest[name];
      if (!servers) continue;
      for (const [serverName, serverConfig] of Object.entries(servers)) {
        if (!config.mcpServers[serverName]) {
          config.mcpServers[serverName] = serverConfig;
          added.push(serverName);
        }
      }
    }
    if (added.length > 0) {
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2) + "\n");
      console.log(`✔ MCP servers agregados a ${configPath}: ${added.join(", ")}`);
    }
NODE
elif [[ ${#INSTALLED[@]} -gt 0 ]]; then
  echo "Nota: no se pudo fusionar mcp-servers.json (falta node o el manifest); revisa manualmente si tus skills necesitan un MCP server." >&2
fi

if [[ ${#INSTALLED[@]} -gt 0 ]]; then
  echo ""
  echo "Listo. Skills instaladas: ${INSTALLED[*]}"
  echo "Reinicia Claude Code (o abre una sesión nueva) para que las detecte."
fi

PLUGINS_MATCHED=()
if [[ -f "$PLUGINS_MANIFEST" ]] && command -v node >/dev/null 2>&1; then
  mkdir -p "$PLUGINS_DIR"
  PLUGIN_NAMES=$(node -e '
    const m = require(process.argv[1]);
    console.log(Object.keys(m).join("\n"));
  ' "$PLUGINS_MANIFEST")

  echo ""
  while IFS= read -r pname; do
    [[ -z "$pname" ]] && continue
    if [[ ${#SELECTED[@]} -gt 0 ]]; then
      match=0
      for s in "${SELECTED[@]}"; do
        [[ "$s" == "$pname" ]] && match=1
      done
      [[ $match -eq 0 ]] && continue
    fi

    repo=$(node -e '
      const m = require(process.argv[1]);
      console.log(m[process.argv[2]].repo);
    ' "$PLUGINS_MANIFEST" "$pname")
    entry=$(node -e '
      const m = require(process.argv[1]);
      console.log(m[process.argv[2]].entryCommand || "");
    ' "$PLUGINS_MANIFEST" "$pname")
    dest="$PLUGINS_DIR/$pname"

    if [[ -d "$dest/.git" ]]; then
      echo "↻ Actualizando plugin $pname en $dest"
      git -C "$dest" pull --ff-only
    else
      echo "↓ Clonando plugin $pname en $dest"
      rm -rf "$dest"
      git clone --depth 1 "$repo" "$dest"
    fi

    echo "  Para usarlo: claude --plugin-dir \"$dest\"$( [[ -n "$entry" ]] && echo " (luego $entry)")"
    PLUGINS_MATCHED+=("$pname")
  done <<< "$PLUGIN_NAMES"
fi

SELF_INSTALLERS_MATCHED=()
if [[ -f "$SELF_INSTALLERS_MANIFEST" ]] && command -v node >/dev/null 2>&1; then
  mkdir -p "$SKILLS_DIR"
  SI_NAMES=$(node -e '
    const m = require(process.argv[1]);
    console.log(Object.keys(m).join("\n"));
  ' "$SELF_INSTALLERS_MANIFEST")

  echo ""
  while IFS= read -r siname; do
    [[ -z "$siname" ]] && continue
    if [[ ${#SELECTED[@]} -gt 0 ]]; then
      match=0
      for s in "${SELECTED[@]}"; do
        [[ "$s" == "$siname" ]] && match=1
      done
      [[ $match -eq 0 ]] && continue
    fi

    repo=$(node -e '
      const m = require(process.argv[1]);
      console.log(m[process.argv[2]].repo);
    ' "$SELF_INSTALLERS_MANIFEST" "$siname")
    setupCmd=$(node -e '
      const m = require(process.argv[1]);
      console.log(m[process.argv[2]].setupCommand || "");
    ' "$SELF_INSTALLERS_MANIFEST" "$siname")
    dest="$SKILLS_DIR/$siname"

    if [[ -d "$dest/.git" ]]; then
      echo "↻ Actualizando $siname en $dest"
      git -C "$dest" pull --ff-only
    else
      echo "↓ Clonando $siname en $dest (se instala a sí mismo, no se copia como las demás skills)"
      rm -rf "$dest"
      git clone --depth 1 "$repo" "$dest"
    fi

    echo "  Pendiente (manual, necesita sus propias dependencias): cd \"$dest\" && $setupCmd"
    SELF_INSTALLERS_MATCHED+=("$siname")
  done <<< "$SI_NAMES"
fi

if [[ ${#INSTALLED[@]} -eq 0 ]] && [[ ${#PLUGINS_MATCHED[@]} -eq 0 ]] && [[ ${#SELF_INSTALLERS_MATCHED[@]} -eq 0 ]]; then
  echo "No se instaló ninguna skill, plugin, ni self-installer (¿nombre incorrecto?)." >&2
  exit 1
fi
