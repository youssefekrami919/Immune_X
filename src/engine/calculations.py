from .schemas import ImmuneInputs, ImmuneOutputs

def calculate_immune_metrics(
    inputs: ImmuneInputs,
    banked_immune_age: float = None,
    banked_imqs: float = None,
    banked_tscm: float = None,
    banked_irs: float = None,
) -> ImmuneOutputs:
    """
    Calculate intermediate and core Immune X scores based on the deterministic mathematical engine.
    Also calculates IDI (Immune Decline Index) and UPS (Upgrade Potential Score) if banked profile
    data is provided.
    
    Arguments:
        inputs (ImmuneInputs): Pydantic validated input model containing 24 attributes.
        banked_immune_age (float, optional): Stored immune age for comparisons.
        banked_imqs (float, optional): Stored IMQS for comparisons.
        banked_tscm (float, optional): Stored TSCM for comparisons.
        banked_irs (float, optional): Stored IRS for comparisons.
        
    Returns:
        ImmuneOutputs: Structured outputs containing the 12 calculated scores.
    """
    # 1. Inflammation Score (IS)
    is_score = 0.40 * inputs.CRP + 0.30 * inputs.IL6 + 0.30 * inputs.TNFa
    is_score = max(0.0, min(100.0, is_score))
    
    # 2. Lifestyle Score (LS)
    ls_score = 0.30 * inputs.Exercise_Score + 0.30 * inputs.Sleep_Score + 0.20 * inputs.BMI_Score + 0.20 * inputs.Smoking_Score
    ls_score = max(0.0, min(100.0, ls_score))
    
    # 3. Vaccine Response Score (VRS)
    vrs_score = 0.50 * inputs.Antibody_Response + 0.30 * inputs.T_cell_Response + 0.20 * inputs.Response_Durability
    vrs_score = max(0.0, min(100.0, vrs_score))
    
    # 4. Health Score (HS)
    hs_score = 0.35 * inputs.Metabolic_Score + 0.35 * inputs.Cardiovascular_Score + 0.30 * inputs.Immune_Health_Base_Score
    hs_score = max(0.0, min(100.0, hs_score))
    
    # 5. Age Factor (AF)
    expected_lifespan = max(inputs.Expected_Lifespan, 1.0)
    af_score = 100.0 - ((inputs.Age / expected_lifespan) * 100.0)
    af_score = max(0.0, min(100.0, af_score))
    
    # 6. ImmuneAgeGap
    immune_age_gap = inputs.ImmuneAge - inputs.Age
    
    # 7. AgeScore (Revised stepwise range mapping)
    if inputs.Age <= 30.0:
        age_score = 100.0
    elif inputs.Age <= 40.0:
        age_score = 90.0
    elif inputs.Age <= 50.0:
        age_score = 75.0
    elif inputs.Age <= 60.0:
        age_score = 60.0
    elif inputs.Age <= 70.0:
        age_score = 45.0
    else:
        age_score = 30.0

    # 8. Balance Factor
    balance_factor = (0.5 * inputs.NaiveT + 0.3 * inputs.CD4_CD8_Ratio + 0.2 * is_score) / 100.0
    balance_factor = max(0.0, min(1.0, balance_factor))
    
    # 9. Adjusted TSCM
    adjusted_tscm = inputs.TSCM * balance_factor
    adjusted_tscm = max(0.0, min(100.0, adjusted_tscm))
    
    # 10. Immune Memory Quality Score (IMQS)
    imqs_score = (
        0.30 * adjusted_tscm +
        0.20 * inputs.TCRD +
        0.15 * inputs.CD4_CD8_Ratio +
        0.10 * inputs.NaiveT +
        0.10 * vrs_score +
        0.10 * is_score +
        0.05 * ls_score
    )
    imqs_score = max(0.0, min(100.0, imqs_score))
    
    # 11. Biobanking Eligibility Score (BES)
    bes_score = 0.50 * imqs_score + 0.20 * hs_score + 0.30 * age_score
    bes_score = max(0.0, min(100.0, bes_score))
    
    # 12. Immune Resiliency Score (IRS)
    irs_score = 0.40 * inputs.TSCM + 0.30 * vrs_score + 0.30 * ls_score
    irs_score = max(0.0, min(100.0, irs_score))
    
    # 13. Immune Decline Risk Score (IDRS)
    inflammation_risk = 100.0 - is_score
    immune_age_gap_risk = max(0.0, min(100.0, (immune_age_gap + 20.0) / 40.0 * 100.0))
    bmi_risk = 100.0 - inputs.BMI_Score
    smoking_risk = inputs.Smoking_Score
    comorbidity_risk = inputs.Comorbidity_Score
    
    idrs_score = (
        0.30 * inflammation_risk +
        0.25 * immune_age_gap_risk +
        0.15 * bmi_risk +
        0.15 * smoking_risk +
        0.15 * comorbidity_risk
    )
    idrs_score = max(0.0, min(100.0, idrs_score))
    
    # 14. Immune Health Index (IHI)
    ihi_score = 0.40 * imqs_score + 0.30 * (100.0 - idrs_score) + 0.30 * bes_score
    ihi_score = max(0.0, min(100.0, ihi_score))
    
    # IDI and UPS calculations (if banked session info is provided)
    idi_score = None
    ups_score = None
    
    if (banked_immune_age is not None and 
        banked_imqs is not None and 
        banked_tscm is not None and 
        banked_irs is not None):
        
        # DeltaImmuneAge = CurrentImmuneAge - BankedImmuneAge
        delta_immune_age = inputs.ImmuneAge - banked_immune_age
        delta_immune_age_score = max(0.0, min(100.0, (delta_immune_age / 20.0) * 100.0))
        
        # DeltaIMQS = BankedIMQS - CurrentIMQS
        delta_imqs = banked_imqs - imqs_score
        if delta_imqs < 0.0:
            delta_imqs = 0.0
            
        # IDI = 0.50(DeltaImmuneAge) + 0.30(DeltaIMQS) + 0.20(TimeSinceBankingFactor)
        idi_score = 0.50 * delta_immune_age_score + 0.30 * delta_imqs + 0.20 * inputs.TimeSinceBankingFactor
        idi_score = max(0.0, min(100.0, idi_score))
        
        # UPS = 0.40(CurrentIMQS-BankedIMQS) + 0.30(CurrentTSCM-BankedTSCM) + 0.30(CurrentIRS-BankedIRS)
        ups_score = (
            0.40 * (imqs_score - banked_imqs) + 
            0.30 * (inputs.TSCM - banked_tscm) + 
            0.30 * (irs_score - banked_irs)
        )
    
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
        IDI=idi_score,
        UPS=ups_score,
        IRS=irs_score,
        IHI=ihi_score
    )
