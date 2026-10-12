import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

@pytest.fixture(scope="session")
def test_db_file():
    """Creates a temporary SQLite database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_students_")
    os.close(fd)
    yield path
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

@pytest.fixture(scope="session")
def engine(test_db_file):
    """Engine tied to the temporary test database."""
    test_db_url = f"sqlite:///{test_db_file.replace(os.sep, '/')}"
    test_engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    """Provides an isolated database session per test function with rollback/clean state."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        # Clean tables between tests to ensure complete test isolation
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
