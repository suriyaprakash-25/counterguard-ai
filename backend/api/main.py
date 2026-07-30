import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    alerts,
    analytics,
    auth,
    browser,
    case_management,

    closed_loop,
    dashboard,
    discovery,
    fraud_rings,
    graph,
    health,
    intelligence,
    investigation,
    investigations,
    memory,
    monitoring,
    providers,
    recommendations,
    scoring,
    settings,
    threat_graph,
    threat_reports,
    watchlists,
)
from backend.dependencies import neo4j_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from backend.services.monitoring_scheduler import monitoring_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up CounterGuard API...")
    neo4j_client.connect()
    monitoring_scheduler.start()
    yield
    # Shutdown
    logger.info("Shutting down CounterGuard API...")
    monitoring_scheduler.shutdown()
    neo4j_client.close()


app = FastAPI(
    title="CounterGuard API",
    description="""
    Backend API for CounterGuard autonomous agent network.

    ## Features
    * **Autonomous Scraping:** Uses custom PageFetcher and ParserFactory to intelligently scrape data from Amazon, Flipkart, eBay, etc.
    * **Multi-Agent Engine:** Analyzes products using AI agents (Analyzer, Collector, Assessor, Reporter).
    * **Risk Assessment:** Returns comprehensive, deterministic risk levels and JSON structured evidence.
    * **Investigation History:** Persistent SQLite/Postgres querying, filtering, sorting, and management of investigation executions.
    """,
    version="1.1.0",
    lifespan=lifespan,
)

# CORS Middleware
origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:80,http://localhost,http://localhost:8080",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Logging Middleware Example (Native FastAPI middleware)
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(discovery.router, tags=["Discovery"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(alerts.router, tags=["Alerts"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(intelligence.router, tags=["Intelligence"])
api_router.include_router(graph.router, tags=["Graph"])
api_router.include_router(threat_graph.router, tags=["Threat Knowledge Graph"])
api_router.include_router(fraud_rings.router, tags=["Fraud Ring Intelligence"])
api_router.include_router(memory.router, tags=["Organizational Memory"])
api_router.include_router(scoring.router, tags=["Hierarchical Threat Scoring"])
api_router.include_router(
    threat_reports.router, tags=["Executive Threat Intelligence Reports"]
)
api_router.include_router(monitoring.router, tags=["Proactive Continuous Monitoring"])
api_router.include_router(watchlists.router, tags=["Watchlist Management"])
api_router.include_router(
    recommendations.router, tags=["AI Prescriptive Recommendations"]
)
api_router.include_router(
    case_management.router, tags=["Collaborative Case Management"]
)
api_router.include_router(closed_loop.router, tags=["Closed-Loop Intelligence Engine"])
api_router.include_router(settings.router, tags=["Settings"])
api_router.include_router(investigation.router, tags=["Investigation"])
api_router.include_router(investigations.router, tags=["Investigation History"])
api_router.include_router(providers.router, tags=["Providers"])
api_router.include_router(browser.router, tags=["Browser Extension"])
app.include_router(api_router)



@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return {"status": "ok", "service": "counterguard-backend"}
