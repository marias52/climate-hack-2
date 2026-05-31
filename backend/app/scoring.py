"""
Priority scoring utilities.

Add your scoring logic here.

Suggested MVP formula (0-100 output):
- 0.35 * forestLoss
- 0.30 * charcoalPressure
- 0.25 * landDegradation
- 0.10 * communityVulnerability

All indicator inputs should be normalized to 0-100 first.
"""

from __future__ import annotations

from .typing import RiskCategory, ScoreWeights

DEFAULT_WEIGHTS: ScoreWeights = {
    "forestLoss": 0.35,
    "charcoalPressure": 0.30,
    "landDegradation": 0.25,
    "communityVulnerability": 0.10,
}


def normalize_weights(weights: ScoreWeights) -> ScoreWeights:
    """Normalize weights so they sum to 1.0 (fallback to defaults if sum is 0)."""
    w1 = max(0.0, float(weights.get("forestLoss", 0.0)))
    w2 = max(0.0, float(weights.get("charcoalPressure", 0.0)))
    w3 = max(0.0, float(weights.get("landDegradation", 0.0)))
    w4 = max(0.0, float(weights.get("communityVulnerability", 0.0)))
    total = w1 + w2 + w3 + w4
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)
    return {
        "forestLoss": w1 / total,
        "charcoalPressure": w2 / total,
        "landDegradation": w3 / total,
        "communityVulnerability": w4 / total,
    }


def compute_priority_score(indicators: dict, weights: ScoreWeights | None = None) -> float:
    """Return a 0-100 score based on indicators and weights (all indicator values are 0-100)."""
    w = normalize_weights(weights or DEFAULT_WEIGHTS)

    def clamp100(x: float) -> float:
        try:
            n = float(x)
        except Exception:
            n = 0.0
        return max(0.0, min(100.0, n))

    forest = clamp100(indicators.get("forestLoss", 0.0)) / 100.0
    charcoal = clamp100(indicators.get("charcoalPressure", 0.0)) / 100.0
    land = clamp100(indicators.get("landDegradation", 0.0)) / 100.0
    community = clamp100(indicators.get("communityVulnerability", 0.0)) / 100.0

    score01 = (
        w["forestLoss"] * forest
        + w["charcoalPressure"] * charcoal
        + w["landDegradation"] * land
        + w["communityVulnerability"] * community
    )
    return max(0.0, min(100.0, score01 * 100.0))


def categorize_risk(score: float) -> RiskCategory:
    """
    Map a 0-100 Priority Score to a risk bucket.

    Hackathon-friendly thresholds (tune later):
    - Critical: 85-100
    - High: 70-84.99
    - Medium: 50-69.99
    - Low: 0-49.99
    """
    try:
        s = float(score)
    except Exception:
        s = 0.0

    if s >= 85:
        return "Critical"
    if s >= 70:
        return "High"
    if s >= 50:
        return "Medium"
    return "Low"
