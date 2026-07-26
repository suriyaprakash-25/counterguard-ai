import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import investigation
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
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:8501").split(",")

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
api_router.include_router(investigation.router, tags=["Investigation"])
app.include_router(api_router)

# Versioned router prefix (placeholder for future routes)
# api_router = APIRouter(prefix="/api/v1")
# app.include_router(api_router)


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return {"status": "ok", "service": "counterguard-backend"}
