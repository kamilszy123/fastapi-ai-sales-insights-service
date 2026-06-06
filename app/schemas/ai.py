from pydantic import BaseModel


class SalesAnalysisResult(BaseModel):
    executive_summary: str
    sales_insights: list[str]
    return_analysis: list[str]
    risks: list[str]
    recommendations: list[str]


class AIUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str


class SalesAnalysisResponse(BaseModel):
    analysis: SalesAnalysisResult
    usage: AIUsage
