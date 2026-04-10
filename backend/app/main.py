"""
zkTransact — FastAPI Application Entry Point

Privacy-preserving fraud ring detection using graph analytics.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.api import transactions, alerts, graph, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: initialize database tables
    await init_db()
    print("✓ Database initialized")
    print("✓ Graph store ready")
    print("✓ zkTransact backend running")
    yield
    # Shutdown: cleanup
    print("⏏ Shutting down zkTransact")


settings = get_settings()

app = FastAPI(
    title="zkTransact",
    description="Privacy-preserving fraud ring detection using graph analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(graph.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    """Health check."""
    return {
        "service": "zkTransact",
        "status": "operational",
        "version": "1.0.0",
    }


@app.get("/health", tags=["health"])
async def health():
    """Detailed health check."""
    from app.core.graph_store import get_graph_store
    graph = get_graph_store()
    return {
        "status": "healthy",
        "graph_nodes": sum(graph.node_count().values()),
        "graph_edges": graph.edge_count(),
    }
