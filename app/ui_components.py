import streamlit as st
from src.engine.schemas import ImmuneInputs
from src.utils.helpers import normalize_crp, normalize_il6, normalize_tnfa, normalize_cd4_cd8

def render_header():
    """Renders the dashboard header with only the title top bar."""
    st.markdown(
        """
        <div style="background-color: #FFFFFF; text-align: center; padding: 15px 0px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0, 180, 216, 0.15); border: 1px solid rgba(0, 180, 216, 0.15);">
            <h1 class="gradient-text" style="font-size: 2.6rem; margin: 0; padding: 0; line-height: 1; font-weight: 800; font-family: 'Outfit', sans-serif; letter-spacing: 3px;">IMMUNE X</h1>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_input_form() -> ImmuneInputs:
    """
    Renders the form with 23 inputs grouped logically.
    Takes inputs directly as raw clinical lab units.
    
    Returns:
        ImmuneInputs: Validated input schema model.
    """
    st.markdown('<h3 class="card-title">🧬 Patient Input Parameters</h3>', unsafe_allow_html=True)
    st.write("---")
    
    # 4 tabs for logical grouping
    tab1, tab2, tab3, tab4 = st.tabs([
        "🩸 Biomarkers & Lab Results", 
        "👥 Demographics & Lifestyle", 
        "📋 Medical History", 
        "🤖 Temporal & Historical Data"
    ])
    
    # Initialize dictionary to hold all 23 parameters
    vals = {}
    
    with tab1:
        st.markdown('<div class="form-section-header">Inflammatory & Cellular Biomarkers</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            raw_crp = st.number_input(
                "C-Reactive Protein (CRP) [mg/L]",
                min_value=0.0, max_value=100.0, value=1.5, step=0.1,
                help="Normal healthy level is typically < 1.0 mg/L. High risk > 3.0 mg/L. Values > 10.0 mg/L indicate acute inflammation."
            )
            vals['CRP'] = normalize_crp(raw_crp)
            st.caption(f"Normalized CRP Score: **{vals['CRP']:.1f} / 100**")
            
            raw_il6 = st.number_input(
                "Interleukin-6 (IL-6) [pg/mL]",
                min_value=0.0, max_value=200.0, value=1.8, step=0.1,
                help="Normal range is typically < 2.0 pg/mL. Elevated levels represent systemic inflammation."
            )
            vals['IL6'] = normalize_il6(raw_il6)
            st.caption(f"Normalized IL-6 Score: **{vals['IL6']:.1f} / 100**")
            
            raw_tnfa = st.number_input(
                "TNF-Alpha [pg/mL]",
                min_value=0.0, max_value=150.0, value=2.5, step=0.1,
                help="Tumor Necrosis Factor-alpha. Healthy baseline is < 3.0 pg/mL. High levels signify active immune response."
            )
            vals['TNFa'] = normalize_tnfa(raw_tnfa)
            st.caption(f"Normalized TNF-Alpha Score: **{vals['TNFa']:.1f} / 100**")
            
            vals['TSCM'] = st.slider(
                "T Memory Stem Cells (TSCM)", 
                0.0, 100.0, 75.0, step=1.0,
                help="Key cells for long-term immunological memory. Higher values represent better preservation."
            )
            
        with col2:
            vals['TCRD'] = st.slider(
                "T-cell Receptor Diversity (TCRD)", 
                0.0, 100.0, 80.0, step=1.0,
                help="Repertoire diversity of T-cells. Crucial for recognizing novel pathogens."
            )
            
            raw_ratio = st.number_input(
                "CD4/CD8 Ratio [Ratio Value]",
                min_value=0.0, max_value=10.0, value=1.8, step=0.1,
                help="Healthy ratio is typically between 1.0 and 4.0. Inversion (< 1.0) is a hallmark of immunosenescence."
            )
            vals['CD4_CD8_Ratio'] = normalize_cd4_cd8(raw_ratio)
            st.caption(f"Normalized CD4/CD8 Score: **{vals['CD4_CD8_Ratio']:.1f} / 100**")
                
            vals['NaiveT'] = st.slider(
                "Naive T Cell Score", 
                0.0, 100.0, 70.0, step=1.0,
                help="Proportion of un-encountered T cells. Dictates ability to respond to new antigens."
            )
            
    with tab2:
        st.markdown('<div class="form-section-header">Age & Lifestyle Quality Indicators</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            vals['Age'] = st.number_input("Chronological Age (years)", min_value=18.0, max_value=120.0, value=35.0, step=1.0)
            vals['Expected_Lifespan'] = st.number_input("Expected Lifespan (years)", min_value=50.0, max_value=120.0, value=85.0, step=1.0)
            vals['BMI_Score'] = st.slider("BMI Score", 0.0, 100.0, 80.0, step=1.0, help="Body Mass Index score (higher indicates a healthier body mass index profile)")
            vals['Smoking_Score'] = st.slider("Smoking Score", 0.0, 100.0, 10.0, step=1.0, help="High score indicates high tobacco usage, 0 indicates non-smoker")
            
        with col2:
            vals['Exercise_Score'] = st.slider("Exercise Score", 0.0, 100.0, 75.0, step=1.0, help="Physical activity level (100 = highly active)")
            vals['Sleep_Score'] = st.slider("Sleep Score", 0.0, 100.0, 70.0, step=1.0, help="Sleep duration and quality (100 = optimal)")
            vals['Comorbidity_Score'] = st.slider("Comorbidity Score", 0.0, 100.0, 5.0, step=1.0, help="Presence of chronic illnesses (100 = severe load, 0 = none)")
            
    with tab3:
        st.markdown('<div class="form-section-header">Immunological & Base Health History</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            vals['Antibody_Response'] = st.slider("Antibody Response", 0.0, 100.0, 80.0, step=1.0, help="Peak antibody titer response to vaccinations")
            vals['T_cell_Response'] = st.slider("T-Cell Response", 0.0, 100.0, 75.0, step=1.0, help="T-cell activation response to vaccination")
            vals['Response_Durability'] = st.slider("Response Durability", 0.0, 100.0, 70.0, step=1.0, help="Speed of antibody decline post-immunization")
            
        with col2:
            vals['Metabolic_Score'] = st.slider("Metabolic Score", 0.0, 100.0, 85.0, step=1.0, help="Glucose control and lipid profiles")
            vals['Cardiovascular_Score'] = st.slider("Cardiovascular Score", 0.0, 100.0, 80.0, step=1.0, help="Blood pressure and cardiac performance indices")
            vals['Immune_Health_Base_Score'] = st.slider("Immune Health Base Score", 0.0, 100.0, 85.0, step=1.0, help="Historical frequency of infectious events")
            
    with tab4:
        st.markdown('<div class="form-section-header">Biological Immune Age & Longitudinal History</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            vals['ImmuneAge'] = st.number_input(
                "Biological Immune Age (years)", 
                min_value=18.0, max_value=120.0, value=33.0, step=1.0,
                help="Estimated age of the immune system based on epigenetic clocks or cellular assays."
            )
            
            vals['DeltaImmuneAge'] = st.number_input(
                "Delta Immune Age (years)", 
                min_value=-50.0, max_value=50.0, value=-1.5, step=0.1,
                help="Longitudinal change in biological immune age compared to previous tests. Negative is good."
            )
            
        with col2:
            vals['DeltaIMQS'] = st.number_input(
                "Delta IMQS Score", 
                min_value=-100.0, max_value=100.0, value=4.5, step=0.1,
                help="Longitudinal change in the calculated Immune Memory Quality Score. Positive is good."
            )
            
    return ImmuneInputs(**vals)
