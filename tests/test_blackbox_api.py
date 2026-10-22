"""
BLACK-BOX Functional/System Tests
Technique : Equivalence Class Partitioning (ECP) & Boundary Value
            Analysis (BVA), applied purely against the HTTP interface —
            no knowledge of internal code structure used to design these.
Tool      : pytest + Flask test client (real HTTP requests)
Level     : System / Functional Testing
"""
from conftest import VALID_ASSESSMENT_FORM


# ================= Index route redirects =================
def test_index_redirects_to_login_when_logged_out(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_index_redirects_to_new_assessment_when_logged_in(registered_client):
    resp = registered_client.get("/")
    assert resp.status_code == 302
    assert "/assessment/new" in resp.location


def test_register_page_loads_on_get(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create an Account" in resp.data


# ================= ECP: Registration =================
def test_ecp_missing_fields_rejected(client):
    resp = client.post("/register", data={"name": "", "email": "x@test.com", "password": "pass123"},
                        follow_redirects=True)
    assert b"all required" in resp.data


def test_ecp_valid_registration(client):
    resp = client.post("/register", data={
        "name": "Sayali", "email": "valid@test.com", "password": "pass123"
    }, follow_redirects=True)
    assert b"Registration successful" in resp.data


def test_ecp_invalid_email_rejected(client):
    resp = client.post("/register", data={
        "name": "Sayali", "email": "invalid-email.com", "password": "pass123"
    }, follow_redirects=True)
    assert b"valid email" in resp.data


def test_ecp_duplicate_email_rejected(client):
    client.post("/register", data={"name": "A", "email": "dup@test.com", "password": "pass123"})
    resp = client.post("/register", data={"name": "B", "email": "dup@test.com", "password": "pass456"},
                        follow_redirects=True)
    assert b"already exists" in resp.data


# ================= BVA: Password length boundary (min 6) =================
def test_bva_password_5_chars_rejected(client):
    resp = client.post("/register", data={
        "name": "Sayali", "email": "a@test.com", "password": "12345"
    }, follow_redirects=True)
    assert b"at least 6 characters" in resp.data


def test_bva_password_6_chars_accepted(client):
    resp = client.post("/register", data={
        "name": "Sayali", "email": "b@test.com", "password": "123456"
    }, follow_redirects=True)
    assert b"Registration successful" in resp.data


# ================= Login =================
def test_ecp_correct_login(client):
    client.post("/register", data={"name": "A", "email": "c@test.com", "password": "pass123"})
    resp = client.post("/login", data={"email": "c@test.com", "password": "pass123"}, follow_redirects=True)
    assert b"Welcome back" in resp.data


def test_ecp_wrong_password_rejected(client):
    client.post("/register", data={"name": "A", "email": "d@test.com", "password": "pass123"})
    resp = client.post("/login", data={"email": "d@test.com", "password": "wrong"}, follow_redirects=True)
    assert b"Invalid email or password" in resp.data


# ================= Access control =================
def test_new_assessment_requires_login(client):
    resp = client.get("/assessment/new")
    assert resp.status_code == 302
    assert "/login" in resp.location


# ================= BVA: Age boundary (spec: 1-120) =================
def test_bva_age_0_rejected(registered_client):
    data = dict(VALID_ASSESSMENT_FORM, age="0")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"age must be between 1 and 120" in resp.data


def test_bva_age_1_accepted(registered_client):
    data = dict(VALID_ASSESSMENT_FORM, age="1")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"Risk" in resp.data  # result page shown


def test_bva_age_120_accepted(registered_client):
    data = dict(VALID_ASSESSMENT_FORM, age="120")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"Risk" in resp.data


def test_bva_age_121_rejected(registered_client):
    data = dict(VALID_ASSESSMENT_FORM, age="121")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"age must be between 1 and 120" in resp.data


# ================= ECP: BMI categories via full form submission =================
def test_ecp_underweight_bmi_class(registered_client):
    # height 170cm, weight 45kg -> BMI ~15.6 (underweight)
    data = dict(VALID_ASSESSMENT_FORM, height_cm="170", weight_kg="45")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b"BMI: 15.57" in resp.data


def test_ecp_obese_bmi_class(registered_client):
    # height 170cm, weight 100kg -> BMI ~34.6 (obese category -> +10 risk
    # points). With all other factors neutral, overall category correctly
    # stays Low Risk (10 <= 20 threshold) -- this test verifies the BMI
    # classification itself displays correctly, not the overall category.
    data = dict(VALID_ASSESSMENT_FORM, height_cm="170", weight_kg="100")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"BMI: 34.6" in resp.data


def test_ecp_obese_bmi_combined_with_other_risk_factors_reaches_high_risk(registered_client):
    # Same obese BMI, but combined with smoking + heavy alcohol + no
    # exercise + family history + chronic condition -> crosses into High Risk
    data = dict(VALID_ASSESSMENT_FORM, height_cm="170", weight_kg="100",
                 smoker="yes", alcohol_frequency="heavy", exercise_frequency="none",
                 family_history="yes", chronic_condition="yes")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"High Risk" in resp.data


# ================= Invalid numeric input handling =================
def test_non_numeric_age_rejected(registered_client):
    data = dict(VALID_ASSESSMENT_FORM, age="not-a-number")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"valid numeric values" in resp.data


def test_zero_height_rejected(registered_client):
    data = dict(VALID_ASSESSMENT_FORM, height_cm="0")
    resp = registered_client.post("/assessment/new", data=data, follow_redirects=True)
    assert b"must be positive" in resp.data


# ================= Full black-box user journey =================
def test_blackbox_full_user_journey(client):
    client.post("/register", data={"name": "Sayali", "email": "e@test.com", "password": "pass123"})
    client.post("/login", data={"email": "e@test.com", "password": "pass123"})
    resp = client.post("/assessment/new", data=VALID_ASSESSMENT_FORM, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Assessment computed successfully" in resp.data

    resp = client.get("/history")
    assert b"#1" in resp.data


# ================= Security: cross-user access control =================
def test_cross_user_assessment_access_denied(client):
    client.post("/register", data={"name": "UserA", "email": "ua@test.com", "password": "pass123"})
    client.post("/login", data={"email": "ua@test.com", "password": "pass123"})
    client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)
    client.get("/logout")

    client.post("/register", data={"name": "UserB", "email": "ub@test.com", "password": "pass123"})
    client.post("/login", data={"email": "ub@test.com", "password": "pass123"})
    resp = client.get("/assessment/1", follow_redirects=True)
    assert b"do not have access" in resp.data


def test_nonexistent_assessment_handled(registered_client):
    resp = registered_client.get("/assessment/999", follow_redirects=True)
    assert b"not found" in resp.data