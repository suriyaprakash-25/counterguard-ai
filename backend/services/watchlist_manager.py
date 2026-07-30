"""
watchlist_manager.py — Phase 4: Production Persistent Watchlist Manager Service
Manages 8 target entity categories with SQLite persistence via WatchlistRepository and links with MonitoringJobRepository.
"""
import json
import logging
from datetime import datetime
from typing import List

from backend.models.monitoring import MonitoringJobModel, WatchlistModel
from backend.repositories.monitoring_repository import (
    monitoring_job_repo,
    watchlist_repo,
)
from backend.schemas.watchlist import WatchlistCreateRequest, WatchlistItemDTO
from backend.services.monitoring_scheduler import monitoring_scheduler

logger = logging.getLogger("counterguard.watchlist_manager")


class WatchlistManager:
    """
    Central Watchlist Management Service.
    Manages analyst-defined watchlists persisted in SQLite across 8 target entity types.
    """

    def get_all_watchlists(self) -> List[WatchlistItemDTO]:
        """Fetch all configured watchlist targets from SQLite, seeding defaults if empty."""
        models = watchlist_repo.get_all()
        if not models:
            self._seed_default_watchlists()
            models = watchlist_repo.get_all()

        dtos = []
        for m in models:
            dtos.append(
                WatchlistItemDTO(
                    id=m.id,
                    category=m.entity_type,
                    value=m.query,
                    name=m.entity_name,
                    status="ACTIVE" if m.enabled else "PAUSED",
                    created_at=m.created_at.isoformat()
                    if m.created_at
                    else datetime.utcnow().isoformat(),
                    alert_count=3,
                )
            )
        return dtos

    def _seed_default_watchlists(self):
        """Seed 8 default enterprise watchlists into SQLite if database is empty."""
        now = datetime.utcnow()
        defaults = [
            ("wl-1", "BRAND", "Nothing Brand Watchlist", "Nothing Tech"),
            ("wl-2", "PRODUCT", "CMF Buds 2a SKU Watchlist", "CMF Buds 2a"),
            (
                "wl-3",
                "SELLER",
                "Radha Wholesale Merchant Watch",
                "Radha Wholesale Enterprise",
            ),
            ("wl-4", "PHONE", "Surat Contact Handle Watch", "+91 98765-43210"),
            ("wl-5", "EMAIL", "Syndicate Email Watch", "wholesale@surat-replica.com"),
            ("wl-6", "GST", "Surat Syndicate Tax Registration", "07AAAAA0000A1Z5"),
            (
                "wl-7",
                "FRAUD_RING",
                "Surat Replica Supply Syndicate-A",
                "ring-surat-alpha",
            ),
            ("wl-8", "MARKETPLACE", "Meesho High-Risk Seller Watch", "Meesho"),
        ]
        for item_id, cat, name, query in defaults:
            m = WatchlistModel(
                id=item_id,
                entity_type=cat,
                entity_name=name,
                query=query,
                marketplaces=json.dumps(["Amazon", "Flipkart", "Meesho", "TradeIndia"]),
                priority="HIGH",
                interval="15m",
                enabled=True,
                created_at=now,
                updated_at=now,
            )
            watchlist_repo.save(m)

    def create_watchlist_item(
        self, request: WatchlistCreateRequest
    ) -> WatchlistItemDTO:
        """Create a new target entry in watchlists and create corresponding monitoring job in SQLite."""
        item_id = f"wl-{int(datetime.utcnow().timestamp())}"
        now = datetime.utcnow()

        model = WatchlistModel(
            id=item_id,
            entity_type=request.category.upper(),
            entity_name=request.name,
            query=request.value,
            marketplaces=json.dumps(["Amazon", "Flipkart", "Meesho", "TradeIndia"]),
            priority="HIGH",
            interval="15m",
            enabled=True,
            created_at=now,
            updated_at=now,
        )
        watchlist_repo.save(model)

        # Create corresponding monitoring job in SQLite
        job_id = f"job-{item_id}"
        job_model = MonitoringJobModel(
            id=job_id,
            name=f"{request.name} Watchlist",
            query=request.value,
            marketplaces=json.dumps(["Amazon", "Flipkart", "Meesho", "TradeIndia"]),
            interval="15m",
            status="ACTIVE",
            created_at=now,
            updated_at=now,
            last_run=now.isoformat(),
            next_run=(now).isoformat(),
            total_scans=0,
            total_discovered=0,
            total_investigations=0,
            total_reports=0,
        )
        monitoring_job_repo.save(job_model)
        monitoring_scheduler._schedule_job_in_apscheduler(job_model)

        logger.info(
            f"[WatchlistManager] Created new watchlist target '{request.name}' ({request.category}) & job '{job_id}' in SQLite."
        )
        return WatchlistItemDTO(
            id=item_id,
            category=model.entity_type,
            value=request.value,
            name=model.entity_name,
            status="ACTIVE",
            created_at=now.isoformat(),
            alert_count=0,
        )

    def delete_watchlist_item(self, item_id: str) -> bool:
        """Delete a target entry from watchlists and corresponding monitoring job."""
        success = watchlist_repo.delete(item_id)
        if success:
            job_id = f"job-{item_id}"
            monitoring_job_repo.delete(job_id)
            if monitoring_scheduler._scheduler.get_job(job_id):
                monitoring_scheduler._scheduler.remove_job(job_id)
        return success

    def pause_watchlist_item(self, item_id: str) -> WatchlistItemDTO:
        """Pause monitoring for a target entry."""
        models = watchlist_repo.get_all()
        target = next((m for m in models if m.id == item_id), None)
        if not target:
            raise ValueError(f"Watchlist item '{item_id}' not found.")

        target.enabled = False
        watchlist_repo.save(target)

        job_id = f"job-{item_id}"
        monitoring_scheduler.pause_job(job_id)

        return WatchlistItemDTO(
            id=target.id,
            category=target.entity_type,
            value=target.query,
            name=target.entity_name,
            status="PAUSED",
            created_at=target.created_at.isoformat()
            if target.created_at
            else datetime.utcnow().isoformat(),
            alert_count=0,
        )

    def resume_watchlist_item(self, item_id: str) -> WatchlistItemDTO:
        """Resume monitoring for a target entry."""
        models = watchlist_repo.get_all()
        target = next((m for m in models if m.id == item_id), None)
        if not target:
            raise ValueError(f"Watchlist item '{item_id}' not found.")

        target.enabled = True
        watchlist_repo.save(target)

        job_id = f"job-{item_id}"
        monitoring_scheduler.resume_job(job_id)

        return WatchlistItemDTO(
            id=target.id,
            category=target.entity_type,
            value=target.query,
            name=target.entity_name,
            status="ACTIVE",
            created_at=target.created_at.isoformat()
            if target.created_at
            else datetime.utcnow().isoformat(),
            alert_count=0,
        )

    def export_watchlists_csv(self) -> str:
        """Export watchlists in CSV format."""
        models = watchlist_repo.get_all()
        csv = "ID,Category,Query,Name,Status,Created At\n"
        for m in models:
            status = "ACTIVE" if m.enabled else "PAUSED"
            created = m.created_at.isoformat() if m.created_at else ""
            csv += f'"{m.id}","{m.entity_type}","{m.query}","{m.entity_name}","{status}","{created}"\n'
        return csv


watchlist_manager = WatchlistManager()
