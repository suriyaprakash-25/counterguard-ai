import json
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.schemas.investigation import InvestigationReport

if TYPE_CHECKING:
    from backend.models.investigation import InvestigationModel


class ReportModel(Base):
    """
    ORM model representing the synthesized assessment report for an investigation.
    """

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    investigation_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    product: Mapped[str] = mapped_column(String, nullable=False)
    marketplace: Mapped[str] = mapped_column(String, nullable=False)
    seller: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String, nullable=False, index=True)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    findings: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    investigation_timestamp: Mapped[str] = mapped_column(String, nullable=False)
    recommended_products: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    investigation: Mapped["InvestigationModel"] = relationship(
        "InvestigationModel", back_populates="report"
    )

    def get_evidence_summary_dict(self) -> Dict[str, Any]:
        """
        Deserialize JSON evidence summary back into a Python dictionary.
        """
        return json.loads(self.evidence_summary)

    def get_findings_list(self) -> List[str]:
        """
        Deserialize JSON findings back into a Python list of strings.
        """
        return json.loads(self.findings)

    def get_recommended_products_list(self) -> List[Dict[str, Any]]:
        """
        Deserialize JSON recommended products back into a Python list of dictionaries.
        """
        try:
            return json.loads(self.recommended_products) if self.recommended_products else []
        except Exception:
            return []

    def to_pydantic(self) -> InvestigationReport:
        """
        Convert this database report entity into the InvestigationReport Pydantic domain schema.
        """
        return InvestigationReport(
            summary=self.summary,
            product=self.product,
            marketplace=self.marketplace,
            seller=self.seller,
            price=self.price,
            risk_score=self.risk_score,
            risk_level=self.risk_level,
            evidence_summary=self.get_evidence_summary_dict(),
            findings=self.get_findings_list(),
            recommendation=self.recommendation,
            confidence=self.confidence,
            ai_summary=self.ai_summary,
            ai_reasoning=self.ai_reasoning,
            investigation_timestamp=self.investigation_timestamp,
            recommended_products=self.get_recommended_products_list(),
        )

    @classmethod
    def from_pydantic(
        cls,
        report_schema: InvestigationReport,
        investigation_id: str,
        id: Optional[str] = None,
    ) -> "ReportModel":
        """
        Construct a ReportModel DB entity from an InvestigationReport Pydantic schema and investigation ID.
        """
        kwargs = {
            "investigation_id": investigation_id,
            "summary": report_schema.summary,
            "product": report_schema.product,
            "marketplace": report_schema.marketplace,
            "seller": report_schema.seller,
            "price": report_schema.price,
            "risk_score": report_schema.risk_score,
            "risk_level": report_schema.risk_level,
            "evidence_summary": json.dumps(report_schema.evidence_summary),
            "findings": json.dumps(report_schema.findings),
            "recommendation": report_schema.recommendation,
            "confidence": report_schema.confidence,
            "ai_summary": report_schema.ai_summary,
            "ai_reasoning": report_schema.ai_reasoning,
            "investigation_timestamp": report_schema.investigation_timestamp,
            "recommended_products": json.dumps(report_schema.recommended_products),
        }
        if id is not None:
            kwargs["id"] = id
        return cls(**kwargs)

    def __repr__(self) -> str:
        return f"<ReportModel(id='{self.id}', product='{self.product}', risk_level='{self.risk_level}')>"
