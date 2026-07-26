import time

import pytest

from backend.agents.specialists import BrandAgent, SellerAgent
from backend.schemas.scraping import ParsedListing, ScrapingResult
from backend.state import InvestigationState
from backend.tools.base import global_cache, global_rate_limiter, metrics_collector
from backend.tools.exceptions import (
    ToolRateLimitError,
    ToolTimeoutError,
    ToolTransientError,
)
from backend.tools.mocks import (
    MockProductCatalogTool,
    MockSellerReputationTool,
    MockTrademarkTool,
    MockWhoisTool,
    TrademarkInput,
    WhoisInput,
)
from backend.tools.registry import ToolRegistry


@pytest.fixture(autouse=True)
def reset_infrastructure():
    global_cache.clear()
    global_rate_limiter.requests.clear()
    metrics_collector.clear()
    yield


def test_registry_register_and_lookup():
    registry = ToolRegistry()
    tool = MockTrademarkTool()
    registry.register(tool)

    retrieved = registry.get_tool("trademark_lookup")
    assert retrieved == tool


def test_registry_lookup_missing():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="is not registered"):
        registry.get_tool("missing_tool")


def test_agent_multi_tool_execution():
    tool1 = MockTrademarkTool()
    tool2 = MockProductCatalogTool()

    agent = BrandAgent(tools=[tool1, tool2])

    state: InvestigationState = {
        "scraping_result": ScrapingResult(
            success=True, listing=ParsedListing(brand="Nike", title="Air Force 1")
        )
    }

    prompt_data, state_updates = agent._execute_tools(state)
    assert prompt_data is not None
    assert "trademark_lookup" in prompt_data
    assert "product_catalog" in prompt_data

    assert prompt_data["trademark_lookup"]["is_registered"] is True
    assert prompt_data["product_catalog"]["in_catalog"] is True


def test_agent_partial_tool_failure(mocker):
    tool1 = MockWhoisTool()
    tool2 = MockSellerReputationTool()

    agent = SellerAgent(tools=[tool1, tool2])

    state: InvestigationState = {
        "scraping_result": ScrapingResult(
            success=True, listing=ParsedListing(seller_name="Amazon")
        )
    }

    # Induce a crash in the first tool only (in `run`, which `execute` wraps)
    mocker.patch.object(tool1, "run", side_effect=Exception("API limit exceeded"))

    prompt_data, state_updates = agent._execute_tools(state)

    assert prompt_data is not None
    assert "whois_lookup" not in prompt_data
    assert "seller_reputation" in prompt_data


def test_tool_cache():
    tool = MockWhoisTool()
    input_data = WhoisInput(domain="amazon")

    # First execution should cache it
    out1 = tool.execute(input_data)
    assert out1.domain_age_days == 5000

    # Second execution should hit the cache. We can test this by mocking run
    from unittest import mock

    with mock.patch.object(tool, "run") as mock_run:
        out2 = tool.execute(input_data)
        mock_run.assert_not_called()
        assert out2.domain_age_days == 5000


def test_tool_retry_success(mocker):
    tool = MockTrademarkTool()
    input_data = TrademarkInput(brand_name="Nike")

    call_count = 0
    original_run = tool.run

    def flaky_run(inp):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ToolTransientError("Temporary network glitch")
        return original_run(inp)

    mocker.patch.object(tool, "run", side_effect=flaky_run)

    # Tool max retries default to 3. Should succeed on 3rd attempt
    out = tool.execute(input_data)

    assert out.is_registered is True
    assert call_count == 3
    assert metrics_collector.retry_count[tool.name] == 2
    assert metrics_collector.success_count[tool.name] == 1


def test_tool_timeout(mocker):
    tool = MockTrademarkTool()
    input_data = TrademarkInput(brand_name="Nike")

    def slow_run(inp):
        time.sleep(15)  # Default timeout is 10s
        return tool.output_schema()

    mocker.patch.object(tool, "run", side_effect=slow_run)
    mocker.patch(
        "backend.tools.base.tool_settings.tool_timeout_seconds", 1
    )  # Speed up test

    with pytest.raises(ToolTimeoutError):
        tool.execute(input_data)

    assert metrics_collector.timeout_count[tool.name] == 1


def test_tool_rate_limit(mocker):
    tool = MockTrademarkTool()
    input_data = TrademarkInput(brand_name="Nike")

    # Lower limit to 2 for this test
    mocker.patch.object(global_rate_limiter, "max_requests", 2)

    # First two should succeed
    tool.execute(input_data)
    tool.execute(input_data)

    # Third should raise rate limit error
    with pytest.raises(ToolRateLimitError):
        tool.execute(input_data)

    assert metrics_collector.failure_count[tool.name] == 1
