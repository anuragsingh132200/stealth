import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

from app.main import app
from app.db import Base, get_db, engine as _engine
from app.tasks import celery_app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override the database URL for testing
engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Set up test database
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Fixture to override the get_db dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# Configure Celery for testing
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
)

# Fixture for the test client
@pytest.fixture(scope="module")
async def client():
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Initialize the test database
    await init_test_db()
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides = {}

# Fixture for a database session
@pytest.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

# Fixture for event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
