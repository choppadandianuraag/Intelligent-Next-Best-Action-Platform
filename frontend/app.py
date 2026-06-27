"""
Meridian — Streamlit frontend entry point.

Launch: streamlit run frontend/app.py
Requires backend running at BACKEND_URL (default: http://localhost:8000)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import streamlit as st
from dotenv import load_dotenv

from frontend.components.agent_trace import render_agent_trace
from frontend.components.recommendation_panel import render_recommendations
from frontend.components.memory_panel import render_memory_context
from frontend.components.hitl_widget import render_hitl

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Meridian — Decision Intelligence",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stButton > button { border-radius: 6px; }
    .stTextArea textarea { font-family: 'Inter', monospace; font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Account map (id → display label)
# ---------------------------------------------------------------------------
ACCOUNTS = {
    "acme_corp": "Acme Corp — At Risk (Manufacturing)",
    "bluewave_tech": "BlueWave Tech — At Risk (Technology)",
    "nexus_systems": "Nexus Systems — At Risk (Enterprise SW)",
    "globex_corp": "Globex Corp — Healthy (Financial Services)",
    "techcorp": "TechCorp — Onboarding (SaaS)",
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("# 🧭 Meridian")
    st.markdown("*Decision intelligence for CS teams*")
    st.markdown("---")

    selected_id = st.selectbox(
        "Account",
        options=list(ACCOUNTS.keys()),
        format_func=lambda k: ACCOUNTS[k],
        key="account_select",
    )

    transcript = st.text_area(
        "Paste meeting transcript",
        height=300,
        placeholder="Paste the meeting notes or transcript here...",
        key="transcript_input",
    )

    analyse_btn = st.button(
        "🔍 Analyse Account",
        use_container_width=True,
        type="primary",
        disabled=not transcript.strip(),
    )

    st.markdown("---")
    st.caption(f"Backend: {BACKEND_URL}")

    # Quick health check
    try:
        r = httpx.get(f"{BACKEND_URL}/health", timeout=2.0)
        if r.status_code == 200:
            st.success("✅ Backend online")
        else:
            st.warning("⚠️ Backend unreachable")
    except Exception:
        st.error("❌ Backend offline")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "loading" not in st.session_state:
    st.session_state.loading = False

# ---------------------------------------------------------------------------
# Analyse trigger
# ---------------------------------------------------------------------------
if analyse_btn and transcript.strip():
    st.session_state.loading = True
    st.session_state.result = None

    with st.spinner("Running agent pipeline…"):
        try:
            response = httpx.post(
                f"{BACKEND_URL}/analyze",
                json={"account_id": selected_id, "interaction_text": transcript},
                timeout=120.0,
            )
            response.raise_for_status()
            st.session_state.result = response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            st.error(f"Failed to reach backend: {e}")
    st.session_state.loading = False

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
result = st.session_state.result

if result is None:
    # Placeholder
    st.markdown(
        """
        <div style="display:flex;flex-direction:column;align-items:center;
        justify-content:center;height:60vh;text-align:center;color:#9ca3af;">
        <div style="font-size:3rem;margin-bottom:16px;">🧭</div>
        <div style="font-size:1.2rem;font-weight:600;color:#374151;">Meridian</div>
        <div style="font-size:0.9rem;margin-top:8px;">
          Select an account, paste a transcript, and click <strong>Analyse Account</strong>
        </div>
        <div style="font-size:0.8rem;margin-top:4px;color:#d1d5db;">
          The agent pipeline will extract signals, retrieve knowledge, assess risk,
          and generate next-best-actions.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Results layout
    left_col, right_col = st.columns([3, 2])

    with left_col:
        # Recommendations
        render_recommendations(result)

        st.markdown("---")

        # HITL
        render_hitl(result.get("request_id", ""))

    with right_col:
        # Memory context
        st.markdown("### 🧠 Memory Context")
        render_memory_context(result.get("memory_context"))

        st.markdown("---")

        # Agent trace
        render_agent_trace(result.get("agent_trace", []))

        # Evidence
        evidence = result.get("evidence", [])
        if evidence:
            with st.expander(f"📄 Evidence ({len(evidence)} sources)", expanded=False):
                for ev in evidence:
                    source_type = ev.get("source_type", "")
                    source_name = ev.get("source_name", "")
                    relevance = ev.get("relevance_score", 0)
                    excerpt = ev.get("excerpt", "")

                    type_icon = "📘" if source_type == "playbook" else "📝"
                    st.markdown(
                        f"{type_icon} **{source_name}** — relevance: {relevance:.0%}"
                    )
                    st.caption(excerpt[:250] + ("..." if len(excerpt) > 250 else ""))
                    st.markdown("---")
