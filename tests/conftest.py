import os

os.environ["DATABASE_URL"] = "sqlite:///./test_finance.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient

from database import Base, engine
from main import app


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Usuario Teste",
            "email": "teste@example.com",
            "password": "senha123",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "teste@example.com", "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
