from pydantic import BaseModel


class SalesAnalysisResult(BaseModel):
    executive_summary: str
    sales_insights: list[str]
    return_analysis: list[str]
    risks: list[str]
    recommendations: list[str]
