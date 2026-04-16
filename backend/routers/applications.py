from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.job import Application, ApplicationStatusLog
from backend.schemas.job import (
    ApplicationCreate, ApplicationUpdate, ApplicationRead, StatusUpdateRequest
)

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    app = Application(**payload.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Application)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    return query.order_by(Application.created_at.desc()).all()


@router.get("/{app_id}", response_model=ApplicationRead)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.patch("/{app_id}", response_model=ApplicationRead)
def update_application(app_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return app


@router.post("/{app_id}/status", response_model=ApplicationRead)
def update_status(app_id: int, payload: StatusUpdateRequest, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    log = ApplicationStatusLog(
        application_id=app_id,
        old_status=app.status,
        new_status=payload.new_status,
        note=payload.note,
    )
    db.add(log)
    app.status = payload.new_status
    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
