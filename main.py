import os
import streamlit as st
from src.database import init_db
from app.ui_components import render_header
from app.pages.page_home import page_home
from app.pages.page_patient import page_patient
from app.pages.page_session_result import page_session_result

# ─────────────────────────────────────────────
# 1. Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Immune X — Clinical Portal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# 2. Inject Custom CSS
# ─────────────────────────────────────────────
def _load_css(file_name: str):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(__file__), "app", "style.css")
_load_css(css_path)

# ─────────────────────────────────────────────
# 3. Database Initialization (once per session)
# ─────────────────────────────────────────────
if "db_initialized" not in st.session_state:
    try:
        init_db()
        st.session_state["db_initialized"] = True
    except Exception as e:
        st.error(
            "⚠️ **Database Connection Failed.** "
            "Please check your `.streamlit/secrets.toml` credentials and try again.\n\n"
            f"Details: `{e}`"
        )
        st.stop()

# ─────────────────────────────────────────────
# 4. Navigation State Initialization
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "home"

# ─────────────────────────────────────────────
# 5. Global Header (shown on every page)
# ─────────────────────────────────────────────
render_header()

# ─────────────────────────────────────────────
# 6. Page Router
# ─────────────────────────────────────────────
page = st.session_state.get("page", "home")

if page == "home":
    page_home()
elif page == "patient":
    page_patient()
elif page == "session_result":
    page_session_result()
else:
    # Fallback
    st.session_state["page"] = "home"
    st.rerun()
