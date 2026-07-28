import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.investigation import InvestigationModel
from backend.models.report import ReportModel
from backend.models.evidence import EvidenceModel


class IntelligenceRepository:
    """
    Provides intelligence data derived from completed investigations,
    reports, and evidence stored in the SQLite database.
    Falls back to safe empty structures when no data exists yet.
    """

    def __init__(self, session: Session = None):
        self._session = session

    def get_summary(self) -> Dict[str, Any]:
        if not self._session:
            return self._empty_summary()

        total_investigations = self._session.query(func.count(InvestigationModel.id)).scalar() or 0
        total_reports = self._session.query(func.count(ReportModel.id)).scalar() or 0

        # Unique sellers extracted from reports
        sellers = self._session.query(ReportModel.seller).distinct().all()
        total_sellers = len([s for s in sellers if s[0]])

        return {
            "knownSellers": total_sellers,
            "knownFraudRings": 0,
            "knownCounterfeitListings": total_reports,
            "repeatedAssets": 0,
            "historicalInvestigations": total_investigations,
            "memoryEpisodes": total_investigations,
            "graphNodes": 0,
            "graphRelationships": 0,
        }

    def get_sellers(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self._session:
            return []

        reports = (
            self._session.query(ReportModel)
            .filter(ReportModel.seller != None, ReportModel.seller != "")
            .limit(limit)
            .all()
        )
        seen = set()
        sellers = []
        for i, r in enumerate(reports):
            if r.seller not in seen:
                seen.add(r.seller)
                risk = r.risk_score or 0
                sellers.append({
                    "id": f"seller-{i}",
                    "name": r.seller,
                    "marketplace": r.marketplace,
                    "riskScore": risk,
                    "historicalInvestigations": 1,
                    "status": "banned" if risk > 80 else ("monitoring" if risk > 50 else "active"),
                    "lastSeen": r.investigation_timestamp,
                })
        return sellers

    def get_fraud_rings(self) -> List[Dict[str, Any]]:
        # Fraud rings require Neo4j graph data — return empty list until populated
        return []

    def get_known_patterns(self) -> List[Dict[str, Any]]:
        if not self._session:
            return []

        findings_rows = (
            self._session.query(ReportModel.findings)
            .filter(ReportModel.findings != None, ReportModel.findings != "[]")
            .limit(50)
            .all()
        )

        import json
        pattern_counts: Dict[str, int] = {}
        for row in findings_rows:
            try:
                findings = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                for finding in findings:
                    pattern_counts[finding] = pattern_counts.get(finding, 0) + 1
            except Exception:
                pass

        patterns = []
        for i, (title, count) in enumerate(sorted(pattern_counts.items(), key=lambda x: -x[1])[:20]):
            patterns.append({
                "id": f"pattern-{i}",
                "type": "behavioral",
                "title": title,
                "description": title,
                "occurrences": count,
            })
        return patterns

    def get_repeated_images(self) -> List[Dict[str, Any]]:
        return []  # Requires image fingerprint data from Neo4j

    def get_repeated_phones(self) -> List[Dict[str, Any]]:
        return []  # Requires entity extraction data

    def get_repeated_invoices(self) -> List[Dict[str, Any]]:
        return []  # Requires entity extraction data

    def get_memory_insights(self) -> List[Dict[str, Any]]:
        if not self._session:
            return []

        reports = (
            self._session.query(ReportModel)
            .filter(ReportModel.ai_summary != None, ReportModel.ai_summary != "")
            .limit(10)
            .all()
        )

        insights = []
        for i, r in enumerate(reports):
            insights.append({
                "id": f"insight-{i}",
                "title": f"{r.risk_level} Risk — {r.product}",
                "description": r.ai_summary,
                "context": f"From investigation on {r.marketplace}",
                "confidence": int(r.confidence * 100) if r.confidence else 0,
            })
        return insights

    def _empty_summary(self) -> Dict[str, Any]:
        return {
            "knownSellers": 0,
            "knownFraudRings": 0,
            "knownCounterfeitListings": 0,
            "repeatedAssets": 0,
            "historicalInvestigations": 0,
            "memoryEpisodes": 0,
            "graphNodes": 0,
            "graphRelationships": 0,
        }
