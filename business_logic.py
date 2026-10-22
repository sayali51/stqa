"""
Pure business logic — no Flask, no database, no I/O.

IMPORTANT ACADEMIC DISCLAIMER:
This module implements a simplified, RULE-BASED, EDUCATIONAL estimation
model for a Software Testing & Quality Assurance mini-project (based on
the "Death Prediction System" OOMD/OOAD case study). The coefficients
and formula below are illustrative assumptions chosen to produce varied,
testable branches and boundary conditions — they are NOT derived from
real actuarial, clinical, or epidemiological data, and this system must
NEVER be used for actual health, medical, or insurance decisions. Its
sole purpose is to demonstrate white-box/black-box/integration testing
technique on a non-trivial piece of business logic.

Kept framework-free so it can be unit tested in complete isolation.
"""

BASE_LIFE_EXPECTANCY = 78.0  # illustrative baseline assumption (years)

# BMI category thresholds (standard WHO bands, used only as illustrative
# input classification for this academic model)
BMI_UNDERWEIGHT = 18.5
BMI_NORMAL_MAX = 24.9
BMI_OVERWEIGHT_MAX = 29.9

RISK_LOW_MAX = 20
RISK_MODERATE_MAX = 50


def calculate_bmi(height_cm, weight_kg):
    """BMI = weight(kg) / height(m)^2. Raises on invalid (non-positive) input."""
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Height and weight must be positive values")
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def bmi_risk_points(bmi):
    """Illustrative risk points contributed by BMI category."""
    if bmi < BMI_UNDERWEIGHT:
        return 3
    elif bmi <= BMI_NORMAL_MAX:
        return 0
    elif bmi <= BMI_OVERWEIGHT_MAX:
        return 5
    else:
        return 10


def lifestyle_risk_points(smoker, alcohol_frequency, exercise_frequency):
    """
    smoker: bool
    alcohol_frequency: 'none' | 'moderate' | 'heavy'
    exercise_frequency: 'none' | 'moderate' | 'regular'
    """
    valid_alcohol = {'none', 'moderate', 'heavy'}
    valid_exercise = {'none', 'moderate', 'regular'}
    if alcohol_frequency not in valid_alcohol:
        raise ValueError(f"alcohol_frequency must be one of {valid_alcohol}")
    if exercise_frequency not in valid_exercise:
        raise ValueError(f"exercise_frequency must be one of {valid_exercise}")

    points = 0
    if smoker:
        points += 15

    if alcohol_frequency == 'heavy':
        points += 5
    elif alcohol_frequency == 'moderate':
        points += 2
    # 'none' adds 0

    if exercise_frequency == 'none':
        points += 5
    elif exercise_frequency == 'regular':
        points -= 5
    # 'moderate' adds 0

    return points


def medical_history_risk_points(family_history, chronic_condition):
    points = 0
    if family_history:
        points += 8
    if chronic_condition:
        points += 12
    return points


def calculate_risk_score(bmi, smoker, alcohol_frequency, exercise_frequency,
                          family_history, chronic_condition):
    """Combines all factors into a single risk score, clamped to [0, 100]."""
    score = (
        bmi_risk_points(bmi)
        + lifestyle_risk_points(smoker, alcohol_frequency, exercise_frequency)
        + medical_history_risk_points(family_history, chronic_condition)
    )
    return max(0, min(100, score))


def categorize_risk(risk_score):
    if risk_score < 0 or risk_score > 100:
        raise ValueError("risk_score must be between 0 and 100")
    if risk_score <= RISK_LOW_MAX:
        return "Low Risk"
    elif risk_score <= RISK_MODERATE_MAX:
        return "Moderate Risk"
    else:
        return "High Risk"


def estimate_remaining_years(age, risk_score):
    """
    Illustrative formula: remaining years = (baseline - current age),
    reduced by the risk score at a fixed rate, floored at 0.
    """
    if age < 0 or age > 120:
        raise ValueError("age must be between 0 and 120")
    if risk_score < 0 or risk_score > 100:
        raise ValueError("risk_score must be between 0 and 100")

    base_remaining = BASE_LIFE_EXPECTANCY - age
    adjusted = base_remaining - (risk_score * 0.2)
    return round(max(0.0, adjusted), 1)


