from .schemas import ImmuneInputs, ImmuneOutputs

def calculate_immune_metrics(inputs: ImmuneInputs) -> ImmuneOutputs:
    """
    Calculate intermediate and core Immune X scores based on the deterministic mathematical engine.
    
    Arguments:
        inputs (ImmuneInputs): Pydantic validated input model containing 23 attributes.
        
    Returns:
        ImmuneOutputs: Structured outputs containing the 11 calculated scores.
    """
    # 1. Inflammation Score (IS)
    is_score = 0.40 * inputs.CRP + 0.30 * inputs.IL6 + 0.30 * inputs.TNFa
    
    # 2. Lifestyle Score (LS)
    ls_score = 0.30 * inputs.Exercise_Score + 0.30 * inputs.Sleep_Score + 0.20 * inputs.BMI_Score + 0.20 * inputs.Smoking_Score
    
    # 3. Vaccine Response Score (VRS)
    vrs_score = 0.50 * inputs.Antibody_Response + 0.30 * inputs.T_cell_Response + 0.20 * inputs.Response_Durability
    
    # 4. Health Score (HS)
    hs_score = 0.35 * inputs.Metabolic_Score + 0.35 * inputs.Cardiovascular_Score + 0.30 * inputs.Immune_Health_Base_Score
    
    # 5. Age Factor (AF)
    # Handle division by zero edge cases just in case, though schemas restrict Expected_Lifespan to >= 1.0
    expected_lifespan = max(inputs.Expected_Lifespan, 1.0)
    af_score = 100.0 - ((inputs.Age / expected_lifespan) * 100.0)
    
    # 6. ImmuneAgeGap
    immune_age_gap = inputs.ImmuneAge - inputs.Age
    
    # 7. Immune Memory Quality Score (IMQS)
    imqs_score = (
        0.25 * inputs.TSCM +
        0.20 * inputs.TCRD +
        0.15 * inputs.CD4_CD8_Ratio +
        0.10 * inputs.NaiveT +
        0.10 * vrs_score +
        0.10 * is_score +
        0.05 * ls_score +
        0.05 * af_score
    )
    
    # 8. Biobanking Eligibility Score (BES)
    # AgeFactor is used here as AgeScore (af_score)
    bes_score = 0.60 * imqs_score + 0.20 * hs_score + 0.20 * af_score
    
    # 9. Immune Decline Risk Score (IDRS)
    idrs_score = (
        0.30 * is_score +
        0.25 * immune_age_gap +
        0.15 * inputs.BMI_Score +
        0.15 * inputs.Smoking_Score +
        0.15 * inputs.Comorbidity_Score
    )
    
    # 10. Re-Banking Index (RBI)
    # Re-Banking Index = 0.50(DeltaImmuneAge) - 0.30(DeltaIMQS) + 0.20(IDRS)
    rebanking_index = 0.50 * inputs.DeltaImmuneAge - 0.30 * inputs.DeltaIMQS + 0.20 * idrs_score
    
    # 11. Immune Health Index (IHI)
    ihi_score = 0.40 * imqs_score + 0.30 * (100.0 - idrs_score) + 0.30 * bes_score
    
    return ImmuneOutputs(
        InflammationScore=is_score,
        LifestyleScore=ls_score,
        VaccineResponseScore=vrs_score,
        HealthScore=hs_score,
        AgeFactor=af_score,
        ImmuneAgeGap=immune_age_gap,
        IMQS=imqs_score,
        BES=bes_score,
        IDRS=idrs_score,
        ReBankingIndex=rebanking_index,
        IHI=ihi_score
    )
