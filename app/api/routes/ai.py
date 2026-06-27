from fastapi import APIRouter, Depends

from app.core.dependencies import get_ai_analysis_service, get_agentic_analysis_service
from app.core.security import get_current_user
from app.models import User
from app.schemas.ai import AgenticAnswer, AskQuestionRequest, SalesAnalysisResponse
from app.services.agentic_analysis_service import AgenticAnalysisService
from app.services.ai_analysis_service import AIAnalysisService

router = APIRouter(prefix="/ai")


@router.post("/sales-analysis", response_model=SalesAnalysisResponse)
async def analyze_sales(
        current_user: User = Depends(get_current_user),
        ai_analysis_service: AIAnalysisService = Depends(get_ai_analysis_service)
):
    return await ai_analysis_service.analyze_sales(current_user.id)


@router.post("/ask", response_model=AgenticAnswer)
async def ask(
        request: AskQuestionRequest,
        current_user: User = Depends(get_current_user),
        service: AgenticAnalysisService = Depends(get_agentic_analysis_service),
):
    return await service.run(request.question, user_id=current_user.id)
