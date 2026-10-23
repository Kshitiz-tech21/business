
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from ..main import app
from ..models.base import User, Workspace, WorkspaceMember, Project

# Test database
SQLITE_URL = "sqlite:///./test_analytics.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def get_session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def get_client(session: Session):
    # Override dependency for testing
    from ..main import get_session
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def create_user(session: Session):
    user = User(email="test@example.com", hashed_password="hashed", full_name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="test_workspace")
def create_workspace(session: Session, test_user: User):
    ws = Workspace(name="Test Org", slug="test-org")
    session.add(ws)
    session.commit()
    session.refresh(ws)
    
    member = WorkspaceMember(workspace_id=ws.id, user_id=test_user.id, role="OWNER")
    session.add(member)
    session.commit()
    return ws
