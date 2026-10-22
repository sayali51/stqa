"""
Life Expectancy & Health Risk Estimator
(OOMD/OOAD case study: "Death Prediction System" — implemented as an
educational, rule-based actuarial-style estimator for an STQA
mini-project. See business_logic.py for the academic disclaimer.)

- Persistent SQLite database (via SQLAlchemy)
- Hashed passwords (werkzeug security)
- Session-based authentication
- Server-rendered HTML pages (Jinja2 templates)
- Application factory (create_app) so tests run against an isolated
  in-memory database.
"""
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

from models import db, User, Assessment, Feedback
from business_logic import (compute_assessment, risk_breakdown, get_recommendations,
                            what_if_scenarios, validate_feedback, BASE_LIFE_EXPECTANCY)
import charts


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///death_prediction.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    def login_required(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "error")
                return redirect(url_for("login"))
            return view_func(*args, **kwargs)
        return wrapped

    # ---------------- routes ----------------
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("new_assessment"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()

            if not name or not email or not password:
                flash("Name, email and password are all required.", "error")
                return render_template("register.html")
            if "@" not in email:
                flash("Please enter a valid email address.", "error")
                return render_template("register.html")
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "error")
                return render_template("register.html")
            if User.query.filter_by(email=email).first() is not None:
                flash("An account with this email already exists.", "error")
                return render_template("register.html")

            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                session["user_id"] = user.id
                session["user_name"] = user.name
                flash(f"Welcome back, {user.name}!", "success")
                return redirect(url_for("new_assessment"))
            flash("Invalid email or password.", "error")
            return render_template("login.html")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    @app.route("/assessment/new", methods=["GET", "POST"])
    @login_required
    def new_assessment():
        if request.method == "POST":
            try:
                age = int(request.form.get("age", ""))
                gender = request.form.get("gender", "")
                height_cm = float(request.form.get("height_cm", ""))
                weight_kg = float(request.form.get("weight_kg", ""))
                smoker = request.form.get("smoker") == "yes"
                alcohol_frequency = request.form.get("alcohol_frequency", "")
                exercise_frequency = request.form.get("exercise_frequency", "")
                family_history = request.form.get("family_history") == "yes"
                chronic_condition = request.form.get("chronic_condition") == "yes"
            except ValueError:
                flash("Please enter valid numeric values for age, height, and weight.", "error")
                return render_template("assessment_form.html")

            try:
                result = compute_assessment(
                    age=age, gender=gender, height_cm=height_cm, weight_kg=weight_kg,
                    smoker=smoker, alcohol_frequency=alcohol_frequency,
                    exercise_frequency=exercise_frequency,
                    family_history=family_history, chronic_condition=chronic_condition
                )
            except ValueError as e:
                flash(str(e), "error")
                return render_template("assessment_form.html")

            assessment = Assessment(
                user_id=session["user_id"], age=age, gender=gender,
                height_cm=height_cm, weight_kg=weight_kg, smoker=smoker,
                alcohol_frequency=alcohol_frequency, exercise_frequency=exercise_frequency,
                family_history=family_history, chronic_condition=chronic_condition,
                bmi=result["bmi"], risk_score=result["risk_score"],
                risk_category=result["risk_category"],
                estimated_remaining_years=result["estimated_remaining_years"],
            )
            db.session.add(assessment)
            db.session.commit()
            flash("Assessment computed successfully.", "success")
            return redirect(url_for("assessment_detail", assessment_id=assessment.id))

        return render_template("assessment_form.html")

    @app.route("/assessment/<int:assessment_id>")
    @login_required
    def assessment_detail(assessment_id):
        assessment = db.session.get(Assessment, assessment_id)
        if assessment is None:
            flash("Assessment not found.", "error")
            return redirect(url_for("history"))
        if assessment.user_id != session["user_id"]:
            flash("You do not have access to this assessment.", "error")
            return redirect(url_for("history"))
        args = (assessment.bmi, assessment.smoker, assessment.alcohol_frequency,
                assessment.exercise_frequency, assessment.family_history,
                assessment.chronic_condition)
        breakdown = risk_breakdown(*args)
        advice = get_recommendations(assessment.risk_category, *args)
        scenarios = what_if_scenarios(assessment.age, *args)
        return render_template(
            "assessment_detail.html", a=assessment, breakdown=breakdown, advice=advice,
            scenarios=scenarios,
            gauge=charts.risk_gauge(assessment.risk_score, assessment.risk_category),
            factor_chart=charts.factor_bar_chart(breakdown),
            years_chart=charts.years_comparison_chart(
                assessment.age, assessment.estimated_remaining_years, BASE_LIFE_EXPECTANCY),
            whatif_chart=charts.what_if_chart(assessment.risk_score, scenarios),
        )

    @app.route("/history")
    @login_required
    def history():
        assessments = Assessment.query.filter_by(
            user_id=session["user_id"]
        ).order_by(Assessment.id.desc()).all()
        trend = charts.trend_chart([a.risk_score for a in reversed(assessments)])
        return render_template("history.html", assessments=assessments, trend=trend)

    @app.route("/feedback", methods=["GET", "POST"])
    @login_required
    def feedback():
        assessment_id = request.values.get("assessment_id", type=int)
        if assessment_id is not None:
            owned = db.session.get(Assessment, assessment_id)
            if owned is None or owned.user_id != session["user_id"]:
                flash("Invalid assessment for feedback.", "error")
                return redirect(url_for("feedback"))

        if request.method == "POST":
            try:
                rating, helpful, comment = validate_feedback(
                    request.form.get("rating"), request.form.get("helpful"),
                    request.form.get("comment"))
            except ValueError as e:
                flash(str(e), "error")
                return redirect(url_for("feedback", assessment_id=assessment_id)) \
                    if assessment_id else redirect(url_for("feedback"))
            db.session.add(Feedback(user_id=session["user_id"], assessment_id=assessment_id,
                                    rating=rating, helpful=helpful, comment=comment))
            db.session.commit()
            flash("Thank you! Your feedback has been recorded.", "success")
            return redirect(url_for("feedback"))

        mine = Feedback.query.filter_by(user_id=session["user_id"]).order_by(Feedback.id.desc()).all()
        return render_template("feedback.html", assessment_id=assessment_id, past=mine)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)