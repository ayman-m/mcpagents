# XSIAM Task Agent (Playbook Command)

Task-oriented wrapper around the shared MCP/Gemini agent. Runs only inside Cortex XSIAM/XSOAR after importing `integration.yml`, exposing playbook commands that call MCP tools via Gemini.

## Deployment
- Import `integration.yml` into XSIAM/XSOAR.
- Configure params, enable the integration, and use the provided commands in playbooks (e.g., run enrichments, XQL lookups).
- Dockerfile included for building a container image if needed for custom runners.

## Required parameters (XSIAM)
- `platform_url`: XSIAM base URL.
- `api_key` / `api_key_id`: XSIAM API credentials.
- `mcp_uri`: MCP streaming endpoint (e.g., `https://10.10.0.6:9010/api/v1/stream/mcp`).
- `mcp_api_key`: Bearer token presented to MCP.
- Gemini/Vertex:
  - `gemini_api_key` **or**
  - `google_creds_json` (service account JSON) with Vertex permissions.
- Optional:
  - `unsecure`: disable SSL verification for platform calls.

## Behavior
- Playbook commands invoke the same agent logic as the Slackbot/Streamlit UI but are triggered from automations/playbooks.
- MCP tool list is auto-discovered; Gemini may call tools and return results to the playbook context/logs.
- TLS to MCP is unverified by default (httpx verify=False); ensure MCP endpoint is trusted.

## References
- Integration spec: `xsiam-task/integration.yml`
- Runtime code: `xsiam-task/integration.py`
