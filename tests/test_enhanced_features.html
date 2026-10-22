"""
Tests for the enhanced features: factor breakdown, tailored advice,
what-if simulator, SVG charts, and the feedback module.
Mix of white-box (unit), black-box (HTTP) and integration (DB) tests.
"""
import re
import pytest
from conftest import VALID_ASSESSMENT_FORM
import business_logic as bl
import charts
from app import create_app
from models import db, Feedback

WORST = dict(age="35", gender="Female", height_cm="165", weight_kg="95", smoker="yes",
             alcohol_frequency="heavy", exercise_frequency="none",
             family_history="yes", chronic_condition="yes")


# ------------------------- white-box: business logic -------------------------
class TestRiskBreakdown:
    def test_breakdown_sum_equals_risk_score(self):
        args = (34.6, True, 'heavy', 'none', True, True)
        assert sum(f["points"] for f in bl.risk_breakdown(*args)) == bl.calculate_risk_score(*args)

    def test_breakdown_healthy_profile_negative_exercise(self):
        bd = {f["key"]: f["points"] for f in bl.risk_breakdown(22, False, 'none', 'regular', False, False)}
        assert bd["exercise"] == -5 and bd["smoking"] == 0 and bd["bmi"] == 0

    def test_breakdown_moderate_alcohol(self):
        bd = {f["key"]: f["points"] for f in bl.risk_breakdown(22, False, 'moderate', 'moderate', False, False)}
        assert bd["alcohol"] == 2 and bd["exercise"] == 0

    def test_breakdown_rejects_invalid_alcohol(self):
        with pytest.raises(ValueError):
            bl.risk_breakdown(22, False, 'lots', 'none', False, False)

    def test_family_and_chronic_not_modifiable(self):
        mod = {f["key"]: f["modifiable"] for f in bl.risk_breakdown(22, False, 'none', 'none', True, True)}
        assert mod["family"] is False and mod["chronic"] is False and mod["smoking"] is True


class TestRecommendations:
    def test_unknown_category_rejected(self):
        with pytest.raises(ValueError):
            bl.get_recommendations("Extreme", 22, False, 'none', 'regular', False, False)

    def test_healthy_profile_gets_maintenance_advice(self):
        r = bl.get_recommendations("Low Risk", 22, False, 'none', 'regular', False, False)
        assert len(r["items"]) == 1 and r["items"][0]["title"] == "Maintain your healthy routine"

    def test_worst_profile_all_high_items_first(self):
        r = bl.get_recommendations("High Risk", 34.6, True, 'heavy', 'none', True, True)
        prios = [i["priority"] for i in r["items"]]
        assert prios == sorted(prios, key=lambda p: {"high": 0, "medium": 1, "low": 2}[p])
        titles = [i["title"] for i in r["items"]]
        assert "Quit smoking" in titles and "Cut down on alcohol" in titles
        assert "prioritise" in r["headline"].lower()

    @pytest.mark.parametrize("bmi,expected", [
        (17.0, "Increase nutrition intake"), (27.0, "Move BMI into the normal range"),
        (32.0, "Work towards a healthier weight")])
    def test_bmi_specific_advice(self, bmi, expected):
        r = bl.get_recommendations("Moderate Risk", bmi, False, 'none', 'regular', False, False)
        assert expected in [i["title"] for i in r["items"]]

    def test_moderate_alcohol_and_exercise_low_priority_tips(self):
        r = bl.get_recommendations("Low Risk", 22, False, 'moderate', 'moderate', False, False)
        titles = [i["title"] for i in r["items"]]
        assert "Keep alcohol occasional" in titles and "Step up to regular exercise" in titles

    def test_no_smoking_advice_for_non_smoker(self):
        r = bl.get_recommendations("Low Risk", 22, False, 'none', 'moderate', False, False)
        assert "Quit smoking" not in [i["title"] for i in r["items"]]


class TestWhatIf:
    def test_no_scenarios_for_ideal_profile(self):
        assert bl.what_if_scenarios(30, 22, False, 'none', 'regular', False, False) == []

    def test_single_change_has_no_combined_scenario(self):
        s = bl.what_if_scenarios(30, 22, True, 'none', 'regular', False, False)
        assert [x["label"] for x in s] == ["Quit smoking"]

    def test_quit_smoking_reduces_score_by_15_and_gains_3_years(self):
        s = bl.what_if_scenarios(35, 22, True, 'none', 'moderate', False, False)[0]
        assert (s["score_change"], s["new_score"], s["years_gained"]) == (-15, 0, 3.0)

    def test_combined_scenario_is_best(self):
        s = bl.what_if_scenarios(35, 34.6, True, 'heavy', 'none', True, True)
        assert s[-1]["label"] == "All changes together"
        assert s[-1]["new_score"] == min(x["new_score"] for x in s)
        assert s[-1]["new_category"] == "Low Risk"

    def test_underweight_bmi_scenario_present(self):
        labels = [x["label"] for x in bl.what_if_scenarios(30, 17, False, 'none', 'regular', False, False)]
        assert labels == ["Reach a normal BMI"]


