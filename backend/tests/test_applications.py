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
