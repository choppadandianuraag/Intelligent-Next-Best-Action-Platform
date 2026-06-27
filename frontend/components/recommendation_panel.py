"""
Recommendation panel — renders risk gauge, primary action, and 2 alternatives.
"""
import streamlit as st


RISK_COLORS = {
    "critical": "#dc2626",
    "high": "#ea580c",
    "medium": "#d97706",
    "low": "#16a34a",
}

RISK_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}


def _confidence_bar(confidence: float, color: str = "#3b82f6") -> str:
    pct = int(confidence * 100)
    return (
        f'<div style="margin:4px 0;">'
        f'<div style="background:#e5e7eb;border-radius:4px;height:6px;">'
        f'<div style="background:{color};width:{pct}%;border-radius:4px;height:6px;"></div>'
        f"</div>"
        f'<span style="font-size:0.7rem;color:#6b7280;">{pct}% confidence</span>'
        f"</div>"
    )


def render_recommendations(output: dict) -> None:
    """Render the full recommendation panel from a RecommendationOutput dict."""
    risk_level = output.get("risk_level", "medium")
    risk_score = output.get("risk_score", 0.5)
    signal_count = output.get("signal_count", 0)
    color = RISK_COLORS.get(risk_level, "#d97706")
    emoji = RISK_EMOJI.get(risk_level, "🟡")

    # Risk header
    st.markdown(
        f"""
        <div style="background:{color}20;border:1px solid {color};border-radius:8px;
        padding:16px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:12px;">
          <span style="font-size:2rem;">{emoji}</span>
          <div>
            <div style="font-size:1.5rem;font-weight:700;color:{color};">
              {int(risk_score * 100)}% Churn Risk
            </div>
            <div style="color:#6b7280;font-size:0.85rem;">
              {risk_level.upper()} · {signal_count} signals detected ·
              {output.get('account_name', '')} · CSM: {output.get('csm_name', '')} ·
              Renewal: {output.get('renewal_date', '')}
            </div>
          </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Primary recommendation
    primary = output.get("primary_recommendation", {})
    st.markdown("### ⚡ Primary Recommendation")
    with st.container():
        st.markdown(
            f"""
            <div style="background:#1e40af10;border:1px solid #3b82f6;border-radius:8px;
            padding:16px;margin-bottom:8px;">
            <div style="font-weight:700;font-size:1.05rem;color:#1e3a8a;">
              {primary.get('title', 'N/A')}
            </div>
            <div style="color:#374151;margin:8px 0;font-size:0.9rem;">
              {primary.get('description', '')}
            </div>
            <div style="color:#6b7280;font-size:0.8rem;">
              📊 {primary.get('estimated_impact', '')}
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            _confidence_bar(primary.get("confidence", 0.73), "#3b82f6"),
            unsafe_allow_html=True,
        )
        if primary.get("precedent_accounts"):
            st.caption(f"📚 Precedent: {', '.join(primary['precedent_accounts'])}")

    # Alternatives
    alternatives = output.get("alternatives", [])
    if alternatives:
        st.markdown("### 🔀 Alternatives")
        cols = st.columns(len(alternatives))
        for col, alt in zip(cols, alternatives):
            with col:
                st.markdown(
                    f"""
                    <div style="background:#f9fafb;border:1px solid #e5e7eb;
                    border-radius:8px;padding:12px;">
                    <div style="font-weight:600;font-size:0.9rem;color:#111827;">
                      {alt.get('title', '')}
                    </div>
                    <div style="color:#6b7280;font-size:0.8rem;margin:6px 0;">
                      {alt.get('description', '')[:150]}...
                    </div>
                    <div style="color:#9ca3af;font-size:0.75rem;">
                      {alt.get('estimated_impact', '')}
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    _confidence_bar(alt.get("confidence", 0.5), "#6b7280"),
                    unsafe_allow_html=True,
                )
