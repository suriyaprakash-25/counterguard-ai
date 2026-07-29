import logging
import time
import traceback
from datetime import datetime, timezone

from backend.database.engine import get_session_maker
from backend.database.repositories.investigation_repo import InvestigationRepository
from backend.database.repositories.report_repo import ReportRepository
from backend.models.evidence import EvidenceModel
from backend.models.report import ReportModel
from backend.schemas.investigation import InvestigationRequest
from backend.services.investigation_service import InvestigationService

logger = logging.getLogger(__name__)


class InvestigationRunner:
    """
    Dedicated orchestration component to run investigations asynchronously.
    Creates its own database session and manages the full status state machine:
      PENDING -> IN_PROGRESS -> COMPLETED | FAILED
    """

    @staticmethod
    def execute(investigation_id: str, request_dto: InvestigationRequest):
        logger.info(f"[Runner] Starting investigation {investigation_id}")
        # Brief pause so the API session's SQLite commit is fully flushed
        # before this thread opens a new DB session to read the investigation.
        time.sleep(1)

        session_maker = get_session_maker()
        db_session = session_maker()
        inv_repo = InvestigationRepository(db_session)
        report_repo = ReportRepository(db_session)

        try:
            # --- 1. PENDING → IN_PROGRESS ---
            investigation = inv_repo.get_by_id(investigation_id)
            if not investigation:
                logger.error(
                    f"[Runner] Investigation {investigation_id} not found in DB."
                )
                return

            investigation.status = "in_progress"
            db_session.commit()
            # FUTURE WEBSOCKET: publish("InvestigationStarted", investigation_id)

            # --- 2. Execute LangGraph pipeline ---
            service = InvestigationService()
            logger.info(f"[Runner] Invoking LangGraph for {investigation_id}")
            report = service.run_investigation(request_dto)

            logger.info(
                f"[Runner] LangGraph done for {investigation_id}. "
                f"Product={report.product}, RiskLevel={report.risk_level}, "
                f"Confidence={report.confidence:.2f}, Findings={len(report.findings)}"
            )
            # FUTURE WEBSOCKET: publish("ReportGenerated", investigation_id)

            # --- 3. Persist the InvestigationReport to the database ---
            report_model = ReportModel.from_pydantic(report, investigation_id)
            report_repo.add(report_model)
            logger.info(f"[Runner] Report persisted for {investigation_id}")

            # --- 4. Persist evidence timeline events ---
            now = datetime.now(timezone.utc).isoformat()

            timeline_entries = []

            # One entry per finding
            num_findings = max(len(report.findings), 1)
            for finding in report.findings:
                timeline_entries.append(
                    EvidenceModel(
                        investigation_id=investigation_id,
                        agent="ReportGenerator",
                        action="Finding Identified",
                        detail=finding,
                        confidence_delta=round(report.confidence / num_findings, 4),
                        timestamp=now,
                    )
                )

            # AI assessment summary
            if report.ai_summary:
                timeline_entries.append(
                    EvidenceModel(
                        investigation_id=investigation_id,
                        agent="CoordinatorAgent",
                        action="AI Assessment Completed",
                        detail=report.ai_summary,
                        confidence_delta=report.confidence,
                        timestamp=now,
                    )
                )

            # Risk score entry
            timeline_entries.append(
                EvidenceModel(
                    investigation_id=investigation_id,
                    agent="RiskAssessor",
                    action="Risk Score Assigned",
                    detail=(
                        f"Risk Level: {report.risk_level} | Score: {report.risk_score}/100 | "
                        f"{report.recommendation}"
                    ),
                    confidence_delta=report.confidence,
                    timestamp=now,
                )
            )

            # AI reasoning entry
            if report.ai_reasoning:
                timeline_entries.append(
                    EvidenceModel(
                        investigation_id=investigation_id,
                        agent="ExplainabilityEngine",
                        action="Reasoning Generated",
                        detail=report.ai_reasoning,
                        confidence_delta=0.0,
                        timestamp=now,
                    )
                )

            for ev in timeline_entries:
                db_session.add(ev)
            db_session.commit()
            logger.info(
                f"[Runner] Persisted {len(timeline_entries)} timeline events for {investigation_id}"
            )

            # --- 5. IN_PROGRESS → COMPLETED ---
            investigation.status = "completed"
            db_session.commit()
            logger.info(f"[Runner] Investigation {investigation_id} → COMPLETED")
            # FUTURE WEBSOCKET: publish("InvestigationCompleted", investigation_id)

        except Exception as e:
            # --- 6. IN_PROGRESS → FAILED ---
            logger.error(f"[Runner] Investigation {investigation_id} FAILED: {e}")
            logger.error(traceback.format_exc())
            try:
                db_session.rollback()
                investigation = inv_repo.get_by_id(investigation_id)
                if investigation:
                    investigation.status = "failed"
                    db_session.commit()
            except Exception as inner_err:
                logger.error(
                    f"[Runner] Could not mark investigation as failed: {inner_err}"
                )
        finally:
            db_session.close()
