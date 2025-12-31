import streamlit as st
import asyncio
import logging
import io
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from agent import run_agent_async
from PIL import Image

# Configure Logging to capture in UI
class StreamlitLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_buffer = io.StringIO()

    def emit(self, record):
        msg = self.format(record)
        self.log_buffer.write(msg + "\n")

    def get_logs(self):
        return self.log_buffer.getvalue()

# Get the icon path
icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.png")
if os.path.exists(icon_path):
    try:
        page_icon = Image.open(icon_path)
    except:
        page_icon = "🛡️"
else:
    page_icon = "🛡️"

st.set_page_config(
    page_title="ESET Agent - Cortex XSIAM",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=page_icon
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }

    /* Header styling */
    .stTitle {
        color: #00d4ff !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        margin-bottom: 0.5rem !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #e4e4e4;
    }

    /* Sidebar headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00d4ff !important;
        font-weight: 600 !important;
    }

    /* Chat messages */
    .stChatMessage {
        background: rgba(15, 15, 30, 0.8) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        backdrop-filter: blur(10px);
    }

    /* User message */
    [data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }

    /* Force white text in chat messages */
    .stChatMessage p,
    .stChatMessage span,
    .stChatMessage div,
    .stChatMessage li {
        color: #ffffff !important;
    }

    /* Input box styling */
    .stChatInputContainer {
        border-radius: 25px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        backdrop-filter: blur(10px);
    }

    .stChatInput input {
        background: transparent !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0090ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5) !important;
    }

    /* Text input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #000000 !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3) !important;
        background: rgba(255, 255, 255, 0.95) !important;
    }

    /* Status indicators */
    .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        color: #00ff88 !important;
        border-left: 4px solid #00ff88 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    .stError {
        background: rgba(255, 68, 68, 0.1) !important;
        color: #ff4444 !important;
        border-left: 4px solid #ff4444 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    .stWarning {
        background: rgba(255, 200, 0, 0.1) !important;
        color: #ffc800 !important;
        border-left: 4px solid #ffc800 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(0, 212, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #00d4ff !important;
        font-weight: 600 !important;
    }

    .streamlit-expanderHeader p,
    .streamlit-expanderHeader span {
        color: #00d4ff !important;
    }

    /* Expander content */
    .streamlit-expanderContent {
        background: rgba(15, 15, 30, 0.5) !important;
        color: #ffffff !important;
    }

    .streamlit-expanderContent p,
    .streamlit-expanderContent span,
    .streamlit-expanderContent div {
        color: #e4e4e4 !important;
    }

    /* Code blocks */
    .stCodeBlock {
        background: rgba(0, 0, 0, 0.5) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
    }

    .stCodeBlock code {
        color: #e4e4e4 !important;
    }

    /* Info/Alert boxes */
    .stAlert {
        background: rgba(15, 15, 30, 0.8) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    .stAlert p,
    .stAlert span,
    .stAlert div {
        color: #ffffff !important;
    }

    /* Info box specific */
    [data-testid="stNotification"] {
        background: rgba(0, 212, 255, 0.1) !important;
        color: #00d4ff !important;
    }

    /* Divider */
    hr {
        border-color: rgba(0, 212, 255, 0.2) !important;
        margin: 2rem 0 !important;
    }

    /* Markdown text */
    .stMarkdown {
        color: #e4e4e4 !important;
    }

    /* =========================
       STATUS WIDGET STYLING
       ========================= */

    /* Base container */
    [data-testid="stStatusWidget"] {
        border-radius: 15px !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        backdrop-filter: blur(10px);
    }

    /* COLLAPSED STATE - Gray background, white text */
    [data-testid="stStatusWidget"]:not([open]) summary {
        background: rgba(128, 128, 128, 0.3) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
    }

    /* COLLAPSED HOVER - Keep gray background, white text */
    [data-testid="stStatusWidget"]:not([open]):hover summary {
        background: rgba(128, 128, 128, 0.3) !important;
        color: #ffffff !important;
    }

    /* EXPANDED STATE (NOT HOVERING) - White background, black text */
    [data-testid="stStatusWidget"][open]:not(:hover) summary {
        background: #ffffff !important;
        color: #000000 !important;
    }

    /* EXPANDED HOVER - Gray background, white text */
    [data-testid="stStatusWidget"][open]:hover summary {
        background: rgba(128, 128, 128, 0.3) !important;
        color: #ffffff !important;
    }

    /* Status content - white text */
    [data-testid="stStatusWidget"] div {
        color: #ffffff !important;
        background: transparent !important;
    }

    /* Icon - always cyan */
    [data-testid="stStatusWidget"] svg {
        color: #00d4ff !important;
        fill: #00d4ff !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d4ff 0%, #0090ff 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #00e4ff 0%, #00a0ff 100%);
    }
</style>
""", unsafe_allow_html=True)

# Helper function for base64 encoding images
def get_image_base64(image_path):
    import base64
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Authentication ---
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        user = st.session_state["username"]
        password = st.session_state["password"]
        
        correct_user = os.environ.get("UI_USER", "admin")
        correct_password = os.environ.get("UI_PASSWORD", "admin")

        if user == correct_user and password == correct_password:
            st.session_state["authenticated"] = True
            # Clear input buffers
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["authenticated"] = False

    if st.session_state.get("authenticated", False):
        return True

    # Login page styling with icon
    login_html = '<div style="text-align: center; margin-top: 2rem;">'

    # Add icon if available
    if os.path.exists(icon_path):
        login_html += f'<img src="data:image/png;base64,{get_image_base64(icon_path)}" style="width: 100px; height: 100px; margin-bottom: 1rem; border-radius: 50%; border: 3px solid #00d4ff; box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);">'
    else:
        login_html += '<div style="font-size: 5rem; margin-bottom: 1rem;">🛡️</div>'

    login_html += '''
        <h1 style="color: #00d4ff; font-size: 3rem; margin-bottom: 2rem; text-shadow: 0 0 30px rgba(0, 212, 255, 0.4);">
            ESET Security Agent
        </h1>
    </div>
    '''

    st.markdown(login_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h3 style="color: #000000;">🔐 Authentication</h3>', unsafe_allow_html=True)
        st.text_input("👤 Username", key="username", placeholder="Enter your username")
        st.text_input("🔑 Password", type="password", key="password", placeholder="Enter your password")
        st.button("🚀 Login", on_click=password_entered, use_container_width=True)

        if "authenticated" in st.session_state and not st.session_state["authenticated"]:
            st.error("😕 Invalid credentials. Please try again.")

    return False

if not check_password():
    st.stop()
# ----------------------

# Setup Logger
if "log_handler" not in st.session_state:
    log_handler = StreamlitLogHandler()
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    
    # Attach to root logger or agent logger
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    st.session_state["log_handler"] = log_handler
else:
    log_handler = st.session_state["log_handler"]

# Sidebar status
with st.sidebar:
    st.markdown("### 🔧 Configuration")

    # Allow overriding MCP URI with white label
    default_uri = os.environ.get("MCP_URL") or "https://127.0.0.1:9010/api/v1/stream/mcp"
    st.markdown('<p style="color: white; font-size: 0.875rem; margin-bottom: 0.25rem;">MCP Server URI</p>', unsafe_allow_html=True)
    mcp_uri = st.text_input("MCP Server URI", value=default_uri, help="Configure the MCP server endpoint", label_visibility="collapsed")
    if mcp_uri:
        os.environ["MCP_URL"] = mcp_uri

    st.markdown("---")

    # System Status Section
    st.markdown("### 📊 System Status")

    # Status indicators with custom styling
    col1, col2 = st.columns([1, 4])
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GEMINI_API_KEY"):
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**Gemini AI**")
    else:
        with col1:
            st.markdown("🔴")
        with col2:
            st.markdown("**Gemini AI**")

    col1, col2 = st.columns([1, 4])
    if mcp_uri:
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**MCP Server**")
    else:
        with col1:
            st.markdown("🟡")
        with col2:
            st.markdown("**MCP Server**")

    st.markdown("---")

    # Actions Section
    st.markdown("### 🎯 Actions")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
if len(st.session_state.messages) == 0:
    # Welcome message for new sessions with icon
    welcome_html = '<div style="text-align: center; padding: 0.5rem 1rem; margin: 0.25rem 0;">'
    welcome_html += '<div style="background: rgba(0, 212, 255, 0.05); border-radius: 14px; padding: 0.85rem; border: 2px solid rgba(0, 212, 255, 0.2);">'

    # Add icon if available
    if os.path.exists(icon_path):
        welcome_html += f'<img src="data:image/png;base64,{get_image_base64(icon_path)}" style="width: 50px; height: 50px; border-radius: 50%; margin-bottom: 0.5rem; border: 2px solid #00d4ff; box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);">'
    else:
        welcome_html += '<div style="font-size: 2.5rem; margin-bottom: 0.35rem;">🛡️</div>'

    welcome_html += '''
            <h2 style="color: #00d4ff; margin-bottom: 0.5rem; font-size: 1.5rem;">Welcome to ESET Security Agent</h2>
            <p style="color: #a0a0a0; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0.5rem;">
                I'm your AI-powered security analyst, ready to help you investigate threats, analyze alerts, and manage security incidents.
            </p>
            <p style="color: #808080; font-size: 0.85rem; margin-bottom: 0.65rem;">
                Powered by <strong style="color: #00d4ff;">Osiris MCP</strong> & <strong style="color: #00d4ff;">Gemini AI</strong>
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.55rem; margin-top: 0.65rem;">
                <div style="background: rgba(0, 212, 255, 0.08); padding: 0.6rem; border-radius: 10px; border: 1px solid rgba(0, 212, 255, 0.2);">
                    <h4 style="color: #00d4ff; margin-bottom: 0.25rem; font-size: 0.9rem;">🎯 Threat Analysis</h4>
                    <p style="color: #c0c0c0; font-size: 0.8rem; margin: 0;">Investigate alerts and security incidents</p>
                </div>
                <div style="background: rgba(0, 212, 255, 0.08); padding: 0.6rem; border-radius: 10px; border: 1px solid rgba(0, 212, 255, 0.2);">
                    <h4 style="color: #00d4ff; margin-bottom: 0.25rem; font-size: 0.9rem;">🔍 Endpoint Monitoring</h4>
                    <p style="color: #c0c0c0; font-size: 0.8rem; margin: 0;">Query endpoint data and activities</p>
                </div>
                <div style="background: rgba(0, 212, 255, 0.08); padding: 0.6rem; border-radius: 10px; border: 1px solid rgba(0, 212, 255, 0.2);">
                    <h4 style="color: #00d4ff; margin-bottom: 0.25rem; font-size: 0.9rem;">⚡ Playbook Execution</h4>
                    <p style="color: #c0c0c0; font-size: 0.8rem; margin: 0;">Run automated response playbooks</p>
                </div>
            </div>
            <p style="color: #808080; font-size: 0.8rem; margin-top: 0.65rem; margin-bottom: 0;">
                💡 Tip: Start by asking about recent alerts or suspicious activities
            </p>
        </div>
    </div>
    '''

    st.markdown(welcome_html, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input with custom placeholder
st.markdown("""
<div style="margin-top: 0.5rem; margin-bottom: 0.25rem;">
    <p style="color: #a0a0a0; font-size: 0.75rem; text-align: center;">
        💬 Ask about threats, alerts, endpoints, or security incidents...
    </p>
</div>
""", unsafe_allow_html=True)

if prompt := st.chat_input("Type your security query here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        # Create a status container for the reasoning process
        with st.status("🧠 ESET Thinking", expanded=True) as status:
            
            def status_callback(step, details, state="info"):
                # Update the status container
                if state == "running":
                    status.write(f"🔄 **{step}**: {details}")
                elif state == "success":
                    status.write(f"✅ **{step}**: {details}")
                elif state == "error":
                    status.update(label=f"❌ Error in {step}", state="error")
                    status.error(f"**{step}**: {details}")
                else:
                    status.write(f"ℹ️ **{step}**: {details}")

            try:
                # Helper to run async in Streamlit safe manner
                async def run_wrapper():
                    return await run_agent_async(prompt, status_callback=status_callback)

                # Run async agent with callback
                response_text = asyncio.run(run_wrapper())
                
                status.update(label="✅ Response Generated", state="complete", expanded=False)
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                status.update(label="❌ Agent Failed", state="error")
                st.error(f"Error: {e}")

# Debug Logs Section
st.markdown("---")

with st.expander("📝 View Detailed Logs", expanded=False):
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 10px; border: 1px solid rgba(0, 212, 255, 0.2);">
    """, unsafe_allow_html=True)

    logs = log_handler.get_logs()
    if logs:
        st.code(logs, language="log")
    else:
        st.info("No logs available yet. Start a conversation to see debug information.")

    st.markdown("</div>", unsafe_allow_html=True)
