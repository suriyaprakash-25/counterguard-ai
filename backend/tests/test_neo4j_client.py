from unittest.mock import MagicMock, patch

import pytest

from backend.infrastructure.graph.neo4j_client import Neo4jClient
from backend.settings import settings


@pytest.fixture
def mock_neo4j_driver():
    with patch(
        "backend.infrastructure.graph.neo4j_client.GraphDatabase.driver"
    ) as mock_driver:
        yield mock_driver


@patch("backend.infrastructure.graph.neo4j_client.NEO4J_AVAILABLE", True)
def test_neo4j_client_successful_connect(mock_neo4j_driver):
    mock_instance = MagicMock()
    mock_neo4j_driver.return_value = mock_instance

    client = Neo4jClient()
    result = client.connect()

    assert result is True
    assert client.is_connected is True
    assert client.driver == mock_instance
    mock_neo4j_driver.assert_called_once_with(
        settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    mock_instance.verify_connectivity.assert_called_once()

    # Should create constraints
    assert mock_instance.session.call_count == 1


@patch("backend.infrastructure.graph.neo4j_client.NEO4J_AVAILABLE", True)
def test_neo4j_client_connection_failure(mock_neo4j_driver):
    mock_instance = MagicMock()
    # Simulate a ServiceUnavailable or network error on connect
    mock_instance.verify_connectivity.side_effect = Exception("Service Unavailable")
    mock_neo4j_driver.return_value = mock_instance

    client = Neo4jClient()
    result = client.connect()

    assert result is False
    assert client.is_connected is False
    assert client.driver is None
    mock_neo4j_driver.assert_called_once()


@patch("backend.infrastructure.graph.neo4j_client.NEO4J_AVAILABLE", False)
def test_neo4j_client_unavailable_driver():
    client = Neo4jClient()
    result = client.connect()

    assert result is False
    assert client.is_connected is False
    assert client.driver is None


def test_neo4j_client_session_without_connect():
    client = Neo4jClient()
    with pytest.raises(RuntimeError, match="Neo4j client is not connected."):
        client.session()


@patch("backend.infrastructure.graph.neo4j_client.NEO4J_AVAILABLE", True)
def test_neo4j_client_session_success(mock_neo4j_driver):
    mock_instance = MagicMock()
    mock_neo4j_driver.return_value = mock_instance

    client = Neo4jClient()
    client.connect()

    # Test session creation
    mock_session = MagicMock()
    mock_instance.session.return_value = mock_session

    session = client.session()

    assert session == mock_session
    # Verify the configured database was requested
    mock_instance.session.assert_called_with(database=settings.NEO4J_DATABASE)
