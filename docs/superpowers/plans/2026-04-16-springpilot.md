# SpringPilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local web application that combines spring recruitment management (application tracking, study planning, AI mock interviews) with fitness tracking (weight, diet, training logs, AI-powered trainer plan parsing).

**Architecture:** FastAPI backend with SQLite via SQLAlchemy; Vue 3 + Vite SPA frontend; LangChain AI engine supporting multiple LLM providers (GLM, DeepSeek, Claude, OpenAI) with configurable API keys and base URLs; MinerU API for PDF/DOCX → Markdown document parsing.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, LangChain, Vue 3, Vite, Chart.js, Pinia, Vue Router, SQLite, MinerU API

---

## File Structure

```
SpringPilot/
├── backend/
│   ├── main.py                    # FastAPI app, CORS, router registration
│   ├── database.py                # SQLAlchemy engine + session factory
│   ├── config.py                  # App config (DB path, upload dir, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py                 # Application, ApplicationStatusLog, StudyTask, InterviewQuestion
│   │   ├── fitness.py             # WeightRecord, DietLog, TrainingLog, TrainerPlan
│   │   └── system.py             # UserConfig
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── job.py                 # Pydantic request/response schemas for job models
│   │   ├── fitness.py             # Pydantic request/response schemas for fitness models
│   │   └── system.py             # Pydantic schemas for UserConfig
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── applications.py        # /api/applications CRUD + status log
│   │   ├── study_tasks.py         # /api/study-tasks CRUD
│   │   ├── weight.py              # /api/weight CRUD
│   │   ├── diet.py                # /api/diet CRUD
│   │   ├── training.py            # /api/training CRUD
│   │   ├── trainer_plans.py       # /api/trainer-plans upload + parse
│   │   ├── ai.py                  # /api/ai (JD analysis, interview gen, mock chat, suggestions)
│   │   └── settings.py            # /api/settings UserConfig CRUD
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py          # LangChain multi-model router
│   │   └── mineru_service.py      # MinerU API document parsing
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/index.js
│       ├── stores/
│       │   ├── settings.js        # Pinia store for LLM config + user profile
│       │   └── notifications.js   # Global notification state
│       ├── api/
│       │   ├── client.js          # Axios instance with base URL
│       │   ├── applications.js    # Application API calls
│       │   ├── fitness.js         # Weight/diet/training API calls
│       │   ├── ai.js              # AI API calls
│       │   └── settings.js        # Settings API calls
│       ├── views/
│       │   ├── Dashboard.vue      # Home: job + fitness overview + daily AI advice
│       │   ├── Applications.vue   # Application list + filter + create
│       │   ├── ApplicationDetail.vue  # Status timeline + AI question gen
│       │   ├── StudyTasks.vue     # Task board with tags + completion
│       │   ├── MockInterview.vue  # Chat-style mock interview UI
│       │   ├── JDAnalysis.vue     # Paste JD → AI analysis result
│       │   ├── FitnessOverview.vue    # Weight chart + calorie chart + training log
│       │   ├── TrainerPlans.vue   # Upload + parse + AI integrate trainer plans
│       │   └── Settings.vue       # LLM config + user profile + export
│       └── components/
│           ├── WeightChart.vue    # Chart.js line chart for weight trend
│           ├── CalorieChart.vue   # Chart.js bar chart for calorie intake
│           ├── TrainingHeatmap.vue    # Training frequency display
│           ├── StatusBadge.vue    # Application status badge with color
│           └── ChatMessage.vue    # Single message bubble for mock interview
└── docs/
    └── superpowers/
        ├── specs/
        └── plans/
```

---

## Task 1: Backend Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/config.py`
- Create: `backend/database.py`
- Create: `backend/main.py`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
pydantic==2.9.2
pydantic-settings==2.5.2
python-multipart==0.0.12
langchain==0.3.7
langchain-openai==0.2.8
langchain-community==0.3.7
httpx==0.27.2
aiofiles==24.1.0
python-dotenv==1.0.1
```

- [ ] **Step 2: Create config.py**

```python
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{BASE_DIR}/springpilot.db"
    upload_dir: str = str(BASE_DIR / "uploads")
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 3: Create database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
import os

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="SpringPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Install dependencies and verify server starts**

