#!/usr/bin/env bash
set -euo pipefail

readonly MAPA="MAPA-DO-REPOSITORIO.md"

ir_para_raiz_do_repositorio() {
  cd "$(dirname "$0")/../.."
}

executando_como_hook() {
  [ ! -t 0 ]
}

hook_ja_bloqueou_esta_resposta() {
  printf '%s' "$1" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'
}

listar_markdown_versionavel() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git ls-files --cached --others --exclude-standard -- '*.md'
  else
    find . -name '*.md' -not -path './.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' | sed 's|^\./||'
  fi
}

listar_configuracao_do_claude() {
  if [ -d .claude/hooks ]; then
    find .claude/hooks -type f
  fi
  if [ -f .claude/settings.json ]; then
    echo .claude/settings.json
  fi
}

listar_itens_obrigatorios() {
  { listar_markdown_versionavel; listar_configuracao_do_claude; } | sort -u
}

esta_no_mapa() {
  grep -qF "]($1)" "$MAPA" || grep -qF "]($1#" "$MAPA"
}

listar_itens_fora_do_mapa() {
  listar_itens_obrigatorios | while IFS= read -r caminho; do
    esta_no_mapa "$caminho" || echo "falta no mapa: $caminho"
  done
}

listar_alvos_de_link_do_mapa() {
  grep -oE '\]\([^)]+\)' "$MAPA" \
    | sed -E 's/^\]\(//; s/\)$//; s/#.*$//' \
    | grep -vE '^(https?:|mailto:|$)' \
    | sort -u || true
}

listar_links_quebrados() {
  listar_alvos_de_link_do_mapa | while IFS= read -r alvo; do
    [ -e "$alvo" ] || echo "link para arquivo que não existe: $alvo"
  done
}

listar_pendencias() {
  if [ ! -f "$MAPA" ]; then
    echo "o arquivo $MAPA não existe"
    return
  fi
  listar_itens_fora_do_mapa
  listar_links_quebrados
}

escapar_para_json() {
  printf '%s' "$1" \
    | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' \
    | awk 'NR > 1 { printf "\\n" } { printf "%s", $0 }'
}

pedir_ao_claude_que_atualize_o_mapa() {
  local motivo="O $MAPA está desatualizado. Antes de encerrar, atualize o mapa seguindo a seção \"Como adicionar um item novo\":
$1"
  printf '{"decision":"block","reason":"%s"}\n' "$(escapar_para_json "$motivo")"
}

main() {
  ir_para_raiz_do_repositorio

  if executando_como_hook && hook_ja_bloqueou_esta_resposta "$(cat)"; then
    exit 0
  fi

  local pendencias
  pendencias="$(listar_pendencias)"

  if [ -z "$pendencias" ]; then
    exit 0
  fi

  if executando_como_hook; then
    pedir_ao_claude_que_atualize_o_mapa "$pendencias"
  else
    printf '%s\n' "$pendencias" >&2
    exit 1
  fi
}

main
