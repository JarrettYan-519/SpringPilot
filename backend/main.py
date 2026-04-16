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
