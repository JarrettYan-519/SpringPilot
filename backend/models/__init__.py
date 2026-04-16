from backend.models.job import Application, ApplicationStatusLog, StudyTask, InterviewQuestion
from backend.models.fitness import WeightRecord, DietLog, TrainingLog, TrainerPlan
from backend.models.system import UserConfig

__all__ = [
    "Application", "ApplicationStatusLog", "StudyTask", "InterviewQuestion",
    "WeightRecord", "DietLog", "TrainingLog", "TrainerPlan",
    "UserConfig",
]
