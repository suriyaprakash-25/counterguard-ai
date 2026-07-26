from datetime import datetime
from typing import Any, Dict, List


class TimelineService:
    """
    Maintains a chronological, append-only history of the investigation for replay and debugging.
    """

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def record_event(
        self, event_type: str, actor: str, details: str, metadata: Dict[str, Any] = None
    ) -> None:
        """
        Records an event to the timeline.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "actor": actor,
            "details": details,
            "metadata": metadata or {},
        }
        self.events.append(event)

    def get_timeline(self) -> List[Dict[str, Any]]:
        return self.events
