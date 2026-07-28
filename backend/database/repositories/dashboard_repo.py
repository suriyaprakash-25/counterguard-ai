from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.infrastructure.graph.neo4j_client import Neo4jClient
from backend.models.investigation import InvestigationModel
from backend.models.alert import AlertModel


class DashboardRepository:
    def __init__(self, session: Session, neo4j_client: Neo4jClient):
        self._session = session
        self._neo4j = neo4j_client

    def get_summary_metrics(self) -> Dict[str, Any]:
        active_investigations = self._session.query(InvestigationModel).filter(InvestigationModel.status == "in_progress").count()
        active_alerts = self._session.query(AlertModel).count()

        # We can query neo4j for high risk sellers and fraud rings
        # For a hackathon/MVP, if neo4j doesn't have these, return 0
        high_risk_sellers = 0
        fraud_rings = 0
        try:
            with self._neo4j.driver.session(database=self._neo4j.database) as session:
                result = session.run("MATCH (s:Seller) WHERE s.risk_score >= 80 RETURN count(s) as count")
                high_risk_sellers = result.single()["count"]
        except Exception:
            pass

        return {
            "activeInvestigations": active_investigations,
            "activeAlerts": active_alerts,
            "highRiskSellers": high_risk_sellers,
            "fraudRingsDetected": fraud_rings,
            "investigationTrend": 0.0,
            "alertTrend": 0.0,
            "sellerTrend": 0.0,
            "ringTrend": 0.0,
        }

    def get_marketplace_metrics(self) -> List[Dict[str, Any]]:
        results = (
            self._session.query(
                InvestigationModel.marketplace,
                func.count(InvestigationModel.id).label("count")
            )
            .group_by(InvestigationModel.marketplace)
            .all()
        )

        metrics = []
        for row in results:
            metrics.append({
                "name": row.marketplace,
                "investigations": row.count,
            })
        return metrics

    def get_risk_trend(self) -> List[Dict[str, Any]]:
        from datetime import date, timedelta
        from backend.models.report import ReportModel

        trend = []
        today = datetime.utcnow().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = datetime(day.year, day.month, day.day)
            day_end = day_start + timedelta(days=1)
            rows = (
                self._session.query(ReportModel.risk_score)
                .join(InvestigationModel, ReportModel.investigation_id == InvestigationModel.id)
                .filter(
                    InvestigationModel.created_at >= day_start,
                    InvestigationModel.created_at < day_end,
                )
                .all()
            )
            scores = [r[0] for r in rows if r[0] is not None]
            avg_risk = round(sum(scores) / len(scores)) if scores else 0
            trend.append({"date": day.isoformat(), "avgRisk": avg_risk, "count": len(scores)})
        return trend

    def get_fraud_node_preview(self) -> List[Dict[str, Any]]:
        nodes = []
        try:
            with self._neo4j.driver.session(database=self._neo4j.database) as session:
                result = session.run("MATCH (n:Seller) RETURN n.id as id, n.name as label LIMIT 3")
                for record in result:
                    nodes.append({
                        "id": record["id"],
                        "type": "seller",
                        "label": record["label"] or record["id"]
                    })
        except Exception:
            pass
        return nodes
