"""
Home Page — IMMUNE X Clinical Platform.

Provides two primary actions for clinicians:
  1. Register a new patient by National ID.
  2. Open an existing patient's profile by National ID.
"""

import streamlit as st
from src.database import add_patient, get_patient


def _nav(page: str, **kwargs):
    """Helper to set navigation state and trigger a rerun."""
    st.session_state["page"] = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


def page_home():
    """Render the clinical home / landing page."""

    # ── Welcome Banner ─────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="home-welcome-banner">
            <div class="home-welcome-icon">🏥</div>
            <div>
                <h2 class="home-welcome-title">IMMUNE X Clinical Portal</h2>
                <p class="home-welcome-sub">
                    Preventive Immune Memory Banking — Patient Management System
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two-column action cards ─────────────────────────────────────────────
    col_new, col_open = st.columns(2, gap="large")

    # ── Register New Patient ───────────────────────────────────────────────
    with col_new:
        with st.container(border=True):
            st.markdown(
                """
                <div class="action-card-header">
                    <span class="action-card-icon">➕</span>
                    <span class="action-card-title">Register New Patient</span>
                </div>
                <p class="action-card-desc">
                    Add a patient to the system using their National ID.
                    Once registered, you can begin immune health assessments.
                </p>
                """,
                unsafe_allow_html=True,
            )
            new_id = st.text_input(
                "Patient National ID",
                key="home_new_id",
                placeholder="Enter National ID…",
                label_visibility="collapsed",
            )
            if st.button("🧬 Register Patient", key="btn_register", use_container_width=True):
                if not new_id.strip():
                    st.error("Please enter a valid National ID.")
                else:
                    result = add_patient(new_id.strip())
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])

    # ── Open Patient Profile ───────────────────────────────────────────────
    with col_open:
        with st.container(border=True):
            st.markdown(
                """
                <div class="action-card-header">
                    <span class="action-card-icon">🔍</span>
                    <span class="action-card-title">Open Patient Profile</span>
                </div>
                <p class="action-card-desc">
                    Access an existing patient's immune health record and
                    historical session data by entering their National ID.
                </p>
                """,
                unsafe_allow_html=True,
            )
            open_id = st.text_input(
                "Patient National ID",
                key="home_open_id",
                placeholder="Enter National ID…",
                label_visibility="collapsed",
            )
            if st.button("📂 Open Profile", key="btn_open", use_container_width=True):
                if not open_id.strip():
                    st.error("Please enter a National ID.")
                else:
                    patient = get_patient(open_id.strip())
                    if patient:
                        _nav("patient", current_patient=patient)
                    else:
                        st.error(
                            f"No patient found with National ID **{open_id.strip()}**. "
                            "Please register them first."
                        )

    # ── Info strip ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-strip">
            <span>🩺 This portal is intended for use by licensed medical professionals and laboratory specialists only.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
