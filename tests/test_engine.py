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
        DeltaIMQS=3.5
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
    
    # 7. IMQS = 0.25(80) + 0.20(75) + 0.15(70) + 0.10(85) + 0.10(84) + 0.10(14.5) + 0.05(61.5) + 0.05(62.5)
    # = 20.0 + 15.0 + 10.5 + 8.5 + 8.4 + 1.45 + 3.075 + 3.125 = 70.05
    assert outputs.IMQS == pytest.approx(70.05)
    
    # 8. BES = 0.60(70.05) + 0.20(89.75) + 0.20(62.5) = 42.03 + 17.95 + 12.5 = 72.48
    assert outputs.BES == pytest.approx(72.48)
    
    # 9. IDRS = 0.30(14.5) + 0.25(-2.0) + 0.15(60) + 0.15(0) + 0.15(10)
    # = 4.35 - 0.50 + 9.0 + 0 + 1.5 = 14.35
    assert outputs.IDRS == pytest.approx(14.35)
    
    # 10. Re-Banking Index = 0.50(-1.5) + 0.30(3.5) + 0.20(14.35)
    # = -0.75 + 1.05 + 2.87 = 3.17
    assert outputs.ReBankingIndex == pytest.approx(3.17)
    
    # 11. IHI = 0.40(70.05) + 0.30(100 - 14.35) + 0.30(72.48) = 28.02 + 25.695 + 21.744 = 75.459
    assert outputs.IHI == pytest.approx(75.459)

def test_pydantic_validation():
    inputs = get_default_inputs()
    
    # Test boundary limits
    with pytest.raises(ValidationError):
        inputs.CRP = -1.0 # Out of bounds (ge=0.0)
        ImmuneInputs(**inputs.model_dump())
        
    with pytest.raises(ValidationError):
        inputs.CRP = 101.0 # Out of bounds (le=100.0)
        ImmuneInputs(**inputs.model_dump())

    with pytest.raises(ValidationError):
        inputs.Age = 125.0 # Out of bounds (le=120.0)
        ImmuneInputs(**inputs.model_dump())
