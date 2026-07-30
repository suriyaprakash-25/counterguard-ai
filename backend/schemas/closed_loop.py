"""
closed_loop.py — Phase 1: Closed-Loop Intelligence DTO Schemas
Pydantic models representing the 8-stage closed-loop pipeline, execution telemetry, and evolution metrics.
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class PipelineStageTelemetry(BaseModel):
    stage_number: int = Field(..., description="Stage sequence (1-8)")
    stage_name: str = Field(..., description="Stage name")
    status: str = Field(
        default="COMPLETED", description="Status: COMPLETED, RUNNING, FAILED"
    )
    details: str = Field(..., description="Stage output summary")
    duration_ms: float = Field(..., description="Execution duration in milliseconds")


class ClosedLoopTelemetryDTO(BaseModel):
    execution_id: str = Field(..., description="Unique closed-loop execution ID")
    case_id: str = Field(..., description="Source investigation case ID")
    product_name: str = Field(..., description="Product under audit")
    status: str = Field(default="SUCCESS", description="Execution status")
    total_duration_ms: float = Field(
        ..., description="Total pipeline execution runtime"
    )
    stages: List[PipelineStageTelemetry] = Field(default_factory=list)
    knowledge_nodes_added: int = Field(
        default=14, description="New Neo4j graph nodes added"
    )
    vector_precedents_created: int = Field(
        default=1, description="New ChromaDB memory precedents"
    )
    syndicates_updated: int = Field(default=1, description="Fraud rings updated")
    new_threat_score: float = Field(
        default=88.0, description="Recalculated threat score"
    )
    recommendations_count: int = Field(
        default=4, description="Prescriptive recommendations generated"
    )
    report_id: str = Field(..., description="Generated executive threat report ID")
    alerts_triggered: int = Field(
        default=2, description="Multi-channel alerts dispatched"
    )
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ClosedLoopTriggerRequest(BaseModel):
    case_id: str = Field(default="INV-8901", description="Investigation case ID")
    product_name: str = Field(default="CMF Buds 2a", description="Product title")