class TestValidateFeedback:
    def test_valid_feedback_is_cleaned(self):
        assert bl.validate_feedback("4", "yes", "  nice  ") == (4, "yes", "nice")

    @pytest.mark.parametrize("rating", ["0", "6", "-1", "abc", "", None])
    def test_invalid_rating_rejected(self, rating):
        with pytest.raises(ValueError):
            bl.validate_feedback(rating, "yes", "")

    @pytest.mark.parametrize("rating", [1, 5])
    def test_rating_boundaries_accepted(self, rating):
        assert bl.validate_feedback(rating, "no", "")[0] == rating

    def test_invalid_helpful_rejected(self):
        with pytest.raises(ValueError):
            bl.validate_feedback(3, "maybe", "")

    def test_comment_length_boundary(self):
        assert bl.validate_feedback(3, "yes", "x" * 500)[2] == "x" * 500
        with pytest.raises(ValueError):
            bl.validate_feedback(3, "yes", "x" * 501)

    def test_none_comment_becomes_empty(self):
        assert bl.validate_feedback(3, "yes", None)[2] == ""


# ----------------------------- white-box: charts -----------------------------
class TestCharts:
    def test_gauge_contains_score_and_category(self):
        svg = charts.risk_gauge(55, "High Risk")
        assert "<svg" in svg and "55 / 100" in svg and "High Risk" in svg

    def test_gauge_clamps_out_of_range_scores(self):
        assert "100 / 100" in charts.risk_gauge(250, "High Risk")
        assert "0 / 100" in charts.risk_gauge(-5, "Low Risk")

    def test_gauge_escapes_category(self):
        assert "<script>" not in charts.risk_gauge(10, "<script>alert(1)</script>")

    def test_factor_chart_shows_signs(self):
        svg = charts.factor_bar_chart(bl.risk_breakdown(22, True, 'none', 'regular', False, False))
        assert "+15" in svg and "-5" in svg

    def test_factor_chart_zero_points_has_no_bar_but_label(self):
        svg = charts.factor_bar_chart([{"label": "BMI", "points": 0}])
        assert "<rect" not in svg and ">0<" in svg

    def test_years_chart_values(self):
        svg = charts.years_comparison_chart(35, 30.0, 78.0)
        assert "43.0 yrs" in svg and "30.0 yrs" in svg

    def test_years_chart_handles_zero_remaining(self):
        assert "0.0 yrs" in charts.years_comparison_chart(100, 0.0, 78.0)

    def test_what_if_chart_lists_current_and_scenarios(self):
        s = bl.what_if_scenarios(35, 34.6, True, 'heavy', 'none', True, True)
        svg = charts.what_if_chart(55, s)
        assert "Current" in svg and "Quit smoking" in svg

    def test_trend_empty(self):
        assert "No assessments yet" in charts.trend_chart([])

    def test_trend_single_point_has_no_line(self):
        svg = charts.trend_chart([30])
        assert "<polyline" not in svg and "<circle" in svg

    def test_trend_multiple_points_has_line(self):
        svg = charts.trend_chart([10, 30, 55])
        assert "<polyline" in svg and svg.count("<circle") == 3


# --------------------------- black-box: result page --------------------------
class TestResultDashboard:
    def test_dashboard_has_charts_advice_whatif_feedback(self, registered_client):
        r = registered_client.post("/assessment/new", data=WORST, follow_redirects=True)
        t = r.text
        assert t.count("<svg") >= 4
        assert "Personalised advice" in t and "Quit smoking" in t
        assert "What if you changed something?" in t and "All changes together" in t
        assert "Quick feedback" in t and 'name="assessment_id"' in t

    def test_low_risk_user_sees_maintenance_advice_and_no_whatif_table(self, registered_client):
        form = dict(VALID_ASSESSMENT_FORM, exercise_frequency="regular")
        t = registered_client.post("/assessment/new", data=form, follow_redirects=True).text
        assert "Maintain your healthy routine" in t
        assert "no modifiable risk factors left" in t

    def test_advice_differs_between_risk_levels(self, registered_client):
        hi = registered_client.post("/assessment/new", data=WORST, follow_redirects=True).text
        lo = registered_client.post("/assessment/new", data=dict(VALID_ASSESSMENT_FORM, exercise_frequency="regular"),
                                    follow_redirects=True).text
        assert "high-risk band" in hi and "low-risk band" in lo

    def test_history_shows_trend_chart(self, registered_client):
        registered_client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)
        registered_client.post("/assessment/new", data=WORST)
        t = registered_client.get("/history").text
        assert "Risk score trend" in t and "<polyline" in t

    def test_history_empty_has_no_trend(self, registered_client):
        assert "Risk score trend" not in registered_client.get("/history").text


