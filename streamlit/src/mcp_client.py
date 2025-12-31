import os
import logging
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import httpx

logger = logging.getLogger(__name__)

def unverified_client_factory(**kwargs):
    """Factory to create an unverified httpx client."""
    # Force verify=False
    kwargs["verify"] = False
    return httpx.AsyncClient(**kwargs)

class CortexMCPClient:
    def __init__(self):
        # Use MCP_URL or fallback to default
        # Default: https://mcp-xsiam:9010/api/v1/stream/mcp
        default_url = "https://mcp-xsiam:9010/api/v1/stream/mcp"
        self.base_url = os.environ.get("MCP_URL") or default_url

        logger.info(f"Initializing MCP Client with URI: {self.base_url}")

        if "127.0.0.1" in self.base_url or "localhost" in self.base_url:
            logger.warning("⚠️ Connected to localhost/127.0.0.1. If running in Docker, this refers to the container itself!")
        # Agent-specific token (decoupled from server env var)
        self.api_key = os.environ.get("MCP_TOKEN")
        self.client = None

        # Configure transport with unverified client factory
        transport = StreamableHttpTransport(
            url=self.base_url,
            httpx_client_factory=unverified_client_factory
        )

        # Initialize Client with custom transport and auth
        self.client = Client(transport, auth=self.api_key)

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def list_tools(self):
        return await self.client.list_tools()

    async def call_tool(self, name, arguments):
        return await self.client.call_tool(name, arguments)

    async def list_resources(self):
        return await self.client.list_resources()

    async def list_prompts(self):
        return await self.client.list_prompts()
