from __future__ import annotations

from typing import Literal, TypedDict

RiskCategory = Literal["Low", "Medium", "High", "Critical"]


class DistrictIndicators(TypedDict):
    id: str
    name: str
    region: str
    forestLoss: float  # 0-100
    charcoalPressure: float  # 0-100
    landDegradation: float  # 0-100
    communityVulnerability: float  # 0-100 (optional in data; default 0)


class ScoreWeights(TypedDict):
    forestLoss: float
    charcoalPressure: float
    landDegradation: float
    communityVulnerability: float


class Intervention(TypedDict):
    id: str
    title: str
    rationale: list[str]
    tags: list[str]


class ImpactForecast(TypedDict):
    charcoalDependenceDelta: float
    forestProtectionDelta: float
    landRestorationDelta: float
    resilienceDelta: float

