# Life Expectancy & Health Risk Estimator

A Flask web app built as a **Software Testing & Quality Assurance (STQA) mini-project**. It is based on the "Death Prediction System" OOMD/OOAD case study and implemented as a simple, rule-based estimator whose main purpose is to demonstrate **white-box, black-box and integration testing** on non-trivial business logic.

> ⚠️ **Academic disclaimer:** The coefficients and formulas are illustrative assumptions, **not** derived from real actuarial, clinical or epidemiological data. This system must **never** be used for actual health, medical or insurance decisions.

---

## Features

- User registration and login with hashed passwords (Werkzeug)
- Session-based authentication with a `login_required` guard
- Health assessment form (age, gender, height, weight, smoking, alcohol, exercise, family history, chronic condition)
- Computed BMI, risk score (0-100), risk category and estimated remaining years
- Assessment history per user, with access control (users can only view their own assessments)
- Persistent storage using SQLite via Flask-SQLAlchemy
- Server-rendered pages using Jinja2 templates
- Application factory (`create_app`) so tests run against an isolated in-memory database

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask 3.1 |
| Database | SQLite, Flask-SQLAlchemy 3.1 |
| Security | Werkzeug password hashing, Flask sessions |
| Frontend | Jinja2 templates, CSS |
| Testing | pytest, pytest-cov |

## Project Structure

```
stqa/
├── app.py                  # Flask app factory and routes
├── business_logic.py       # Pure logic: BMI, risk score, categories, life expectancy
├── models.py               # SQLAlchemy models (User, Assessment)
├── conftest.py             # Shared pytest fixtures (in-memory test app/client)
├── test_unit_whitebox.py   # White-box unit tests for business_logic.py
├── test_blackbox_api.py    # Black-box tests through the HTTP routes
├── test_integration.py     # End-to-end / integration tests
├── requirements.txt
├── static/                 # CSS
└── templates/              # base, login, register, assessment_form,
                            # assessment_detail, history
```

## Getting Started

### Prerequisites
- Python 3.10+

### Installation

```bash
git clone https://github.com/sayali51/stqa.git
cd stqa

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### Run the app

```bash
python app.py
```

Open **http://localhost:5000**, register an account, log in and create an assessment.

## How the Estimation Works

All logic lives in `business_logic.py` (no Flask, no database, no I/O) so it can be tested in isolation.

**1. BMI** = weight (kg) / height (m)². Non-positive inputs raise `ValueError`.

| BMI | Risk points |
|---|---|
| < 18.5 (underweight) | 3 |
| 18.5 - 24.9 (normal) | 0 |
| 25 - 29.9 (overweight) | 5 |
| ≥ 30 (obese) | 10 |

**2. Lifestyle points**

| Factor | Points |
|---|---|
| Smoker | +15 |
| Alcohol: heavy / moderate / none | +5 / +2 / 0 |
| Exercise: none / moderate / regular | +5 / 0 / -5 |

**3. Medical history points**

| Factor | Points |
|---|---|
| Family history | +8 |
| Chronic condition | +12 |

**4. Risk score** = BMI + lifestyle + medical points, clamped to **[0, 100]**.

**5. Risk category**

| Score | Category |
|---|---|
| 0 - 20 | Low Risk |
| 21 - 50 | Moderate Risk |
| 51 - 100 | High Risk |

**6. Estimated remaining years** = `max(0, (78 - age) - risk_score × 0.2)`, rounded to 1 decimal.

**Input validation:** age must be 1-120, gender must be `Male`, `Female` or `Other`, and alcohol/exercise values must be from the allowed sets.

## Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/` | GET | - | Redirects to login or new assessment |
| `/register` | GET, POST | - | Create an account |
| `/login` | GET, POST | - | Log in |
| `/logout` | GET | - | Clear session |
| `/assessment/new` | GET, POST | ✅ | Submit a new assessment |
| `/assessment/<id>` | GET | ✅ | View one assessment (owner only) |
| `/history` | GET | ✅ | List your past assessments |

## Testing

The test suite is organised by testing technique:

| File | Technique | Covers |
|---|---|---|
| `test_unit_whitebox.py` | White-box | Branch, condition and boundary coverage of `business_logic.py` |
| `test_blackbox_api.py` | Black-box | Registration, login, validation and access control via HTTP |
| `test_integration.py` | Integration | Full flow: form → business logic → database → result page |

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=term-missing
pytest --cov=. --cov-report=html     # HTML report in htmlcov/
```

## Security Notes

- `SECRET_KEY` in `app.py` is a development placeholder. Load it from an environment variable before any real deployment.
- The app runs with `debug=True` for local development only.

## Author

**Sayali**, Final-year B.E. Computer Engineering, SPPU
GitHub: [@sayali51](https://github.com/sayali51)

## License

Academic project, for educational use only.
