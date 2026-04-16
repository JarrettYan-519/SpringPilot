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


from backend.schemas.job import ApplicationCreate, ApplicationRead
from backend.schemas.fitness import WeightRecordCreate

def test_application_schema_validation():
    data = ApplicationCreate(company="腾讯", position="前端工程师")
    assert data.status == "Pending"
    assert data.channel is None

def test_weight_schema_validation():
    data = WeightRecordCreate(weight_kg=75.0)
    assert data.weight_kg == 75.0
