# CounterGuard Backend

This is the FastAPI backend service for CounterGuard.

## Getting Started

1. Install requirements: `pip install -r requirements.txt`
2. Run server: `uvicorn backend.api.main:app --reload`

## Architecture & Models

- `backend.state.InvestigationState`: Canonical TypedDict single-source of truth.
- `backend.models.types`: Shared TypedDict domain definitions.
- `backend.services.mock_investigation_service`: Service provider generating investigation states.

## Endpoints

- `/health`: Basic health check.
- `/api/v1/investigate`: Start an automated investigation and return canonical InvestigationState payload.
