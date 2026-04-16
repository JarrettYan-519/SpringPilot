import aiofiles
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.config import settings
from backend.models.fitness import TrainerPlan
from backend.models.system import UserConfig
from backend.schemas.fitness import TrainerPlanRead
from backend.services.mineru_service import MinerUService

router = APIRouter(prefix="/api/trainer-plans", tags=["trainer-plans"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md"}


@router.get("", response_model=list[TrainerPlanRead])
def list_plans(db: Session = Depends(get_db)):
    return db.query(TrainerPlan).order_by(TrainerPlan.created_at.desc()).all()


@router.post("", response_model=TrainerPlanRead, status_code=status.HTTP_201_CREATED)
async def upload_plan(
    title: str = Form(...),
    plan_date_range: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}. Allowed: {ALLOWED_EXTENSIONS}")

    # Save uploaded file
    save_path = os.path.join(settings.upload_dir, file.filename)
    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Get MinerU API key from settings
    mineru_config = db.query(UserConfig).filter(UserConfig.key == "mineru_api_key").first()
    mineru_key = mineru_config.value if mineru_config else None

    # Parse document
    service = MinerUService(api_key=mineru_key)
    try:
        parsed_content = await service.parse_file(save_path)
    except Exception as e:
        parsed_content = f"[解析失败: {str(e)}]"

    plan = TrainerPlan(
        title=title,
        file_path=save_path,
        parsed_content=parsed_content,
        plan_date_range=plan_date_range,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TrainerPlan).filter(TrainerPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
