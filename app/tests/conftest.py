import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

from app.main import app
from app.database import get_session
from app.models import Base
from app.models import User

load_dotenv()

url = os.getenv("TEST_DB")
engine = create_engine(url)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture()
def test_session():
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture()
def client(test_session):
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def set_bcrypt_rounds(monkeypatch):
    monkeypatch.setenv("BCRYPT_ROUNDS", "4")