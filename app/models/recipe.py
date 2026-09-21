"""
app/models/recipe.py
Bảng: recipes, steps, tags, recipe_tags
"""
from datetime import datetime, timezone
from app import db


def _utcnow():
    return datetime.now(timezone.utc)


# Bảng trung gian nhiều-nhiều recipe ↔ tag
recipe_tags = db.Table(
    "recipe_tags",
    db.Column(
        "recipe_id",
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(10), nullable=False, default="#607D8B")  # hex color

    # Relationships
    recipes = db.relationship("Recipe", secondary=recipe_tags, back_populates="tags")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
        }

    def __repr__(self):
        return f"<Tag {self.name}>"


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    difficulty = db.Column(
        db.Enum("easy", "medium", "hard", name="difficulty_enum"),
        nullable=False,
        default="medium",
    )
    cook_time_min = db.Column(db.Integer, nullable=False, default=30)
    prep_time_min = db.Column(db.Integer, nullable=False, default=15)
    servings = db.Column(db.Integer, nullable=False, default=4)

    avg_rating = db.Column(db.Float, default=0.0, nullable=False)
    rating_count = db.Column(db.Integer, default=0, nullable=False)

    is_published = db.Column(db.Boolean, default=False, nullable=False)

    # Vùng miền: 'mien_nam' | 'mien_bac' | 'mien_trung' | 'quoc_te'
    region = db.Column(db.String(20), nullable=True)

    created_by = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    tags = db.relationship("Tag", secondary=recipe_tags, back_populates="recipes")
    steps = db.relationship(
        "Step",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="Step.step_number",
    )
    recipe_ingredients = db.relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    ratings = db.relationship(
        "Rating", back_populates="recipe", cascade="all, delete-orphan"
    )
    view_history = db.relationship(
        "ViewHistory", back_populates="recipe", cascade="all, delete-orphan"
    )

    def to_dict_list(self):
        """Trả về dữ liệu rút gọn dùng trong danh sách (list view)."""
        return {
            "id": self.id,
            "name": self.name,
            "image_url": self.image_url,
            "difficulty": self.difficulty,
            "cook_time_min": self.cook_time_min,
            "prep_time_min": self.prep_time_min,
            "servings": self.servings,
            "avg_rating": round(self.avg_rating, 1),
            "rating_count": self.rating_count,
            "region": self.region,
            "tags": [t.name for t in self.tags],
            "ingredient_count": len(
                [ri for ri in self.recipe_ingredients if not ri.is_optional]
            ),
            "is_published": self.is_published,
        }

    def to_dict_detail(self):
        """Trả về dữ liệu đầy đủ cho trang chi tiết."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "difficulty": self.difficulty,
            "cook_time_min": self.cook_time_min,
            "prep_time_min": self.prep_time_min,
            "servings": self.servings,
            "avg_rating": round(self.avg_rating, 1),
            "rating_count": self.rating_count,
            "region": self.region,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tags": [t.to_dict() for t in self.tags],
            "ingredients": [ri.to_dict() for ri in self.recipe_ingredients],
            "steps": [s.to_dict() for s in self.steps],
        }

    def __repr__(self):
        return f"<Recipe {self.name}>"


class Step(db.Model):
    __tablename__ = "steps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    duration_min = db.Column(db.Integer, nullable=True)

    # Relationships
    recipe = db.relationship("Recipe", back_populates="steps")

    def to_dict(self):
        return {
            "step_number": self.step_number,
            "description": self.description,
            "image_url": self.image_url,
            "duration_min": self.duration_min,
        }

    def __repr__(self):
        return f"<Step {self.recipe_id}#{self.step_number}>"


# Alias để import rõ ràng từ bên ngoài
RecipeTag = recipe_tags
