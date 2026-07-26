import logging
import math
from typing import Optional

from backend.database.repositories import (
    IEvidenceRepository,
    IInvestigationRepository,
    IReportRepository,
)
from backend.exceptions import CounterGuardError
from backend.schemas.history import (
    DeleteInvestigationResponse,
    EvidenceItemSchema,
    InvestigationDetailResponse,
    InvestigationHistoryItem,
    InvestigationListResponse,
)

logger = logging.getLogger(__name__)


class InvestigationHistoryService:
    """
    Service layer encapsulating business logic for retrieving, filtering,
    paginating, and deleting investigation records.
    """

    def __init__(
        self,
        investigation_repo: IInvestigationRepository,
        evidence_repo: Optional[IEvidenceRepository] = None,
        report_repo: Optional[IReportRepository] = None,
    ):
        self.investigation_repo = investigation_repo
        self.evidence_repo = evidence_repo
        self.report_repo = report_repo

    def list_investigations(
        self,
        page: int = 1,
        page_size: int = 20,
        marketplace: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> InvestigationListResponse:
        """
        Retrieves a paginated list of investigations matching criteria.
        """
        try:
            page = max(1, page)
            page_size = max(1, page_size)
            offset = (page - 1) * page_size

            total_count = self.investigation_repo.count(
                marketplace=marketplace, status=status
            )
            inv_models = self.investigation_repo.get_all(
                limit=page_size,
                offset=offset,
                marketplace=marketplace,
                status=status,
                sort_by=sort_by,
                sort_order=sort_order,
            )

            items = []
            for inv in inv_models:
                product = None
                risk_level = None
                risk_score = None
                summary = None

                report_model = inv.report
                if report_model is None and self.report_repo is not None:
                    report_model = self.report_repo.get_by_investigation(inv.id)

                if report_model:
                    product = report_model.product
                    risk_level = report_model.risk_level
                    risk_score = report_model.risk_score
                    summary = report_model.summary

                item = InvestigationHistoryItem(
                    id=inv.id,
                    listing_url=inv.listing_url,
                    marketplace=inv.marketplace,
                    status=inv.status,
                    created_at=inv.created_at,
                    updated_at=inv.updated_at,
                    product=product,
                    risk_level=risk_level,
                    risk_score=risk_score,
                    summary=summary,
                )
                items.append(item)

            total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

            return InvestigationListResponse(
                items=items,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )
        except Exception as e:
            logger.error(f"Error listing investigation history: {e}")
            raise CounterGuardError(
                f"Failed to retrieve investigation list: {e}"
            ) from e

    def get_investigation_detail(
        self, investigation_id: str
    ) -> Optional[InvestigationDetailResponse]:
        """
        Retrieves complete details of an investigation, including report and evidence timeline.
        """
        try:
            inv = self.investigation_repo.get_by_id(investigation_id)
            if not inv:
                return None

            report_schema = None
            report_model = inv.report
            if report_model is None and self.report_repo is not None:
                report_model = self.report_repo.get_by_investigation(inv.id)
            if report_model:
                report_schema = report_model.to_pydantic()

            evidence_models = inv.evidence
            if (not evidence_models) and self.evidence_repo is not None:
                evidence_models = self.evidence_repo.get_by_investigation(inv.id)

            timeline = [EvidenceItemSchema.model_validate(ev) for ev in evidence_models]

            return InvestigationDetailResponse(
                id=inv.id,
                listing_url=inv.listing_url,
                marketplace=inv.marketplace,
                status=inv.status,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                report=report_schema,
                evidence_timeline=timeline,
            )
        except Exception as e:
            logger.error(
                f"Error fetching detail for investigation {investigation_id}: {e}"
            )
            raise CounterGuardError(
                f"Failed to retrieve investigation detail: {e}"
            ) from e

    def delete_investigation(
        self, investigation_id: str
    ) -> Optional[DeleteInvestigationResponse]:
        """
        Deletes an investigation record and all its associated reports and evidence.
        """
        try:
            success = self.investigation_repo.delete(investigation_id)
            if not success:
                return None

            return DeleteInvestigationResponse(
                id=investigation_id,
                message="Investigation and associated records deleted successfully.",
                success=True,
            )
        except Exception as e:
            logger.error(f"Error deleting investigation {investigation_id}: {e}")
            raise CounterGuardError(f"Failed to delete investigation: {e}") from e
