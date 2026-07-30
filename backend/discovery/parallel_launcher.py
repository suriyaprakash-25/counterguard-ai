"""
ParallelInvestigationLauncher — Sprint 2.3
Accepts a list of ListingCandidate-derived items, creates one InvestigationModel
per candidate, then fans out concurrent InvestigationRunner threads.

Design constraints:
  - REUSES InvestigationRunner.execute() — zero logic duplication.
  - REUSES the existing DB session / transaction pattern.
  - Each investigation runs in its own daemon thread (matching the existing pattern).
  - In-memory batch registry maps batch_id → [investigation_ids] for status polling.
  - No external queue / broker required.
"""
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from backend.database.engine import get_session_maker
from backend.database.repositories.investigation_repo import InvestigationRepository
from backend.models.investigation import InvestigationModel
from backend.schemas.investigation import InvestigationRequest
from backend.schemas.parallel_launch import (
    BatchStatusResponse,
    CandidateLaunchItem,
    LaunchJobStatus,
    ParallelLaunchRequest,
    ParallelLaunchResponse,
)
from backend.services.investigation_runner import InvestigationRunner

logger = logging.getLogger(__name__)

# ── In-memory batch registry ─────────────────────────────────────────────────
# Maps batch_id → {"jobs": List[LaunchJobStatus], "investigation_ids": List[str]}
# This is sufficient for a single-process server; replace with Redis for multi-process.
_BATCH_REGISTRY: Dict[str, dict] = {}
_REGISTRY_LOCK = threading.Lock()


def _register_batch(batch_id: str, jobs: List[LaunchJobStatus]) -> None:
    with _REGISTRY_LOCK:
        _BATCH_REGISTRY[batch_id] = {
            "jobs": jobs,
            "investigation_ids": [j.investigation_id for j in jobs],
        }


def _get_batch(batch_id: str) -> dict | None:
    with _REGISTRY_LOCK:
        return _BATCH_REGISTRY.get(batch_id)


