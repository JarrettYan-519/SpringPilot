from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from backend.database import get_db
from backend.models.fitness import DietLog
from backend.schemas.fitness import DietLogCreate, DietLogRead

router = APIRouter(prefix="/api/diet", tags=["diet"])


@router.post("", response_model=DietLogRead, status_code=status.HTTP_201_CREATED)
def create_log(payload: DietLogCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if data["recorded_at"] is None:
        data["recorded_at"] = datetime.utcnow()
    log = DietLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[DietLogRead])
def list_logs(day: date | None = None, db: Session = Depends(get_db)):
    query = db.query(DietLog)
    if day:
        start = datetime(day.year, day.month, day.day)
        end = datetime(day.year, day.month, day.day, 23, 59, 59)
        query = query.filter(DietLog.recorded_at.between(start, end))
    return query.order_by(DietLog.recorded_at.desc()).all()


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(DietLog).filter(DietLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Diet log not found")
    db.delete(log)
    db.commit()