def compute_assessment(age, gender, height_cm, weight_kg, smoker,
                        alcohol_frequency, exercise_frequency,
                        family_history, chronic_condition):
    """
    Top-level orchestration function — computes the full assessment result
    from raw inputs. This is the function the Flask route calls; it is
    also the single function most heavily covered by integration tests
    (since it combines every branch above).
    """
    if age < 1 or age > 120:
        raise ValueError("age must be between 1 and 120")
    if gender not in ('Male', 'Female', 'Other'):
        raise ValueError("gender must be Male, Female, or Other")

    bmi = calculate_bmi(height_cm, weight_kg)
    risk_score = calculate_risk_score(
        bmi, smoker, alcohol_frequency, exercise_frequency,
        family_history, chronic_condition
    )
    risk_category = categorize_risk(risk_score)
    remaining_years = estimate_remaining_years(age, risk_score)

    return {
        "bmi": bmi,
        "risk_score": risk_score,
        "risk_category": risk_category,
        "estimated_remaining_years": remaining_years,
    }


# ======================================================================
# Enhanced features: factor breakdown, tailored advice, what-if simulator,
# and feedback validation. All pure functions (no Flask / DB).
# ======================================================================

NORMAL_BMI_TARGET = 22.0  # mid-point of the normal band, used in what-if
HELPFUL_CHOICES = ('yes', 'somewhat', 'no')
MAX_COMMENT_LENGTH = 500


def risk_breakdown(bmi, smoker, alcohol_frequency, exercise_frequency,
                   family_history, chronic_condition):
    """
    Per-factor contribution to the risk score (used by the factor chart).
    Returns a list of dicts: {key, label, points, modifiable}.
    The sum of 'points' equals the unclamped risk score.
    """
    # Validates alcohol/exercise values (raises ValueError if invalid)
    lifestyle_risk_points(smoker, alcohol_frequency, exercise_frequency)

    alcohol_points = {'none': 0, 'moderate': 2, 'heavy': 5}[alcohol_frequency]
    exercise_points = {'none': 5, 'moderate': 0, 'regular': -5}[exercise_frequency]

    return [
        {"key": "bmi", "label": "BMI", "points": bmi_risk_points(bmi), "modifiable": True},
        {"key": "smoking", "label": "Smoking", "points": 15 if smoker else 0, "modifiable": True},
        {"key": "alcohol", "label": "Alcohol", "points": alcohol_points, "modifiable": True},
        {"key": "exercise", "label": "Exercise", "points": exercise_points, "modifiable": True},
        {"key": "family", "label": "Family history", "points": 8 if family_history else 0, "modifiable": False},
        {"key": "chronic", "label": "Chronic condition", "points": 12 if chronic_condition else 0, "modifiable": False},
    ]


_CATEGORY_HEADLINES = {
    "Low Risk": "Your current profile is in the low-risk band. Focus on keeping your healthy habits going.",
    "Moderate Risk": "Your profile is in the moderate-risk band. A few targeted changes can move you down a band.",
    "High Risk": "Your profile is in the high-risk band. Prioritise the high-priority actions below and speak to a doctor.",
}


