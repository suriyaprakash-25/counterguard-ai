"""
monitoring.py — Phase 1: SQLite Persistence Models for Continuous Monitoring & Watchlists
Defines normalized SQLAlchemy models for monitoring_jobs, monitoring_history, monitoring_events, and watchlists.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from backend.models.base import Base


class MonitoringJobModel(Base):
    __tablename__ = "monitoring_jobs"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    query = Column(String(255), nullable=False)
    marketplaces = Column(Text, nullable=False, default="[]")  # JSON string
    interval = Column(String(50), nullable=False, default="15m")  # 15m, 30m, 1h, 24h
    status = Column(
        String(50), nullable=False, default="ACTIVE"
    )  # ACTIVE, PAUSED, RUNNING, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = Column(String(100), nullable=True)
    next_run = Column(String(100), nullable=True)
    total_scans = Column(Integer, default=0)
    total_discovered = Column(Integer, default=0)
    total_investigations = Column(Integer, default=0)
    total_reports = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    configuration_json = Column(Text, nullable=True, default="{}")


class MonitoringHistoryModel(Base):
    __tablename__ = "monitoring_history"

    id = Column(String(100), primary_key=True, index=True)
    job_id = Column(
        String(100), ForeignKey("monitoring_jobs.id"), nullable=False, index=True
    )
    started_at = Column(String(100), nullable=False)
    completed_at = Column(String(100), nullable=False)
    duration_ms = Column(Float, default=0.0)
    status = Column(String(50), default="SUCCESS")
    discoveries = Column(Integer, default=0)
    investigations = Column(Integer, default=0)
    reports = Column(Integer, default=0)
    errors = Column(Text, nullable=True)


class MonitoringEventModel(Base):
    __tablename__ = "monitoring_events"

    id = Column(String(100), primary_key=True, index=True)
    job_id = Column(String(100), nullable=False, index=True)
    event_type = Column(
        String(100), nullable=False
    )  # NEW_LISTING, PRICE_CHANGE, SELLER_CHANGE
    listing_id = Column(String(100), nullable=True)
    seller_id = Column(String(100), nullable=True)
    marketplace = Column(String(100), nullable=False)
    timestamp = Column(String(100), nullable=False)
    payload_json = Column(Text, nullable=True, default="{}")


class WatchlistModel(Base):
    __tablename__ = "watchlists"

    id = Column(String(100), primary_key=True, index=True)
    entity_type = Column(
        String(50), nullable=False
    )  # BRAND, PRODUCT, SELLER, PHONE, EMAIL, GST, FRAUD_RING, MARKETPLACE
    entity_name = Column(String(255), nullable=False)
    query = Column(String(255), nullable=False)
    marketplaces = Column(Text, nullable=False, default="[]")  # JSON string
    priority = Column(String(50), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    interval = Column(String(50), default="15m")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProviderHealthModel(Base):
    __tablename__ = "provider_health"

    id = Column(String(100), primary_key=True, index=True)
    marketplace = Column(String(100), nullable=False, unique=True, index=True)
    status = Column(
        String(50), nullable=False, default="HEALTHY"
    )  # HEALTHY, DEGRADED, BLOCKED, RATE_LIMITED, OFFLINE
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    blocked_403_count = Column(Integer, default=0)
    rate_limit_429_count = Column(Integer, default=0)
    captcha_count = Column(Integer, default=0)
    timeout_count = Column(Integer, default=0)
    average_latency_ms = Column(Float, default=0.0)
    last_successful_at = Column(String(100), nullable=True)
    last_failure_at = Column(String(100), nullable=True)
    last_error_message = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RawEvidenceArchiveModel(Base):
    __tablename__ = "raw_evidence_archive"

    id = Column(String(100), primary_key=True, index=True)
    evidence_id = Column(String(100), nullable=False, index=True)
    marketplace = Column(String(100), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    http_status = Column(Integer, default=200)
    response_hash = Column(String(100), nullable=False, index=True)
    parser_version = Column(String(50), default="v1.2.0")
    retrieval_timestamp = Column(String(100), nullable=False)
    content_type = Column(String(100), default="text/html")
    compressed_size_bytes = Column(Integer, default=0)
    storage_path = Column(Text, nullable=False)
    payload_json = Column(Text, nullable=True, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class ParserExecutionHistoryModel(Base):
    __tablename__ = "parser_execution_history"

    id = Column(String(100), primary_key=True, index=True)
    marketplace = Column(String(100), nullable=False, index=True)
    parser_name = Column(String(100), nullable=False)
    parser_version = Column(String(50), default="v1.2.0-bs4")
    http_status = Column(Integer, default=200)
    html_size_bytes = Column(Integer, default=0)
    dom_nodes = Column(Integer, default=0)
    selectors_executed = Column(Integer, default=0)
    selectors_failed = Column(Integer, default=0)
    cards_found = Column(Integer, default=0)
    cards_parsed = Column(Integer, default=0)
    cards_rejected = Column(Integer, default=0)
    duration_ms = Column(Float, default=0.0)
    parser_success_pct = Column(Float, default=100.0)
    confidence_score = Column(Float, default=95.0)
    confidence_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ParserRejectedItemModel(Base):
    __tablename__ = "parser_rejected_items"

    id = Column(String(100), primary_key=True, index=True)
    execution_id = Column(
        String(100),
        ForeignKey("parser_execution_history.id"),
        nullable=False,
        index=True,
    )
    marketplace = Column(String(100), nullable=False)
    listing_position = Column(Integer, default=1)
    reason = Column(
        String(100), nullable=False
    )  # MISSING_TITLE, MISSING_PRICE, MISSING_SELLER, ADVERTISEMENT, BROKEN_HTML
    raw_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CandidateLineageModel(Base):
    __tablename__ = "candidate_lineage"

    id = Column(String(100), primary_key=True, index=True)
    candidate_id = Column(String(100), nullable=False, index=True)
    http_request_id = Column(String(100), nullable=True)
    response_sha256 = Column(String(100), nullable=True)
    evidence_archive_id = Column(String(100), nullable=True)
    parser_version = Column(String(50), default="v1.2.0-bs4")
    parser_confidence = Column(Float, default=95.0)
    retrieval_mode = Column(String(50), default="LIVE_HTTP")
    deduplication_group_id = Column(String(100), nullable=True)
    ranking_score = Column(Float, default=0.0)
    investigation_id = Column(String(100), nullable=True, index=True)
    report_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RuntimeMetricsModel(Base):
    __tablename__ = "runtime_metrics"

    id = Column(String(100), primary_key=True, index=True)
    stage_name = Column(
        String(100), nullable=False, index=True
    )  # discovery, http_retrieval, parser, deduplication, ranking, investigation_launch, langgraph, persistence
    duration_ms = Column(Float, nullable=False)
    correlation_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