```bash
cd /Users/jarrett/Desktop/SpringPilot
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Expected: Server starts, `GET http://localhost:8000/api/health` returns `{"status":"ok"}`

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: scaffold FastAPI backend with config, database, and health endpoint"
```

---

## Task 2: Database Models

**Files:**
- Create: `backend/models/__init__.py`
- Create: `backend/models/job.py`
- Create: `backend/models/fitness.py`
- Create: `backend/models/system.py`

- [ ] **Step 1: Write failing test for model creation**

Create `backend/tests/__init__.py` (empty) and `backend/tests/test_models.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.job import Application, ApplicationStatusLog, StudyTask, InterviewQuestion
from backend.models.fitness import WeightRecord, DietLog, TrainingLog, TrainerPlan
from backend.models.system import UserConfig

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_application(db):
    app = Application(company="字节跳动", position="后端工程师", channel="Boss直聘", status="Applied")
    db.add(app)
    db.commit()
    assert db.query(Application).count() == 1
    assert db.query(Application).first().company == "字节跳动"

def test_create_weight_record(db):
    record = WeightRecord(weight_kg=75.5, note="早晨空腹")
    db.add(record)
    db.commit()
    assert db.query(WeightRecord).first().weight_kg == 75.5

def test_create_user_config(db):
    config = UserConfig(key="height_cm", value="178")
    db.add(config)
    db.commit()
    assert db.query(UserConfig).filter_by(key="height_cm").first().value == "178"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/jarrett/Desktop/SpringPilot
source .venv/bin/activate
pip install pytest
pytest backend/tests/test_models.py -v
```

Expected: ImportError — models not yet defined.

- [ ] **Step 3: Create backend/models/__init__.py**

```python
from backend.models.job import Application, ApplicationStatusLog, StudyTask, InterviewQuestion
from backend.models.fitness import WeightRecord, DietLog, TrainingLog, TrainerPlan
from backend.models.system import UserConfig

__all__ = [
    "Application", "ApplicationStatusLog", "StudyTask", "InterviewQuestion",
    "WeightRecord", "DietLog", "TrainingLog", "TrainerPlan",
    "UserConfig",
]
```

- [ ] **Step 4: Create backend/models/job.py**

```python
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    channel: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="Pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    status_logs: Mapped[list["ApplicationStatusLog"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    interview_questions: Mapped[list["InterviewQuestion"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class ApplicationStatusLog(Base):
    __tablename__ = "application_status_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    old_status: Mapped[str | None] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["Application"] = relationship(back_populates="status_logs")


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(String(300))  # comma-separated
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id"))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text)
    feedback: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(30), default="generated")  # generated | mock
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["Application | None"] = relationship(back_populates="interview_questions")
```

- [ ] **Step 5: Create backend/models/fitness.py**

```python
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base


class WeightRecord(Base):
    __tablename__ = "weight_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    note: Mapped[str | None] = mapped_column(Text)


class DietLog(Base):
    __tablename__ = "diet_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)  # breakfast/lunch/dinner/snack
    content: Mapped[str] = mapped_column(Text, nullable=False)
    calories: Mapped[int | None] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TrainingLog(Base):
    __tablename__ = "training_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    training_type: Mapped[str] = mapped_column(String(30), nullable=False)  # strength/cardio/stretching
    content: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TrainerPlan(Base):
    __tablename__ = "trainer_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500))
    parsed_content: Mapped[str | None] = mapped_column(Text)  # Markdown from MinerU
    plan_date_range: Mapped[str | None] = mapped_column(String(100))  # e.g. "2026-04-01 ~ 2026-04-30"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 6: Create backend/models/system.py**

