"""
Impact forecasting (very simple MVP).

This can be:
- heuristic rules (fast to demo), or
- a model-based forecast later.

Recommended output fields (percent-point deltas):
- charcoalDependenceDelta
- forestProtectionDelta
- landRestorationDelta
- resilienceDelta
"""

from __future__ import annotations

from .typing import ImpactForecast, Intervention


def forecast_impact(indicators: dict, interventions: list[Intervention]) -> ImpactForecast:
    """Return a small, explainable impact forecast (heuristic, percent-point deltas)."""
    ids = {i["id"] for i in interventions}

    def num(key: str) -> float:
        try:
            return float(indicators.get(key, 0.0))
        except Exception:
            return 0.0

    # Baselines: higher risk -> more "headroom" for improvement
    charcoal = 5 + (num("charcoalPressure") / 100.0) * 10
    forest = 4 + (num("forestLoss") / 100.0) * 10
    land = 4 + (num("landDegradation") / 100.0) * 10
    resilience = 3 + (num("communityVulnerability") / 100.0) * 8

    if "cookstoves" in ids:
        charcoal += 8
    if "reforestation" in ids:
        forest += 8
    if "soil_water" in ids:
        land += 8
        resilience += 3
    if "woodlots" in ids:
        forest += 3
        charcoal += 3

    # Cap to keep numbers believable for MVP.
    def clamp(x: float) -> float:
        return max(-35.0, min(35.0, float(x)))

    return {
        "charcoalDependenceDelta": clamp(charcoal),
        "forestProtectionDelta": clamp(forest),
        "landRestorationDelta": clamp(land),
        "resilienceDelta": clamp(resilience),
    }
