import streamlit as st
import plotly.graph_objects as go
from src.engine.schemas import ImmuneOutputs, ImmuneInputs


def render_dashboard(inputs: ImmuneInputs, outputs: ImmuneOutputs):
    """
    Renders the visual dashboard displaying all 11 outputs.

    Arguments:
        inputs (ImmuneInputs): Raw patient inputs.
        outputs (ImmuneOutputs): Calculated output scores.
    """
    # ─────────────────────────────────────────────
    # 1. Main Key Metrics Summary (Metrics Bar)
    # ─────────────────────────────────────────────
    st.markdown('<h3 class="card-title">📊 Executive Immune Summary</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    gap_val = outputs.ImmuneAgeGap
    gap_str = f"{gap_val:+.1f} years"
    if gap_val < 0:
        gap_delta = "Healthy Advantage"
        gap_color = "normal"
    elif gap_val == 0:
        gap_delta = "Neutral"
        gap_color = "off"
    else:
        gap_delta = "Accelerated Aging"
        gap_color = "inverse"

    with col1:
        st.metric(
            label="Immune Health Index (IHI)",
            value=f"{outputs.IHI:.1f} / 100",
            delta="Optimal State" if outputs.IHI >= 75 else ("Fair State" if outputs.IHI >= 50 else "High Senescence Risk"),
            delta_color="normal" if outputs.IHI >= 50 else "inverse",
        )

    with col2:
        st.metric(
            label="Biobanking Eligibility Score (BES)",
            value=f"{outputs.BES:.1f} / 100",
            delta="Highly Eligible" if outputs.BES >= 75 else ("Eligible" if outputs.BES >= 50 else "Postpone / Treat First"),
            delta_color="normal" if outputs.BES >= 50 else "inverse",
        )

    with col3:
        st.metric(
            label="Immune Age Gap",
            value=gap_str,
            delta=gap_delta,
            delta_color=gap_color,
        )

    st.write("---")

    # ─────────────────────────────────────────────
    # 2. Interactive Gauges — IHI and BES
    # ─────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    _GAUGE_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC", family="Outfit"),
        height=250,
        margin=dict(l=20, r=20, t=30, b=20),
    )

    with col_g1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h5>Immune Health Index (IHI)</h5>", unsafe_allow_html=True)
        fig_ihi = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=outputs.IHI,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#F8FAFC"},
                    "bar": {"color": "#00F5D4"},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 2,
                    "bordercolor": "#00B4D8",
                    "steps": [
                        {"range": [0, 45], "color": "rgba(247, 37, 133, 0.15)"},
                        {"range": [45, 75], "color": "rgba(255, 190, 11, 0.15)"},
                        {"range": [75, 100], "color": "rgba(0, 245, 212, 0.15)"},
                    ],
                    "threshold": {
                        "line": {"color": "#F8FAFC", "width": 4},
                        "thickness": 0.75,
                        "value": outputs.IHI,
                    },
                },
            )
        )
        fig_ihi.update_layout(**_GAUGE_LAYOUT)
        st.plotly_chart(fig_ihi, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h5>Biobanking Eligibility (BES)</h5>", unsafe_allow_html=True)
        fig_bes = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=outputs.BES,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#F8FAFC"},
                    "bar": {"color": "#00B4D8"},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 2,
                    "bordercolor": "#00B4D8",
                    "steps": [
                        {"range": [0, 50], "color": "rgba(247, 37, 133, 0.15)"},
                        {"range": [50, 75], "color": "rgba(255, 190, 11, 0.15)"},
                        {"range": [75, 100], "color": "rgba(0, 180, 216, 0.15)"},
                    ],
                    "threshold": {
                        "line": {"color": "#F8FAFC", "width": 4},
                        "thickness": 0.75,
                        "value": outputs.BES,
                    },
                },
            )
        )
        fig_bes.update_layout(**_GAUGE_LAYOUT)
        st.plotly_chart(fig_bes, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2)

    # ─────────────────────────────────────────────
    # 3. Radar Chart — 5 Supporting Dimensions
    # ─────────────────────────────────────────────
    with col_c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h5>Biomarker &amp; Health Profile Dimensions</h5>", unsafe_allow_html=True)

        categories = [
            "Inflammation (IS)",
            "Lifestyle (LS)",
            "Vaccine Resp. (VRS)",
            "Health Score (HS)",
            "Age Factor (AF)",
        ]
        values = [
            outputs.InflammationScore,
            outputs.LifestyleScore,
            outputs.VaccineResponseScore,
            outputs.HealthScore,
            outputs.AgeFactor,
        ]
        # Close the radar loop
        categories.append(categories[0])
        values.append(values[0])

        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                fillcolor="rgba(0, 180, 216, 0.25)",
                line=dict(color="#00B4D8", width=2),
                marker=dict(color="#00F5D4", size=6),
                name="Patient Scores",
            )
        )
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    color="#94A3B8",
                    gridcolor="rgba(148, 163, 184, 0.2)",
                ),
                angularaxis=dict(
                    color="#F8FAFC",
                    gridcolor="rgba(148, 163, 184, 0.2)",
                ),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC", family="Outfit"),
            height=300,
            margin=dict(l=40, r=40, t=30, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # 4. Biological vs Chronological Age Bar Chart
    # ─────────────────────────────────────────────
    with col_c2:
        st.markdown('<div class="glass-card" style="height: 355px;">', unsafe_allow_html=True)
        st.markdown("<h5>Biological vs Chronological Age</h5>", unsafe_allow_html=True)

        fig_age = go.Figure()
        fig_age.add_trace(
            go.Bar(
                y=["Chronological Age", "Immune Age (Biological)"],
                x=[inputs.Age, inputs.ImmuneAge],
                orientation="h",
                marker=dict(
                    color=["rgba(148, 163, 184, 0.6)", "#00F5D4"],
                    line=dict(color=["#94A3B8", "#00B4D8"], width=1.5),
                ),
                width=0.4,
            )
        )
        fig_age.update_layout(
            xaxis=dict(
                title=dict(text="Years", font=dict(color="#F8FAFC")),
                tickfont=dict(color="#94A3B8"),
                gridcolor="rgba(148, 163, 184, 0.15)",
            ),
            yaxis=dict(
                tickfont=dict(color="#F8FAFC"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC", family="Outfit"),
            height=250,
            margin=dict(l=20, r=20, t=10, b=20),
        )
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # 5. Complete Metrics Breakdown Cards
    # ─────────────────────────────────────────────
    st.markdown('<h3 class="card-title">📋 Complete Metrics Breakdown</h3>', unsafe_allow_html=True)
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    def _metric_card(label: str, value: float, color: str) -> str:
        return (
            f'<div class="glass-card" style="padding:15px;text-align:center;margin-bottom:10px;">'
            f'<p style="font-size:0.85rem;color:#94A3B8;margin-bottom:5px;">{label}</p>'
            f'<h4 style="color:{color};font-size:1.6rem;font-weight:700;margin:0;">{value:.1f}</h4>'
            f"</div>"
        )

    with col_s1:
        st.markdown(_metric_card("Inflammation Score (IS)", outputs.InflammationScore, "#F72585"), unsafe_allow_html=True)
        st.markdown(_metric_card("Lifestyle Score (LS)", outputs.LifestyleScore, "#00F5D4"), unsafe_allow_html=True)

    with col_s2:
        st.markdown(_metric_card("Vaccine Response (VRS)", outputs.VaccineResponseScore, "#00B4D8"), unsafe_allow_html=True)
        st.markdown(_metric_card("Health Score (HS)", outputs.HealthScore, "#00B4D8"), unsafe_allow_html=True)

    with col_s3:
        st.markdown(_metric_card("Age Factor (AF)", outputs.AgeFactor, "#E2E8F0"), unsafe_allow_html=True)
        st.markdown(_metric_card("Immune Decline Risk (IDRS)", outputs.IDRS, "#F72585"), unsafe_allow_html=True)

    with col_s4:
        st.markdown(_metric_card("Re-Banking Index (RBI)", outputs.ReBankingIndex, "#00F5D4"), unsafe_allow_html=True)
        st.markdown(_metric_card("Immune Quality (IMQS)", outputs.IMQS, "#00B4D8"), unsafe_allow_html=True)

    st.write("---")

    # ─────────────────────────────────────────────
    # 6. Clinical Analysis & Recommendations
    # ─────────────────────────────────────────────
    st.markdown('<h3 class="card-title">🩺 Clinical Analysis &amp; Recommendations</h3>', unsafe_allow_html=True)

    if outputs.BES >= 75:
        st.markdown(
            f'<div class="glass-card success-card">'
            f"<strong style='color:#00F5D4;'>🟢 RECOMMENDED: Immediate Immune Memory Biobanking</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>Your Biobanking Eligibility Score (BES) is outstanding "
            f"(<strong>{outputs.BES:.1f}</strong>). This indicates a highly preserved T-cell receptor diversity and healthy "
            f"stem-cell-like T Memory cells (TSCM). Biobanking cells now will lock in a high-fidelity, youthful immune profile "
            f"for future therapeutics.</p></div>",
            unsafe_allow_html=True,
        )
    elif outputs.BES >= 50:
        st.markdown(
            f'<div class="glass-card info-card">'
            f"<strong style='color:#00B4D8;'>🔵 ELIGIBLE: Moderate Immune Banking Priority</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>Your BES is <strong>{outputs.BES:.1f}</strong>. "
            f"Your cellular metrics are suitable for banking. However, optimizing your Lifestyle Score (LS) or addressing "
            f"minor inflammatory markers can help elevate the potency of your stored cells.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="glass-card alert-card">'
            f"<strong style='color:#F72585;'>🔴 ACTION REQUIRED: Pre-Biobanking Stabilization Phase</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>Your Biobanking Score is below threshold "
            f"(<strong>{outputs.BES:.1f}</strong>). Immune aging or systemic inflammation is elevated. We recommend "
            f"checking with your immunologist to optimize biomarker readings (CRP, IL-6) and improve physical health "
            f"metrics before initiating the cell collection process.</p></div>",
            unsafe_allow_html=True,
        )

    if outputs.ReBankingIndex >= 5.0:
        st.markdown(
            f'<div class="glass-card alert-card">'
            f"<strong style='color:#F72585;'>⚠️ HIGH PRIORITY: Re-banking Suggested</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>The Re-Banking Index is elevated "
            f"(<strong>{outputs.ReBankingIndex:.1f}</strong>), driven by longitudinal acceleration in immune age "
            f"(Delta Immune Age: <strong>{inputs.DeltaImmuneAge:+.1f} years</strong>) and rising immune decline risk. "
            f"A booster cell collection or clinical immune support is advised.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="glass-card success-card">'
            f"<strong style='color:#00F5D4;'>✓ STABLE: Re-banking Deferred</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>Your longitudinal metrics are highly stable "
            f"(Re-Banking Index: <strong>{outputs.ReBankingIndex:.1f}</strong>). No accelerated immune aging detected "
            f"since your last profile. Continue routine annual surveillance.</p></div>",
            unsafe_allow_html=True,
        )
