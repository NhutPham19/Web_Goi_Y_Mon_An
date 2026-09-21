"""
app/services/ingredient_search.py
Thuật toán tìm công thức theo danh sách nguyên liệu có sẵn.
"""
from sqlalchemy import func, distinct
from app import db
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient, RecipeIngredient


def search_by_ingredients(ingredient_ids: list, match_mode: str = "any") -> list:
    """
    Tìm công thức phù hợp với danh sách nguyên liệu đã có.
    
    Args:
        ingredient_ids: List[int] — ID các nguyên liệu người dùng có
        match_mode:
            "any" — công thức dùng ít nhất 1 trong số nguyên liệu trên
            "all" — công thức chỉ dùng những nguyên liệu người dùng có (có thể thiếu optional)
    
    Returns:
        List[dict] sorted by matched_count DESC
    """
    if not ingredient_ids:
        return []

    # Subquery: đếm số nguyên liệu bắt buộc mỗi recipe
    total_required_sq = (
        db.session.query(
            RecipeIngredient.recipe_id,
            func.count(RecipeIngredient.id).label("total_required"),
        )
        .filter(RecipeIngredient.is_optional == False)  # noqa
        .group_by(RecipeIngredient.recipe_id)
        .subquery()
    )

    # Subquery: đếm số nguyên liệu match với list người dùng có
    matched_sq = (
        db.session.query(
            RecipeIngredient.recipe_id,
            func.count(distinct(RecipeIngredient.ingredient_id)).label("matched_count"),
        )
        .filter(RecipeIngredient.ingredient_id.in_(ingredient_ids))
        .filter(RecipeIngredient.is_optional == False)  # noqa
        .group_by(RecipeIngredient.recipe_id)
        .subquery()
    )

    # Join recipe với 2 subquery
    rows = (
        db.session.query(
            Recipe,
            matched_sq.c.matched_count,
            total_required_sq.c.total_required,
        )
        .join(matched_sq, Recipe.id == matched_sq.c.recipe_id)
        .join(total_required_sq, Recipe.id == total_required_sq.c.recipe_id)
        .filter(Recipe.is_published == True)  # noqa
        .order_by(matched_sq.c.matched_count.desc())
        .all()
    )

    results = []
    for recipe, matched_count, total_required in rows:
        # Lọc theo match_mode
        if match_mode == "all":
            # "all": tất cả nguyên liệu bắt buộc phải được match
            if matched_count < total_required:
                continue

        match_percent = round((matched_count / total_required * 100), 1) if total_required else 0

        # Lấy danh sách nguyên liệu đã match
        matched_ings = (
            db.session.query(Ingredient)
            .join(RecipeIngredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .filter(
                RecipeIngredient.recipe_id == recipe.id,
                RecipeIngredient.ingredient_id.in_(ingredient_ids),
                RecipeIngredient.is_optional == False,  # noqa
            )
            .all()
        )

        # Lấy danh sách nguyên liệu còn thiếu
        missing_ings = (
            db.session.query(Ingredient)
            .join(RecipeIngredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .filter(
                RecipeIngredient.recipe_id == recipe.id,
                RecipeIngredient.ingredient_id.notin_(ingredient_ids),
                RecipeIngredient.is_optional == False,  # noqa
            )
            .all()
        )

        results.append({
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "image_url": recipe.image_url,
            "difficulty": recipe.difficulty,
            "cook_time_min": recipe.cook_time_min,
            "avg_rating": round(recipe.avg_rating, 1),
            "tags": [t.name for t in recipe.tags],
            "matched_ingredients": [f"{i.name} {i.emoji}" for i in matched_ings],
            "matched_count": matched_count,
            "total_required": total_required,
            "match_percent": match_percent,
            "missing_ingredients": [f"{i.name} {i.emoji}" for i in missing_ings],
        })

    return results
