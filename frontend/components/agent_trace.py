import streamlit as st


def render_agent_trace(steps: list[dict]):
    with st.expander("Agent trace", expanded=True):
        for step in steps:
            cols = st.columns([1, 4, 2])
            cols[0].markdown(f"**{step['agent_name']}**")
            cols[1].markdown(
                f"{step['action']}  \n<span style='color:gray;font-size:12px'>{step['reasoning']}</span>",
                unsafe_allow_html=True
            )
            cols[2].markdown(
                f"<div style='text-align:right'>{step['duration_ms']} ms</div>",
                unsafe_allow_html=True
            )
