from abc import ABC, abstractmethod
from typing import List, Optional

from backend.models.evidence import EvidenceModel
from backend.models.investigation import InvestigationModel
from backend.models.report import ReportModel


class IInvestigationRepository(ABC):
    """
    Interface definition for Investigation persistent storage.
    """

    @abstractmethod
    def add(self, investigation: InvestigationModel) -> InvestigationModel:
        pass

    @abstractmethod
    def get_by_id(self, investigation_id: str) -> Optional[InvestigationModel]:
        pass

    @abstractmethod
    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        marketplace: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[InvestigationModel]:
        pass

    @abstractmethod
    def count(
        self,
        marketplace: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        pass

    @abstractmethod
    def update_status(
        self, investigation_id: str, status: str
    ) -> Optional[InvestigationModel]:
        pass

    @abstractmethod
    def delete(self, investigation_id: str) -> bool:
        pass


class IEvidenceRepository(ABC):
    """
    Interface definition for Evidence persistent storage.
    """

    @abstractmethod
    def add(self, evidence: EvidenceModel) -> EvidenceModel:
        pass

    @abstractmethod
    def add_batch(self, evidence_list: List[EvidenceModel]) -> List[EvidenceModel]:
        pass

    @abstractmethod
    def get_by_id(self, evidence_id: str) -> Optional[EvidenceModel]:
        pass

    @abstractmethod
    def get_by_investigation(self, investigation_id: str) -> List[EvidenceModel]:
        pass

    @abstractmethod
    def delete_by_investigation(self, investigation_id: str) -> int:
        pass


class IReportRepository(ABC):
    """
    Interface definition for Report persistent storage.
    """

    @abstractmethod
    def add(self, report: ReportModel) -> ReportModel:
        pass

    @abstractmethod
    def get_by_id(self, report_id: str) -> Optional[ReportModel]:
        pass

    @abstractmethod
    def get_by_investigation(self, investigation_id: str) -> Optional[ReportModel]:
        pass

    @abstractmethod
    def delete(self, report_id: str) -> bool:
        pass
