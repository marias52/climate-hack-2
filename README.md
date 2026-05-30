# EcoRestore Somalia (Hackathon MVP)

EcoRestore Somalia is an AI-powered decision-support dashboard that helps NGOs prioritize environmental interventions across Somali districts by combining multiple risk factors into a single Priority Score and generating recommended intervention packages.

This repo is split into:
- `backend/` FastAPI API (Python, managed with `uv`)
- `frontend/` static dashboard (HTML/CSS/JS) that calls the API

## What This MVP Does
- Loads mock environmental indicator data for Somali districts
- Calculates a `Priority Score (0-100)` from weighted indicators
- Categorizes risk: `Low`, `Medium`, `High`, `Critical`
- Recommends intervention packages based on rule logic
- Shows a simple NGO-facing decision dashboard

## Priority Score Formula
Default weights:
- `0.35` Forest Loss
- `0.30` Charcoal Pressure
- `0.25` Land Degradation
- `0.10` Community Vulnerability (optional; mocked here)

## Run Locally (Python)
1. Start the API:
   - `cd backend`
   - `uv sync`
   - `uv run uvicorn app.main:app --reload --port 8000`
2. Open the dashboard:
   - `http://localhost:8000`

## Key Files
- `backend/app/data/districts.mock.json` mock district indicators
- `backend/app/scoring.py` priority score + risk categories
- `backend/app/interventions.py` intervention rules + packages
- `backend/app/impact.py` simple impact forecasting (heuristic)
- `frontend/index.html` dashboard shell
- `frontend/assets/app.js` dashboard logic
- `frontend/assets/styles.css` styling
