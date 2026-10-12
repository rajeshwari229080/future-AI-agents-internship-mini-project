from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AIQuestionRequest, AIAnswerResponse
from app.services import ollama_service

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post(
    "/ask",
    response_model=AIAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask AI Assistant about student records",
    description="Processes natural-language queries grounded safely in student database context.",
)
async def ask_ai(
    request: AIQuestionRequest,
    db: Session = Depends(get_db)
):
    return await ollama_service.process_ai_question(request.question, db)


@router.get(
    "/status",
    summary="Check Ollama service status",
    description="Returns connectivity status of the local Ollama daemon.",
)
async def get_ai_status():
    return await ollama_service.check_ollama_availability()
