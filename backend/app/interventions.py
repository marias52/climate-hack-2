"""
Intervention recommendation rules.

Add "if indicator is high -> recommend X" rules here.

Example rules:
- high charcoalPressure -> efficient cookstoves
- high landDegradation -> reforestation + soil/water work
- loss of grazing land (proxy via landDegradation) -> grazing management
- multiple high factors -> combined package
"""

from __future__ import annotations

from .typing import Intervention


def recommend_interventions(indicators: dict) -> list[Intervention]:
    """TODO: Return a list of intervention packages based on indicator thresholds."""
    _ = indicators
    return []
