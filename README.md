[![Python](https://img.shields.io/badge/Python-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-ff4b4b?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini / Vertex AI](https://img.shields.io/badge/LLM-Gemini%20%2F%20Vertex%20AI-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview)
[![Cortex XSOAR/XSIAM](https://img.shields.io/badge/Cortex-XSOAR%20%7C%20XSIAM-0071c5)](https://www.paloaltonetworks.com/cortex)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Snyk Security](https://snyk.io/test/github/ayman-m/mcpagents/badge.svg)](https://snyk.io/test/github/ayman-m/mcpagents)
[![Cortex AppSec](https://img.shields.io/badge/CortexAppSec-monitored-32CD32)](https://www.paloaltonetworks.com/cortex/cloud/application-security)

# MCP Agents

Agentic helpers that bridge Gemini/Vertex AI with Cortex MCP tools and XSOAR/XSIAM workflows, plus a Streamlit UI and Slack bot for operators.

## Overview
- Secure analyst chat UI (Streamlit) with Gemini and MCP tool auto-discovery.
- Cortex XSOAR/XSIAM actions via a single prompt or Slack mentions.
- Deployable locally or with Docker Compose; configurable via API keys or Vertex creds.

## Repo layout
- `streamlit/` — Secure analyst chat UI backed by Gemini, auto-discovers MCP tools, and exposes a polished HTTPS Streamlit front end.
- `xsiam-task/` — ESET Agent Demisto/XSIAM integration that sends a single prompt to MCP tools via Gemini/Vertex.
- `xsiam-slackbot/` — Slack bot integration that listens for mentions and can run remote commands or MCP-backed actions through XSOAR/XSIAM.

## Quick start
- Streamlit agent UI: `cd streamlit && pip install -r requirements.txt && streamlit run src/main.py` (set `GEMINI_API_KEY` or Vertex creds plus `MCP_URL`/`MCP_AUTH_TOKEN`; use `docker-compose.yml` for a containerized run).
- XSIAM task integration: import `xsiam-task/integration.yml` into Cortex XSIAM/XSOAR; configure MCP URL/token, Gemini model/API key or Vertex service account, then invoke the `eset-agent-run` command with a prompt.
- Slack bot: import `xsiam-slackbot/integration.yml`, set Slack bot/app tokens and platform API keys, then deploy to let the bot route Slack mentions into XSOAR/XSIAM (with optional MCP tool access).
