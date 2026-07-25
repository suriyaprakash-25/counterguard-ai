import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.investigation import InvestigationModel


class EvidenceModel(Base):
    """
    ORM model representing an investigation evidence artifact or timeline event.
    """

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    investigation_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_delta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)

    investigation: Mapped["InvestigationModel"] = relationship(
        "InvestigationModel", back_populates="evidence"
    )

    def __repr__(self) -> str:
        return f"<EvidenceModel(id='{self.id}', agent='{self.agent}', action='{self.action}')>"
