import streamlit as st
import os
from src.engine import calculate_immune_metrics
from app.ui_components import render_header, render_input_form
from app.dashboard import render_dashboard

# 1. Page Configuration
st.set_page_config(
    page_title="Immune X - AI Memory Banking Engine",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Path to CSS relative to root
css_path = os.path.join(os.path.dirname(__file__), "app", "style.css")
local_css(css_path)

# 3. Sidebar Information
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        <h2 style="color: #00B4D8; font-weight: 700; margin-bottom: 5px;">IMMUNE X</h2>
        <span style="background-color: #172A45; color: #00F5D4; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">MVP ENGINE v1.0</span>
    </div>
    <hr style="margin-top: 15px; margin-bottom: 15px; border-color: rgba(0, 180, 216, 0.2);"/>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown("### 📋 Platform Info")
st.sidebar.info(
    "Immune X integrates cellular biomarkers, lifestyle factors, and clinical history "
    "to optimize immune banking decisions and monitor longevity scores over time."
)

st.sidebar.markdown("### 🔧 Future ML Swapping")
st.sidebar.warning(
    "Currently operating on deterministic equations. The modular architecture is designed "
    "to swap formulas directly with trained ML predictors (e.g. XGBoost, RF) without modifying the UI."
)

st.sidebar.markdown(
    """
    <hr style="border-color: rgba(0, 180, 216, 0.2);"/>
    <div style="text-align: center; font-size: 0.8rem; color: #94A3B8;">
        © 2026 Immune X Inc.<br>All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)

# 4. Main App Layout
render_header()

# Create a two-column layout: Form on the left, Dashboard on the right
col_form, col_dash = st.columns([1, 1.3])

with col_form:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    # Render inputs and get validated pydantic object
    try:
        inputs = render_input_form()
    except Exception as e:
        st.error(f"Input validation error: {e}")
        inputs = None
    st.markdown('</div>', unsafe_allow_html=True)

with col_dash:
    if inputs:
        # Run calculation engine
        outputs = calculate_immune_metrics(inputs)
        
        # Render visual dashboard
        render_dashboard(inputs, outputs)
        
        # Developer Panel
        st.write("---")
        with st.expander("🛠️ Developer & API Diagnostics (JSON Payload)"):
            st.markdown("#### Input JSON Payload")
            st.json(inputs.model_dump())
            st.markdown("#### Engine Outputs JSON Payload")
            st.json(outputs.model_dump())
    else:
        st.info("Please fill out the inputs in the left panel to calculate immune health metrics.")
