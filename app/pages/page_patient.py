"""
Patient Profile Page — IMMUNE X Clinical Platform.

Displays:
  - Patient header (National ID + registration date)
  - Session history table with quality badges
  - Session trend comparison chart (when > 1 session)
  - "Add New Session" form (reuses render_input_form)
"""

import json
import streamlit as st
import plotly.graph_objects as go
from src.database import add_session, get_sessions
from src.engine import calculate_immune_metrics
from app.ui_components import render_input_form


def _nav(page: str, **kwargs):
    st.session_state["page"] = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


def _ihi_badge(ihi: float) -> str:
    """Return HTML badge based on IHI score."""
    if ihi >= 75:
        return '<span class="session-badge badge-good">🟢 Optimal</span>'
    elif ihi >= 50:
        return '<span class="session-badge badge-fair">🟡 Fair</span>'
    else:
        return '<span class="session-badge badge-poor">🔴 High Risk</span>'


def _bes_badge(bes: float) -> str:
    if bes >= 75:
        return '<span class="session-badge badge-good">✅ Highly Eligible</span>'
    elif bes >= 50:
        return '<span class="session-badge badge-fair">🔵 Eligible</span>'
    else:
        return '<span class="session-badge badge-poor">⚠️ Not Eligible</span>'


def _render_session_comparison(sessions: list):
    """Render a Plotly trend chart comparing IHI and BES across sessions."""
    labels = [f"Session {i + 1}\n{s['session_date'].strftime('%Y-%m-%d')}" for i, s in enumerate(sessions)]
    ihi_vals = [s["ihi_score"] for s in sessions]
    bes_vals = [s["bes_score"] for s in sessions]

    best_idx = ihi_vals.index(max(ihi_vals))

    fig = go.Figure()

    # IHI line
    fig.add_trace(go.Scatter(
        x=labels, y=ihi_vals,
        mode="lines+markers",
        name="IHI — Immune Health Index",
        line=dict(color="#00F5D4", width=2.5),
        marker=dict(size=8, color="#00F5D4"),
    ))

    # BES line
    fig.add_trace(go.Scatter(
        x=labels, y=bes_vals,
        mode="lines+markers",
        name="BES — Biobanking Eligibility",
        line=dict(color="#00B4D8", width=2.5, dash="dot"),
        marker=dict(size=8, color="#00B4D8"),
    ))

    # Star marker on the best session (highest IHI)
    fig.add_trace(go.Scatter(
        x=[labels[best_idx]],
        y=[ihi_vals[best_idx]],
        mode="markers+text",
        name="Best Session ⭐",
        marker=dict(size=18, color="#FFBE0B", symbol="star"),
        text=["⭐ Best"],
        textposition="top center",
        textfont=dict(color="#FFBE0B", size=12),
    ))

    # Reference lines
    fig.add_hline(y=75, line_dash="dash", line_color="rgba(0,245,212,0.3)",
                  annotation_text="Optimal Threshold (75)", annotation_position="top right",
                  annotation_font_color="#00F5D4")
    fig.add_hline(y=50, line_dash="dash", line_color="rgba(255,190,11,0.3)",
                  annotation_text="Fair Threshold (50)", annotation_position="top right",
                  annotation_font_color="#FFBE0B")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC", family="Outfit"),
        height=320,
        margin=dict(l=20, r=20, t=30, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=11),
        ),
        xaxis=dict(
            tickfont=dict(color="#94A3B8"),
            gridcolor="rgba(148, 163, 184, 0.1)",
        ),
        yaxis=dict(
            range=[0, 105],
            tickfont=dict(color="#94A3B8"),
            gridcolor="rgba(148, 163, 184, 0.1)",
            title=dict(text="Score (0–100)", font=dict(color="#94A3B8")),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def page_patient():
    """Render the patient profile page."""
    patient = st.session_state.get("current_patient")
    if not patient:
        _nav("home")
        return

    national_id = patient["national_id"]
    created_at = patient["created_at"]

    # ── Breadcrumb ──────────────────────────────────────────────────────────
    if st.button("← Back to Home", key="btn_back_home"):
        _nav("home")

    # ── Patient Header ──────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="patient-header-card">
            <div class="patient-header-left">
                <div class="patient-avatar">👤</div>
                <div>
                    <div class="patient-label">Patient National ID</div>
                    <div class="patient-id">{national_id}</div>
                    <div class="patient-meta">Registered: {created_at.strftime("%d %B %Y") if hasattr(created_at, "strftime") else created_at}</div>
                </div>
            </div>
            <div class="patient-header-right">
                <div class="patient-status-pill">🏥 Active Patient</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Load sessions ───────────────────────────────────────────────────────
    sessions = get_sessions(national_id)

    # ── Session comparison chart (only if > 1 session) ──────────────────────
    if len(sessions) > 1:
        with st.container(border=True):
            best_idx = max(range(len(sessions)), key=lambda i: sessions[i]["ihi_score"])
            best_session = sessions[best_idx]
            st.markdown(
                f"""
                <h3 class="card-title">📈 Session Trend — IHI &amp; BES Over Time</h3>
                <p class="section-desc">
                    Tracking immune health across <strong>{len(sessions)}</strong> sessions.
                    Best performance: <strong>Session {best_idx + 1}</strong>
                    (IHI: <strong>{best_session['ihi_score']:.1f}</strong> ⭐)
                </p>
                """,
                unsafe_allow_html=True,
            )
            _render_session_comparison(sessions)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Sessions List ───────────────────────────────────────────────────────
    st.markdown('<h3 class="card-title">🗂️ Session History</h3>', unsafe_allow_html=True)

    if not sessions:
        st.markdown(
            """
            <div class="empty-state-card">
                <div class="empty-state-icon">🔬</div>
                <p>No sessions recorded yet for this patient.</p>
                <p class="empty-state-hint">Add the first session using the form below.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        best_ihi_id = max(sessions, key=lambda s: s["ihi_score"])["id"]

        for i, s in enumerate(sessions):
            outputs_data = json.loads(s["outputs_json"])
            inputs_data = json.loads(s["inputs_json"])
            ihi = s["ihi_score"]
            bes = s["bes_score"]
            is_best = s["id"] == best_ihi_id

            session_label = f"Session {i + 1}"
            if is_best and len(sessions) > 1:
                session_label += " ⭐ Best"

            border_style = "border: 1.5px solid #FFBE0B !important;" if is_best and len(sessions) > 1 else ""

            with st.container(border=True):
                # Apply gold border for best session via inline hack
                if is_best and len(sessions) > 1:
                    st.markdown(
                        '<style>div[data-testid="stVerticalBlockBorder"]:last-of-type { border-color: #FFBE0B !important; }</style>',
                        unsafe_allow_html=True,
                    )

                col_info, col_scores, col_action = st.columns([2, 3, 1])

                with col_info:
                    date_str = s["session_date"].strftime("%d %b %Y, %H:%M") if hasattr(s["session_date"], "strftime") else str(s["session_date"])
                    st.markdown(
                        f"""
                        <div class="session-info">
                            <div class="session-number">{session_label}</div>
                            <div class="session-date">📅 {date_str}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_scores:
                    st.markdown(
                        f"""
                        <div class="session-scores-row">
                            <div class="session-score-item">
                                <span class="score-label">IHI</span>
                                <span class="score-value" style="color:#00F5D4;">{ihi:.1f}</span>
                                {_ihi_badge(ihi)}
                            </div>
                            <div class="session-score-item">
                                <span class="score-label">BES</span>
                                <span class="score-value" style="color:#00B4D8;">{bes:.1f}</span>
                                {_bes_badge(bes)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_action:
                    if st.button("📊 Results", key=f"btn_view_{s['id']}", use_container_width=True):
                        _nav(
                            "session_result",
                            session_inputs=inputs_data,
                            session_outputs=outputs_data,
                            session_label=session_label,
                            session_date=date_str,
                            back_patient=patient,
                            is_first_session=(i == 0),
                        )

    # ── Add New Session ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">🔬 Add New Session</h3>', unsafe_allow_html=True)

    with st.expander("📝 Open Immune Assessment Form", expanded=len(sessions) == 0):
        with st.form(key="new_session_form"):
            try:
                prev_sess = sessions[-1] if sessions else None
                inputs = render_input_form(previous_session=prev_sess)
            except Exception as e:
                st.error(f"Input validation error: {e}")
                inputs = None

            submitted = st.form_submit_button(
                "💾 Save Session & Calculate Results",
                use_container_width=True,
            )

        if submitted and inputs:
            outputs = calculate_immune_metrics(inputs)
            result = add_session(
                national_id,
                inputs.model_dump(),
                outputs.model_dump(),
            )
            if result["success"]:
                st.success("✅ " + result["message"])
                st.rerun()
            else:
                st.error("❌ " + result["message"])
