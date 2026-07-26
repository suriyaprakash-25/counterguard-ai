import pytest

from backend.exceptions import ToolExecutionError, ToolNotFoundError
from backend.tools import (
    MockBrandRegistryTool,
    MockExchangeRatesTool,
    MockGoogleSearchTool,
    MockMarketplaceAPITool,
    MockReverseImageSearchTool,
)
from backend.tools.base_tool import BaseTool
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
