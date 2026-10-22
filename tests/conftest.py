"""
Shared pytest fixtures — spins up a fresh Flask app with an isolated
in-memory SQLite database for every single test.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app
from models import db


@pytest.fixture
def app():
    application = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
    })
    yield application
    with application.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def registered_client(client):
    """A client that has already registered and logged in as a test user."""
    client.post("/register", data={
        "name": "Sayali", "email": "sayali@test.com", "password": "pass123"
    })
    client.post("/login", data={"email": "sayali@test.com", "password": "pass123"})
    return client


VALID_ASSESSMENT_FORM = {
    "age": "35", "gender": "Female", "height_cm": "165", "weight_kg": "60",
    "smoker": "no", "alcohol_frequency": "none", "exercise_frequency": "moderate",
    "family_history": "no", "chronic_condition": "no",
}