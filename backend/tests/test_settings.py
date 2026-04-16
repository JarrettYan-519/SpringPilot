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
