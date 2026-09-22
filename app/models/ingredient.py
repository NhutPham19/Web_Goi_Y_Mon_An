"""
app/models/ingredient.py
Bảng: ingredients, recipe_ingredients, ingredient_substitutes
"""
from app import db


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    # Phân loại: 'rau_cu', 'thit', 'hai_san', 'gia_vi', 'bot_duong', 'nuoc_sot',
    #            'trai_cay', 'sua_trung', 'hat', 'do_kho', 'khac'
    category = db.Column(db.String(50), nullable=False, default="khac")
    unit = db.Column(db.String(30), nullable=False, default="g")
    emoji = db.Column(db.String(10), nullable=False, default="🥗")
    calories_per_100g = db.Column(db.Float, nullable=True)

    # Relationships
    recipe_ingredients = db.relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan"
    )
    substitutes_as_original = db.relationship(
        "IngredientSubstitute",
        foreign_keys="IngredientSubstitute.ingredient_id",
        back_populates="original_ingredient",
        cascade="all, delete-orphan",
    )
    substitutes_as_substitute = db.relationship(
        "IngredientSubstitute",
        foreign_keys="IngredientSubstitute.substitute_id",
        back_populates="substitute_ingredient",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "unit": self.unit,
            "emoji": self.emoji,
            "calories_per_100g": self.calories_per_100g,
        }

    def __repr__(self):
        return f"<Ingredient {self.name}>"


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(30), nullable=False, default="g")
    is_optional = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    recipe = db.relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = db.relationship("Ingredient", back_populates="recipe_ingredients")

    def to_dict(self):
        ing = self.ingredient
        return {
            "ingredient_id": self.ingredient_id,
            "name": ing.name if ing else None,
            "emoji": ing.emoji if ing else None,
            "quantity": self.quantity,
            "unit": self.unit,
            "is_optional": self.is_optional,
        }

    def __repr__(self):
        return f"<RecipeIngredient recipe={self.recipe_id} ing={self.ingredient_id}>"


class IngredientSubstitute(db.Model):
    __tablename__ = "ingredient_substitutes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    substitute_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    note = db.Column(db.String(255), nullable=True)

    # Relationships
    original_ingredient = db.relationship(
        "Ingredient",
        foreign_keys=[ingredient_id],
        back_populates="substitutes_as_original",
    )
    substitute_ingredient = db.relationship(
        "Ingredient",
        foreign_keys=[substitute_id],
        back_populates="substitutes_as_substitute",
    )

    def to_dict(self):
        sub = self.substitute_ingredient
        return {
            "id": sub.id if sub else None,
            "name": sub.name if sub else None,
            "substitute_name": sub.name if sub else None,  # alias cho Frontend
            "emoji": sub.emoji if sub else None,
            "note": self.note,
        }

    def __repr__(self):
        return f"<IngredientSubstitute {self.ingredient_id}→{self.substitute_id}>"