```python
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base


class UserConfig(Base):
    __tablename__ = "user_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str | None] = mapped_column(Text)
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
pytest backend/tests/test_models.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/models/ backend/tests/
git commit -m "feat: add SQLAlchemy models for job, fitness, and system modules"
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `backend/schemas/__init__.py`
- Create: `backend/schemas/job.py`
- Create: `backend/schemas/fitness.py`
- Create: `backend/schemas/system.py`

- [ ] **Step 1: Create backend/schemas/__init__.py** (empty file)

```python
```

- [ ] **Step 2: Create backend/schemas/job.py**

```python
from datetime import datetime
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    company: str
    position: str
    description: str | None = None
    channel: str | None = None
    status: str = "Pending"


class ApplicationUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    description: str | None = None
    channel: str | None = None
    status: str | None = None


class ApplicationStatusLogRead(BaseModel):
    id: int
    old_status: str | None
    new_status: str
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationRead(BaseModel):
    id: int
    company: str
    position: str
    description: str | None
    channel: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    status_logs: list[ApplicationStatusLogRead] = []

    model_config = {"from_attributes": True}


class StatusUpdateRequest(BaseModel):
    new_status: str
    note: str | None = None


class StudyTaskCreate(BaseModel):
    title: str
    description: str | None = None
    tags: str | None = None
    due_date: datetime | None = None


class StudyTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: str | None = None
    due_date: datetime | None = None
    completed: bool | None = None


class StudyTaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    tags: str | None
    due_date: datetime | None
    completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewQuestionCreate(BaseModel):
    application_id: int | None = None
    question: str
    answer: str | None = None
    source_type: str = "generated"


class InterviewQuestionRead(BaseModel):
    id: int
    application_id: int | None
    question: str
    answer: str | None
    feedback: str | None
    source_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Create backend/schemas/fitness.py**

```python
from datetime import datetime
from pydantic import BaseModel


class WeightRecordCreate(BaseModel):
    weight_kg: float
    recorded_at: datetime | None = None
    note: str | None = None


class WeightRecordRead(BaseModel):
    id: int
    weight_kg: float
    recorded_at: datetime
    note: str | None

    model_config = {"from_attributes": True}


class DietLogCreate(BaseModel):
    meal_type: str
    content: str
    calories: int | None = None
    recorded_at: datetime | None = None


class DietLogRead(BaseModel):
    id: int
    meal_type: str
    content: str
    calories: int | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class TrainingLogCreate(BaseModel):
    training_type: str
    content: str
    duration_minutes: int | None = None
    completed: bool = False
    recorded_at: datetime | None = None


class TrainingLogUpdate(BaseModel):
    completed: bool | None = None
    duration_minutes: int | None = None


class TrainingLogRead(BaseModel):
    id: int
    training_type: str
    content: str
    duration_minutes: int | None
    completed: bool
    recorded_at: datetime

    model_config = {"from_attributes": True}


class TrainerPlanRead(BaseModel):
    id: int
    title: str
    file_path: str | None
    parsed_content: str | None
    plan_date_range: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Create backend/schemas/system.py**

```python
from pydantic import BaseModel


class UserConfigSet(BaseModel):
    value: str | None


class UserConfigRead(BaseModel):
    key: str
    value: str | None

    model_config = {"from_attributes": True}


class UserConfigBulkRead(BaseModel):
    configs: dict[str, str | None]
```

- [ ] **Step 5: Write a quick schema validation test**

Add to `backend/tests/test_models.py`:

```python
from backend.schemas.job import ApplicationCreate, ApplicationRead
from backend.schemas.fitness import WeightRecordCreate

def test_application_schema_validation():
    data = ApplicationCreate(company="腾讯", position="前端工程师")
    assert data.status == "Pending"
    assert data.channel is None

def test_weight_schema_validation():
    data = WeightRecordCreate(weight_kg=75.0)
    assert data.weight_kg == 75.0
