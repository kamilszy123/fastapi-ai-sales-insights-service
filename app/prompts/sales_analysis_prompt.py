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
