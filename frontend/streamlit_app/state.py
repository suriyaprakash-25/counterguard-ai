"""
Session state management utilities for the CounterGuard Streamlit frontend.
Provides typed getter and setter abstractions over st.session_state.
"""

from typing import Optional

import streamlit as st

from frontend.streamlit_app.models.investigation import InvestigationState

_INVESTIGATION_KEY = "investigation_data"


def get_current_investigation() -> Optional[InvestigationState]:
    """
    Retrieve the active typed investigation model from user session state.

    Returns:
        The current InvestigationState instance, or None if unassigned.
    """
    data = st.session_state.get(_INVESTIGATION_KEY)
    if isinstance(data, dict):
        # Convert dictionary to Pydantic model on the fly using v2 model_validate
        typed_data = InvestigationState.model_validate(data)
        st.session_state[_INVESTIGATION_KEY] = typed_data
        return typed_data
    return data if isinstance(data, InvestigationState) else None


def set_current_investigation(investigation: InvestigationState) -> None:
    """
    Store a validated investigation model into the current user session state.

    Args:
        investigation: Active Pydantic representation of the state.
    """
    st.session_state[_INVESTIGATION_KEY] = investigation


def clear_current_investigation() -> None:
    """Evict the active investigation state from session storage."""
    if _INVESTIGATION_KEY in st.session_state:
        del st.session_state[_INVESTIGATION_KEY]
