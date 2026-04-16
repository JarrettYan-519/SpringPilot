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