def get_recommendations(risk_category, bmi, smoker, alcohol_frequency,
                        exercise_frequency, family_history, chronic_condition):
    """
    Returns {"headline": str, "items": [ {priority, title, text}, ... ]}
    Advice depends on BOTH the risk category and the specific factors the
    user entered. Items are sorted high -> medium -> low priority.
    """
    if risk_category not in _CATEGORY_HEADLINES:
        raise ValueError("Unknown risk category")

    items = []

    if smoker:
        items.append({"priority": "high", "title": "Quit smoking",
                      "text": "Smoking is the largest single factor in this model (+15 points). "
                              "Ask a doctor about cessation programmes or nicotine replacement."})
    if chronic_condition:
        items.append({"priority": "high", "title": "Keep up regular medical check-ups",
                      "text": "A chronic condition adds +12 points. Follow your treatment plan and "
                              "schedule periodic reviews with your doctor."})
    if bmi > BMI_OVERWEIGHT_MAX:
        items.append({"priority": "high", "title": "Work towards a healthier weight",
                      "text": f"Your BMI ({bmi:.1f}) is in the obese range (+10 points). A gradual, "
                              "sustainable plan with a dietitian is more effective than crash diets."})
    elif bmi > BMI_NORMAL_MAX:
        items.append({"priority": "medium", "title": "Move BMI into the normal range",
                      "text": f"Your BMI ({bmi:.1f}) is in the overweight range (+5 points). "
                              "Balanced meals and more daily movement can bring it down."})
    elif bmi < BMI_UNDERWEIGHT:
        items.append({"priority": "medium", "title": "Increase nutrition intake",
                      "text": f"Your BMI ({bmi:.1f}) is underweight (+3 points). Consider "
                              "nutrient-dense meals and speak to a dietitian."})

    if alcohol_frequency == 'heavy':
        items.append({"priority": "high", "title": "Cut down on alcohol",
                      "text": "Heavy drinking adds +5 points. Reducing to occasional or no alcohol "
                              "removes this factor completely."})
    elif alcohol_frequency == 'moderate':
        items.append({"priority": "low", "title": "Keep alcohol occasional",
                      "text": "Moderate drinking adds +2 points; cutting back further removes it."})

    if exercise_frequency == 'none':
        items.append({"priority": "medium", "title": "Start light regular exercise",
                      "text": "No exercise adds +5 points. Even 30 minutes of brisk walking, "
                              "5 days a week, moves you to the neutral band."})
    elif exercise_frequency == 'moderate':
        items.append({"priority": "low", "title": "Step up to regular exercise",
                      "text": "Regular exercise earns -5 points. Try adding one or two extra sessions per week."})

    if family_history:
        items.append({"priority": "medium", "title": "Screen early for inherited conditions",
                      "text": "Family history cannot be changed (+8 points), but early screening "
                              "helps catch problems sooner."})

    if not items:
        items.append({"priority": "low", "title": "Maintain your healthy routine",
                      "text": "No risk-raising factors were found. Keep exercising, eating well "
                              "and having routine check-ups."})

    order = {"high": 0, "medium": 1, "low": 2}
    items.sort(key=lambda i: order[i["priority"]])
    return {"headline": _CATEGORY_HEADLINES[risk_category], "items": items}


def what_if_scenarios(age, bmi, smoker, alcohol_frequency, exercise_frequency,
                      family_history, chronic_condition):
    """
    Simulates the effect of changing ONE modifiable factor at a time (plus
    all together). Only scenarios that actually change something are returned.
    Each: {label, new_score, new_category, new_years, years_gained, score_change}
    """
    base_score = calculate_risk_score(bmi, smoker, alcohol_frequency, exercise_frequency,
                                      family_history, chronic_condition)
    base_years = estimate_remaining_years(age, base_score)

    changes = []  # (label, kwargs overriding the inputs)
    if smoker:
        changes.append(("Quit smoking", {"smoker": False}))
    if alcohol_frequency != 'none':
        changes.append(("Stop drinking alcohol", {"alcohol_frequency": 'none'}))
    if exercise_frequency != 'regular':
        changes.append(("Exercise regularly", {"exercise_frequency": 'regular'}))
    if bmi < BMI_UNDERWEIGHT or bmi > BMI_NORMAL_MAX:
        changes.append(("Reach a normal BMI", {"bmi": NORMAL_BMI_TARGET}))

    def run(label, overrides):
        params = dict(bmi=bmi, smoker=smoker, alcohol_frequency=alcohol_frequency,
                      exercise_frequency=exercise_frequency, family_history=family_history,
                      chronic_condition=chronic_condition)
        params.update(overrides)
        score = calculate_risk_score(**params)
        years = estimate_remaining_years(age, score)
        return {"label": label, "new_score": score,
                "new_category": categorize_risk(score), "new_years": years,
                "years_gained": round(years - base_years, 1),
                "score_change": score - base_score}

    scenarios = [run(label, ov) for label, ov in changes]
    if len(changes) > 1:
        combined = {}
        for _, ov in changes:
            combined.update(ov)
        scenarios.append(run("All changes together", combined))
    return scenarios


def validate_feedback(rating, helpful, comment):
    """
    Validates feedback input. Returns (rating:int, helpful:str, comment:str).
    Raises ValueError with a user-facing message on invalid input.
    """
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        raise ValueError("Please select a star rating from 1 to 5.")
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5.")
    if helpful not in HELPFUL_CHOICES:
        raise ValueError("Please tell us whether the advice was helpful.")
    comment = (comment or "").strip()
    if len(comment) > MAX_COMMENT_LENGTH:
        raise ValueError(f"Comment must be at most {MAX_COMMENT_LENGTH} characters.")
    return rating, helpful, comment