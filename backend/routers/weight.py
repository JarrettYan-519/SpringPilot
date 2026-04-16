from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend.models.fitness import WeightRecord
from backend.schemas.fitness import WeightRecordCreate, WeightRecordRead

router = APIRouter(prefix="/api/weight", tags=["weight"])


@router.post("", response_model=WeightRecordRead, status_code=status.HTTP_201_CREATED)
def create_record(payload: WeightRecordCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if data["recorded_at"] is None:
        data["recorded_at"] = datetime.utcnow()
    record = WeightRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[WeightRecordRead])
def list_records(limit: int = 90, db: Session = Depends(get_db)):
    return db.query(WeightRecord).order_by(WeightRecord.recorded_at.desc()).limit(limit).all()


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(WeightRecord).filter(WeightRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
