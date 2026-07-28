from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.investigation import InvestigationModel
from backend.models.report import ReportModel
from backend.models.evidence import EvidenceModel


class AnalyticsRepository:
    def __init__(self, session: Session = None):
        self._session = session

    def get_dashboard_data(self) -> Dict[str, Any]:
        if not self._session:
            return self._empty_analytics()

        # 1. 7-Day Trend: d (date), c (count), r (avg risk)
        today = datetime.utcnow().date()
        trends = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = datetime(day.year, day.month, day.day)
            day_end = day_start + timedelta(days=1)

            inv_count = (
                self._session.query(func.count(InvestigationModel.id))
                .filter(
                    InvestigationModel.created_at >= day_start,
                    InvestigationModel.created_at < day_end,
                )
                .scalar()
                or 0
            )

            risk_rows = (
                self._session.query(ReportModel.risk_score)
                .join(InvestigationModel, ReportModel.investigation_id == InvestigationModel.id)
                .filter(
                    InvestigationModel.created_at >= day_start,
                    InvestigationModel.created_at < day_end,
                )
                .all()
            )
            scores = [r[0] for r in risk_rows if r[0] is not None]
            avg_risk = round(sum(scores) / len(scores)) if scores else 0

            trends.append({
                "d": day.strftime("%b %d"),
                "c": inv_count,
                "r": avg_risk
            })

        # 2. Marketplace Distribution: n (name), v (value)
        mp_results = (
            self._session.query(
                InvestigationModel.marketplace,
                func.count(InvestigationModel.id).label("count")
            )
            .group_by(InvestigationModel.marketplace)
            .all()
        )
        marketplaces = [{"n": row.marketplace, "v": row.count} for row in mp_results]
        if not marketplaces:
            marketplaces = [
                {"n": "Amazon", "v": 0},
                {"n": "eBay", "v": 0},
                {"n": "Walmart", "v": 0},
                {"n": "AliExpress", "v": 0},
            ]

        # 3. Agent Utilization: n (name), v (value)
        agent_results = (
            self._session.query(
                EvidenceModel.agent,
                func.count(EvidenceModel.id).label("count")
            )
            .group_by(EvidenceModel.agent)
            .all()
        )
        agents = [{"n": row.agent, "v": row.count} for row in agent_results]
        if not agents:
            agents = [
                {"n": "PlanningAgent", "v": 0},
                {"n": "ScrapingService", "v": 0},
                {"n": "PriceAgent", "v": 0},
                {"n": "SellerAgent", "v": 0},
                {"n": "BrandAgent", "v": 0},
                {"n": "ReviewAgent", "v": 0},
                {"n": "CoordinatorAgent", "v": 0},
            ]

        # 4. Top Brands: n (name), v (value)
        brand_results = (
            self._session.query(
                ReportModel.seller,
                func.count(ReportModel.id).label("count")
            )
            .filter(ReportModel.seller != None, ReportModel.seller != "")
            .group_by(ReportModel.seller)
            .limit(5)
            .all()
        )
        brands = [{"n": row.seller, "v": row.count} for row in brand_results]

        return {
            "trends": trends,
            "marketplaces": marketplaces,
            "agents": agents,
            "brands": brands
        }

    def _empty_analytics(self) -> Dict[str, Any]:
        return {
            "trends": [],
            "marketplaces": [
                {"n": "Amazon", "v": 0},
                {"n": "eBay", "v": 0},
                {"n": "Walmart", "v": 0},
                {"n": "AliExpress", "v": 0},
            ],
            "agents": [
                {"n": "PlanningAgent", "v": 0},
                {"n": "ScrapingService", "v": 0},
                {"n": "PriceAgent", "v": 0},
                {"n": "SellerAgent", "v": 0},
                {"n": "BrandAgent", "v": 0},
                {"n": "ReviewAgent", "v": 0},
                {"n": "CoordinatorAgent", "v": 0},
            ],
            "brands": []
        }
