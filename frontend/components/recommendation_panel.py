import streamlit as st


def render_recommendation_panel(result: dict):
    st.subheader(f"{result['account_name']} — Risk Assessment")
    c1, c2, c3 = st.columns([1, 2, 1])
    c1.metric("Risk Score", f"{result['risk_score']:.0%}")
    c2.progress(result['risk_score'])
    c3.metric("Signals", result['signal_count'])

    st.subheader("Evidence")
    for ev in result["evidence"][:3]:
        with st.container():
            badge_color = {
                "meeting_note": "#E6F1FB",
                "playbook": "#EEEDFE",
                "memory": "#EAF3DE",
                "crm": "#FFF4E6"
            }
            bg = badge_color.get(ev["source_type"], "#f0f0f0")
            st.markdown(
                f"<span style='background:{bg};padding:2px 8px;border-radius:4px;font-size:12px'>"
                f"{ev['source_type']}</span> **{ev['source_name']}** — relevance {ev['relevance_score']:.2f}",
                unsafe_allow_html=True
            )
            st.caption(ev["excerpt"][:300])

    st.subheader("Primary Recommendation")
    primary = result["primary_recommendation"]
    st.markdown(f"### {primary['title']}")
    st.markdown(primary['description'])
    st.markdown(f"Confidence: **{primary['confidence']:.0%}** | Impact: {primary['estimated_impact']}")

    if result.get("alternatives"):
        st.subheader("Alternatives")
        for alt in result["alternatives"]:
            with st.expander(f"{alt['title']} ({alt['confidence']:.0%})"):
                st.write(alt['description'])
