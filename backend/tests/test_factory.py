import pytest

from backend.exceptions import InvalidListingError
from backend.services.investigation_factory import InvestigationFactory


def test_create_state_valid():
    state = InvestigationFactory.create_state("LISTING-123", {"price": 100})
    assert state["listing_id"] == "LISTING-123"
    assert state["listing_data"]["price"] == 100
    assert state["evidence_timeline"] == []
    assert state["confidence_score"] == 0.0


def test_create_state_invalid_id():
    with pytest.raises(InvalidListingError):
        InvestigationFactory.create_state("")
    with pytest.raises(InvalidListingError):
        InvestigationFactory.create_state(None)