```

- [ ] **Step 6: Run tests**

```bash
pytest backend/tests/test_models.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/schemas/
git commit -m "feat: add Pydantic schemas for all API request/response types"
```

---

## Task 4: Application & StudyTask CRUD Routers

**Files:**
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/applications.py`
- Create: `backend/routers/study_tasks.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_applications.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_create_application(client):
    resp = client.post("/api/applications", json={"company": "字节跳动", "position": "后端工程师"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["company"] == "字节跳动"
    assert data["status"] == "Pending"

def test_list_applications(client):
    client.post("/api/applications", json={"company": "腾讯", "position": "前端"})
    resp = client.get("/api/applications")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

def test_update_application_status(client):
    create_resp = client.post("/api/applications", json={"company": "阿里", "position": "算法"})
    app_id = create_resp.json()["id"]
    resp = client.post(f"/api/applications/{app_id}/status", json={"new_status": "Applied", "note": "已投递"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "Applied"

def test_delete_application(client):
    create_resp = client.post("/api/applications", json={"company": "美团", "position": "测试"})
    app_id = create_resp.json()["id"]
    resp = client.delete(f"/api/applications/{app_id}")
    assert resp.status_code == 204
```

Create `backend/tests/test_study_tasks.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_create_study_task(client):
    resp = client.post("/api/study-tasks", json={"title": "LeetCode 两数之和", "tags": "algorithm"})
    assert resp.status_code == 201
    assert resp.json()["completed"] is False

def test_complete_study_task(client):
    create_resp = client.post("/api/study-tasks", json={"title": "系统设计学习"})
    task_id = create_resp.json()["id"]
    resp = client.patch(f"/api/study-tasks/{task_id}", json={"completed": True})
    assert resp.status_code == 200
    assert resp.json()["completed"] is True
```

- [ ] **Step 2: Run tests to confirm failure**

```bash
pytest backend/tests/test_applications.py backend/tests/test_study_tasks.py -v
```

Expected: 404 errors — routes not yet registered.

- [ ] **Step 3: Create backend/routers/__init__.py** (empty file)

```python
```

- [ ] **Step 4: Create backend/routers/applications.py**

```python
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
```

- [ ] **Step 5: Create backend/routers/study_tasks.py**

```python
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
```

- [ ] **Step 6: Register routers in main.py**

Replace the contents of `backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.routers import applications, study_tasks
import os

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="SpringPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(study_tasks.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
pytest backend/tests/test_applications.py backend/tests/test_study_tasks.py -v
```

Expected: 6 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/routers/ backend/tests/ backend/main.py
git commit -m "feat: add Application and StudyTask CRUD API endpoints"
```

---

## Task 5: Fitness CRUD Routers

**Files:**
- Create: `backend/routers/weight.py`
- Create: `backend/routers/diet.py`
- Create: `backend/routers/training.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_fitness.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_create_weight_record(client):
    resp = client.post("/api/weight", json={"weight_kg": 75.5, "note": "早晨"})
    assert resp.status_code == 201
    assert resp.json()["weight_kg"] == 75.5

def test_list_weight_records(client):
    client.post("/api/weight", json={"weight_kg": 75.0})
    client.post("/api/weight", json={"weight_kg": 74.8})
    resp = client.get("/api/weight")
    assert resp.status_code == 200
    assert len(resp.json()) == 2

def test_create_diet_log(client):
    resp = client.post("/api/diet", json={"meal_type": "breakfast", "content": "燕麦粥", "calories": 350})
    assert resp.status_code == 201
    assert resp.json()["calories"] == 350

def test_create_training_log(client):
    resp = client.post("/api/training", json={"training_type": "strength", "content": "卧推3x8", "duration_minutes": 60})
    assert resp.status_code == 201
    assert resp.json()["completed"] is False

