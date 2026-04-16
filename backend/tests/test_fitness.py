import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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
