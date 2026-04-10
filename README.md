# zkTransact — Privacy-Preserving Fraud Ring Detection

Graph-based fraud detection system that identifies cross-merchant fraud rings while preserving privacy through SHA-256 hashing of all PII.

## Architecture

```
React Frontend (Cytoscape.js)
        ↓
FastAPI Backend
        ↓
NetworkX Graph (in-memory)  +  SQLite (alerts)
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Seed demo data
python scripts/generate_demo_data.py
# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/transaction` | Ingest a transaction (PII auto-hashed) |
| GET | `/api/v1/alerts` | List all fraud alerts |
| GET | `/api/v1/alerts/{id}` | Alert detail + explanation |
| GET | `/api/v1/graph/{account_id}` | N-hop subgraph for visualization |
| GET | `/api/v1/stats` | Dashboard statistics |

## Fraud Detection Rules

- **Shared Device**: Multiple accounts using the same device fingerprint
- **Velocity Anomaly**: High transaction frequency from a single account
- **Cycle Detection**: Circular money flow patterns (A→B→C→A)
- **Fan-out**: Single account transacting at unusually many merchants

## Tech Stack

- **Backend**: Python, FastAPI, NetworkX, SQLite
- **Frontend**: React, TypeScript, Cytoscape.js, Recharts
- **Privacy**: SHA-256 hashing — zero raw PII in the system
# neofuture
