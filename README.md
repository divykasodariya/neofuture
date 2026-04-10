# zkTransact — Privacy-Preserving Fraud Ring Detection

zkTransact is a comprehensive full-stack fraud detection system designed to identify hidden cross-merchant fraud rings, account takeovers, and money mules while strictly preserving user privacy.

## How the Application Functions

The system is built on a **Zero-Knowledge** philosophy for PII (Personally Identifiable Information).

1. **Ingestion & Privacy**: Transactions are ingested via a REST API. Before any data enters the processing engine, attributes like Account IDs, Merchant IDs, and Device Fingerprints are **irreversibly hashed** using SHA-256 with a secure salt.
2. **In-Memory Analytics**: The hashed data forms a continuous data stream that is mapped into an interactive in-memory graph.
3. **Automated Detection**: A background detection engine recursively scans the graph to identify anomalous behavioral topographies and surfaces them as **Alerts**.
4. **Cinematic Dashboard**: A high-end React frontend visualizes both network-wide statistics and node-specific relationships to allow investigators to act upon the generated alerts.

## The Graph Mechanics Explained

The core of zkTransact relies on a tripartite mathematical graph constructed using Python's `NetworkX` library.

### Graph Topology
- **Nodes (Vertices)**: Represent three distinct entities in the financial ecosystem:
  - `Account`: The user initiating the transaction.
  - `Merchant`: The recipient of the transaction.
  - `Device`: The physical or virtual machine fingerprinted during the attempt.
- **Edges (Relationships)**: Connect the nodes based on transactional behavior:
  - `TRANSACTED_AT`: Account → Merchant (edge data stores amount, currency, and timestamp).
  - `USED_DEVICE`: Account → Device (creates a static link).

### Detection Algorithms
Because all operations are mapped as a mathematical graph, the backend uses advanced traversal techniques to find fraud rings:
- **Shared Device Detection**: Identifies `Device` nodes with an unusually high number of incoming `USED_DEVICE` edges (indicates account takeovers or mule networks).
- **Fan-out Anomalies**: Detects `Account` nodes emitting dozens of `TRANSACTED_AT` edges to different `Merchant` nodes in tight time windows (card testing).
- **Cycle Detection**: Discovers circular subgraph loops where money flows from A → B → C → A (layering/money laundering).

### Frontend Visualization
The frontend utilizes `Cytoscape.js` nested within a custom React component (`GraphExplorer.tsx`). 
The backend serves the network graph as a JSON object natively formatted for Cytoscape (containing `nodes` and `edges` arrays). `Cytoscape.js` renders these geometries using a physics-based layout algorithm (`cose`), dynamically distributing the nodes based on edge tensions so investigators can visually comprehend complex fraud rings immediately.

## Recent Project Updates

*   **Cinematic UI Remaster**: Overhauled the frontend with `Tailwind CSS v4`, Glassmorphism, and `Framer Motion` to create a fluid, highly responsive, dashboard experience.
*   **CORS & Port Integration**: Resolved cross-origin resource sharing (CORS) blocks between the backend FastAPI server and the dynamic Vite development environment (port `5174`).
*   **Data Structure Mapping**: Corrected JSON serialization formats out of the backend (`AlertListOut`) so the frontend TypeScript interfaces properly parse arrays (`data.alerts`) and safely validate numeric IDs preventing rendering crashes.
*   **Full Graph API Endpoint**: Introduced the `GET /api/v1/graph` endpoint allowing the React Graph Explorer comprehensive access to the full dataset.

## Tech Stack

- **Backend**: Python, FastAPI, NetworkX, SQLite
- **Frontend**: React, TypeScript, Cytoscape.js, Recharts, Framer Motion, Tailwind CSS v4
- **Privacy**: SHA-256 local hashing

## Quick Start
*Make sure to copy `.env.example` to `.env` in the backend before running.*

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/generate_demo_data.py
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```
