"""
Memory panel — renders the memory context (similar cases, confidence boost).
This is the "money moment" component for the demo.
"""
import streamlit as st


def render_memory_context(memory_context: dict | None) -> None:
    """Render the memory context panel."""
    if not memory_context or memory_context.get("similar_cases_found", 0) == 0:
        st.markdown(
            """
            <div style="background:#f3f4f6;border:1px dashed #d1d5db;border-radius:8px;
            padding:16px;text-align:center;">
            <div style="color:#9ca3af;font-size:0.85rem;">
              🧠 No memory context — cold start
            </div>
            <div style="color:#d1d5db;font-size:0.75rem;margin-top:4px;">
              Accept a recommendation to build episodic memory
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    similar = memory_context.get("similar_cases_found", 0)
    base = memory_context.get("base_confidence", 0.73)
    boosted = memory_context.get("boosted_confidence", 0.73)
    boost = memory_context.get("confidence_boost", 0.0)
    precedents = memory_context.get("precedent_accounts", [])

    st.markdown(
        f"""
        <div style="background:#ecfdf5;border:1px solid #10b981;border-radius:8px;
        padding:16px;">
        <div style="font-weight:700;color:#065f46;font-size:0.95rem;margin-bottom:8px;">
          🧠 Memory Context Active
        </div>
        <div style="color:#047857;font-size:0.85rem;">
          {similar} similar resolved case{"s" if similar != 1 else ""} found:
          <strong>{', '.join(precedents) if precedents else 'N/A'}</strong>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Confidence Boost**")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.metric("Base Confidence", f"{int(base * 100)}%")
    with col2:
        st.markdown(
            f'<div style="text-align:center;font-size:1.5rem;padding-top:8px;">→</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.metric(
            "Boosted Confidence",
            f"{int(boosted * 100)}%",
            delta=f"+{int(boost * 100)}%",
        )

    # Visual boost bar
    base_pct = int(base * 100)
    boost_pct = int(boost * 100)
    st.markdown(
        f"""
        <div style="margin-top:8px;">
          <div style="background:#e5e7eb;border-radius:4px;height:10px;position:relative;">
            <div style="background:#10b981;width:{base_pct}%;border-radius:4px;
            height:10px;position:absolute;left:0;"></div>
            <div style="background:#34d399;width:{boost_pct}%;border-radius:4px;
            height:10px;position:absolute;left:{base_pct}%;opacity:0.8;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;
          font-size:0.7rem;color:#6b7280;margin-top:2px;">
            <span>0%</span>
            <span style="color:#10b981;">▲ +{boost_pct}% from memory</span>
            <span>100%</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
