import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone
from app.main import app
from app.db import User, Message, Conversation
from app.auth import get_session, get_current_user

src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(username="testuser", password="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(client: TestClient, test_user: User):
    def get_current_user_override():
        return test_user

    app.dependency_overrides[get_current_user] = get_current_user_override
    return client