# CounterGuard Deployment Guide

CounterGuard Version 1.0 is a robust, multi-container architecture composed of a FastAPI backend and a React/Vite frontend.

## Prerequisites
- Docker Engine & Docker Compose
- Node 20 (Local Dev only)
- Python 3.11 (Local Dev only)

## Production Deployment (Docker Compose)

The standard method of deploying CounterGuard is via `docker-compose`. This spins up the unified stack with all networking internal to the Docker host.

### 1. Configure Environments
Copy the example environments and adjust the production settings:
```bash
cp frontend/web/.env.example frontend/web/.env.production
```

### 2. Launch Services
From the repository root:
```bash
docker compose up --build -d
```

This will:
- Build the `backend` using Python 3.11.
- Build the `frontend` using a multi-stage Docker build, injecting the React bundle into an `nginx:alpine` image.
- Expose the frontend at `http://localhost:80`.
- Proxy all `/api` requests seamlessly through Nginx to the backend, bypassing any CORS complications.

## Monitoring & Observability

- **Logs**: We employ structured JSON logging in both frontend and backend. View via `docker compose logs -f`.
- **Health Checks**: The frontend automatically pings backend health endpoints (`/health`) and routes errors into the Global Error Boundary.

## Security Posture
- **CSP**: The frontend embeds strict Content Security Policies in `index.html`.
- **Authentication**: JWTs are managed locally. In production, ensure Nginx sits behind a TLS-terminating load balancer (HTTPS) to prevent man-in-the-middle attacks on the Authorization headers.
