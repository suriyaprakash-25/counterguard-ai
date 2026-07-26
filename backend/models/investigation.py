import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.evidence import EvidenceModel
    from backend.models.report import ReportModel


class InvestigationModel(Base):
    """
    ORM model representing a CounterGuard investigation execution.
    """

    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    listing_url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    marketplace: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="completed", index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    evidence: Mapped[List["EvidenceModel"]] = relationship(
        "EvidenceModel", back_populates="investigation", cascade="all, delete-orphan"
    )
    report: Mapped[Optional["ReportModel"]] = relationship(
        "ReportModel",
        back_populates="investigation",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<InvestigationModel(id='{self.id}', marketplace='{self.marketplace}', status='{self.status}')>"
