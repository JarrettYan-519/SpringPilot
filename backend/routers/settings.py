from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.system import UserConfig
from backend.schemas.system import UserConfigSet, UserConfigRead, UserConfigBulkRead

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=UserConfigBulkRead)
def get_all_settings(db: Session = Depends(get_db)):
    configs = db.query(UserConfig).all()
    return UserConfigBulkRead(configs={c.key: c.value for c in configs})


@router.get("/{key}", response_model=UserConfigRead)
def get_setting(key: str, db: Session = Depends(get_db)):
    config = db.query(UserConfig).filter(UserConfig.key == key).first()
    if not config:
        return UserConfigRead(key=key, value=None)
    return config


@router.put("/{key}", response_model=UserConfigRead)
def set_setting(key: str, payload: UserConfigSet, db: Session = Depends(get_db)):
    config = db.query(UserConfig).filter(UserConfig.key == key).first()
    if config:
        config.value = payload.value
    else:
        config = UserConfig(key=key, value=payload.value)
        db.add(config)
    db.commit()
    db.refresh(config)
    return config
