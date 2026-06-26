#!/usr/bin/env bash
# =============================================================================
#  Meeting Guardian — setup como Claude Managed Agent
#  Cria: environment -> agent -> deployments (digest + lembretes)
#
#  Pré-requisitos:
#   - CLI `ant` instalada (ver README) e `ANTHROPIC_API_KEY` exportada
#   - URLs reais dos MCP servers preenchidas em agent/agent.json
#   - Vault com as credenciais dos MCP já criado (ver passo 1)
#
#  Todas as chamadas exigem o header beta: managed-agents-2026-04-01
#  (a CLI/SDK adicionam automaticamente; no curl é explícito).
# =============================================================================
set -euo pipefail

: "${ANTHROPIC_API_KEY:?Exporte ANTHROPIC_API_KEY antes de rodar}"
BETA="managed-agents-2026-04-01"
API="https://api.anthropic.com/v1"

# -----------------------------------------------------------------------------
# 1) VAULT — credenciais dos MCP (Calendar OAuth, Slack bot token, e-mail).
#    O formato exato de criação de vault está em:
#    https://platform.claude.com/docs/en/managed-agents/vaults
#    Depois de criar, exporte o ID:
#        export VAULT_ID="vault_..."
: "${VAULT_ID:?Crie um vault com as credenciais dos MCP e exporte VAULT_ID}"

# -----------------------------------------------------------------------------
# 2) ENVIRONMENT — sandbox na nuvem da Anthropic, com rede liberada para os
#    domínios dos MCP/Google/Slack.
echo "==> Criando environment..."
ENVIRONMENT_ID=$(ant beta:environments create \
  --name "meeting-guardian-env" \
  --config '{type: cloud, networking: {type: unrestricted}}' \
  | jq -er '.id')
echo "    environment_id=$ENVIRONMENT_ID"

# -----------------------------------------------------------------------------
# 3) AGENT — model + system prompt + MCP servers + toolsets (de agent/agent.json).
#    OBS.: o mcp_toolset usa por padrão a política de permissão `always_ask`,
#    que EXIGE aprovação humana. Como este agente roda sem humano no loop,
#    configure uma política de auto-aprovação para os MCP. Veja:
#    https://platform.claude.com/docs/en/managed-agents/permission-policies
echo "==> Criando agent..."
AGENT_ID=$(curl -sS --fail-with-body "$API/agents" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: $BETA" \
  -H "content-type: application/json" \
  -d @agent/agent.json | jq -er '.id')
echo "    agent_id=$AGENT_ID"

# -----------------------------------------------------------------------------
# 4) MEMORY STORE — para deduplicar lembretes já enviados.
#    Formato em: https://platform.claude.com/docs/en/managed-agents/memory
: "${MEMORY_STORE_ID:?Crie um memory store e exporte MEMORY_STORE_ID}"

# -----------------------------------------------------------------------------
# 5) DEPLOYMENTS — substitui as variáveis nos YAMLs e cria os dois agendamentos.
export AGENT_ID ENVIRONMENT_ID VAULT_ID MEMORY_STORE_ID

echo "==> Criando deployment do digest diário (06:00)..."
envsubst < deployments/daily-digest.yaml | ant beta:deployments create
echo "==> Criando deployment da varredura de lembretes (a cada 15 min)..."
envsubst < deployments/reminder-sweep.yaml | ant beta:deployments create

echo "✅ Pronto. Acompanhe os runs com:"
echo "   ant beta:deployment-runs list --deployment-id <DEPLOYMENT_ID>"
echo "   ant beta:deployments run     --deployment-id <DEPLOYMENT_ID>   # teste manual"
