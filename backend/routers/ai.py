from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["ai"])


class JDAnalysisRequest(BaseModel):
    jd_text: str
    resume_text: str | None = None


class InterviewGenRequest(BaseModel):
    position: str
    jd_text: str
    question_count: int = 10


class MockInterviewRequest(BaseModel):
    history: list[dict]
    user_answer: str


class CalorieEstimateRequest(BaseModel):
    food_description: str


class DailyAdviceRequest(BaseModel):
    job_summary: str
    fitness_summary: str


@router.post("/analyze-jd")
async def analyze_jd(payload: JDAnalysisRequest, db: Session = Depends(get_db)):
    try:
        service = AIService(db)
        return await service.analyze_jd(payload.jd_text, payload.resume_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-questions")
async def generate_questions(payload: InterviewGenRequest, db: Session = Depends(get_db)):
    try:
        service = AIService(db)
        questions = await service.generate_interview_questions(
            payload.position, payload.jd_text, payload.question_count
        )
        return {"questions": questions}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mock-interview")
async def mock_interview(payload: MockInterviewRequest, db: Session = Depends(get_db)):
    try:
        service = AIService(db)
        reply = await service.mock_interview_reply(payload.history, payload.user_answer)
        return {"reply": reply}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/estimate-calories")
async def estimate_calories(payload: CalorieEstimateRequest, db: Session = Depends(get_db)):
    try:
        service = AIService(db)
        calories = await service.estimate_calories(payload.food_description)
        return {"calories": calories}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/daily-advice")
async def daily_advice(payload: DailyAdviceRequest, db: Session = Depends(get_db)):
    try:
        service = AIService(db)
        advice = await service.daily_advice(payload.job_summary, payload.fitness_summary)
        return {"advice": advice}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
