# XSIAM Slackbot Agent

Slack-facing wrapper around the shared MCP/Gemini agent. Runs inside Cortex XSIAM only (long-running job) after importing `integration.yml`. Listens for app mentions/DMs, calls MCP tools via Gemini, and replies in-channel.

## Deployment
- In XSIAM/XSOAR, import `integration.yml` as an integration instance.
- Provide params, then run as a long-running job.
- Dockerfile is included for building a container image if needed in a custom runner environment.

## Required parameters (XSIAM)
- `slack_bot_token` / `slack_app_token`: Slack bot/app tokens.
- `platform_url`: XSIAM base URL.
- `api_key` / `api_key_id`: XSIAM API credentials for alert/incident ops.
- `mcp_uri`: MCP streaming endpoint (e.g., `https://10.10.0.6:9010/api/v1/stream/mcp`).
- `mcp_api_key`: Bearer token presented to MCP.
- Gemini/Vertex:
  - `gemini_api_key` **or**
  - `google_creds_json` (service account JSON) with Vertex permissions.
- Optional:
  - `unsecure`: disable SSL verification for platform calls.
  - `debug_start`: extra logging on startup.

## Behavior
- On mention/DM, the agent routes user requests to Gemini; Gemini may call MCP tools; responses are posted back to Slack.
- Uses the same tool-loading logic as the Streamlit and task agents; only the interface differs.
- TLS to MCP is unverified by default (httpx verify=False); ensure MCP endpoint is trusted in your environment.

## References
- Integration spec: `xsiam-slackbot/integration.yml`
- Runtime code: `xsiam-slackbot/integration.py`
