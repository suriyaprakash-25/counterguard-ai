# CounterGuard

Autonomous Counterfeit & Grey-Market Intelligence Network.

## Overview

This repository contains the core platform infrastructure for CounterGuard, orchestrating multiple AI agents to investigate counterfeit listings and grey-market anomalies.

## Architecture

Please refer to `ARCHITECTURE.md` for a detailed technical spec on the multi-agent design.

## Running Locally

1. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Build and start the services using Docker Compose:
   ```bash
   make build
   make up
   ```

3. Access the services:
   - Frontend Dashboard: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
