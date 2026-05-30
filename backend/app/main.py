"""
EcoRestore Somalia backend (FastAPI).

Goal for MVP:
- Load district indicator data
- Compute Priority Score + risk category
- Recommend intervention package + expected impact
- Serve a tiny dashboard frontend (optional)

This file is intentionally kept as a scaffold with TODOs so the team can
fill in implementation during the hackathon.
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="EcoRestore Somalia API", version="0.0.1")

# TODO: (optional) serve the static frontend in `../frontend/`
# - mount StaticFiles for `/assets`
# - return `frontend/index.html` on `/`

# TODO: implement API routes the frontend can call:
# - GET `/api/districts` -> list districts with computed `priorityScore` + `riskCategory`
# - GET `/api/districts/{id}` -> one district + computed fields
# - GET `/api/districts/{id}/package` -> recommendations + impact + actionPlan
# - POST `/api/score` -> compute score for custom weights / indicators

