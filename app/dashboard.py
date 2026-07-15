import streamlit as st
import plotly.graph_objects as go
from src.engine.schemas import ImmuneOutputs, ImmuneInputs


def _render_idi_bar(idi_value: float):
    """
    Render a horizontal gauge bar for the Immune Decline Index (IDI).
    Display ranges:
      0-20: Minimal
      21-40: Mild
      41-60: Moderate
      61-80: Significant
      81-100: Severe
    """
    val = max(0.0, min(100.0, idi_value))
    
    if val <= 20.0:
        color = "#00F5D4"
        status = "Minimal Decline"
    elif val <= 40.0:
        color = "#00B4D8"
        status = "Mild Decline"
    elif val <= 60.0:
        color = "#FFBE0B"
        status = "Moderate Decline"
    elif val <= 80.0:
        color = "#FF9F1C"
        status = "Significant Decline"
    else:
        color = "#F72585"
        status = "Severe Decline"

    fig = go.Figure()
    
    shapes = [
        dict(type="rect", xref="x", yref="paper", x0=0, x1=20, y0=0.2, y1=0.8,
             fillcolor="rgba(0,245,212,0.1)", line=dict(width=0)),
        dict(type="rect", xref="x", yref="paper", x0=20, x1=40, y0=0.2, y1=0.8,
             fillcolor="rgba(0,180,216,0.1)", line=dict(width=0)),
        dict(type="rect", xref="x", yref="paper", x0=40, x1=60, y0=0.2, y1=0.8,
             fillcolor="rgba(255,190,11,0.1)", line=dict(width=0)),
        dict(type="rect", xref="x", yref="paper", x0=60, x1=80, y0=0.2, y1=0.8,
             fillcolor="rgba(255,159,28,0.1)", line=dict(width=0)),
        dict(type="rect", xref="x", yref="paper", x0=80, x1=100, y0=0.2, y1=0.8,
             fillcolor="rgba(247,37,133,0.1)", line=dict(width=0)),
        dict(type="line", xref="x", yref="paper", x0=val, x1=val, y0=0, y1=1,
             line=dict(color=color, width=4)),
    ]
    
    fig.add_trace(go.Scatter(
        x=[val],
        y=[0.5],
        mode="markers",
        marker=dict(
            size=18,
            color=color,
            symbol="triangle-up",
            line=dict(color="#FFFFFF", width=2),
        ),
        showlegend=False,
        hovertemplate=(
            f"<b>Immune Decline Index</b><br>"
            f"Value: <b>{val:.1f} / 100</b><br>"
            f"Classification: <b>{status}</b><br>"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        shapes=shapes,
        xaxis=dict(
            range=[0, 100],
            tickmode="array",
            tickvals=[0, 20, 40, 60, 80, 100],
            ticktext=["0", "20", "40", "60", "80", "100"],
            tickfont=dict(color="#94A3B8", size=10, family="Outfit"),
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor="rgba(148,163,184,0.25)",
            linewidth=1,
        ),
        yaxis=dict(visible=False, range=[0, 1]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=90,
        margin=dict(l=10, r=10, t=5, b=30),
        showlegend=False,
        font=dict(family="Outfit", color="#F8FAFC"),
    )
    return fig


def render_dashboard(inputs: ImmuneInputs, outputs: ImmuneOutputs, is_first_session: bool = False):
    """
    Renders the visual dashboard displaying all 11 outputs.

    Arguments:
        inputs (ImmuneInputs): Raw patient inputs.
        outputs (ImmuneOutputs): Calculated output scores.
        is_first_session (bool): Whether this is the first session for the patient.
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
        with st.container(border=True):
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

    with col_g2:
        with st.container(border=True):
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

    col_c1, col_c2 = st.columns(2)

    # ─────────────────────────────────────────────
    # 3. Radar Chart — 5 Supporting Dimensions
    # ─────────────────────────────────────────────
    with col_c1:
        with st.container(border=True):
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

    # ─────────────────────────────────────────────
    # 4. Biological vs Chronological Age Bar Chart
    # ─────────────────────────────────────────────
    with col_c2:
        with st.container(border=True):
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
        st.markdown(_metric_card("Immune Quality (IMQS)", outputs.IMQS, "#00B4D8"), unsafe_allow_html=True)
        st.markdown(_metric_card("Immune Resiliency (IRS)", outputs.IRS, "#00F5D4"), unsafe_allow_html=True)

    st.write("---")

    # ─────────────────────────────────────────────
    # 6. Longitudinal Comparison — IDI & Upgrade Potential
    # ─────────────────────────────────────────────
    st.markdown('<h3 class="card-title">🎯 Longitudinal Comparison (Relative to Banked Sample)</h3>', unsafe_allow_html=True)

    with st.container(border=True):
        if is_first_session or outputs.IDI is None or outputs.UPS is None:
            st.markdown(
                """
                <div style="text-align:center; padding: 40px 20px;">
                    <h3 style="color:#94A3B8; margin-bottom: 5px;">N/A</h3>
                    <p style="color:#64748B; font-size: 1.1rem;">Initial Profile — No Previously Banked Cells</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("<h5>Immune Decline Index (IDI)</h5>", unsafe_allow_html=True)
                raw_idi = outputs.IDI
                
                if raw_idi <= 20.0:
                    idi_color, idi_label = "#00F5D4", "🟢 Minimal Decline"
                elif raw_idi <= 40.0:
                    idi_color, idi_label = "#00B4D8", "🔵 Mild Decline"
                elif raw_idi <= 60.0:
                    idi_color, idi_label = "#FFBE0B", "🟡 Moderate Decline"
                elif raw_idi <= 80.0:
                    idi_color, idi_label = "#FF9F1C", "🟠 Significant Decline"
                else:
                    idi_color, idi_label = "#F72585", "🔴 Severe Decline"
                    
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                        <div>
                            <span style="font-size:1.8rem; font-weight:800; color:{idi_color};">{raw_idi:.1f}</span>
                            <span style="color:#64748B; font-size:0.85rem;"> / 100</span>
                        </div>
                        <span style="font-size:1rem; font-weight:700; color:{idi_color};">{idi_label}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.plotly_chart(_render_idi_bar(raw_idi), use_container_width=True)
                
            with col_right:
                st.markdown("<h5>Upgrade Potential Score (UPS)</h5>", unsafe_allow_html=True)
                raw_ups = outputs.UPS
                
                if raw_ups > 0.0:
                    ups_color = "#00F5D4"
                    ups_title = "🟢 Sample Upgrade Suggested"
                    ups_desc = f"The current immune profile is superior (UPS: <strong>+{raw_ups:.1f}</strong>) to your banked profile. Immediate re-banking is recommended to preserve this peak immunity."
                    ups_bg = "rgba(0,245,212,0.08)"
                    ups_border = "rgba(0,245,212,0.3)"
                else:
                    ups_color = "#00B4D8"
                    ups_title = "🔵 Retain Original Banked Sample"
                    ups_desc = f"The stored sample in the biobank remains biologically superior (UPS: <strong>{raw_ups:.1f}</strong>). Defer any new cell collections at this time."
                    ups_bg = "rgba(0,180,216,0.08)"
                    ups_border = "rgba(0,180,216,0.3)"
                    
                st.markdown(
                    f"""
                    <div style="background:{ups_bg}; border:1px solid {ups_border}; border-radius:8px; padding:15px; height:100%;">
                        <strong style="color:{ups_color}; font-size:1rem;">{ups_title}</strong>
                        <p style="margin-top:6px; color:#E2E8F0; font-size:0.85rem; line-height:1.4;">{ups_desc}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.write("---")

    # ─────────────────────────────────────────────
    # 7. Clinical Analysis & Recommendations
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

    if is_first_session or outputs.IDI is None or outputs.UPS is None:
        st.markdown(
            f'<div class="glass-card info-card">'
            f"<strong style='color:#00B4D8;'>ℹ️ INITIAL PROFILE: Longitudinal Metrics Deferred</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>This session establishes your initial baseline profile. "
            f"Subsequent session tests will automatically calculate the Immune Decline Index (IDI) and Upgrade Potential Score (UPS) "
            f"relative to this baseline to guide future banking recommendations.</p></div>",
            unsafe_allow_html=True,
        )
    elif outputs.UPS > 0.0:
        st.markdown(
            f'<div class="glass-card success-card">'
            f"<strong style='color:#00F5D4;'>✓ ACTION SUGGESTED: Update Banked Cells</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>Your current immune metrics represent a biological improvement "
            f"over your previously stored sample (Upgrade Potential Score: <strong>+{outputs.UPS:.1f}</strong>). "
            f"We suggest performing a cell collection booster session to capture and preserve this improved state.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        # IDI and UPS <= 0
        st.markdown(
            f'<div class="glass-card alert-card">'
            f"<strong style='color:#FFBE0B;'>✓ DEFER RE-BANKING: Keep Current Stored Sample</strong><br>"
            f"<p style='margin-top:8px;color:#E2E8F0;font-size:0.95rem;'>Your stored sample remains superior to your current profile "
            f"(Upgrade Potential Score: <strong>{outputs.UPS:.1f}</strong>). "
            f"Your Immune Decline Index stands at <strong>{outputs.IDI:.1f} / 100</strong>. "
            f"We recommend deferring new banking sessions and focusing on health optimization routines.</p></div>",
            unsafe_allow_html=True,
        )
