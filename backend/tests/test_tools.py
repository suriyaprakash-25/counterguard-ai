import time
from unittest import mock

import pytest

from backend.agents.specialists import BrandAgent, SellerAgent
from backend.exceptions import ToolExecutionError, ToolNotFoundError
from backend.schemas.scraping import ParsedListing, ScrapingResult
from backend.state import InvestigationState
from backend.tools import (
    MockBrandRegistryTool,
    MockExchangeRatesTool,
    MockGoogleSearchTool,
    MockMarketplaceAPITool,
    MockReverseImageSearchTool,
)
from backend.tools.base import global_cache, global_rate_limiter, metrics_collector
from backend.tools.base_tool import BaseTool
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
from backend.tools.registry import ToolRegistry as InstanceToolRegistry
from backend.tools.tool_registry import ToolRegistry


class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy_tool"

    @property
    def description(self) -> str:
        return "A dummy tool for testing purposes."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        }

    def run(self, **kwargs) -> dict:
        value = kwargs.get("value")
        if not value:
            raise ToolExecutionError("Missing required argument: 'value'")
        return {"result": f"processed_{value}"}


@pytest.fixture(autouse=True)
def restore_registry():
    """Backup and restore ToolRegistry state between tests to avoid side effects."""
    existing = dict(ToolRegistry._tools)
    yield
    ToolRegistry._tools = existing


@pytest.fixture(autouse=True)
def reset_infrastructure():
    global_cache.clear()
    global_rate_limiter.requests.clear()
    metrics_collector.clear()
    yield


def test_base_tool_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseTool()


def test_dummy_tool_execution_and_schema():
    tool = DummyTool()
    assert tool.name == "dummy_tool"
    assert tool.description == "A dummy tool for testing purposes."
    schema = tool.to_schema()
    assert schema["name"] == "dummy_tool"
    assert "parameters" in schema

    res = tool.run(value="test_item")
    assert res == {"result": "processed_test_item"}

    with pytest.raises(ToolExecutionError):
        tool.run()


def test_tool_registry_registration_and_retrieval():
    ToolRegistry.clear()
    assert ToolRegistry.list_tools() == []

    ToolRegistry.register_tool(DummyTool)
    assert ToolRegistry.list_tools() == ["dummy_tool"]

    cls = ToolRegistry.get_tool("dummy_tool")
    assert cls is DummyTool

    instance = ToolRegistry.create_tool("dummy_tool")
    assert isinstance(instance, DummyTool)


def test_tool_registry_missing_tool():
    ToolRegistry.clear()
    with pytest.raises(ToolNotFoundError):
        ToolRegistry.get_tool("non_existent_tool")
    with pytest.raises(ToolNotFoundError):
        ToolRegistry.create_tool("non_existent_tool")


def test_tool_registry_register_with_explicit_name():
    ToolRegistry.clear()

    @ToolRegistry.register(name="custom_name_tool")
    class AnotherTool(DummyTool):
        pass

    assert "custom_name_tool" in ToolRegistry.list_tools()
    assert "dummy_tool" not in ToolRegistry.list_tools()


def test_tool_registry_schemas():
    ToolRegistry.clear()
    ToolRegistry.register_tool(DummyTool)
    schemas = ToolRegistry.get_tool_schemas()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "dummy_tool"


def test_mock_marketplace_api_tool():
    tool = MockMarketplaceAPITool()
    assert tool.name == "marketplace_api"
    with pytest.raises(ToolExecutionError):
        tool.run()
    result = tool.run(listing_id="B08N5WRWNW", marketplace="Amazon")
    assert result["listing_id"] == "B08N5WRWNW"
    assert result["marketplace"] == "amazon"
    assert "seller_info" in result
    assert result["status"] == "active"


def test_mock_brand_registry_tool():
    tool = MockBrandRegistryTool()
    assert tool.name == "brand_registry"
    with pytest.raises(ToolExecutionError):
        tool.run()
    result_auth = tool.run(brand_name="Nike", seller_name="Official Nike Shop")
    assert result_auth["is_authorized_reseller"] is True

    result_unauth = tool.run(brand_name="Nike", seller_name="Unauthorized Fake Shop")
    assert result_unauth["is_authorized_reseller"] is False


