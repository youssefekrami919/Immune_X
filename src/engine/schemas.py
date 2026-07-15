from pydantic import BaseModel, Field
from typing import Optional

class ImmuneInputs(BaseModel):
    # Biomarkers & Lab Results (7)
    CRP: float = Field(..., ge=0.0, le=100.0, description="C-Reactive Protein score (0-100)")
    IL6: float = Field(..., ge=0.0, le=100.0, description="Interleukin-6 score (0-100)")
    TNFa: float = Field(..., ge=0.0, le=100.0, description="Tumor Necrosis Factor-alpha score (0-100)")
    TSCM: float = Field(..., ge=0.0, le=100.0, description="T Memory Stem Cells score (0-100)")
    TCRD: float = Field(..., ge=0.0, le=100.0, description="T-cell Receptor Diversity score (0-100)")
    CD4_CD8_Ratio: float = Field(..., ge=0.0, le=100.0, description="CD4/CD8 Ratio Score (0-100)")
    NaiveT: float = Field(..., ge=0.0, le=100.0, description="Naive T Cell Score (0-100)")

    # Demographics & Lifestyle (7)
    Age: float = Field(..., ge=0.0, le=120.0, description="Chronological Age in years")
    Expected_Lifespan: float = Field(..., ge=1.0, le=120.0, description="Expected Lifespan in years")
    BMI_Score: float = Field(..., ge=0.0, le=100.0, description="Body Mass Index score (0-100)")
    Smoking_Score: float = Field(..., ge=0.0, le=100.0, description="Smoking score (0-100, where 0 is healthiest/non-smoker)")
    Exercise_Score: float = Field(..., ge=0.0, le=100.0, description="Exercise activity score (0-100)")
    Sleep_Score: float = Field(..., ge=0.0, le=100.0, description="Sleep quality score (0-100)")
    Comorbidity_Score: float = Field(..., ge=0.0, le=100.0, description="Comorbidity presence score (0-100, where 0 is none)")

    # Medical History (6)
    Antibody_Response: float = Field(..., ge=0.0, le=100.0, description="Vaccine antibody response (0-100)")
    T_cell_Response: float = Field(..., ge=0.0, le=100.0, description="Vaccine T-cell response (0-100)")
    Response_Durability: float = Field(..., ge=0.0, le=100.0, description="Vaccine response durability (0-100)")
    Metabolic_Score: float = Field(..., ge=0.0, le=100.0, description="Metabolic health score (0-100)")
    Cardiovascular_Score: float = Field(..., ge=0.0, le=100.0, description="Cardiovascular health score (0-100)")
    Immune_Health_Base_Score: float = Field(..., ge=0.0, le=100.0, description="Base immune health score (0-100)")

    # AI / Historical Data (4)
    ImmuneAge: float = Field(..., ge=0.0, le=120.0, description="Estimated Biological Immune Age in years")
    DeltaImmuneAge: float = Field(..., ge=-100.0, le=100.0, description="Change in biological immune age since last test")
    DeltaIMQS: float = Field(..., ge=-100.0, le=100.0, description="Change in Immune Memory Quality Score since last test")
    TimeSinceBankingFactor: float = Field(10.0, ge=0.0, le=100.0, description="Time since last banking factor (0-100)")


class ImmuneOutputs(BaseModel):
    # Supporting Equations
    InflammationScore: float = Field(..., description="IS: 0.40*CRP + 0.30*IL6 + 0.30*TNFa")
    LifestyleScore: float = Field(..., description="LS: 0.30*Exercise_Score + 0.30*Sleep_Score + 0.20*BMI_Score + 0.20*Smoking_Score")
    VaccineResponseScore: float = Field(..., description="VRS: 0.50*Antibody_Response + 0.30*T_cell_Response + 0.20*Response_Durability")
    HealthScore: float = Field(..., description="HS: 0.35*Metabolic_Score + 0.35*Cardiovascular_Score + 0.30*Immune_Health_Base_Score")
    AgeFactor: float = Field(..., description="AF: 100 - ((Age / Expected_Lifespan) * 100)")

    # Core Equations
    ImmuneAgeGap: float = Field(..., description="ImmuneAgeGap: ImmuneAge - ChronologicalAge")
    IMQS: float = Field(..., description="Immune Memory Quality Score")
    BES: float = Field(..., description="Biobanking Eligibility Score")
    IDRS: float = Field(..., description="Immune Decline Risk Score")
    IDI: Optional[float] = Field(None, description="Immune Decline Index")
    UPS: Optional[float] = Field(None, description="Upgrade Potential Score")
    IRS: float = Field(..., description="Immune Resiliency Score")
    IHI: float = Field(..., description="Immune Health Index")
