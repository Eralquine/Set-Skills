#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
MCP_MANIFEST="$SCRIPT_DIR/mcp-servers.json"

SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
MCP_CONFIG="${CLAUDE_MCP_CONFIG:-$HOME/.claude/.mcp.json}"

usage() {
  cat <<'EOF'
Uso: install.sh [--project <ruta>] [skill1 skill2 ...]

Sin argumentos: instala todas las skills del repo en ~/.claude/skills
(disponibles en cualquier proyecto de esta máquina).

  --project <ruta>   Instala en <ruta>/.claude/skills en vez de ~/.claude/skills
  skill1 skill2 ...   Instala solo esas skills (por nombre de carpeta)

Variables de entorno:
  CLAUDE_SKILLS_DIR   Sobrescribe el destino de las skills
  CLAUDE_MCP_CONFIG   Sobrescribe la ruta del .mcp.json a fusionar
EOF
}

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
  echo "No se instaló ninguna skill (¿nombre incorrecto?)." >&2
  exit 1
fi

if [[ -f "$MCP_MANIFEST" ]] && command -v node >/dev/null 2>&1; then
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
else
  echo "Nota: no se pudo fusionar mcp-servers.json (falta node o el manifest); revisa manualmente si tus skills necesitan un MCP server." >&2
fi

echo ""
echo "Listo. Skills instaladas: ${INSTALLED[*]}"
echo "Reinicia Claude Code (o abre una sesión nueva) para que las detecte."
