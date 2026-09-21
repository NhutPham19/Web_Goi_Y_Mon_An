# Expose tất cả models để Flask-Migrate tự detect
from app.models.user import User, UserPreference          # noqa
from app.models.recipe import Recipe, Step, Tag, RecipeTag  # noqa
from app.models.ingredient import (                       # noqa
    Ingredient, RecipeIngredient, IngredientSubstitute
)
from app.models.rating import Rating, ViewHistory         # noqa
from app.models.meal_plan import MealPlan, SavedRecipe, RecommendationCache  # noqa
