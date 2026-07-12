"""
Helper functions for data normalization, scaling, and conversion.
These utilities allow clinical lab units to be converted to the 0-100 scale
expected by the calculation engine.
"""

def normalize_crp(value_mg_l: float) -> float:
    """
    Normalize C-Reactive Protein (CRP) from mg/L to a 0-100 scale.
    - Optimal: < 1.0 mg/L (Score: 0 - 15)
    - Average: 1.0 - 3.0 mg/L (Score: 15 - 40)
    - High Risk: 3.0 - 10.0 mg/L (Score: 40 - 80)
    - Severe: > 10.0 mg/L (Score: 80 - 100)
    """
    if value_mg_l <= 0.0:
        return 0.0
    if value_mg_l < 1.0:
        # Map [0, 1) to [0, 15)
        return value_mg_l * 15.0
    elif value_mg_l <= 3.0:
        # Map [1, 3] to [15, 40]
        return 15.0 + (value_mg_l - 1.0) * (25.0 / 2.0)
    elif value_mg_l <= 10.0:
        # Map [3, 10] to [40, 80]
        return 40.0 + (value_mg_l - 3.0) * (40.0 / 7.0)
    else:
        # Map > 10 to [80, 100] capped at 30 mg/L
        capped = min(value_mg_l, 30.0)
        return 80.0 + (capped - 10.0) * (20.0 / 20.0)


def normalize_il6(value_pg_ml: float) -> float:
    """
    Normalize Interleukin-6 (IL-6) from pg/mL to 0-100.
    - Normal: < 2.0 pg/mL (Score: 0 - 20)
    - Elevated: 2.0 - 10.0 pg/mL (Score: 20 - 60)
    - High: > 10.0 pg/mL (Score: 60 - 100)
    """
    if value_pg_ml <= 0.0:
        return 0.0
    if value_pg_ml < 2.0:
        return value_pg_ml * 10.0
    elif value_pg_ml <= 10.0:
        return 20.0 + (value_pg_ml - 2.0) * (40.0 / 8.0)
    else:
        capped = min(value_pg_ml, 50.0)
        return 60.0 + (capped - 10.0) * (40.0 / 40.0)


def normalize_tnfa(value_pg_ml: float) -> float:
    """
    Normalize TNF-alpha from pg/mL to 0-100.
    - Normal: < 3.0 pg/mL (Score: 0 - 20)
    - Elevated: 3.0 - 15.0 pg/mL (Score: 20 - 70)
    - High: > 15.0 pg/mL (Score: 70 - 100)
    """
    if value_pg_ml <= 0.0:
        return 0.0
    if value_pg_ml < 3.0:
        return value_pg_ml * (20.0 / 3.0)
    elif value_pg_ml <= 15.0:
        return 20.0 + (value_pg_ml - 3.0) * (50.0 / 12.0)
    else:
        capped = min(value_pg_ml, 50.0)
        return 70.0 + (capped - 15.0) * (30.0 / 35.0)


def normalize_cd4_cd8(ratio: float) -> float:
    """
    Normalize CD4/CD8 ratio (typical healthy reference is 1.0 - 4.0) to a 0-100 score.
    Higher score represents healthier/optimal balance, lower score represents risk of immune senescence or inversion.
    - Optimal: 1.5 - 2.5 (Score: 80 - 100)
    - Acceptable: 1.0 - 1.5 or 2.5 - 4.0 (Score: 40 - 80)
    - Out of range: < 1.0 (inverted) or > 4.0 (Score: 0 - 40)
    """
    if ratio <= 0.0:
        return 0.0
    elif ratio < 1.0:
        # Inverted ratio, high risk
        return ratio * 40.0
    elif ratio <= 1.5:
        # Low normal
        return 40.0 + (ratio - 1.0) * 80.0 # 1.0 -> 40, 1.5 -> 80
    elif ratio <= 2.5:
        # Optimal peak
        return 100.0 - abs(ratio - 2.0) * 20.0 # 2.0 -> 100, 1.5/2.5 -> 90
    elif ratio <= 4.0:
        # High normal
        return 90.0 - (ratio - 2.5) * (50.0 / 1.5) # 2.5 -> 90, 4.0 -> 40
    else:
        # Abnormally high
        capped = min(ratio, 10.0)
        return max(0.0, 40.0 - (capped - 4.0) * (40.0 / 6.0))