# --------------------------- black-box: feedback HTTP -------------------------
class TestFeedbackRoutes:
    def test_feedback_requires_login(self, client):
        r = client.get("/feedback")
        assert r.status_code == 302 and "/login" in r.headers["Location"]

    def test_post_feedback_requires_login(self, client):
        assert client.post("/feedback", data={"rating": "5", "helpful": "yes"}).status_code == 302

    def test_feedback_page_renders(self, registered_client):
        t = registered_client.get("/feedback").text
        assert "Share your feedback" in t and "haven't submitted any feedback" in t

    def test_submit_valid_feedback(self, registered_client):
        r = registered_client.post("/feedback", data={"rating": "5", "helpful": "yes", "comment": "Great"},
                                   follow_redirects=True)
        assert "Thank you" in r.text and "Great" in r.text and "5/5" in r.text

    @pytest.mark.parametrize("data,msg", [
        ({"helpful": "yes"}, "star rating"),
        ({"rating": "6", "helpful": "yes"}, "between 1 and 5"),
        ({"rating": "3", "helpful": ""}, "helpful"),
        ({"rating": "3", "helpful": "yes", "comment": "x" * 501}, "at most 500"),
    ])
    def test_invalid_feedback_rejected(self, registered_client, data, msg):
        r = registered_client.post("/feedback", data=data, follow_redirects=True)
        assert msg in r.text and "Thank you" not in r.text

    def test_invalid_feedback_keeps_assessment_link(self, registered_client):
        registered_client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)
        r = registered_client.post("/feedback", data={"rating": "9", "helpful": "yes", "assessment_id": "1"})
        assert r.status_code == 302 and "assessment_id=1" in r.headers["Location"]

    def test_feedback_for_nonexistent_assessment_rejected(self, registered_client):
        r = registered_client.get("/feedback?assessment_id=999", follow_redirects=True)
        assert "Invalid assessment" in r.text


# ------------------------------- integration ---------------------------------
class TestFeedbackIntegration:
    def test_feedback_persisted_and_linked_to_assessment(self, app, registered_client):
        registered_client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)
        registered_client.post("/feedback", data={"rating": "4", "helpful": "somewhat",
                                                  "comment": "ok", "assessment_id": "1"})
        with app.app_context():
            f = Feedback.query.one()
            assert (f.rating, f.helpful, f.comment, f.assessment_id) == (4, "somewhat", "ok", 1)

    def test_general_feedback_has_no_assessment(self, app, registered_client):
        registered_client.post("/feedback", data={"rating": "3", "helpful": "no"})
        with app.app_context():
            assert Feedback.query.one().assessment_id is None

    def test_user_cannot_attach_feedback_to_other_users_assessment(self, app, registered_client):
        registered_client.post("/assessment/new", data=VALID_ASSESSMENT_FORM)
        registered_client.get("/logout")
        other = app.test_client()
        other.post("/register", data={"name": "B", "email": "b@test.com", "password": "pass123"})
        other.post("/login", data={"email": "b@test.com", "password": "pass123"})
        r = other.post("/feedback", data={"rating": "5", "helpful": "yes", "assessment_id": "1"},
                       follow_redirects=True)
        assert "Invalid assessment" in r.text
        with app.app_context():
            assert Feedback.query.count() == 0

    def test_users_only_see_their_own_feedback(self, app, registered_client):
        registered_client.post("/feedback", data={"rating": "5", "helpful": "yes", "comment": "secret-note"})
        registered_client.get("/logout")
        other = app.test_client()
        other.post("/register", data={"name": "B", "email": "b@test.com", "password": "pass123"})
        other.post("/login", data={"email": "b@test.com", "password": "pass123"})
        assert "secret-note" not in other.get("/feedback").text

    def test_comment_is_html_escaped_on_display(self, registered_client):
        registered_client.post("/feedback", data={"rating": "5", "helpful": "yes",
                                                  "comment": "<script>alert(1)</script>"})
        t = registered_client.get("/feedback").text
        assert "<script>alert(1)</script>" not in t and "&lt;script&gt;" in t