def test_complete_training_log(client):
    create_resp = client.post("/api/training", json={"training_type": "cardio", "content": "跑步30分钟"})
    log_id = create_resp.json()["id"]
    resp = client.patch(f"/api/training/{log_id}", json={"completed": True})
    assert resp.status_code == 200
    assert resp.json()["completed"] is True
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest backend/tests/test_fitness.py -v
```

Expected: 404/ImportError — routes not registered.

- [ ] **Step 3: Create backend/routers/weight.py**

```python
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
```

- [ ] **Step 4: Create backend/routers/diet.py**

```python
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
```

- [ ] **Step 5: Create backend/routers/training.py**

```python
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
```

- [ ] **Step 6: Register routers in main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.routers import applications, study_tasks, weight, diet, training
import os

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="SpringPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(study_tasks.router)
app.include_router(weight.router)
app.include_router(diet.router)
app.include_router(training.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 7: Run tests**

```bash
pytest backend/tests/test_fitness.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/routers/weight.py backend/routers/diet.py backend/routers/training.py backend/tests/test_fitness.py backend/main.py
git commit -m "feat: add Weight, Diet, and Training CRUD API endpoints"
```

---

## Task 6: Settings API (UserConfig)

**Files:**
- Create: `backend/routers/settings.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_settings.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_set_and_get_config(client):
    resp = client.put("/api/settings/height_cm", json={"value": "178"})
    assert resp.status_code == 200
    assert resp.json()["value"] == "178"

def test_get_all_configs(client):
    client.put("/api/settings/height_cm", json={"value": "178"})
    client.put("/api/settings/target_weight_kg", json={"value": "70"})
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    assert resp.json()["configs"]["height_cm"] == "178"

def test_update_existing_config(client):
    client.put("/api/settings/height_cm", json={"value": "178"})
    resp = client.put("/api/settings/height_cm", json={"value": "180"})
    assert resp.json()["value"] == "180"
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest backend/tests/test_settings.py -v
```

Expected: 404 — routes not registered.

- [ ] **Step 3: Create backend/routers/settings.py**

```python
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
```

- [ ] **Step 4: Register router in main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.routers import applications, study_tasks, weight, diet, training, settings as settings_router
import os

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="SpringPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(study_tasks.router)
app.include_router(weight.router)
app.include_router(diet.router)
app.include_router(training.router)
app.include_router(settings_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run tests**

```bash
pytest backend/tests/test_settings.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 6: Run all tests**

```bash
pytest backend/tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/routers/settings.py backend/tests/test_settings.py backend/main.py
git commit -m "feat: add Settings/UserConfig API for LLM keys and user profile"
```

---

## Task 7: LangChain AI Service (Multi-model Router)

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/ai_service.py`
- Create: `backend/routers/ai.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_ai_service.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.ai_service import AIService


def make_mock_db(configs: dict):
    """Return a mock DB session that returns UserConfig values."""
    from backend.models.system import UserConfig
    mock_db = MagicMock()
    def query_filter_side_effect(key):
        value = configs.get(key)
        mock_config = MagicMock()
        mock_config.value = value
        return mock_config
    mock_query = MagicMock()
    mock_query.filter.return_value.first.side_effect = lambda: (
        MagicMock(value=configs.get(
            mock_query.filter.call_args[0][0].right.value
        ))
    )
    mock_db.query.return_value = mock_query
    return mock_db


def test_ai_service_builds_openai_llm():
    service = AIService.__new__(AIService)
    with patch("backend.services.ai_service.ChatOpenAI") as MockOpenAI:
        llm = service._build_llm(
            provider="openai",
            api_key="sk-test",
            base_url=None,
            model="gpt-4o-mini",
        )
        MockOpenAI.assert_called_once()

def test_ai_service_builds_deepseek_llm():
    service = AIService.__new__(AIService)
    with patch("backend.services.ai_service.ChatOpenAI") as MockOpenAI:
        llm = service._build_llm(
            provider="deepseek",
            api_key="ds-test",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
        )
        call_kwargs = MockOpenAI.call_args[1]
        assert call_kwargs["base_url"] == "https://api.deepseek.com/v1"
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest backend/tests/test_ai_service.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create backend/services/__init__.py** (empty)

```python
```

- [ ] **Step 4: Create backend/services/ai_service.py**

