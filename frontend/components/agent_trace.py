"""
Agent trace component — renders the LangGraph pipeline trace as a Streamlit expander.
"""
import streamlit as st


AGENT_COLORS = {
    "Planner": "#6366f1",
    "Interaction Analyzer": "#f59e0b",
    "Knowledge Retriever": "#10b981",
    "Risk Assessor": "#ef4444",
    "NBA Generator": "#3b82f6",
}


def render_agent_trace(steps: list[dict]) -> None:
    """Render agent trace steps inside an expander."""
    with st.expander("🔍 Agent Trace", expanded=True):
        if not steps:
            st.caption("No trace data available.")
            return

        for i, step in enumerate(steps):
            agent_name = step.get("agent_name", "Unknown")
            action = step.get("action", "")
            reasoning = step.get("reasoning", "")
            duration_ms = step.get("duration_ms", 0)
            color = AGENT_COLORS.get(agent_name, "#8b5cf6")

            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(
                    f'<span style="background:{color};color:white;padding:2px 8px;'
                    f'border-radius:4px;font-size:0.75rem;font-weight:600;">'
                    f"{agent_name}</span> &nbsp; {action}",
                    unsafe_allow_html=True,
                )
                if reasoning:
                    st.caption(reasoning)
            with col2:
                st.markdown(
                    f'<div style="text-align:right;color:#6b7280;font-size:0.75rem;'
                    f'padding-top:4px;">{duration_ms}ms</div>',
                    unsafe_allow_html=True,
                )

            if i < len(steps) - 1:
                st.markdown(
                    '<div style="border-left:2px solid #e5e7eb;margin-left:12px;'
                    'height:12px;"></div>',
                    unsafe_allow_html=True,
                )
