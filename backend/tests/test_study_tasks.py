import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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
