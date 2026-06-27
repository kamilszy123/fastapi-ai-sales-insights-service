from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


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


class ToolDefinition(BaseModel):
    name: str
    description: str
    args_model: type[BaseModel]
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ToolCall(BaseModel):
    call_id: str
    name: str
    arguments: dict


class ToolCallsResult(BaseModel):
    type: Literal["tool_calls"] = "tool_calls"
    tool_calls: list[ToolCall]


class TextResult(BaseModel):
    type: Literal["text"] = "text"
    text: str


CompletionResult = Annotated[ToolCallsResult | TextResult, Field(discriminator="type")]


class AgenticAnswer(BaseModel):
    answer: str
    tool_calls: list[dict]


class AskQuestionRequest(BaseModel):
    question: str
