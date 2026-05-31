# EcoRestore Somalia React Dashboard

This is a separate React/Vite frontend for the EcoRestore Somalia MVP. It lives beside the existing static frontend and does not change the backend.

## Run the React Frontend

1. Open a terminal from the repo root.
2. Install dependencies:

   ```bash
   cd frontend/react-ui
   npm install
   ```

3. Start the Vite dev server:

   ```bash
   npm run dev
   ```

4. Open the local Vite URL, usually:

   ```text
   http://localhost:5173
   ```

## Optional Backend

The React dashboard currently uses mock data inside `src/main.jsx`, so the backend is not required for the UI preview.

To run the existing API separately:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## What Is Included

- Dark logistics/map-inspired dashboard styling
- Left district priority list with search
- Somalia priority heatmap placeholder with clickable district markers
- Right analytics panel for score, risk indicators, recommendation, and predicted impact
- Mock data for forest loss, population impact, charcoal dependency, recovery potential, drought stress, priority score, risk level, intervention package, and predicted impact
