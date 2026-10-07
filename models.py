"""
Database models (SQLAlchemy ORM) — persistent storage backed by SQLite.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    assessments = db.relationship("Assessment", backref="user", lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Assessment(db.Model):
    __tablename__ = "assessments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Inputs
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    smoker = db.Column(db.Boolean, nullable=False, default=False)
    alcohol_frequency = db.Column(db.String(20), nullable=False)
    exercise_frequency = db.Column(db.String(20), nullable=False)
    family_history = db.Column(db.Boolean, nullable=False, default=False)
    chronic_condition = db.Column(db.Boolean, nullable=False, default=False)

    # Computed results
    bmi = db.Column(db.Float, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    risk_category = db.Column(db.String(20), nullable=False)
    estimated_remaining_years = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))