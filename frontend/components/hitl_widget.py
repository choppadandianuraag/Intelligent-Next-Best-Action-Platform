"""
HITL (Human-in-the-Loop) widget — Accept / Modify / Reject buttons with notes.
Calls POST /feedback on the backend API.
"""
import streamlit as st
import httpx
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def render_hitl(request_id: str) -> None:
    """Render the HITL decision widget for a given request_id."""
    if not request_id:
        return

    st.markdown("---")
    st.markdown("### 👤 Your Decision")

    # Track state in session
    decision_key = f"decision_{request_id}"
    notes_key = f"notes_{request_id}"
    submitted_key = f"submitted_{request_id}"

    if st.session_state.get(submitted_key):
        decision = st.session_state.get(decision_key, "")
        _icons = {"accepted": "✅", "modified": "✏️", "rejected": "❌"}
        st.success(
            f"{_icons.get(decision, '✅')} Decision logged: **{decision.upper()}**"
        )
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        accept = st.button(
            "✅ Accept",
            key=f"accept_{request_id}",
            use_container_width=True,
            type="primary",
        )
    with col2:
        modify = st.button(
            "✏️ Modify",
            key=f"modify_{request_id}",
            use_container_width=True,
        )
    with col3:
        reject = st.button(
            "❌ Reject",
            key=f"reject_{request_id}",
            use_container_width=True,
        )

    # Show notes field for modify
    modification_notes = None
    show_notes = st.session_state.get(f"show_notes_{request_id}", False)

    if modify:
        st.session_state[f"show_notes_{request_id}"] = True
        show_notes = True

    if show_notes:
        modification_notes = st.text_area(
            "Modification notes",
            key=f"mod_notes_{request_id}",
            placeholder="Describe what you'd change about this recommendation...",
            height=80,
        )
        confirm_modify = st.button(
            "Confirm Modification",
            key=f"confirm_mod_{request_id}",
            type="primary",
        )
        if confirm_modify:
            _submit_feedback(request_id, "modified", modification_notes, decision_key, submitted_key)

    if accept:
        _submit_feedback(request_id, "accepted", None, decision_key, submitted_key)
    elif reject:
        _submit_feedback(request_id, "rejected", None, decision_key, submitted_key)


def _submit_feedback(
    request_id: str,
    decision: str,
    notes: str | None,
    decision_key: str,
    submitted_key: str,
) -> None:
    try:
        resp = httpx.post(
            f"{BACKEND_URL}/feedback",
            json={
                "request_id": request_id,
                "decision": decision,
                "modification_notes": notes,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        st.session_state[decision_key] = decision
        st.session_state[submitted_key] = True
        st.rerun()
    except Exception as e:
        st.error(f"Failed to log feedback: {e}")
