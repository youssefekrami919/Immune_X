"""
Session Result Page — IMMUNE X Clinical Platform.

Displays the full dashboard output for a specific saved session,
plus an expandable table of all 23 recorded inputs.
"""

import json
import streamlit as st
from src.engine.schemas import ImmuneInputs, ImmuneOutputs
from app.dashboard import render_dashboard


def _nav(page: str, **kwargs):
    st.session_state["page"] = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


# Human-readable labels for the 23 inputs
_INPUT_LABELS = {
    "CRP":                    ("C-Reactive Protein (CRP)", "Score 0–100"),
    "IL6":                    ("Interleukin-6 (IL-6)", "Score 0–100"),
    "TNFa":                   ("TNF-Alpha", "Score 0–100"),
    "TSCM":                   ("T Memory Stem Cells (TSCM)", "Score 0–100"),
    "TCRD":                   ("T-Cell Receptor Diversity", "Score 0–100"),
    "CD4_CD8_Ratio":          ("CD4/CD8 Ratio", "Score 0–100"),
    "NaiveT":                 ("Naive T Cell Score", "Score 0–100"),
    "Age":                    ("Chronological Age", "Years"),
    "Expected_Lifespan":      ("Expected Lifespan", "Years"),
    "BMI_Score":              ("BMI Score", "Score 0–100"),
    "Smoking_Score":          ("Smoking Score", "Score 0–100"),
    "Exercise_Score":         ("Exercise Score", "Score 0–100"),
    "Sleep_Score":            ("Sleep Score", "Score 0–100"),
    "Comorbidity_Score":      ("Comorbidity Score", "Score 0–100"),
    "Antibody_Response":      ("Antibody Response", "Score 0–100"),
    "T_cell_Response":        ("T-Cell Response", "Score 0–100"),
    "Response_Durability":    ("Response Durability", "Score 0–100"),
    "Metabolic_Score":        ("Metabolic Score", "Score 0–100"),
    "Cardiovascular_Score":   ("Cardiovascular Score", "Score 0–100"),
    "Immune_Health_Base_Score":("Immune Health Base Score", "Score 0–100"),
    "ImmuneAge":              ("Biological Immune Age", "Years"),
    "DeltaImmuneAge":         ("Delta Immune Age", "Years"),
    "DeltaIMQS":              ("Delta IMQS Score", "Points"),
}

_INPUT_CATEGORIES = {
    "🩸 Biomarkers & Lab Results": [
        "CRP", "IL6", "TNFa", "TSCM", "TCRD", "CD4_CD8_Ratio", "NaiveT"
    ],
    "👥 Demographics & Lifestyle": [
        "Age", "Expected_Lifespan", "BMI_Score", "Smoking_Score",
        "Exercise_Score", "Sleep_Score", "Comorbidity_Score"
    ],
    "📋 Medical History": [
        "Antibody_Response", "T_cell_Response", "Response_Durability",
        "Metabolic_Score", "Cardiovascular_Score", "Immune_Health_Base_Score"
    ],
    "🤖 Temporal & Historical Data": [
        "ImmuneAge", "DeltaImmuneAge", "DeltaIMQS"
    ],
}


def page_session_result():
    """Render the detailed session result page."""
    inputs_data = st.session_state.get("session_inputs")
    outputs_data = st.session_state.get("session_outputs")
    session_label = st.session_state.get("session_label", "Session")
    session_date = st.session_state.get("session_date", "")
    back_patient = st.session_state.get("back_patient")
    is_first_session = st.session_state.get("is_first_session", False)

    if not inputs_data or not outputs_data:
        _nav("home")
        return

    # ── Breadcrumb Navigation ───────────────────────────────────────────────
    col_back, col_info = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Patient", key="btn_back_patient"):
            if back_patient:
                _nav("patient", current_patient=back_patient)
            else:
                _nav("home")

    # ── Session Header ──────────────────────────────────────────────────────
    national_id = back_patient["national_id"] if back_patient else "Unknown"
    ihi = outputs_data.get("IHI", 0)
    bes = outputs_data.get("BES", 0)

    if ihi >= 75:
        status_color = "#00F5D4"
        status_text = "🟢 Optimal Immune Health"
        status_bg = "rgba(0,245,212,0.08)"
        status_border = "rgba(0,245,212,0.3)"
    elif ihi >= 50:
        status_color = "#FFBE0B"
        status_text = "🟡 Fair Immune Health"
        status_bg = "rgba(255,190,11,0.08)"
        status_border = "rgba(255,190,11,0.3)"
    else:
        status_color = "#F72585"
        status_text = "🔴 High Senescence Risk"
        status_bg = "rgba(247,37,133,0.08)"
        status_border = "rgba(247,37,133,0.3)"

    st.markdown(
        f"""
        <div class="session-result-header" style="background:{status_bg}; border:1.5px solid {status_border};">
            <div class="srh-left">
                <div class="srh-label">Patient National ID</div>
                <div class="srh-id">{national_id}</div>
                <div class="srh-meta">
                    <span>{session_label}</span>
                    &nbsp;·&nbsp;
                    <span>📅 {session_date}</span>
                </div>
            </div>
            <div class="srh-right">
                <div class="srh-kpi">
                    <span class="srh-kpi-label">IHI</span>
                    <span class="srh-kpi-value" style="color:{status_color};">{ihi:.1f}</span>
                </div>
                <div class="srh-kpi">
                    <span class="srh-kpi-label">BES</span>
                    <span class="srh-kpi-value" style="color:#00B4D8;">{bes:.1f}</span>
                </div>
                <div class="srh-status" style="color:{status_color};">{status_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Reconstruct typed objects for render_dashboard ──────────────────────
    try:
        inputs_obj = ImmuneInputs(**inputs_data)
        outputs_obj = ImmuneOutputs(**outputs_data)
    except Exception as e:
        st.error(f"Failed to load session data: {e}")
        return

    # ── Full Dashboard ──────────────────────────────────────────────────────
    render_dashboard(inputs_obj, outputs_obj, is_first_session)

    # ── Inputs Summary ──────────────────────────────────────────────────────
    st.write("---")
    with st.expander("📋 Session Input Parameters (All 23 Recorded Values)", expanded=False):
        for cat_name, field_keys in _INPUT_CATEGORIES.items():
            st.markdown(
                f'<div class="form-section-header">{cat_name}</div>',
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            for j, key in enumerate(field_keys):
                label, unit = _INPUT_LABELS.get(key, (key, ""))
                value = inputs_data.get(key, "N/A")
                display_val = f"{value:.2f}" if isinstance(value, float) else str(value)
                target_col = col1 if j % 2 == 0 else col2
                with target_col:
                    st.markdown(
                        f"""
                        <div class="input-summary-row">
                            <span class="input-summary-label">{label}</span>
                            <span class="input-summary-value">{display_val}
                                <span class="input-summary-unit">{unit}</span>
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # ── Developer Diagnostics ───────────────────────────────────────────────
    with st.expander("🛠️ Developer & API Diagnostics (JSON Payload)"):
        st.markdown("#### Input JSON Payload")
        st.json(inputs_data)
        st.markdown("#### Engine Outputs JSON Payload")
        st.json(outputs_data)
