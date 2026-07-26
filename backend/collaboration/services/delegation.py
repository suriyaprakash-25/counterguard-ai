from backend.collaboration.models.context import InvestigationContext
from backend.collaboration.models.protocol import InvestigationTask, TaskPriority


class DelegationService:
    """
    Analyzes the Investigation Blackboard to assign follow-up tasks to specific agents.
    """

    def evaluate_and_delegate(self, context: InvestigationContext) -> None:
        """
        Reads open questions, hypotheses, and evidence to spawn tasks.
        """
        for question in context.unresolved_questions:
            if not question.is_resolved:
                # Naive routing based on keywords
                assigned_agent = self._route_question(question.content)

                # Check if task already exists
                task_exists = any(
                    t.description == question.content for t in context.tasks
                )

                if not task_exists:
                    new_task = InvestigationTask(
                        description=f"Resolve Question: {question.content}",
                        assigned_agent=assigned_agent,
                        created_by="DelegationService",
                        priority=TaskPriority.HIGH,
                    )
                    context.tasks.append(new_task)

    def _route_question(self, content: str) -> str:
        """Simple keyword-based router for delegation."""
        content_lower = content.lower()
        if "price" in content_lower or "discount" in content_lower:
            return "PriceAgent"
        elif "seller" in content_lower or "domain" in content_lower:
            return "SellerAgent"
        elif "brand" in content_lower or "trademark" in content_lower:
            return "BrandAgent"
        elif "image" in content_lower or "review" in content_lower:
            return "ReviewAgent"
        return "CoordinatorAgent"