```python
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from sqlalchemy.orm import Session
from backend.models.system import UserConfig


PROVIDER_DEFAULTS = {
    "openai": {"model": "gpt-4o-mini", "base_url": None},
    "deepseek": {"model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1"},
    "claude": {"model": "claude-sonnet-4-6", "base_url": None},
    "glm": {"model": "glm-4-flash", "base_url": None},
}


class AIService:
    def __init__(self, db: Session):
        self.db = db

    def _get_config(self, key: str) -> str | None:
        config = self.db.query(UserConfig).filter(UserConfig.key == key).first()
        return config.value if config else None

    def _build_llm(self, provider: str, api_key: str, base_url: str | None, model: str):
        if provider == "glm":
            return ChatZhipuAI(api_key=api_key, model=model)
        kwargs = {"api_key": api_key, "model": model}
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)

    def get_llm(self, scenario: str = "default"):
        """Load LLM for a given scenario from UserConfig. Falls back through providers."""
        # Check scenario-specific provider override
        provider = self._get_config(f"llm_provider_{scenario}") or self._get_config("llm_provider_default") or "openai"
        api_key = self._get_config(f"llm_api_key_{provider}")
        base_url = self._get_config(f"llm_base_url_{provider}") or PROVIDER_DEFAULTS.get(provider, {}).get("base_url")
        model = self._get_config(f"llm_model_{provider}") or PROVIDER_DEFAULTS.get(provider, {}).get("model", "gpt-4o-mini")

        if not api_key:
            raise ValueError(f"No API key configured for provider: {provider}")

        return self._build_llm(provider=provider, api_key=api_key, base_url=base_url, model=model)

    async def analyze_jd(self, jd_text: str, resume_text: str | None = None) -> dict:
        llm = self.get_llm("jd_analysis")
        system_prompt = """你是一位资深HR和技术面试官。分析职位描述(JD)，提取关键技能要求，
        如果提供了简历，给出匹配度分析和差距建议。用JSON格式返回：
        {
          "key_skills": ["技能1", "技能2"],
          "requirements": ["要求1", "要求2"],
          "match_analysis": "匹配度分析（如有简历）",
          "gaps": ["差距1", "差距2"],
          "suggestions": ["建议1", "建议2"]
        }"""
        user_content = f"职位描述：\n{jd_text}"
        if resume_text:
            user_content += f"\n\n我的简历：\n{resume_text}"

        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content),
        ])
        import json, re
        text = response.content
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"raw": text}

    async def generate_interview_questions(self, position: str, jd_text: str, question_count: int = 10) -> list[str]:
        llm = self.get_llm("interview_gen")
        prompt = f"""为以下职位生成{question_count}道面试题（技术题和HR题各半），职位：{position}
        职位描述：{jd_text}
        直接返回问题列表，每行一个问题，不要编号。"""
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        questions = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        return questions[:question_count]

    async def mock_interview_reply(self, history: list[dict], user_answer: str) -> str:
        llm = self.get_llm("mock_interview")
        messages = [SystemMessage(content="""你是一位专业面试官，正在进行技术面试。
        根据候选人的回答，追问更深入的问题，或者给出简短的反馈后进入下一个问题。
        保持专业，语言简洁，每次回复不超过200字。""")]
        for msg in history:
            if msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            else:
                messages.append(HumanMessage(content=msg["content"]))
        messages.append(HumanMessage(content=user_answer))
        response = await llm.ainvoke(messages)
        return response.content

    async def estimate_calories(self, food_description: str) -> int:
        llm = self.get_llm("diet")
        prompt = f"估算以下食物的热量（卡路里），只返回数字，不要单位：{food_description}"
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        try:
            return int(response.content.strip().replace(",", ""))
        except ValueError:
            return 0

    async def daily_advice(self, job_summary: str, fitness_summary: str) -> str:
        llm = self.get_llm("default")
        prompt = f"""根据以下数据，给出今天的综合建议（求职+健身），简洁有重点，200字以内。
        求职情况：{job_summary}
        健身情况：{fitness_summary}"""
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
```

- [ ] **Step 5: Run tests**

```bash
pytest backend/tests/test_ai_service.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 6: Create backend/routers/ai.py**

```python
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
```

- [ ] **Step 7: Register router in main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.routers import applications, study_tasks, weight, diet, training
from backend.routers import settings as settings_router, ai
import os

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="SpringPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(study_tasks.router)
app.include_router(weight.router)
app.include_router(diet.router)
app.include_router(training.router)
app.include_router(settings_router.router)
app.include_router(ai.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 8: Run all tests**

```bash
pytest backend/tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 9: Commit**

