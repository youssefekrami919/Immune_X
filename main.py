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
    initial_sidebar_state="collapsed"
)

# 2. Inject Custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Path to CSS relative to root
css_path = os.path.join(os.path.dirname(__file__), "app", "style.css")
local_css(css_path)


# 4. Main App Layout
render_header()

# Create a two-column layout: Form on the left, Dashboard on the right
col_form, col_dash = st.columns([1, 1.3])

with col_form:
    with st.container(border=True):
        # Render inputs and get validated pydantic object
        try:
            inputs = render_input_form()
        except Exception as e:
            st.error(f"Input validation error: {e}")
            inputs = None

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
