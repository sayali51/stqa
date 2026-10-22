"""
WHITE-BOX Unit Tests — business_logic.py
Technique: Statement & Branch Coverage — every if/elif/else branch
targeted deliberately, with full knowledge of the internal code.
Tool: pytest + pytest-cov
Level: Unit Testing
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from business_logic import (
    calculate_bmi, bmi_risk_points, lifestyle_risk_points,
    medical_history_risk_points, calculate_risk_score, categorize_risk,
    estimate_remaining_years, compute_assessment
)


# ---- calculate_bmi(): validation + formula ----
def test_calculate_bmi_valid():
    assert calculate_bmi(175, 70) == round(70 / (1.75 ** 2), 2)


def test_calculate_bmi_zero_height_raises():
    with pytest.raises(ValueError):
        calculate_bmi(0, 70)


def test_calculate_bmi_negative_weight_raises():
    with pytest.raises(ValueError):
        calculate_bmi(175, -5)


# ---- bmi_risk_points(): all four branches ----
def test_bmi_points_underweight_branch():
    assert bmi_risk_points(17.0) == 3


def test_bmi_points_normal_branch():
    assert bmi_risk_points(22.0) == 0


def test_bmi_points_overweight_branch():
    assert bmi_risk_points(27.0) == 5


def test_bmi_points_obese_branch():
    assert bmi_risk_points(32.0) == 10


# ---- lifestyle_risk_points(): smoker, alcohol, exercise branches ----
def test_lifestyle_points_smoker_adds_15():
    assert lifestyle_risk_points(True, 'none', 'moderate') == 15


def test_lifestyle_points_non_smoker_adds_0():
    assert lifestyle_risk_points(False, 'none', 'moderate') == 0


def test_lifestyle_points_alcohol_heavy_branch():
    assert lifestyle_risk_points(False, 'heavy', 'moderate') == 5


def test_lifestyle_points_alcohol_moderate_branch():
    assert lifestyle_risk_points(False, 'moderate', 'moderate') == 2


def test_lifestyle_points_alcohol_none_branch():
    assert lifestyle_risk_points(False, 'none', 'moderate') == 0


def test_lifestyle_points_exercise_none_branch():
    assert lifestyle_risk_points(False, 'none', 'none') == 5


def test_lifestyle_points_exercise_regular_branch():
    assert lifestyle_risk_points(False, 'none', 'regular') == -5


def test_lifestyle_points_exercise_moderate_branch():
    assert lifestyle_risk_points(False, 'none', 'moderate') == 0


def test_lifestyle_points_invalid_alcohol_raises():
    with pytest.raises(ValueError):
        lifestyle_risk_points(False, 'excessive', 'moderate')


def test_lifestyle_points_invalid_exercise_raises():
    with pytest.raises(ValueError):
        lifestyle_risk_points(False, 'none', 'extreme')


# ---- medical_history_risk_points(): both flags ----
def test_medical_history_both_true():
    assert medical_history_risk_points(True, True) == 20


def test_medical_history_both_false():
    assert medical_history_risk_points(False, False) == 0


# ---- calculate_risk_score(): worst-case sum and clamp-at-zero floor ----
def test_risk_score_worst_case_sum():
    # bmi obese(+10) + smoker(+15) + alcohol heavy(+5) + exercise none(+5)
    # + family history(+8) + chronic condition(+12) = 55 (max achievable
    # with current weights -- confirms the scoring formula sums correctly
    # across every risk factor simultaneously)
    score = calculate_risk_score(32.0, True, 'heavy', 'none', True, True)
    assert score == 55


def test_risk_score_clamped_at_zero_floor():
    # bmi normal(+0) + non-smoker(+0) + no alcohol(+0) + regular exercise(-5)
    # would mathematically go negative (-5); the max(0, ...) clamp must
    # floor it at 0 rather than returning a negative risk score
    score = calculate_risk_score(22.0, False, 'none', 'regular', False, False)
    assert score == 0


# ---- categorize_risk(): all three bands + boundaries ----
def test_categorize_risk_low_boundary_20():
    assert categorize_risk(20) == "Low Risk"


def test_categorize_risk_moderate_boundary_21():
    assert categorize_risk(21) == "Moderate Risk"


def test_categorize_risk_moderate_boundary_50():
    assert categorize_risk(50) == "Moderate Risk"


def test_categorize_risk_high_boundary_51():
    assert categorize_risk(51) == "High Risk"


def test_categorize_risk_invalid_raises():
    with pytest.raises(ValueError):
        categorize_risk(150)


# ---- estimate_remaining_years(): validation + floor ----
def test_estimate_remaining_years_normal():
    assert estimate_remaining_years(40, 20) == round((78 - 40) - (20 * 0.2), 1)


def test_estimate_remaining_years_floored_at_zero():
    # Very old age + max risk score should floor at 0, not go negative
    assert estimate_remaining_years(120, 100) == 0.0


def test_estimate_remaining_years_invalid_age_raises():
    with pytest.raises(ValueError):
        estimate_remaining_years(-5, 20)


def test_estimate_remaining_years_invalid_risk_score_raises():
    with pytest.raises(ValueError):
        estimate_remaining_years(40, 150)


# ---- compute_assessment(): top-level orchestration ----
def test_compute_assessment_full_flow():
    result = compute_assessment(
        age=30, gender='Female', height_cm=165, weight_kg=60,
        smoker=False, alcohol_frequency='none', exercise_frequency='regular',
        family_history=False, chronic_condition=False
    )
    assert result['risk_category'] == 'Low Risk'
    assert result['risk_score'] == 0
    assert result['bmi'] == round(60 / (1.65 ** 2), 2)


def test_compute_assessment_invalid_age_raises():
    with pytest.raises(ValueError):
        compute_assessment(
            age=0, gender='Male', height_cm=170, weight_kg=70,
            smoker=False, alcohol_frequency='none', exercise_frequency='none',
            family_history=False, chronic_condition=False
        )


def test_compute_assessment_invalid_gender_raises():
    with pytest.raises(ValueError):
        compute_assessment(
            age=30, gender='Unknown', height_cm=170, weight_kg=70,
            smoker=False, alcohol_frequency='none', exercise_frequency='none',
            family_history=False, chronic_condition=False
        )