class ParallelInvestigationLauncher:
    """
    Orchestrator that converts selected discovery candidates into concurrent investigations.

    Flow:
      candidates → persist InvestigationModels (PENDING) → fan-out threads → return batch receipt
    """

    def launch(self, request: ParallelLaunchRequest) -> ParallelLaunchResponse:
        """
        Main entry point. Called synchronously from the FastAPI route handler.
        All DB writes are committed before threads start to avoid race conditions.
        """
        batch_id = f"batch-{uuid.uuid4().hex[:12]}"
        launched_at = datetime.now(timezone.utc).isoformat()
        jobs: List[LaunchJobStatus] = []

        logger.info(
            f"[Launcher] Starting parallel batch '{batch_id}' "
            f"for {len(request.candidates)} candidate(s)"
        )

        session_maker = get_session_maker()
        db = session_maker()
        repo = InvestigationRepository(db)

        try:
            # ── Stage 1: Persist all InvestigationModels atomically ──────────
            inv_records: List[
                tuple[CandidateLaunchItem, InvestigationModel, InvestigationRequest]
            ] = []

            for candidate in request.candidates:
                listing_url = candidate.url.strip() or (
                    f"search://{candidate.marketplace}/{candidate.title}"
                )
                marketplace = candidate.marketplace or "Global"

                inv = InvestigationModel(
                    listing_url=listing_url,
                    marketplace=marketplace,
                    status="pending",
                )
                repo.add(inv)

                # Build request DTO that InvestigationRunner expects
                request_dto = InvestigationRequest(
                    listing_url=inv.listing_url,
                    marketplace=inv.marketplace,
                    investigation_type=request.investigation_type,
                    planner_strategy=request.planner_strategy,
                    objectives=request.objectives or [],
                    target_type="Marketplace Product URL",
                    target_value=inv.listing_url,
                    advanced_options=request.advanced_options,
                )

                inv_records.append((candidate, inv, request_dto))

            # Commit all investigation records before spawning threads
            db.commit()
            logger.info(
                f"[Launcher] Persisted {len(inv_records)} investigation records for batch '{batch_id}'"
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"[Launcher] Failed to persist batch '{batch_id}': {e}", exc_info=True
            )
            raise
        finally:
            db.close()

        # ── Stage 2: Priority Queue Sorting (Critical -> High -> Medium -> Low) ──
        PRIORITY_MAP = {"critical": 0, "high": 1, "medium": 2, "normal": 2, "low": 3}

        request_priority = (request.priority or "high").lower()
        priority_rank = PRIORITY_MAP.get(request_priority, 1)

        # Sort inv_records by priority rank so Critical jobs are dispatched first
        inv_records.sort(
            key=lambda item: PRIORITY_MAP.get(
                (item[0].marketplace or "").lower(), priority_rank
            )
        )

        logger.info(
            f"[Launcher] Priority Queue ordered {len(inv_records)} job(s). "
            f"Base Priority: {request_priority.upper()} (Rank {priority_rank})"
        )

        for queue_pos, (candidate, inv, request_dto) in enumerate(inv_records, start=1):
            inv_id_str = str(inv.id) if inv.id else uuid.uuid4().hex
            t = threading.Thread(
                target=InvestigationRunner.execute,
                args=(inv_id_str, request_dto),
                daemon=True,
                name=f"prio-q-{queue_pos}-batch-{batch_id[:6]}-inv-{inv_id_str[:6]}",
            )
            t.start()
            logger.info(
                f"[Launcher] [Priority Queue #{queue_pos}] Spawned thread for investigation {inv.id} "
                f"(candidate: {candidate.candidate_id}, marketplace: {candidate.marketplace})"
            )

            jobs.append(
                LaunchJobStatus(
                    candidate_id=candidate.candidate_id,
                    investigation_id=inv_id_str,
                    marketplace=candidate.marketplace,
                    title=candidate.title,
                    url=candidate.url,
                    status="pending",
                    launched_at=launched_at,
                )
            )

        # ── Stage 3: Register batch for status polling ────────────────────────
        _register_batch(batch_id, jobs)

        investigation_ids = [j.investigation_id for j in jobs]
        summary = (
            f"Dispatched {len(jobs)} priority-queued investigation(s) across "
            f"{len({j.marketplace for j in jobs})} marketplace(s). "
            f"Batch ID: {batch_id}"
        )

        logger.info(
            f"[Launcher] Priority Queue Batch '{batch_id}' dispatched. IDs: {investigation_ids}"
        )

        return ParallelLaunchResponse(
            batch_id=batch_id,
            total_launched=len(jobs),
            jobs=jobs,
            investigation_ids=investigation_ids,
            summary=summary,
            metadata={
                "batch_id": batch_id,
                "launched_at": launched_at,
                "investigation_type": request.investigation_type,
                "planner_strategy": request.planner_strategy,
                "priority_queue_used": True,
                "base_priority": request_priority.upper(),
                "candidate_count": len(request.candidates),
                "marketplace_count": len({c.marketplace for c in request.candidates}),
            },
        )

    @staticmethod
    def get_batch_status(batch_id: str) -> BatchStatusResponse | None:
        """
        Poll live DB status for every investigation in the batch.
        Returns None if the batch_id is unknown.
        """
        batch = _get_batch(batch_id)
        if batch is None:
            return None

        original_jobs: List[LaunchJobStatus] = batch["jobs"]
        investigation_ids: List[str] = batch["investigation_ids"]

        # Re-query live statuses from DB
        session_maker = get_session_maker()
        db = session_maker()
        try:
            repo = InvestigationRepository(db)
            live_statuses: Dict[str, str] = {}
            for inv_id in investigation_ids:
                inv = repo.get_by_id(inv_id)
                live_statuses[inv_id] = inv.status if inv else "unknown"
        finally:
            db.close()

        # Build updated job list
        updated_jobs: List[LaunchJobStatus] = []
        for job in original_jobs:
            updated_jobs.append(
                LaunchJobStatus(
                    candidate_id=job.candidate_id,
                    investigation_id=job.investigation_id,
                    marketplace=job.marketplace,
                    title=job.title,
                    url=job.url,
                    status=live_statuses.get(job.investigation_id, "unknown"),
                    launched_at=job.launched_at,
                )
            )

        total = len(updated_jobs)
        completed = sum(1 for j in updated_jobs if j.status == "completed")
        in_progress = sum(1 for j in updated_jobs if j.status == "in_progress")
        pending = sum(1 for j in updated_jobs if j.status == "pending")
        failed = sum(1 for j in updated_jobs if j.status == "failed")
        progress_pct = round((completed / total) * 100, 1) if total > 0 else 0.0

        return BatchStatusResponse(
            batch_id=batch_id,
            total=total,
            completed=completed,
            in_progress=in_progress,
            pending=pending,
            failed=failed,
            progress_pct=progress_pct,
            jobs=updated_jobs,
            is_complete=(completed + failed == total),
        )
