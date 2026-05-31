"""
EcoRestore Somalia backend (FastAPI).

This is a hackathon-friendly backend:
- Reads a simple CSV dataset from `app/data/raw/district_indicators.csv`
- Computes Priority Score + risk category
- Produces recommended intervention packages + impact forecast
- Serves the static frontend from `../frontend/`
"""

from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .impact import forecast_impact
from .interventions import recommend_interventions
from .scoring import DEFAULT_WEIGHTS, categorize_risk, compute_priority_score, normalize_weights

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"
CSV_PATH = Path(__file__).resolve().parent / "data" / "raw" / "district_indicators.csv"
REGION_POP_PATH = Path(__file__).resolve().parent / "data" / "raw" / "region_population.csv"

REQUIRED_COLUMNS = {
    "district",
    "region",
    "charcoal_pressure",
    "forest_loss",
    "land_degradation",
    "vulnerability",
}

REGION_POP_REQUIRED_COLUMNS = {"region", "population"}


def _slugify(text: str) -> str:
    t = text.strip().lower().replace("_", "-")
    t = re.sub(r"[^a-z0-9-]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t or "unknown"

def _to_float(value: Any, *, field: str, district: str) -> float:
    try:
        return float(value)
    except Exception as e:
        raise ValueError(f"Invalid number for `{field}` in district `{district}`: {value!r}") from e


def _clamp_0_100(value: float) -> float:
    return max(0.0, min(100.0, float(value)))

def _to_int(value: Any, *, field: str, region: str) -> int:
    try:
        # Allow floats that are whole numbers, but store as int.
        return int(float(value))
    except Exception as e:
        raise ValueError(f"Invalid integer for `{field}` in region `{region}`: {value!r}") from e


@lru_cache(maxsize=1)
def _load_rows() -> list[dict[str, Any]]:
    """
    Reads CSV with columns:
    `district,region,charcoal_pressure,forest_loss,land_degradation,vulnerability`

    Converts to internal names used by the app (0-100 values):
    - id, name, region
    - charcoalPressure, forestLoss, landDegradation, communityVulnerability
    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset missing: {CSV_PATH}")

    out: list[dict[str, Any]] = []
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row.")
        present = {h.strip() for h in reader.fieldnames if h}
        missing = sorted(REQUIRED_COLUMNS - present)
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

        seen_ids: set[str] = set()
        for r in reader:
            name = (r.get("district") or "").strip()
            if not name:
                # Skip blank rows rather than crashing the whole app.
                continue
            region = (r.get("region") or "").strip()

            row_id = _slugify(name)
            if row_id in seen_ids:
                raise ValueError(f"Duplicate district id `{row_id}` derived from district name `{name}`.")
            seen_ids.add(row_id)

            charcoal = _clamp_0_100(_to_float(r.get("charcoal_pressure"), field="charcoal_pressure", district=name))
            forest = _clamp_0_100(_to_float(r.get("forest_loss"), field="forest_loss", district=name))
            land = _clamp_0_100(_to_float(r.get("land_degradation"), field="land_degradation", district=name))
            vuln = _clamp_0_100(_to_float(r.get("vulnerability"), field="vulnerability", district=name))
            out.append(
                {
                    "id": row_id,
                    "name": name,
                    "region": region,
                    "charcoalPressure": charcoal,
                    "forestLoss": forest,
                    "landDegradation": land,
                    "communityVulnerability": vuln,
                }
            )
    return out


@lru_cache(maxsize=1)
def _load_region_population() -> dict[str, int]:
    """
    Reads CSV with columns:
    `region,population`

    Returns:
    - { "Lower Juba": 1199276, ... }
    """
    if not REGION_POP_PATH.exists():
        return {}

    with REGION_POP_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("region_population.csv has no header row.")
        present = {h.strip() for h in reader.fieldnames if h}
        missing = sorted(REGION_POP_REQUIRED_COLUMNS - present)
        if missing:
            raise ValueError(f"region_population.csv missing required columns: {', '.join(missing)}")

        out: dict[str, int] = {}
        for r in reader:
            region = (r.get("region") or "").strip()
            if not region:
                continue
            pop = _to_int(r.get("population"), field="population", region=region)
            if pop < 0:
                raise ValueError(f"Population cannot be negative for region `{region}`.")
            out[region] = pop
        return out


def _attach_population(d: dict[str, Any], region_pop: dict[str, int]) -> dict[str, Any]:
    rp = region_pop.get(d.get("region", ""), 0)
    vuln = float(d.get("communityVulnerability", 0.0) or 0.0)
    # Simple MVP heuristic: vulnerable share of region population.
    people_at_risk = int(round(rp * max(0.0, min(100.0, vuln)) / 100.0))
    return {**d, "regionPopulation": rp, "estimatedPeopleAtRisk": people_at_risk}


app = FastAPI(title="EcoRestore Somalia API", version="0.0.1")

@app.get("/")
def index() -> dict[str, str]:
    """
    When `frontend/dist/` exists (after `npm run build`), FastAPI serves the React app.
    During development, run the frontend dev server separately (`npm run dev`).
    """
    if DIST_DIR.exists():
        return {"status": "ok"}
    return {
        "status": "ok",
        "message": "Backend running. Start the React frontend with `cd frontend && npm install && npm run dev`.",
    }


@app.get("/api/districts")
def list_districts() -> dict[str, Any]:
    try:
        rows = _load_rows()
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    try:
        region_pop = _load_region_population()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    weights = normalize_weights(DEFAULT_WEIGHTS)
    enriched: list[dict[str, Any]] = []
    for d in rows:
        score = compute_priority_score(d, weights)
        base = _attach_population(d, region_pop)
        enriched.append({**base, "priorityScore": score, "riskCategory": categorize_risk(score)})
    enriched.sort(key=lambda x: float(x["priorityScore"]), reverse=True)
    return {"districts": enriched, "weights": weights}


@app.get("/api/districts/{district_id}")
def get_district(district_id: str) -> dict[str, Any]:
    try:
        rows = _load_rows()
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    try:
        region_pop = _load_region_population()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    d = next((x for x in rows if x["id"] == district_id), None)
    if not d:
        raise HTTPException(status_code=404, detail="district not found")
    score = compute_priority_score(d, DEFAULT_WEIGHTS)
    base = _attach_population(d, region_pop)
    return {**base, "priorityScore": score, "riskCategory": categorize_risk(score)}


@app.get("/api/districts/{district_id}/package")
def get_package(district_id: str) -> dict[str, Any]:
    try:
        rows = _load_rows()
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    try:
        region_pop = _load_region_population()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    d = next((x for x in rows if x["id"] == district_id), None)
    if not d:
        raise HTTPException(status_code=404, detail="district not found")
    base = _attach_population(d, region_pop)
    score = compute_priority_score(d, DEFAULT_WEIGHTS)
    recs = recommend_interventions(base)
    impact = forecast_impact(base, recs)
    return {
        "district": {**base, "priorityScore": score, "riskCategory": categorize_risk(score)},
        "recommendations": recs,
        "impact": impact,
        "actionPlan": {
            "target": f'{base["name"]} ({base["region"]})',
            "risk": categorize_risk(score),
            "score": score,
            "package": " + ".join([r["title"] for r in recs]) if recs else "No package",
            "firstSteps": "Coordinate district assessment, validate drivers, confirm community priorities, and deploy a pilot package.",
            "estimatedPeopleAtRisk": base["estimatedPeopleAtRisk"],
        },
    }


@app.post("/api/score")
def score(payload: dict[str, Any]) -> dict[str, Any]:
    indicators = payload.get("indicators")
    if not isinstance(indicators, dict):
        raise HTTPException(status_code=400, detail="payload.indicators must be an object")
    weights = payload.get("weights") or DEFAULT_WEIGHTS
    if not isinstance(weights, dict):
        raise HTTPException(status_code=400, detail="payload.weights must be an object")
    score_val = compute_priority_score(indicators, weights)
    return {"priorityScore": score_val, "riskCategory": categorize_risk(score_val), "weights": normalize_weights(weights)}


# If the React app has been built, serve it from `frontend/dist/`.
# NOTE: This mount is added last so `/api/...` routes win.
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="frontend")
