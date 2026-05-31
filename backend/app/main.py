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


def _slugify(text: str) -> str:
    t = text.strip().lower().replace("_", "-")
    t = re.sub(r"[^a-z0-9-]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t or "unknown"


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
        for r in reader:
            name = (r.get("district") or "").strip()
            region = (r.get("region") or "").strip()
            out.append(
                {
                    "id": _slugify(name),
                    "name": name,
                    "region": region,
                    "charcoalPressure": float(r.get("charcoal_pressure") or 0),
                    "forestLoss": float(r.get("forest_loss") or 0),
                    "landDegradation": float(r.get("land_degradation") or 0),
                    "communityVulnerability": float(r.get("vulnerability") or 0),
                }
            )
    return out


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
    rows = _load_rows()
    weights = normalize_weights(DEFAULT_WEIGHTS)
    enriched: list[dict[str, Any]] = []
    for d in rows:
        score = compute_priority_score(d, weights)
        enriched.append({**d, "priorityScore": score, "riskCategory": categorize_risk(score)})
    enriched.sort(key=lambda x: float(x["priorityScore"]), reverse=True)
    return {"districts": enriched, "weights": weights}


@app.get("/api/districts/{district_id}")
def get_district(district_id: str) -> dict[str, Any]:
    d = next((x for x in _load_rows() if x["id"] == district_id), None)
    if not d:
        raise HTTPException(status_code=404, detail="district not found")
    score = compute_priority_score(d, DEFAULT_WEIGHTS)
    return {**d, "priorityScore": score, "riskCategory": categorize_risk(score)}


@app.get("/api/districts/{district_id}/package")
def get_package(district_id: str) -> dict[str, Any]:
    d = next((x for x in _load_rows() if x["id"] == district_id), None)
    if not d:
        raise HTTPException(status_code=404, detail="district not found")
    score = compute_priority_score(d, DEFAULT_WEIGHTS)
    recs = recommend_interventions(d)
    impact = forecast_impact(d, recs)
    return {
        "district": {**d, "priorityScore": score, "riskCategory": categorize_risk(score)},
        "recommendations": recs,
        "impact": impact,
        "actionPlan": {
            "target": f'{d["name"]} ({d["region"]})',
            "risk": categorize_risk(score),
            "score": score,
            "package": " + ".join([r["title"] for r in recs]) if recs else "No package",
            "firstSteps": "Coordinate district assessment, validate drivers, confirm community priorities, and deploy a pilot package.",
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