```bash
git add backend/services/ backend/routers/ai.py backend/tests/test_ai_service.py backend/main.py
git commit -m "feat: add LangChain multi-model AI service and AI API endpoints"
```

---

## Task 8: MinerU Document Parsing & TrainerPlan Upload

**Files:**
- Create: `backend/services/mineru_service.py`
- Create: `backend/routers/trainer_plans.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_trainer_plans.py`:

```python
import pytest
import io
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_list_trainer_plans_empty(client):
    resp = client.get("/api/trainer-plans")
    assert resp.status_code == 200
    assert resp.json() == []

def test_upload_trainer_plan_md(client):
    md_content = b"# Training Plan\n\n## Week 1\n- Monday: Chest 3x8"
    with patch("backend.routers.trainer_plans.MinerUService") as MockMinerU:
        MockMinerU.return_value.parse_file = AsyncMock(return_value=md_content.decode())
        resp = client.post(
            "/api/trainer-plans",
            data={"title": "4月训练计划"},
            files={"file": ("plan.md", io.BytesIO(md_content), "text/markdown")},
        )
    assert resp.status_code == 201
    assert resp.json()["title"] == "4月训练计划"
    assert resp.json()["parsed_content"] is not None
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest backend/tests/test_trainer_plans.py -v
```

Expected: ImportError — module not found.

- [ ] **Step 3: Create backend/services/mineru_service.py**

```python
import httpx
import aiofiles
from pathlib import Path


class MinerUService:
    """
    Wraps the MinerU API for document parsing (PDF/DOCX → Markdown).
    For .md files, returns content directly without calling the API.
    """

    def __init__(self, api_key: str | None = None, base_url: str = "https://mineru.net/api/v4"):
        self.api_key = api_key
        self.base_url = base_url

    async def parse_file(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        # Markdown files: read directly
        if suffix == ".md":
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()

        # PDF/DOCX: call MinerU API
        if not self.api_key:
            raise ValueError("MinerU API key not configured")

        async with aiofiles.open(file_path, "rb") as f:
            file_bytes = await f.read()

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/extract/file",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"file": (path.name, file_bytes, "application/octet-stream")},
                data={"output_format": "markdown"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("markdown", "")
```

- [ ] **Step 4: Create backend/routers/trainer_plans.py**

```python
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
```

