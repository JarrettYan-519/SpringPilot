from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend.models.fitness import TrainingLog
from backend.schemas.fitness import TrainingLogCreate, TrainingLogUpdate, TrainingLogRead

router = APIRouter(prefix="/api/training", tags=["training"])


@router.post("", response_model=TrainingLogRead, status_code=status.HTTP_201_CREATED)
def create_log(payload: TrainingLogCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if data["recorded_at"] is None:
        data["recorded_at"] = datetime.utcnow()
    log = TrainingLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[TrainingLogRead])
def list_logs(limit: int = 30, db: Session = Depends(get_db)):
    return db.query(TrainingLog).order_by(TrainingLog.recorded_at.desc()).limit(limit).all()


@router.patch("/{log_id}", response_model=TrainingLogRead)
def update_log(log_id: int, payload: TrainingLogUpdate, db: Session = Depends(get_db)):
    log = db.query(TrainingLog).filter(TrainingLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Training log not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(TrainingLog).filter(TrainingLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Training log not found")
    db.delete(log)
    db.commit()
