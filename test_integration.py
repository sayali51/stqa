"""
INTEGRATION Tests
Technique : Verifies that independently-tested layers (Auth, Business
            Logic, Database) work correctly TOGETHER end-to-end.
Tool      : pytest + Flask test client + real (in-memory) SQLite DB
"""
import re
from models import db, User, Assessment
from conftest import VALID_ASSESSMENT_FORM


def test_integration_registration_persists_with_hashed_password(client, app):
    client.post("/register", data={"name": "Sayali", "email": "f@test.com", "password": "pass123"})
    with app.app_context():
        user = User.query.filter_by(email="f@test.com").first()
        assert user is not None
        assert user.password_hash != "pass123"  # confirmed hashed, not plain text
        assert user.check_password("pass123") is True
        assert user.check_password("wrongpass") is False


def test_integration_assessment_persists_with_correct_computed_values(registered_client, app):
    data = dict(VALID_ASSESSMENT_FORM, age="50", height_cm="175", weight_kg="95",
                smoker="yes", alcohol_frequency="heavy", exercise_frequency="none",
                family_history="yes", chronic_condition="yes")
    registered_client.post("/assessment/new", data=data)

    with app.app_context():
        a = Assessment.query.first()
        assert a is not None
        assert a.age == 50
        assert a.smoker is True
        # BMI = 95 / 1.75^2 = 31.02 -> obese (+10)
        # smoker +15, alcohol heavy +5, exercise none +5, family +8, chronic +12 = 55
        assert a.risk_score == 55
        assert a.risk_category == "High Risk"


def test_integration_history_shows_only_own_assessments(client, app):
    client.post("/register", data={"name": "UserA", "email": "ia@test.com", "password": "pass123"})
    client.post("/login", data={"email": "ia@test.com", "password": "pass123"})
    client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)
    client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)
    client.get("/logout")

    client.post("/register", data={"name": "UserB", "email": "ib@test.com", "password": "pass123"})
    client.post("/login", data={"email": "ib@test.com", "password": "pass123"})
    client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)

    resp = client.get("/history")
    text = resp.get_data(as_text=True)
    # Match only numeric assessment-detail links (e.g. /assessment/3), not
    # the nav's /assessment/new link which also starts with "/assessment/"
    assessment_links = re.findall(r'href="/assessment/\d+"', text)
    assert len(assessment_links) == 1  # only UserB's single assessment, not UserA's 2


def test_integration_business_logic_matches_persisted_db_values(registered_client, app):
    """Cross-checks that the pure business_logic.py calculation (unit-tested
    separately) produces the exact same numbers that end up stored in the
    database after going through the full HTTP + ORM round trip."""
    from business_logic import compute_assessment
    data = dict(VALID_ASSESSMENT_FORM, age="28", height_cm="160", weight_kg="55",
                smoker="no", alcohol_frequency="none", exercise_frequency="regular",
                family_history="no", chronic_condition="no")
    registered_client.post("/assessment/new", data=data)

    expected = compute_assessment(
        age=28, gender="Female", height_cm=160, weight_kg=55,
        smoker=False, alcohol_frequency="none", exercise_frequency="regular",
        family_history=False, chronic_condition=False
    )
    with app.app_context():
        a = Assessment.query.first()
        assert a.bmi == expected["bmi"]
        assert a.risk_score == expected["risk_score"]
        assert a.risk_category == expected["risk_category"]
        assert a.estimated_remaining_years == expected["estimated_remaining_years"]