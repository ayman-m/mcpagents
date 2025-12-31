# Streamlit Agent UI

Secure Gemini/Vertex AI chat UI that auto-discovers MCP tools, runs over HTTPS, and can pair with any MCP server. This README covers capabilities, env vars, and how to run via local Python, Docker, or Docker Compose.

## Capabilities
- Chat interface backed by Gemini/Vertex AI (Service account).
- Auto-discovers MCP tools and calls them via the MCP streaming endpoint.
- Optional UI auth (basic username/password).
- HTTPS support with provided PEMs or auto-generated self-signed certs.

## Environment variables (quick reference)
- **Agent (Streamlit)**: `MCP_URL` (MCP endpoint), `MCP_TOKEN` (agent bearer token), `GEMINI_API_KEY` or `GOOGLE_APPLICATION_CREDENTIALS` (Vertex SA JSON path/inline), `GEMINI_MODEL` (e.g., `gemini-3-pro-preview`), `UI_USER`/`UI_PASSWORD` (optional), `SSL_CERT_PEM`/`SSL_KEY_PEM` (optional).
- **MCP server (Osiris)**: `CORTEX_MCP_PAPI_URL`, `CORTEX_MCP_PAPI_AUTH_HEADER`, `CORTEX_MCP_PAPI_AUTH_ID`, `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`, `MCP_PATH`, `MCP_AUTH_TOKEN`, `SSL_CERT_PEM`/`SSL_KEY_PEM`, `LOG_FILE_PATH`, `PLAYGROUND_ID`, `SLACK_BOT_TOKEN`.
- See `streamlit/.env.example` for placeholders; copy to `.env` and fill real values.

### Obtaining key values
- **Gemini/Vertex AI**: Use a Gemini API key (`GEMINI_API_KEY`) or a service account JSON with Vertex AI permissions and set `GOOGLE_APPLICATION_CREDENTIALS` to its path (or inline JSON). Pick a model via `GEMINI_MODEL` (defaults to Gemini 3 preview in code).
- **MCP tokens**: `MCP_TOKEN` is what the agent presents; `MCP_AUTH_TOKEN` is what the MCP server expects. Set them to the same value if the agent talks to your bundled server; use a different `MCP_URL`/`MCP_TOKEN` to target another MCP server.
- **Cortex XSIAM PAPI**: Retrieve `CORTEX_MCP_PAPI_URL`, `CORTEX_MCP_PAPI_AUTH_HEADER`, and `CORTEX_MCP_PAPI_AUTH_ID` from your XSIAM tenant API settings.
- **TLS**: Provide PEM content via `SSL_CERT_PEM`/`SSL_KEY_PEM` (single-line with `\n` escapes). If omitted, `start.sh` will generate a self-signed cert for the agent container.

## Run locally (no Docker)
1. `cd streamlit`
2. `pip install -r requirements.txt`
3. Export env vars (or create a `.env` from `.env.example`):
   - Minimum: `GEMINI_API_KEY` **or** `GOOGLE_APPLICATION_CREDENTIALS`, plus `MCP_URL` and `MCP_TOKEN`.
4. Run: `streamlit run src/main.py`
   - Optional: `SSL_CERT_PEM`/`SSL_KEY_PEM` for HTTPS; otherwise Streamlit uses HTTP. (The containerized start script handles HTTPS/self-signed automatically.)

## Build and run with Docker
Build your own image:
```
cd streamlit
docker build -t youruser/eset-streamlit:local .
```

Run with env file (recommended):
```
docker run -p 8501:8501 --env-file .env youruser/eset-streamlit:local
```

Or pass env inline:
```
docker run -p 8501:8501 \
  -e MCP_URL=https://10.10.0.6:9010/api/v1/stream/mcp \
  -e MCP_TOKEN=your_mcp_token \
  -e GEMINI_API_KEY=your_gemini_api_key \
  youruser/eset-streamlit:local
```
`start.sh` will extract PEMs from `SSL_CERT_PEM`/`SSL_KEY_PEM` if provided; otherwise it generates a self-signed cert and serves HTTPS on 8501.

## Full stack with Docker Compose
The compose file (`streamlit/docker-compose.yml`) runs both:
- `mcp-xsiam`: Osiris MCP server (expects `MCP_AUTH_TOKEN`, PAPI creds, transport settings, TLS, etc.).
- `agent-orion`: Streamlit agent (uses `MCP_URL`, `MCP_TOKEN`, Gemini/Vertex, optional UI creds/TLS).

Steps:
1. `cd streamlit`
2. Copy the example env: `cp .env.example .env`
3. Fill in real values for both server and agent sections.
4. `docker compose up -d` (or `docker-compose up -d`).

Adjust `MCP_URL`/`MCP_TOKEN` if the agent should point at a different MCP server than the bundled one.

## Notes
- Logs: MCP server writes to `LOG_FILE_PATH` (volume-backed in compose). Streamlit logs appear in the UI log pane and container stdout.
- Auth: Set `UI_USER`/`UI_PASSWORD` to gate access to the Streamlit UI. Keep MCP tokens secret; use distinct tokens per environment when possible.
