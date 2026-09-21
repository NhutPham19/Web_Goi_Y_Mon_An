"""
app/models/rating.py
Bảng: ratings, view_history
"""
from datetime import datetime, timezone
from app import db


def _utcnow():
    return datetime.now(timezone.utc)


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # score: 1-5
    score = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Mỗi user chỉ rate 1 lần mỗi recipe
    __table_args__ = (
        db.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_rating"),
        db.CheckConstraint("score >= 1 AND score <= 5", name="ck_score_range"),
    )

    # Relationships
    user = db.relationship("User", back_populates="ratings")
    recipe = db.relationship("Recipe", back_populates="ratings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "score": self.score,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_name": self.user.full_name if self.user else None,
        }

    def __repr__(self):
        return f"<Rating user={self.user_id} recipe={self.recipe_id} score={self.score}>"


class ViewHistory(db.Model):
    __tablename__ = "view_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    viewed_at = db.Column(db.DateTime(timezone=True), default=_utcnow)
    duration_sec = db.Column(db.Integer, nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="view_history")
    recipe = db.relationship("Recipe", back_populates="view_history")

    def __repr__(self):
        return f"<ViewHistory user={self.user_id} recipe={self.recipe_id}>"