def test_mock_google_search_tool():
    tool = MockGoogleSearchTool()
    assert tool.name == "google_search"
    with pytest.raises(ToolExecutionError):
        tool.run()
    result = tool.run(query="Nike Air Force 1 fake checks", num_results=2)
    assert result["query"] == "Nike Air Force 1 fake checks"
    assert len(result["results"]) == 2


def test_mock_exchange_rates_tool():
    tool = MockExchangeRatesTool()
    assert tool.name == "exchange_rates"
    with pytest.raises(ToolExecutionError):
        tool.run()
    result = tool.run(base_currency="USD", target_currency="EUR", amount=100)
    assert result["base_currency"] == "USD"
    assert result["target_currency"] == "EUR"
    assert "rate" in result
    assert result["original_amount"] == 100
    assert "converted_amount" in result


def test_mock_reverse_image_search_tool():
    tool = MockReverseImageSearchTool()
    assert tool.name == "reverse_image_search"
    with pytest.raises(ToolExecutionError):
        tool.run()
    result = tool.run(
        image_url="https://example.com/shoe.jpg", similarity_threshold=0.90
    )
    assert result["queried_image_url"] == "https://example.com/shoe.jpg"
    assert result["matches_found"] >= 1
    for match in result["matches"]:
        assert match["similarity_score"] >= 0.90


def test_registry_register_and_lookup():
    registry = InstanceToolRegistry()
    tool = MockTrademarkTool()
    registry.register(tool)

    retrieved = registry.get_tool("trademark_lookup")
    assert retrieved == tool


def test_registry_lookup_missing():
    registry = InstanceToolRegistry()
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


def test_agent_partial_tool_failure():
    tool1 = MockWhoisTool()
    tool2 = MockSellerReputationTool()

    agent = SellerAgent(tools=[tool1, tool2])

    state: InvestigationState = {
        "scraping_result": ScrapingResult(
            success=True, listing=ParsedListing(seller_name="Amazon")
        )
    }

    # Induce a crash in the first tool only (in `run`, which `execute` wraps)
    with mock.patch.object(tool1, "run", side_effect=Exception("API limit exceeded")):
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
    with mock.patch.object(tool, "run") as mock_run:
        out2 = tool.execute(input_data)
        mock_run.assert_not_called()
        assert out2.domain_age_days == 5000


def test_tool_retry_success():
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

    with mock.patch.object(tool, "run", side_effect=flaky_run):
        # Tool max retries default to 3. Should succeed on 3rd attempt
        out = tool.execute(input_data)

    assert out.is_registered is True
    assert call_count == 3
    assert metrics_collector.retry_count[tool.name] == 2
    assert metrics_collector.success_count[tool.name] == 1


def test_tool_timeout():
    tool = MockTrademarkTool()
    input_data = TrademarkInput(brand_name="Nike")

    def slow_run(inp):
        time.sleep(15)  # Default timeout is 10s
        return tool.output_schema()

    with (
        mock.patch.object(tool, "run", side_effect=slow_run),
        mock.patch("backend.tools.base.tool_settings.tool_timeout_seconds", 1),
    ):  # Speed up test
        with pytest.raises(ToolTimeoutError):
            tool.execute(input_data)

    assert metrics_collector.timeout_count[tool.name] == 1


def test_tool_rate_limit():
    tool = MockTrademarkTool()
    input_data = TrademarkInput(brand_name="Nike")

    # Lower limit to 2 for this test
    with mock.patch.object(global_rate_limiter, "max_requests", 2):
        # First two should succeed
        tool.execute(input_data)
        tool.execute(input_data)

        # Third should raise rate limit error
        with pytest.raises(ToolRateLimitError):
            tool.execute(input_data)

    assert metrics_collector.failure_count[tool.name] == 1
