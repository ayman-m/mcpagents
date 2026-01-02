import os
import logging
import asyncio
import json
from google import genai
from google.genai import types
from mcp_client import CortexMCPClient

logger = logging.getLogger(__name__)

def get_tools_schema(tools_list):
    """
    Convert MCP tools list to Gemini function declarations.
    """
    gemini_tools = []
    for tool in tools_list.tools:
        gemini_tools.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        })
    return gemini_tools

async def run_agent_async(text, history=None, status_callback=None):
    """
    Async implementation of the agent logic with optional status callback.
    Callback signature: status_callback(step: str, details: str, status: str = "info")
    """
    if status_callback:
        status_callback("Initialization", "Setting up Vertex AI Client...", "running")
    api_key = os.environ.get("GEMINI_API_KEY")
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Determine model first to decide location
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3-pro-preview")
    location = "us-central1"
    
    # Handle inline credentials if present
    if creds_path and not os.path.exists(creds_path) and creds_path.strip().startswith("{"):
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp:
                temp.write(creds_path)
                creds_path = temp.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
            logger.info("Converted GOOGLE_APPLICATION_CREDENTIALS content to temporary file")
        except Exception as e:
            logger.error(f"Failed to write credentials content to temp file: {e}")
    
    # Logic from user snippet: Route Gemini 3 to global
    if "gemini-3" in model_name.lower() or "experimental" in model_name.lower():
        location = "global"
        logger.info(f"Routing model '{model_name}' to location '{location}'")
        if status_callback:
            status_callback("Config", f"Routing to GLOBAL location for model: {model_name}", "info")

    client = None
    
    # Initialize Client
    if api_key:
        client = genai.Client(api_key=api_key)
    elif creds_path and os.path.exists(creds_path):
        # Vertex AI mode
        try:
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
                project_id = creds_data.get("project_id")
            
            if project_id:
                logger.info(f"Using Vertex AI with project: {project_id} and location: {location}")
                client = genai.Client(vertexai=True, project=project_id, location=location)
            else:
                logger.error("project_id not found in credentials.json")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
    
    if not client:
        return "Error: Neither GEMINI_API_KEY nor valid GOOGLE_APPLICATION_CREDENTIALS found."
    
    
    # 1. Connect to MCP and get tools (Using Context Manager)
    if status_callback:
        status_callback("MCP", "Connecting to MCP Server...", "running")
        
    async with CortexMCPClient() as mcp_client:
        defined_tools = []
        try:
            tools_response = await mcp_client.list_tools()
            
            # Create a tool definition for Gemini
            # fastmcp returns a list of Tool objects directly
            if isinstance(tools_response, list):
                tools_list = tools_response
            else:
                tools_list = tools_response.tools

            # Create a tool definition for Gemini
            gemini_funcs = []
            for t in tools_list:
                # Defensive check for inputSchema vs parameters
                schema = getattr(t, "parameters", getattr(t, "inputSchema", {}))
                
                # Sanitize schema for Gemini compatibility
                # Gemini SDK (Pydantic models) often rejects $defs/definitions and $ref
                # We need to perform simple dereferencing or stripping
                
                def sanitize_schema(s, defs=None, depth=0, processing=None):
                    if not isinstance(s, dict):
                        return s
                    
                    if depth > 10:
                        return {"type": "object", "description": "Complex/Deeply nested object"}
                        
                    processing = processing or set()
                    
                    # Store definitions found at this level
                    current_defs = defs or {}
                    if "$defs" in s:
                        current_defs.update(s.pop("$defs"))
                    if "definitions" in s:
                        current_defs.update(s.pop("definitions"))
                        
                    # Handle $ref
                    if "$ref" in s:
                        ref = s.pop("$ref")
                        ref_name = ref.split("/")[-1]
                        
                        if ref_name in processing:
                            return {"type": "object", "description": f"Recursive reference to {ref_name}"}

                        if ref_name in current_defs:
                            processing.add(ref_name)
                            try:
                                resolved = sanitize_schema(
                                    current_defs[ref_name].copy(), 
                                    current_defs, 
                                    depth + 1,
                                    processing.copy()
                                )
                                s.update(resolved)
                            finally:
                                processing.discard(ref_name)
                        else:
                             s["type"] = "string"
                             s["description"] = f"Reference to {ref_name}"

                    # SIMPLIFICATION FOR GEMINI: oneOf/anyOf/allOf
                    # Gemini often rejects these. We replace them with a generic object type.
                    complex_keys = ["oneOf", "anyOf", "allOf"]
                    found_complex = False
                    for key in complex_keys:
                        if key in s:
                            found_complex = True
                            # Remove the complex key
                            del s[key]
                            
                    if found_complex:
                        # Fallback to loose object
                        s["type"] = "object"
                        s["description"] = s.get("description", "Complex variant type") + " (Validation simplified)"
                        return s

                    # Recursively sanitize properties
                    if "properties" in s:
                        for k, v in s["properties"].items():
                            s["properties"][k] = sanitize_schema(v, current_defs, depth + 1, processing)
                    
                    if "items" in s:
                        # For array items, if it's complex, it will be handled by the recursive call
                        s["items"] = sanitize_schema(s["items"], current_defs, depth + 1, processing)
                            
                    return s

                clean_schema = sanitize_schema(schema.copy())

                gemini_funcs.append(types.FunctionDeclaration(
                    name=t.name,
                    description=t.description,
                    parameters=clean_schema
                ))
                logger.info(f"Registered MCP tool: {t.name}")

            defined_tools = [types.Tool(function_declarations=gemini_funcs)]
            logger.info(f"Loaded {len(gemini_funcs)} tools from MCP total.")
            if status_callback:
                status_callback("MCP", f"Loaded {len(gemini_funcs)} tools", "success")
        except Exception as e:
            logger.warning(f"Could not connect to MCP server: {e}. Proceeding without tools.")
            if status_callback:
                status_callback("MCP", f"Connection Failed: {e}", "error")
            # Proceed without tools
            defined_tools = None

        # Setup the model
        config = types.GenerateContentConfig(
            system_instruction="""You are an advanced Security Analyst Agent in the Troy Security Operations Center (SOC).
Your mission is to protect the Troy network assets from external and internal threats, utilizing a multi-vendor, integrated SOC/NOC architecture.

**The Environment & Topology:**
The architecture is a centralized SOC/NOC stack where **Palo Alto Networks (Cortex XSIAM)** acts as the "Central Brain" for analytics and response.

**1. Palo Alto Networks (Central Operations):**
- **Role**: Primary security analytics, threat prevention, file analysis, and orchestration layer.
- **Capabilities**: Cortex XSIAM (SOC Platform), Strata (Network Security), Advanced Threat Prevention, IoT Security, AIOps.
- **Flow**: Ingests logs from Cisco, Arista, Coerelight; Orchestrates response actions to Arista.

**2. Arista (Network Fabric & Enforcement):**
- **Role**: Provides switching/wireless infrastructure, network visibility, and enforcement.
- **Capabilities**: CV-CUE, CloudVision, AGNI.
- **Flow**: Sends logs to Palo Alto; **Enforces responses** (e.g., Device Quarantine) triggered by Palo Alto; Mirrors traffic (Taps) to Corelight.

**3. Corelight (Network Detection & Response - NDR):**
- **Role**: Deep packet inspection and behavioral analytics.
- **Capabilities**: Zeek, Suricata, Yara, Smart PCAP.
- **Flow**: Receives raw traffic from Arista Taps; Sends enriched NDR telemetry/logs to Palo Alto.

**4. Cisco (Security Cloud & Telemetry):**
- **Role**: Identity, endpoint, cloud, and IoT telemetry provider.
- **Capabilities**: ThousandEyes (Monitoring), Meraki (IoT/Cameras), Duo (Identity), Splunk Attack Analyzer.
- **Flow**: Sends logs and suspicious file submissions to Palo Alto.

**Data Flow Summary:**
- **Logs**: Arista/Cisco/Corelight -> Palo Alto (XSIAM).
- **Response**: Palo Alto -> Arista (Blocking/Quarantine).
- **Taps**: Arista -> Corelight (Inspection).
- **Files**: Cisco -> Palo Alto (Analysis).

**Your Persona & Guidelines:**
- **Team Member**: You are not a robot; you are a valued member of the Troy SOC team. Act like a colleague—be collaborative, encouraging, and clear.
- **Human-Like**: Use natural language. Avoid overly robotic phrasing. It's okay to show personality (e.g., "Good catch!", "Let's dig into this.").
- **Vigilant**: Expect hostile traffic from the Training Rooms (Internal) and Registration Servers (External).
- **Context-Aware**: Understand that an alert from Corelight or Arista isn't isolated—it feeds into XSIAM. Use this context for correlation.
- **Subnet Lookup**: You MUST use the `agentic_subnet_lookup` dataset to identify the physical location/purpose of an IP (e.g., "Which training room is this?").
- **Reporting**: Cite specific tools and flows (e.g., "I'm seeing a correlation in XSIAM matching the Corelight NDR hits...").
"""
        )
        if defined_tools:
            config.tools = defined_tools

        # Prepare history if provided
        full_prompt = text
        if history:
            history_text = "\n".join([f"User {m.get('user', 'Unknown')}: {m.get('text', '')}" for m in history])
            full_prompt = f"Chat History:\n{history_text}\n\nNew Message:\n{text}"

        chat = client.chats.create(
            model=model_name,
            config=config
        )

        if status_callback:
            status_callback("Gemini", "Sending message to model...", "running")
            
        logger.info(f"📝 Sending Prompt to Gemini:\n{full_prompt}")
        response = chat.send_message(full_prompt)
        
        # Handle tool calls
        while response and response.function_calls:
            # Execute tool calls
            parts = []
            for call in response.function_calls:
                logger.info(f"Agent invoking tool: {call.name} with args: {call.args}")
                if status_callback:
                    status_callback("Tool Call", f"Executing **{call.name}**\nArgs: `{call.args}`", "running")

                try:
                    # Call MCP tool
                    result = await mcp_client.call_tool(call.name, call.args)

                    # Convert result content to string if needed for display
                    result_content = result.content
                    logger.info(f"Tool {call.name} returned: {str(result_content)[:500]}")
                    if status_callback:
                        status_callback("Tool Result", f"Result from **{call.name}**:\n```\n{str(result_content)[:500]}...\n```", "success")

                    parts.append(types.Part(
                        function_response=types.FunctionResponse(
                            name=call.name,
                            response={"result": result.content}
                        )
                    ))
                except Exception as e:
                    logger.error(f"Tool {call.name} failed: {e}")
                    if status_callback:
                        status_callback("Tool Error", f"Tool **{call.name}** failed: {str(e)}", "error")
                    parts.append(types.Part(
                        function_response=types.FunctionResponse(
                            name=call.name,
                            response={"error": str(e)}
                        )
                    ))
            
            # Send results back to model
            if status_callback:
                status_callback("Gemini", "Sending tool results back to model...", "running")
            response = chat.send_message(parts)

        return response.text

def process_message(text):
    """
    Synchronous wrapper for async agent.
    """
    return asyncio.run(run_agent_async(text))

def process_thread(text, history):
    """
    Synchronous wrapper for async agent with thread history.
    """
    return asyncio.run(run_agent_async(text, history=history))
