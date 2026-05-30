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

from .types import RiskCategory, ScoreWeights

DEFAULT_WEIGHTS: ScoreWeights = {
    "forestLoss": 0.35,
    "charcoalPressure": 0.30,
    "landDegradation": 0.25,
    "communityVulnerability": 0.10,
}


def normalize_weights(weights: ScoreWeights) -> ScoreWeights:
    """TODO: Normalize weights so they sum to 1.0."""
    return weights


def compute_priority_score(indicators: dict, weights: ScoreWeights | None = None) -> float:
    """TODO: Return a 0-100 score based on indicators and weights."""
    _ = (indicators, weights)
    return 0.0


def categorize_risk(score: float) -> RiskCategory:
    """TODO: Map 0-100 score into Low/Medium/High/Critical."""
    _ = score
    return "Low"
