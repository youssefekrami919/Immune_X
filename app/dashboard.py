import streamlit as st
import plotly.graph_objects as go
from src.engine.schemas import ImmuneOutputs, ImmuneInputs


def _render_rebanking_bar(raw_value: float):
    """
    Render a horizontal colored gauge bar for the Re-Banking Index.

    Visual display range: [-10, 20]  (practical clinical range)
      raw = -10  → bar position =   0  (fully stable)
      raw =   0  → bar position =  33  (no concern)
      raw =   5  → bar position =  50  (action threshold)
      raw =  20  → bar position = 100  (critical)

    Color zones:
      Green  (0–40):   Safe zone      — raw value is comfortably below threshold
      Blue  (40–60):   Caution zone   — raw value is approaching the threshold
      Red   (60–100):  Critical zone  — action required, re-banking needed
    """
    DISPLAY_MIN, DISPLAY_MAX = -10.0, 20.0
    DISPLAY_RANGE = DISPLAY_MAX - DISPLAY_MIN  # 30

    def _pos(v: float) -> float:
        return max(0.0, min(100.0, ((v - DISPLAY_MIN) / DISPLAY_RANGE) * 100.0))

    bar_pos = _pos(raw_value)
    thresh_pos = _pos(5.0)   # 50.0 — action threshold
    zero_pos = _pos(0.0)     # 33.3 — "no concern" reference

    # Determine status color for the marker
    if raw_value < 0:
        color_marker = "#00F5D4"  # teal
    elif raw_value < 5.0:
        color_marker = "#00B4D8"  # blue
    else:
        color_marker = "#F72585"  # red

    # Visual zone boundaries
    green_end = 40.0
    blue_end = 60.0

    fig = go.Figure()

    # ── Colored zone rectangles ──────────────────────────────────────
    shapes = [
        # Green: safe zone
        dict(type="rect", xref="x", yref="paper",
             x0=0, x1=green_end, y0=0.12, y1=0.88,
             fillcolor="rgba(0,245,212,0.15)",
             line=dict(width=1, color="rgba(0,245,212,0.2)")),
        # Blue: caution zone
        dict(type="rect", xref="x", yref="paper",
             x0=green_end, x1=blue_end, y0=0.12, y1=0.88,
             fillcolor="rgba(0,180,216,0.22)",
             line=dict(width=1, color="rgba(0,180,216,0.3)")),
        # Red: critical zone
        dict(type="rect", xref="x", yref="paper",
             x0=blue_end, x1=100, y0=0.12, y1=0.88,
             fillcolor="rgba(247,37,133,0.15)",
             line=dict(width=1, color="rgba(247,37,133,0.2)")),
        # ── Reference line: raw=0 ("stable") ──
        dict(type="line", xref="x", yref="paper",
             x0=zero_pos, x1=zero_pos, y0=0, y1=1,
             line=dict(color="rgba(0,245,212,0.45)", width=1.5, dash="dot")),
        # ── Threshold line: raw=5 (action required) ──
        dict(type="line", xref="x", yref="paper",
             x0=thresh_pos, x1=thresh_pos, y0=0, y1=1,
             line=dict(color="rgba(247,37,133,0.85)", width=2.5, dash="dash")),
        # ── Current value line ──
        dict(type="line", xref="x", yref="paper",
             x0=bar_pos, x1=bar_pos, y0=0, y1=1,
             line=dict(color=color_marker, width=3.5)),
    ]

    # ── Zone text labels ──────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[20.0, 50.0, 80.0],
        y=[0.5, 0.5, 0.5],
        mode="text",
        text=["🟢  Safe Zone", "🔵 Caution", "🔴  Critical"],
        textfont=dict(
            color=["rgba(0,245,212,0.75)",
                   "rgba(0,180,216,0.85)",
                   "rgba(247,37,133,0.75)"],
            size=11,
            family="Outfit",
        ),
        showlegend=False,
        hoverinfo="skip",
    ))

    # ── Current value marker (triangle + hover tooltip) ───────────────
    fig.add_trace(go.Scatter(
        x=[bar_pos],
        y=[0.5],
        mode="markers",
        marker=dict(
            size=18,
            color=color_marker,
            symbol="triangle-up",
            line=dict(color="#FFFFFF", width=2),
        ),
        showlegend=False,
        hovertemplate=(
            f"<b>Re-Banking Index</b><br>"
            f"Raw Clinical Value : <b>{raw_value:.3f}</b><br>"
            f"Bar Position (0-100): <b>{bar_pos:.1f}</b><br>"
            f"──────────────<br>"
            f"⚠ Action Threshold = Raw 5.0  (Position: {thresh_pos:.0f}/100)"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        shapes=shapes,
        xaxis=dict(
            range=[0, 100],
            tickmode="array",
            tickvals=[0, zero_pos, thresh_pos, 75, 100],
            ticktext=[
                "0",
                f"{zero_pos:.0f}<br><span style='color:#00F5D4;font-size:9px'>Raw 0</span>",
                f"<b>{thresh_pos:.0f}</b><br><span style='color:#F72585;font-size:9px'>⚠ Raw 5</span>",
                "75",
                "100",
            ],
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
        height=105,
        margin=dict(l=10, r=10, t=5, b=48),
        showlegend=False,
        font=dict(family="Outfit", color="#F8FAFC"),
    )

    return fig


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
        st.markdown(_metric_card("Re-Banking Index (RBI)", outputs.ReBankingIndex, "#00F5D4"), unsafe_allow_html=True)
        st.markdown(_metric_card("Immune Quality (IMQS)", outputs.IMQS, "#00B4D8"), unsafe_allow_html=True)

    st.write("---")

    # ─────────────────────────────────────────────
    # 6. Re-Banking Index — Visual Risk Gauge
    # ─────────────────────────────────────────────
    st.markdown('<h3 class="card-title">🎯 Re-Banking Index — Risk Position Gauge</h3>', unsafe_allow_html=True)

    with st.container(border=True):
        raw_rbi = outputs.ReBankingIndex
        DISPLAY_MIN_RBI, DISPLAY_MAX_RBI = -10.0, 20.0
        bar_pos_rbi = max(0.0, min(100.0,
            ((raw_rbi - DISPLAY_MIN_RBI) / (DISPLAY_MAX_RBI - DISPLAY_MIN_RBI)) * 100.0
        ))

        if raw_rbi < 0:
            rbi_color, rbi_icon, rbi_label = "#00F5D4", "🟢", "Stable — No Re-Banking Needed"
        elif raw_rbi < 5.0:
            rbi_color, rbi_icon, rbi_label = "#00B4D8", "🔵", "Monitor — Approaching Threshold"
        else:
            rbi_color, rbi_icon, rbi_label = "#F72585", "🔴", "Action Required — Re-Banking Recommended"

        # ── Dual-value header ──
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding: 8px 4px 4px 4px;">
                <div>
                    <div style="font-size:0.72rem; color:#94A3B8; text-transform:uppercase;
                                letter-spacing:1px; margin-bottom:3px;">Raw Clinical Value</div>
                    <span style="font-size:2rem; font-weight:800; color:{rbi_color};">
                        {raw_rbi:.3f}
                    </span>
                    <span style="font-size:0.82rem; color:#64748B;"> &nbsp;/ Action Threshold: <b style='color:#F72585;'>5.0</b></span>
                </div>
                <div style="text-align:center;">
                    <span style="font-size:1rem; font-weight:600; color:{rbi_color};">
                        {rbi_icon} {rbi_label}
                    </span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.72rem; color:#94A3B8; text-transform:uppercase;
                                letter-spacing:1px; margin-bottom:3px;">Bar Position (0–100)</div>
                    <span style="font-size:2rem; font-weight:800; color:{rbi_color};">
                        {bar_pos_rbi:.1f}
                    </span>
                    <span style="font-size:0.82rem; color:#64748B;"> / 100 &nbsp;(⚠ threshold at 50)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.plotly_chart(_render_rebanking_bar(raw_rbi), use_container_width=True)

        st.markdown(
            """
            <div style="font-size:0.78rem; color:#64748B; text-align:center; padding: 2px 0 4px 0;">
                🟢 Safe Zone (pos 0–40 / raw &lt; 2) &nbsp;|&nbsp;
                🔵 Caution Zone (pos 40–60 / raw 2–8) &nbsp;|&nbsp;
                🔴 Critical Zone (pos 60–100 / raw &gt; 8)
                &nbsp;&nbsp;·&nbsp;&nbsp;
                <span style='color:rgba(247,37,133,0.8);'>⚠ Dashed red line = Action Threshold (Raw: 5.0 / Position: 50)</span>
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
