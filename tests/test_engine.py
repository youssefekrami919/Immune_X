import pytest
from pydantic import ValidationError
from src.engine.schemas import ImmuneInputs
from src.engine.calculations import calculate_immune_metrics

def get_default_inputs():
    return ImmuneInputs(
        CRP=10.0,
        IL6=15.0,
        TNFa=20.0,
        TSCM=80.0,
        TCRD=75.0,
        CD4_CD8_Ratio=70.0,
        NaiveT=85.0,
        Age=30.0,
        Expected_Lifespan=80.0,
        BMI_Score=60.0,
        Smoking_Score=0.0,
        Exercise_Score=80.0,
        Sleep_Score=85.0,
        Comorbidity_Score=10.0,
        Antibody_Response=90.0,
        T_cell_Response=80.0,
        Response_Durability=75.0,
        Metabolic_Score=85.0,
        Cardiovascular_Score=90.0,
        Immune_Health_Base_Score=95.0,
        ImmuneAge=28.0,
        DeltaImmuneAge=-1.5,
        DeltaIMQS=3.5,
        TimeSinceBankingFactor=10.0
    )

def test_engine_calculations():
    inputs = get_default_inputs()
    outputs = calculate_immune_metrics(inputs)
    
    # 1. Inflammation Score = 0.40(10) + 0.30(15) + 0.30(20) = 4.0 + 4.5 + 6.0 = 14.5
    assert outputs.InflammationScore == pytest.approx(14.5)
    
    # 2. Lifestyle Score = 0.30(80) + 0.30(85) + 0.20(60) + 0.20(0) = 24.0 + 25.5 + 12.0 + 0 = 61.5
    assert outputs.LifestyleScore == pytest.approx(61.5)
    
    # 3. Vaccine Response Score = 0.50(90) + 0.30(80) + 0.20(75) = 45 + 24 + 15 = 84.0
    assert outputs.VaccineResponseScore == pytest.approx(84.0)
    
    # 4. Health Score = 0.35(85) + 0.35(90) + 0.30(95) = 29.75 + 31.5 + 28.5 = 89.75
    assert outputs.HealthScore == pytest.approx(89.75)
    
    # 5. Age Factor = 100 - ((30 / 80) * 100) = 100 - 37.5 = 62.5
    assert outputs.AgeFactor == pytest.approx(62.5)
    
    # 6. ImmuneAgeGap = 28.0 - 30.0 = -2.0
    assert outputs.ImmuneAgeGap == pytest.approx(-2.0)
    
    # 7. IMQS check
    # balance_factor = (0.5 * 85.0 + 0.3 * 70.0 + 0.2 * 14.5) / 100.0 = 0.664
    # adjusted_tscm = 80.0 * 0.664 = 53.12
    # imqs = 0.30(53.12) + 0.20(75) + 0.15(70) + 0.10(85) + 0.10(84) + 0.10(14.5) + 0.05(61.5)
    # = 15.936 + 15.0 + 10.5 + 8.5 + 8.4 + 1.45 + 3.075 = 62.861
    assert outputs.IMQS == pytest.approx(62.861)
    
    # 8. BES check
    # age_score = 100 (for Age <= 30)
    # bes = 0.50(62.861) + 0.20(89.75) + 0.30(100) = 31.4305 + 17.95 + 30.0 = 79.3805
    assert outputs.BES == pytest.approx(79.3805)
    
    # 9. IDRS check
    # inflammation_risk = 100 - 14.5 = 85.5
    # immune_age_gap_risk = (18.0 / 40.0 * 100) = 45.0
    # idrs = 0.30(85.5) + 0.25(45) + 0.15(40) + 0.15(0) + 0.15(10) = 25.65 + 11.25 + 6 + 0 + 1.5 = 44.4
    assert outputs.IDRS == pytest.approx(44.4)
    
    # 10. IRS check
    # irs = 0.40(80) + 0.30(84) + 0.30(61.5) = 32 + 25.2 + 18.45 = 75.65
    assert outputs.IRS == pytest.approx(75.65)
    
    # 11. IHI check
    # ihi = 0.40(62.861) + 0.30(100 - 44.4) + 0.30(79.3805) = 25.1444 + 16.68 + 23.81415 = 65.63855
    assert outputs.IHI == pytest.approx(65.63855)

def test_decline_and_upgrade_indices():
    inputs = get_default_inputs()
    # Pass banked sample data
    outputs = calculate_immune_metrics(
        inputs,
        banked_immune_age=30.0,
        banked_imqs=60.0,
        banked_tscm=75.0,
        banked_irs=70.0
    )
    
    # delta_immune_age = 28 - 30 = -2 -> delta_immune_age_score = 0.0
    # delta_imqs = 60.0 - 62.861 = -2.861 -> clamped to 0.0
    # IDI = 0.50(0) + 0.30(0) + 0.20(10.0) = 2.0
    assert outputs.IDI == pytest.approx(2.0)
    
    # UPS = 0.40(62.861 - 60) + 0.30(80 - 75) + 0.30(75.65 - 70) = 1.1444 + 1.5 + 1.695 = 4.3394
    assert outputs.UPS == pytest.approx(4.3394)

def test_pydantic_validation():
    inputs = get_default_inputs()
    
    with pytest.raises(ValidationError):
        inputs.CRP = -1.0
        ImmuneInputs(**inputs.model_dump())
        
    with pytest.raises(ValidationError):
        inputs.CRP = 101.0
        ImmuneInputs(**inputs.model_dump())

    with pytest.raises(ValidationError):
        inputs.Age = 125.0
        ImmuneInputs(**inputs.model_dump())
