import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def render_hitl_widget(result: dict, account_id: str):
    st.subheader("Human-in-the-Loop")
    c1, c2, c3 = st.columns(3)
    req_id = result["request_id"]
    payload = {
        "request_id": req_id,
        "account_id": account_id,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "recommendation_title": result["primary_recommendation"]["title"]
    }
    if c1.button("Accept", use_container_width=True):
        httpx.post(f"{API_URL}/feedback", json={**payload, "decision": "accept", "modification_notes": ""})
        st.success("Accepted and logged to memory.")
    if c2.button("Reject", use_container_width=True):
        httpx.post(f"{API_URL}/feedback", json={**payload, "decision": "reject", "modification_notes": ""})
        st.error("Rejected and logged.")
    if c3.button("Modify", use_container_width=True):
        st.session_state["show_modify"] = True

    if st.session_state.get("show_modify"):
        notes = st.text_area(
            "What would you like to change?",
            placeholder="e.g., Change primary action to onboarding check-in"
        )
        if st.button("Submit modification"):
            httpx.post(f"{API_URL}/feedback", json={**payload, "decision": "modify", "modification_notes": notes})
            st.info("Modification logged. Re-analyzing with feedback...")
            new_text = st.session_state.get("transcript", "") + "\n\n" + "[CSM Feedback: " + notes + "]"
            r = httpx.post(
                f"{API_URL}/analyze",
                json={"account_id": account_id, "interaction_text": new_text},
                timeout=120.0
            )
            st.session_state["result"] = r.json()
            st.rerun()
