"""Shared test fixtures: each test gets a fresh in-memory database."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.db import Base, get_db
from app.main import api


@pytest.fixture
def client() -> Iterator[TestClient]:
    """TestClient wired to a throwaway in-memory SQLite database."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Iterator[Session]:
        with TestingSession() as session:
            yield session

    api.dependency_overrides[get_db] = override_get_db
    yield TestClient(api)
    api.dependency_overrides.clear()
    engine.dispose()