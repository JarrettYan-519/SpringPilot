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
