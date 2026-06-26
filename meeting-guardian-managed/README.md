# 🛡️ Meeting Guardian — versão Claude Managed Agent

Esta é a reescrita do Meeting Guardian para rodar **hospedado na Claude
Platform** via **Managed Agents** (beta), em vez de um processo Python num VPS.
A Anthropic cuida do runtime, do sandbox, do agendamento (cron) e da execução
das ferramentas; você só define o agente, conecta os MCP e cria os deployments.

> ⚠️ **Beta + montado a partir da documentação.** Managed Agents está em beta
> público (header `managed-agents-2026-04-01`). Os trechos abaixo seguem o
> formato dos docs oficiais, mas confirme os campos exatos de **vaults**,
> **memory stores** e **permission policies** na documentação antes de subir,
> pois podem mudar entre releases.

---

## O que muda em relação à versão Python

| Versão Python (VPS/Docker) | Versão Managed Agent |
|---|---|
| `scheduler.py` + APScheduler | **Scheduled deployments** (cron na plataforma) |
| `calendar_service.py` | **MCP do Google Calendar** |
| `slack_service.py` / `email_service.py` | **MCP de Slack / e-mail** |
| `ai_summary_service.py` | O **próprio Claude** na sessão |
| `categorizer.py` + análise do dia | **Skill** `meeting-guardian` (regras determinísticas) |
| `guardian.py` (orquestração) | **System prompt** do agente |
| Dockerfile, VPS, systemd | **Infra da Anthropic** (sandbox gerenciado) |

Ou seja: a maior parte do código vira **configuração + prompt + um Skill**.

---

## Arquitetura

```
        Scheduled deployments (cron, na Claude Platform)
        ┌───────────────────────────┬────────────────────────────┐
        │ daily-digest  "0 6 * * *" │ reminder-sweep "*/15 6-23 *"│
        └─────────────┬─────────────┴──────────────┬─────────────┘
                      │ inicia sessão              │ inicia sessão
                      ▼                            ▼
              ┌─────────────────────────────────────────┐
              │            Agent: Meeting Guardian        │
              │  system prompt + Skill(meeting-guardian)  │
              │            sandbox gerenciado             │
              └───────┬─────────────┬─────────────┬───────┘
                      │ MCP         │ MCP         │ MCP
                      ▼             ▼             ▼
              ┌────────────┐ ┌────────────┐ ┌────────────┐
              │  Calendar  │ │   Slack    │ │   E-mail   │
              └────────────┘ └────────────┘ └────────────┘
```

- **Modo digest** (`GERAR_DIGEST_DIARIO`): lê eventos do dia, aplica o Skill, envia o resumo.
- **Modo lembretes** (`VARRER_LEMBRETES`): a cada 15 min checa eventos começando em ~30 min e envia lembrete, usando um **memory store** para não repetir.

---

## Por que a varredura a cada 15 min?

Um deployment agendado dispara em **horário fixo** de cron, não "30 minutos antes
de cada evento". Então, em vez de agendar um job por evento (como o APScheduler
fazia), o agente roda de 15 em 15 minutos e pergunta: *"tem algo começando entre
25 e 35 min a partir de agora que ainda não avisei?"*. O memory store
`reminded_events` guarda os IDs já avisados para evitar duplicatas.

---

## Passo a passo

1. **Instale a CLI `ant`** e exporte a chave:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ant --version
   ```
   (Há também o atalho guiado: rode `/claude-api managed-agents-onboard` no
   Claude Code para um setup interativo.)

2. **Preencha as URLs dos MCP** em `agent/agent.json` (Calendar, Slack, e-mail).
   Precisam ser **remote MCP servers** com endpoint HTTP (transporte streamable
   HTTP). Veja `docs/en/agents-and-tools/remote-mcp-servers`.

3. **Crie um vault** com as credenciais dos MCP (OAuth do Calendar, token do
   Slack, SMTP/Gmail) e exporte `VAULT_ID`. Doc: `docs/en/managed-agents/vaults`.

4. **Crie um memory store** e exporte `MEMORY_STORE_ID`.
   Doc: `docs/en/managed-agents/memory`.

5. **Configure a política de permissão** dos MCP para **auto-aprovar** (sem
   humano no loop o padrão `always_ask` trava a execução).
   Doc: `docs/en/managed-agents/permission-policies`.

6. **Rode o setup**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

7. **Teste sem esperar o cron**:
   ```bash
   ant beta:deployments run --deployment-id <DEPLOYMENT_ID>
   ant beta:deployment-runs list --deployment-id <DEPLOYMENT_ID> --has-error
   ```

---

## Operação

```bash
ant beta:deployments pause   --deployment-id <ID>   # pausa o agendamento
ant beta:deployments unpause --deployment-id <ID>   # retoma
ant beta:deployments archive --deployment-id <ID>   # encerra (terminal)
```

---

## Ressalvas importantes

- **Beta**: comportamento pode mudar; o header `managed-agents-2026-04-01` é obrigatório.
- **Permissões de MCP**: configure auto-aprovação, senão o agente fica esperando aprovação que nunca vem.
- **Custo**: tokens normais da plataforma **+ US$ 0,08 por hora de sessão** de runtime ativo. As sessões aqui são curtas (digest e varreduras), então tendem a custar pouco — mas a varredura roda ~68x/dia, então some isso.
- **Dedup de lembretes** depende do memory store funcionar; teste bem com `deployments run`.
- **DST/fuso**: o cron usa horário de parede local (America/Sao_Paulo). Sem horário de verão no Brasil atualmente, mas vale lembrar.
- **Limite**: até 1.000 deployments agendados por organização.

---

## Quando preferir a versão Python

Para uso pessoal (um usuário só), a versão Python em VPS/Railway/Render costuma
ser **mais simples e barata** — você já tem o código pronto. Os Managed Agents
compensam quando você quer **zero infraestrutura própria** ou pretende oferecer
o Meeting Guardian para **várias pessoas** (ex.: como recurso dentro do ASAS).
