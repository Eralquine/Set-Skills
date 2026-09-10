# Set-Skills

Colección personal de skills de Claude Code, juntadas aquí para poder instalarlas
de golpe en cualquier máquina (incluyendo el ROG) con un solo comando.

Este repo **no se usa como skill directamente** — es el punto de reunión. Cada
skill vive en `skills/<nombre>/` con su propio `SKILL.md`, y `install.sh` las
copia a `~/.claude/skills` (o a un proyecto puntual) en la máquina donde lo
corras.

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

## Agregar una nueva skill a esta colección

1. Crea `skills/<nombre>/SKILL.md` (y cualquier `references/` que necesite).
2. Si necesita un MCP server, agrégalo en `mcp-servers.json` bajo la clave
   `<nombre>`.
3. Documéntala en la tabla de arriba.
4. Commit y push — el siguiente `git pull && install.sh` en el ROG la recoge.
