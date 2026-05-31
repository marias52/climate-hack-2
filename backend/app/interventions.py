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
    """Return a list of intervention packages based on simple threshold rules."""
    def num(key: str) -> float:
        try:
            return float(indicators.get(key, 0.0))
        except Exception:
            return 0.0

    forest = num("forestLoss")
    charcoal = num("charcoalPressure")
    land = num("landDegradation")

    picks: list[Intervention] = []

    # Minimal catalog (kept inline for hackathon speed).
    def add(item: Intervention) -> None:
        if item["id"] not in {p["id"] for p in picks}:
            picks.append(item)

    if charcoal >= 70:
        add(
            {
                "id": "cookstoves",
                "title": "Efficient cookstoves",
                "tags": ["energy", "charcoal"],
                "rationale": ["High charcoal pressure suggests demand-side reduction.", "Quick-to-deploy household impact."],
            }
        )

    if forest >= 70:
        add(
            {
                "id": "reforestation",
                "title": "Reforestation support",
                "tags": ["trees", "restoration"],
                "rationale": ["High forest loss indicates restoration need.", "Pair with protection for best results."],
            }
        )

    if land >= 70:
        add(
            {
                "id": "soil_water",
                "title": "Water harvesting & soil bunds",
                "tags": ["land", "drought"],
                "rationale": ["High land degradation benefits from soil/water structures.", "Improves drought resilience."],
            }
        )

    # If multiple factors are high, add a community woodlots package to reduce pressure.
    high_count = sum([charcoal >= 70, forest >= 70, land >= 70])
    if high_count >= 2:
        add(
            {
                "id": "woodlots",
                "title": "Community woodlots",
                "tags": ["trees", "livelihoods"],
                "rationale": ["Combined risk suggests a bundled approach.", "Creates local fuelwood supply and reduces cutting."],
            }
        )

    return picks[:4]
