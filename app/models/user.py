"""
app/models/user.py
Bảng: users, user_preferences
"""
import uuid
from datetime import datetime, timezone
from app import db


def _utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum("user", "admin", name="user_role_enum"),
        nullable=False,
        default="user",
    )
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    preferences = db.relationship(
        "UserPreference", back_populates="user", cascade="all, delete-orphan"
    )
    ratings = db.relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    view_history = db.relationship(
        "ViewHistory", back_populates="user", cascade="all, delete-orphan"
    )
    meal_plans = db.relationship(
        "MealPlan", back_populates="user", cascade="all, delete-orphan"
    )
    saved_recipes = db.relationship(
        "SavedRecipe", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(self, include_preferences=False):
        data = {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_preferences:
            data["preferences"] = [p.to_dict() for p in self.preferences]
        return data

    def __repr__(self):
        return f"<User {self.email}>"


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # pref_type: 'diet' | 'taste' | 'allergy' | 'serving_size'
    pref_type = db.Column(db.String(50), nullable=False)
    # pref_value: 'vegetarian' | 'spicy' | 'peanut' | '4'
    pref_value = db.Column(db.String(100), nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="preferences")

    def to_dict(self):
        return {
            "id": self.id,
            "pref_type": self.pref_type,
            "pref_value": self.pref_value,
        }

    def __repr__(self):
        return f"<UserPreference {self.pref_type}={self.pref_value}>"
