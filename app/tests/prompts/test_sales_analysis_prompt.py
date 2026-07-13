from pydantic import BaseModel

from app.prompts.sales_analysis_prompt import build_agentic_system_prompt
from app.schemas.ai import ToolDefinition


class _DummyArgs(BaseModel):
    limit: int = 5


def test_build_agentic_system_prompt_lists_tool_names_and_descriptions():
    tools = [
        ToolDefinition(
            name="get_top_products",
            description="Returns top-selling products ranked by revenue.",
            args_model=_DummyArgs,
        ),
        ToolDefinition(
            name="get_monthly_sales",
            description="Returns monthly revenue and order count.",
            args_model=_DummyArgs,
        ),
    ]

    prompt = build_agentic_system_prompt(tools)

    assert "get_top_products" in prompt
    assert "Returns top-selling products ranked by revenue." in prompt
    assert "get_monthly_sales" in prompt
    assert "Returns monthly revenue and order count." in prompt
