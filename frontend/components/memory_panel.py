import streamlit as st


def render_memory_panel(ctx: dict):
    if ctx.get("similar_cases_found", 0) == 0:
        return
    st.subheader("Memory Boost")
    st.markdown(
        f"**{ctx['similar_cases_found']}** similar cases found: "
        f"{', '.join(ctx['precedent_accounts'])}"
    )
    c1, c2 = st.columns(2)
    c1.metric("Base Confidence", f"{ctx['base_confidence']:.0%}")
    c2.metric(
        "Boosted Confidence",
        f"{ctx['boosted_confidence']:.0%}",
        delta=f"+{ctx['confidence_boost']:.0%}"
    )
