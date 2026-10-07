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