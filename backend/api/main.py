import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import auth, investigation, investigations, dashboard, alerts, analytics, intelligence, graph, settings, providers
from backend.dependencies import neo4j_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up CounterGuard API...")
    neo4j_client.connect()
    yield
    # Shutdown
    logger.info("Shutting down CounterGuard API...")
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
    "http://localhost:5173,http://localhost:3000,http://localhost:80,http://localhost,http://localhost:8080"
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
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(alerts.router, tags=["Alerts"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(intelligence.router, tags=["Intelligence"])
api_router.include_router(graph.router, tags=["Graph"])
api_router.include_router(settings.router, tags=["Settings"])
api_router.include_router(investigation.router, tags=["Investigation"])
api_router.include_router(investigations.router, tags=["Investigation History"])
api_router.include_router(providers.router, tags=["Providers"])
app.include_router(api_router)


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return {"status": "ok", "service": "counterguard-backend"}