- [ ] **Step 5: Register router in main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.routers import applications, study_tasks, weight, diet, training
from backend.routers import settings as settings_router, ai, trainer_plans
import os

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="SpringPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(study_tasks.router)
app.include_router(weight.router)
app.include_router(diet.router)
app.include_router(training.router)
app.include_router(settings_router.router)
app.include_router(ai.router)
app.include_router(trainer_plans.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Run tests**

```bash
pytest backend/tests/test_trainer_plans.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 7: Run all backend tests**

```bash
pytest backend/tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/services/mineru_service.py backend/routers/trainer_plans.py backend/tests/test_trainer_plans.py backend/main.py
git commit -m "feat: add MinerU document parsing service and TrainerPlan upload API"
```

---

## Task 9: Frontend Scaffolding (Vue 3 + Vite)

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/stores/settings.js`
- Create: `frontend/src/api/client.js`

- [ ] **Step 1: Initialize Vue 3 project**

```bash
cd /Users/jarrett/Desktop/SpringPilot
npm create vue@latest frontend -- --router --pinia --no-typescript --no-jsx --no-vitest --no-eslint
```

When prompted, select: Router=yes, Pinia=yes, all others=No.

- [ ] **Step 2: Install additional dependencies**

```bash
cd frontend
npm install chart.js vue-chartjs axios
npm install
```

- [ ] **Step 3: Configure Vite proxy in vite.config.js**

Replace `frontend/vite.config.js` with:

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

- [ ] **Step 4: Create frontend/src/api/client.js**

```js
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Request failed'
    return Promise.reject(new Error(message))
  }
)

export default client
```

- [ ] **Step 5: Create frontend/src/stores/settings.js**

```js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'

export const useSettingsStore = defineStore('settings', () => {
  const configs = ref({})

  async function loadAll() {
    const data = await client.get('/settings')
    configs.value = data.configs
  }

  async function set(key, value) {
    await client.put(`/settings/${key}`, { value })
    configs.value[key] = value
  }

  const heightCm = computed(() => configs.value['height_cm'] ? Number(configs.value['height_cm']) : null)
  const targetWeightKg = computed(() => configs.value['target_weight_kg'] ? Number(configs.value['target_weight_kg']) : null)

  return { configs, loadAll, set, heightCm, targetWeightKg }
})
```

- [ ] **Step 6: Set up Vue Router in frontend/src/router/index.js**

```js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/views/Dashboard.vue'), name: 'dashboard' },
  { path: '/applications', component: () => import('@/views/Applications.vue'), name: 'applications' },
  { path: '/applications/:id', component: () => import('@/views/ApplicationDetail.vue'), name: 'application-detail' },
  { path: '/study-tasks', component: () => import('@/views/StudyTasks.vue'), name: 'study-tasks' },
  { path: '/mock-interview', component: () => import('@/views/MockInterview.vue'), name: 'mock-interview' },
  { path: '/jd-analysis', component: () => import('@/views/JDAnalysis.vue'), name: 'jd-analysis' },
  { path: '/fitness', component: () => import('@/views/FitnessOverview.vue'), name: 'fitness' },
  { path: '/trainer-plans', component: () => import('@/views/TrainerPlans.vue'), name: 'trainer-plans' },
  { path: '/settings', component: () => import('@/views/Settings.vue'), name: 'settings' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
```

- [ ] **Step 7: Create minimal App.vue with navigation**

Replace `frontend/src/App.vue`:

```vue
<template>
  <div class="app-layout">
    <nav class="sidebar">
      <div class="logo">SpringPilot</div>
      <ul>
        <li><RouterLink to="/">首页</RouterLink></li>
        <li class="section-label">求职</li>
        <li><RouterLink to="/applications">投递记录</RouterLink></li>
        <li><RouterLink to="/study-tasks">学习任务</RouterLink></li>
        <li><RouterLink to="/jd-analysis">JD 分析</RouterLink></li>
        <li><RouterLink to="/mock-interview">模拟面试</RouterLink></li>
        <li class="section-label">健身</li>
        <li><RouterLink to="/fitness">数据概览</RouterLink></li>
        <li><RouterLink to="/trainer-plans">训练计划</RouterLink></li>
        <li class="section-label">系统</li>
        <li><RouterLink to="/settings">设置</RouterLink></li>
      </ul>
    </nav>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f6fa; }
.app-layout { display: flex; min-height: 100vh; }
.sidebar { width: 200px; background: #1a1a2e; color: #eee; padding: 1rem; flex-shrink: 0; }
.sidebar .logo { font-size: 1.2rem; font-weight: bold; color: #fff; margin-bottom: 1.5rem; }
.sidebar ul { list-style: none; }
.sidebar li { margin: 0.25rem 0; }
.sidebar .section-label { font-size: 0.7rem; color: #888; text-transform: uppercase; margin-top: 1rem; margin-bottom: 0.25rem; }
.sidebar a { color: #ccc; text-decoration: none; display: block; padding: 0.4rem 0.5rem; border-radius: 4px; }
.sidebar a:hover, .sidebar a.router-link-active { background: #16213e; color: #fff; }
.main-content { flex: 1; padding: 2rem; overflow: auto; }
</style>
```

- [ ] **Step 8: Verify dev server starts**

```bash
cd /Users/jarrett/Desktop/SpringPilot/frontend
npm run dev
```

Open http://localhost:5173 — sidebar should appear with navigation links.

- [ ] **Step 9: Commit**

```bash
cd /Users/jarrett/Desktop/SpringPilot
git add frontend/
git commit -m "feat: scaffold Vue 3 frontend with router, Pinia, API client, and sidebar navigation"
```
