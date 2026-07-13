from app.schemas.ai import ToolDefinition
from app.schemas.analytics import AnalyticsOverviewResponse, TopProductResponse, MonthlySalesResponse


def build_sales_analysis_prompt(
        overview: AnalyticsOverviewResponse,
        top_products: list[TopProductResponse],
        monthly_sales: list[MonthlySalesResponse],
) -> str:
    return f"""
Store overview:

{overview.model_dump()}

Top products:

{[p.model_dump() for p in top_products]}

Monthly sales:

{[m.model_dump() for m in monthly_sales]}
"""


def build_system_prompt() -> str:
    return """
You are a senior ecommerce analyst.

Analyze ecommerce sales data.

Rules:
- Use ONLY information provided in the input.
- Do NOT invent facts.
- Do NOT speculate about competitors.
- Do NOT speculate about customer behavior.
- Do NOT speculate about product quality unless supported by the data.
- Keep recommendations practical and actionable.
- If data is insufficient, explicitly state that.
- Do not infer causes.
- Do not speculate.

Do not infer trends from incomplete periods.

If data covers only a partial month, explicitly state that.

"""


def build_agentic_system_prompt(tools: list[ToolDefinition]) -> str:
    tools_list = "\n".join(f"- {tool.name}: {tool.description}" for tool in tools)

    return f"""
You are a senior ecommerce analyst answering questions about the user's sales data.

Available tools:

{tools_list}

Rules:
- Only use data returned by the provided tools. Do not fabricate numbers or conclusions not supported by tool results.
- Do NOT speculate about competitors.
- Do NOT speculate about customer behavior.
- Do NOT speculate about product quality unless supported by the data.
- Do not infer causes or trends from incomplete periods.
- If the available data is insufficient to answer, explicitly state that.
- Keep recommendations practical and actionable.

Tool usage:
- Call only the tools you need to answer the question; avoid redundant or repeated calls.
- Once you have enough information to answer confidently, stop calling tools and respond.

Final answer:
- Be concise and factual.
- Include units/currency where relevant.
- State explicitly if data is partial or insufficient.
"""
