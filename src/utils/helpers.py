"""
Helper functions for data normalization, scaling, and conversion.
These utilities allow clinical lab units to be converted to the 0-100 scale
expected by the calculation engine.
"""

def _interpolate(val: float, points: list[tuple[float, float]]) -> float:
    """
    Perform linear interpolation for a value given a list of (x, y) coordinates sorted by x.
    """
    if val <= points[0][0]:
        return points[0][1]
    if val >= points[-1][0]:
        return points[-1][1]
        
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        if x1 <= val <= x2:
            return y1 + (val - x1) * (y2 - y1) / (x2 - x1)
            
    return points[-1][1]


def normalize_crp(value_mg_l: float) -> float:
    """
    Normalize CRP: >=10=0, 7=25, 5=50, 2=75, <=1=100
    """
    points = [(1.0, 100.0), (2.0, 75.0), (5.0, 50.0), (7.0, 25.0), (10.0, 0.0)]
    return _interpolate(value_mg_l, points)


def normalize_il6(value_pg_ml: float) -> float:
    """
    Normalize IL-6: >=20=0, 15=25, 10=50, 5=75, <=2=100
    """
    points = [(2.0, 100.0), (5.0, 75.0), (10.0, 50.0), (15.0, 25.0), (20.0, 0.0)]
    return _interpolate(value_pg_ml, points)


def normalize_tnfa(value_pg_ml: float) -> float:
    """
    Normalize TNF-a: >=20=0, 15=25, 10=50, 5=75, <=2=100
    """
    points = [(2.0, 100.0), (5.0, 75.0), (10.0, 50.0), (15.0, 25.0), (20.0, 0.0)]
    return _interpolate(value_pg_ml, points)


def normalize_cd4_cd8(ratio: float) -> float:
    """
    Normalize CD4/CD8 ratio: <=0.8=0, 1.0=25, 1.5=60, 2.0=85, >=2.5=100
    """
    points = [(0.8, 0.0), (1.0, 25.0), (1.5, 60.0), (2.0, 85.0), (2.5, 100.0)]
    return _interpolate(ratio, points)


def normalize_naive_t(value_pct: float) -> float:
    """
    Normalize Naive T Cells (%): <=10=0, 20=25, 30=50, 40=75, >=50=100
    """
    points = [(10.0, 0.0), (20.0, 25.0), (30.0, 50.0), (40.0, 75.0), (50.0, 100.0)]
    return _interpolate(value_pct, points)


def normalize_tscm(value_pct: float) -> float:
    """
    Normalize TSCM (%): <=2=0, 5=25, 8=50, 12=75, >=15=100
    """
    points = [(2.0, 0.0), (5.0, 25.0), (8.0, 50.0), (12.0, 75.0), (15.0, 100.0)]
    return _interpolate(value_pct, points)
