import pytest
import io
from unittest.mock import patch, AsyncMock
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
