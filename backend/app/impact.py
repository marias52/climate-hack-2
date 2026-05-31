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
    """TODO: Return a small, explainable impact forecast for the recommended package."""
    _ = (indicators, interventions)
    return {
        "charcoalDependenceDelta": 0.0,
        "forestProtectionDelta": 0.0,
        "landRestorationDelta": 0.0,
        "resilienceDelta": 0.0,
    }
