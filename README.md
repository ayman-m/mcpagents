[![Python](https://img.shields.io/badge/Python-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-ff4b4b?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini / Vertex AI](https://img.shields.io/badge/LLM-Gemini%20%2F%20Vertex%20AI-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview)
[![Cortex XSOAR/XSIAM](https://img.shields.io/badge/Cortex-XSOAR%20%7C%20XSIAM-0071c5)](https://www.paloaltonetworks.com/cortex)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Snyk Security](https://snyk.io/test/github/ayman-m/mcpagents/badge.svg)](https://snyk.io/test/github/ayman-m/mcpagents)
[![Cortex AppSec](https://img.shields.io/badge/CortexAppSec-monitored-32CD32)](https://www.paloaltonetworks.com/cortex/cloud/application-security)

# MCP Agents

One agent, three interfaces:
- **Streamlit UI** (standalone HTTPS web app; Docker/Compose ready)
- **Slackbot** (XSIAM-only; import integration and run as a long-running job)
- **Task/Playbook** (XSIAM-only; commands callable from playbooks/automations)

All variants auto-discover MCP tools, call them through Gemini/Vertex AI, and share the same backend logic; only the interface differs.

## Repo layout
- `streamlit/` — Streamlit chat UI. See `streamlit/README.md` (Dockerfile + docker-compose included).
- `xsiam-slackbot/` — Slack bot integration for Cortex XSIAM. See `xsiam-slackbot/README.md`.
- `xsiam-task/` — Playbook/command integration for Cortex XSIAM. See `xsiam-task/README.md`.

## Quick start
- **Streamlit UI**: `cd streamlit && pip install -r requirements.txt && streamlit run src/main.py` (set `GEMINI_API_KEY` or Vertex creds plus `MCP_URL`/`MCP_TOKEN`; use `docker-compose.yml` for a containerized run with the MCP server).
- **XSIAM Task**: import `xsiam-task/integration.yml` into XSIAM/XSOAR; configure MCP URL/token, Gemini model/API key or Vertex service account; call the command from a playbook.
- **Slackbot**: import `xsiam-slackbot/integration.yml`, set Slack bot/app tokens, platform API keys, MCP URL/token, and Gemini/Vertex creds; run as a long-running job in XSIAM.
