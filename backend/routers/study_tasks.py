from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.job import StudyTask
from backend.schemas.job import StudyTaskCreate, StudyTaskUpdate, StudyTaskRead

router = APIRouter(prefix="/api/study-tasks", tags=["study-tasks"])


@router.post("", response_model=StudyTaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: StudyTaskCreate, db: Session = Depends(get_db)):
    task = StudyTask(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[StudyTaskRead])
def list_tasks(completed: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(StudyTask)
    if completed is not None:
        query = query.filter(StudyTask.completed == completed)
    return query.order_by(StudyTask.created_at.desc()).all()


@router.patch("/{task_id}", response_model=StudyTaskRead)
def update_task(task_id: int, payload: StudyTaskUpdate, db: Session = Depends(get_db)):
    task = db.query(StudyTask).filter(StudyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(StudyTask).filter(StudyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
