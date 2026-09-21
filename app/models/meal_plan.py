"""
app/models/meal_plan.py
Bảng: meal_plans, saved_recipes, recommendation_cache
"""
from datetime import datetime, timezone
from app import db


def _utcnow():
    return datetime.now(timezone.utc)


class MealPlan(db.Model):
    __tablename__ = "meal_plans"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week_start = db.Column(db.Date, nullable=False)
    # 0=Thứ 2, 1=Thứ 3, ..., 6=Chủ nhật
    day_of_week = db.Column(db.Integer, nullable=False)
    meal_type = db.Column(
        db.Enum("breakfast", "lunch", "dinner", name="meal_type_enum"),
        nullable=False,
    )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)

    __table_args__ = (
        db.CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_day_of_week"),
    )

    # Relationships
    user = db.relationship("User", back_populates="meal_plans")
    recipe = db.relationship("Recipe")

    def to_dict(self):
        return {
            "id": self.id,
            "week_start": self.week_start.isoformat() if self.week_start else None,
            "day_of_week": self.day_of_week,
            "meal_type": self.meal_type,
            "recipe": self.recipe.to_dict_list() if self.recipe else None,
        }

    def __repr__(self):
        return f"<MealPlan user={self.user_id} day={self.day_of_week} {self.meal_type}>"


class SavedRecipe(db.Model):
    __tablename__ = "saved_recipes"

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    saved_at = db.Column(db.DateTime(timezone=True), default=_utcnow)

    # Relationships
    user = db.relationship("User", back_populates="saved_recipes")
    recipe = db.relationship("Recipe")

    def to_dict(self):
        return {
            "recipe_id": self.recipe_id,
            "saved_at": self.saved_at.isoformat() if self.saved_at else None,
            "recipe": self.recipe.to_dict_list() if self.recipe else None,
        }

    def __repr__(self):
        return f"<SavedRecipe user={self.user_id} recipe={self.recipe_id}>"


class RecommendationCache(db.Model):
    """Cache kết quả gợi ý để tránh tính toán ML mỗi request."""
    __tablename__ = "recommendation_cache"

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    score = db.Column(db.Float, nullable=False, default=0.0)
    # algorithm: 'cbf' | 'cf' | 'hybrid' | 'popular'
    algorithm = db.Column(db.String(20), nullable=False, default="cbf")
    generated_at = db.Column(db.DateTime(timezone=True), default=_utcnow)

    def __repr__(self):
        return f"<RecommendationCache user={self.user_id} recipe={self.recipe_id} algo={self.algorithm}>"
