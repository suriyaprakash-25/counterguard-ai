"""
case_management_service.py — Phase 1: Collaborative Investigation Case Management Service
Manages 7 case states, analyst assignments, comments, tags, attachments, and auditable history timelines.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from backend.schemas.case_management import (
    CaseAssignRequest,
    CaseCommentDTO,
    CaseCommentRequest,
    CaseStateUpdateRequest,
    CaseTimelineEventDTO,
    CollaborativeCaseDTO,
)

logger = logging.getLogger("counterguard.case_management_service")


class CaseManagementService:
    """
    Central Collaborative Case Management Service.
    Tracks investigation lifecycle across 7 states with full auditability.
    """

    VALID_STATES = [
        "Open",
        "Assigned",
        "Investigating",
        "Evidence Collected",
        "Legal Review",
        "Resolved",
        "Closed",
    ]

    def __init__(self):
        self._seed_cases()

    def _seed_cases(self):
        """Seed initial collaborative investigation cases."""
        now = datetime.utcnow()
        self._cases: Dict[str, CollaborativeCaseDTO] = {
            "INV-8901": CollaborativeCaseDTO(
                id="INV-8901",
                title="CMF Buds 2a Price Anomaly & Surat Syndicate Audit",
                product_name="CMF Buds 2a",
                state="Investigating",
                assignee="Lead Investigator",
                priority="CRITICAL",
                tags=["Surat Syndicate", "Price Anomaly", "Meesho"],
                comments=[
                    CaseCommentDTO(
                        id="c-1",
                        author="Lead Investigator",
                        text="Confirmed price drop -70% MSRP on Meesho.",
                        timestamp=(now - timedelta(hours=5)).isoformat(),
                    ),
                    CaseCommentDTO(
                        id="c-2",
                        author="RecommendationAgent",
                        text="AI Prescriptive Action: Issue Immediate Marketplace Takedown.",
                        timestamp=(now - timedelta(hours=2)).isoformat(),
                    ),
                ],
                attachments=["evidence_meesho_799.png", "surat_syndicate_graph.json"],
                history_timeline=[
                    CaseTimelineEventDTO(
                        event_id="t-1",
                        event_type="ACTION",
                        actor="System",
                        description="Case created via Proactive Continuous Scan.",
                        timestamp=(now - timedelta(days=1)).isoformat(),
                    ),
                    CaseTimelineEventDTO(
                        event_id="t-2",
                        event_type="STATE_CHANGE",
                        actor="Lead Investigator",
                        description="State updated to 'Assigned'.",
                        timestamp=(now - timedelta(hours=12)).isoformat(),
                    ),
                    CaseTimelineEventDTO(
                        event_id="t-3",
                        event_type="RECOMMENDATION",
                        actor="RecommendationAgent",
                        description="Prescriptive Recommendation: Issue Takedown & Escalate to Legal.",
                        timestamp=(now - timedelta(hours=2)).isoformat(),
                    ),
                    CaseTimelineEventDTO(
                        event_id="t-4",
                        event_type="STATE_CHANGE",
                        actor="Lead Investigator",
                        description="State updated to 'Investigating'.",
                        timestamp=(now - timedelta(minutes=30)).isoformat(),
                    ),
                ],
                created_at=(now - timedelta(days=1)).isoformat(),
                updated_at=(now - timedelta(minutes=30)).isoformat(),
                due_date=(now + timedelta(days=2)).isoformat(),
            ),
            "INV-8854": CollaborativeCaseDTO(
                id="INV-8854",
                title="Sony WH-1000XM5 OEM Clone Supplier Audit",
                product_name="Sony WH-1000XM5",
                state="Legal Review",
                assignee="Legal Counsel",
                priority="HIGH",
                tags=["TradeIndia", "Shenzhen Mfg", "OEM Clone"],
                comments=[
                    CaseCommentDTO(
                        id="c-3",
                        author="Legal Counsel",
                        text="Drafted formal Notice of Infringement.",
                        timestamp=(now - timedelta(hours=1)).isoformat(),
                    ),
                ],
                attachments=["tradeindia_bulk_quote.pdf"],
                history_timeline=[
                    CaseTimelineEventDTO(
                        event_id="t-5",
                        event_type="ACTION",
                        actor="System",
                        description="Case created.",
                        timestamp=(now - timedelta(days=2)).isoformat(),
                    ),
                    CaseTimelineEventDTO(
                        event_id="t-6",
                        event_type="STATE_CHANGE",
                        actor="Legal Counsel",
                        description="State updated to 'Legal Review'.",
                        timestamp=(now - timedelta(hours=1)).isoformat(),
                    ),
                ],
                created_at=(now - timedelta(days=2)).isoformat(),
                updated_at=(now - timedelta(hours=1)).isoformat(),
                due_date=(now + timedelta(days=1)).isoformat(),
            ),
        }

    def get_cases(self, filter_type: str = "all") -> List[CollaborativeCaseDTO]:
        """Fetch cases filtered by 'my_cases', 'team', 'high_priority', 'overdue', 'recently_updated'."""
        cases = list(self._cases.values())
        if filter_type == "my_cases":
            return [c for c in cases if c.assignee == "Lead Investigator"]
        elif filter_type == "high_priority":
            return [c for c in cases if c.priority in ["CRITICAL", "HIGH"]]
        elif filter_type == "overdue":
            now_iso = datetime.utcnow().isoformat()
            return [c for c in cases if c.due_date and c.due_date < now_iso]
        return cases

    def get_case_by_id(self, case_id: str) -> Optional[CollaborativeCaseDTO]:
        """Fetch a specific case by ID."""
        return self._cases.get(case_id)

    def update_case_state(
        self, case_id: str, request: CaseStateUpdateRequest
    ) -> CollaborativeCaseDTO:
        """Update case state through the 7 lifecycle states."""
        if case_id not in self._cases:
            raise ValueError(f"Case '{case_id}' not found.")
        if request.state not in self.VALID_STATES:
            raise ValueError(
                f"Invalid state '{request.state}'. Must be one of {self.VALID_STATES}"
            )

        case = self._cases[case_id]
        old_state = case.state
        case.state = request.state
        case.updated_at = datetime.utcnow().isoformat()

        # Add Timeline Event
        evt = CaseTimelineEventDTO(
            event_id=f"t-{int(datetime.utcnow().timestamp())}",
            event_type="STATE_CHANGE",
            actor="Lead Investigator",
            description=f"State transitioned from '{old_state}' to '{request.state}'. Notes: {request.notes or 'None'}",
        )
        case.history_timeline.insert(0, evt)
        logger.info(
            f"[CaseManagementService] Updated case {case_id} state to '{request.state}'."
        )
        return case

    def add_comment(self, case_id: str, request: CaseCommentRequest) -> CaseCommentDTO:
        """Add an analyst note/comment to a case."""
        if case_id not in self._cases:
            raise ValueError(f"Case '{case_id}' not found.")

        comment = CaseCommentDTO(
            id=f"c-{int(datetime.utcnow().timestamp())}",
            author=request.author,
            text=request.text,
        )
        case = self._cases[case_id]
        case.comments.append(comment)
        case.updated_at = datetime.utcnow().isoformat()

        # Add Timeline Event
        evt = CaseTimelineEventDTO(
            event_id=f"t-{int(datetime.utcnow().timestamp())}",
            event_type="COMMENT",
            actor=request.author,
            description=f"Posted note: {request.text}",
        )
        case.history_timeline.insert(0, evt)
        return comment

    def assign_case(
        self, case_id: str, request: CaseAssignRequest
    ) -> CollaborativeCaseDTO:
        """Reassign case to analyst."""
        if case_id not in self._cases:
            raise ValueError(f"Case '{case_id}' not found.")

        case = self._cases[case_id]
        old_assignee = case.assignee
        case.assignee = request.assignee
        if case.state == "Open":
            case.state = "Assigned"

        # Add Timeline Event
        evt = CaseTimelineEventDTO(
            event_id=f"t-{int(datetime.utcnow().timestamp())}",
            event_type="STATE_CHANGE",
            actor="Lead Investigator",
            description=f"Reassigned from '{old_assignee}' to '{request.assignee}'.",
        )
        case.history_timeline.insert(0, evt)
        return case


case_management_service = CaseManagementService()
