import streamlit as st
import httpx
import os
import json
import glob

st.set_page_config(page_title="Meridian", layout="wide")
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Load customer profiles for the account dropdown
profiles = {}
for path in glob.glob("backend/data/customer_profiles/*.json"):
    with open(path) as f:
        data = json.load(f)
    profiles[data["account_name"]] = os.path.basename(path).replace(".json", "")

# Sidebar
with st.sidebar:
    st.header("Meridian")
    if profiles:
        account_name = st.selectbox("Account", list(profiles.keys()))
        account_id = profiles[account_name]
    else:
        st.warning("No customer profiles found. Add JSON files to backend/data/customer_profiles/")
        account_name = st.text_input("Account Name", value="acme_corp")
        account_id = account_name.lower().replace(" ", "_")
    transcript = st.text_area("Paste meeting transcript", height=300)
    analyze_btn = st.button("Analyse account", type="primary")

# Run analysis on button click
if analyze_btn and transcript:
    with st.spinner("Running agent pipeline..."):
        try:
            r = httpx.post(
                f"{API_URL}/analyze",
                json={"account_id": account_id, "interaction_text": transcript},
                timeout=120.0
            )
            r.raise_for_status()
            result = r.json()
            st.session_state["result"] = result
            st.session_state["account_id"] = account_id
            st.session_state["transcript"] = transcript
        except httpx.ConnectError:
            st.error(f"Cannot connect to API at {API_URL}. Make sure `uvicorn backend.main:app --port 8000` is running.")
        except Exception as e:
            st.error(f"Error: {e}")

# Render results
if "result" in st.session_state:
    result = st.session_state["result"]
    account_id = st.session_state.get("account_id", "")

    from frontend.components.agent_trace import render_agent_trace
    from frontend.components.recommendation_panel import render_recommendation_panel
    from frontend.components.memory_panel import render_memory_panel
    from frontend.components.hitl_widget import render_hitl_widget

    render_agent_trace(result["agent_trace"])
    render_recommendation_panel(result)
    if result.get("memory_context"):
        render_memory_panel(result["memory_context"])
    render_hitl_widget(result, account_id)
elif not analyze_btn:
    # Placeholder shown before any analysis
    st.markdown(
        "<div style='display:flex;align-items:center;justify-content:center;height:300px;"
        "color:gray;font-size:18px'>Select an account and paste a transcript to begin.</div>",
        unsafe_allow_html=True
    )
