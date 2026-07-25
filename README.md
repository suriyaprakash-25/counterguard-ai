# CounterGuard

Autonomous Counterfeit & Grey-Market Intelligence Network.

## Overview

This repository contains the core platform infrastructure for CounterGuard is a modular AI-powered application designed to automate the investigation of counterfeit products and policy violations. It integrates autonomous web scraping with a multi-agent assessment system to rapidly score risks and generate actionable investigation reports.

## Architecture

The system utilizes Clean Architecture and SOLID principles.

### Components
- **API Layer (`backend/api`)**: FastAPI application exposing endpoints.
- **Scraping Engine (`backend/scrapers`)**: Factory pattern managing multiple marketplace-specific parsers.
  - `PageFetcher`: Resilient HTTP client handling timeouts and errors.
  - `ParserFactory`: Routes HTML to appropriate `BaseParser` implementations (Amazon, Flipkart, etc.).
- **Investigation Engine (`backend/agents`)**: Multi-agent system orchestrated by LangGraph.
- **State Management (`backend/state.py`)**: Centralized Pydantic state passed through the agent graph.

## Investigation Workflow
1. **Request Phase**: `POST /api/v1/investigate` receives a URL.
2. **Scraping Phase**: `ScrapingService` fetches HTML and delegates parsing via `ParserFactory`.
3. **Analysis Phase**: `AnalyzerAgent` extracts heuristics (keyword stuffing, title caps, ratings).
4. **Evidence Collection**: `EvidenceCollector` transforms heuristics into structured evidence JSON.
5. **Risk Assessment**: `RiskAssessor` applies deterministic weightings to output a normalized 0-100 score.
6. **Reporting Phase**: `ReportGenerator` compiles findings and generates a recommendation.

## Extensibility
### Adding a New Marketplace Parser
1. Add a new `Marketplace` enum in `marketplace_detector.py`.
2. Create a new class inheriting from `BaseParser` or `GenericParser` in `backend/scrapers`.
3. Register the new parser in `ParserFactory.get_parser()`.

### Customizing Investigation Rules
Modify thresholds and risk weights inside `backend/constants.py` to tune the `RiskAssessor` logic.

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
