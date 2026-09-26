"""
app/services/ingredient_search.py
Thuật toán tìm công thức theo danh sách nguyên liệu có sẵn.
"""
from sqlalchemy import func, distinct
from app import db
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient, RecipeIngredient


PANTRY_STAPLE_NAMES = {
    "Muối", "Đường trắng", "Đường thốt nốt", "Nước mắm",
    "Nước tương (xì dầu)", "Dầu ăn", "Bột ngọt (mì chính)",
    "Hạt nêm", "Tiêu đen"
}


def search_by_ingredients(ingredient_ids: list, match_mode: str = "any") -> list:
    """
    Tìm công thức phù hợp với danh sách nguyên liệu đã có.
    Tự động hỗ trợ Pantry Staples (gia vị cơ bản) để người dùng không phải chọn mắm, muối, dầu ăn.
    
    Args:
        ingredient_ids: List[int] — ID các nguyên liệu người dùng chọn
        match_mode: "any" hoặc "all"
    
    Returns:
        List[dict] sorted by match_percent DESC, protein_match DESC
    """
    if not ingredient_ids:
        return []

    # Lấy danh sách ID của các gia vị cơ bản bếp nào cũng có
    staple_rows = db.session.query(Ingredient.id).filter(Ingredient.name.in_(PANTRY_STAPLE_NAMES)).all()
    staple_ids = {r[0] for r in staple_rows}

    # Danh sách nguyên liệu hiệu dụng: Nguyên liệu người dùng chọn + Gia vị cơ bản
    effective_ids = list(set(ingredient_ids) | staple_ids)

    # Subquery: đếm số nguyên liệu bắt buộc (loại trừ gia vị cơ bản để tính mẫu số chính xác)
    total_required_sq = (
        db.session.query(
            RecipeIngredient.recipe_id,
            func.count(RecipeIngredient.id).label("total_required"),
        )
        .filter(RecipeIngredient.is_optional == False)
        .filter(RecipeIngredient.ingredient_id.notin_(staple_ids))
        .group_by(RecipeIngredient.recipe_id)
        .subquery()
    )

    # Subquery: đếm số nguyên liệu match từ danh sách người dùng chọn (loại trừ gia vị cơ bản)
    matched_sq = (
        db.session.query(
            RecipeIngredient.recipe_id,
            func.count(distinct(RecipeIngredient.ingredient_id)).label("matched_count"),
        )
        .filter(RecipeIngredient.ingredient_id.in_(ingredient_ids))
        .filter(RecipeIngredient.is_optional == False)
        .filter(RecipeIngredient.ingredient_id.notin_(staple_ids))
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
        .filter(Recipe.is_published == True)
        .all()
    )

    # Xác định các ID nguyên liệu đạm/thịt/hải sản mà người dùng đã chọn
    user_protein_ids = set(
        r[0] for r in db.session.query(Ingredient.id)
        .filter(Ingredient.id.in_(ingredient_ids))
        .filter(Ingredient.category.in_(["thit", "hai_san", "sua_trung"]))
        .all()
    )

    results = []
    for recipe, matched_count, total_required in rows:
        if matched_count <= 0:
            continue

        # Lọc theo match_mode
        if match_mode == "all":
            if matched_count < total_required:
                continue

        # Tính % khớp trên các nguyên liệu cốt lõi (đã loại trừ gia vị cơ bản)
        raw_percent = (matched_count / total_required * 100) if total_required else 100
        match_percent = min(100.0, max(0.0, round(raw_percent, 1)))

        # Kiểm tra món này có khớp nguyên liệu đạm chính không
        recipe_ing_ids = {ri.ingredient_id for ri in recipe.recipe_ingredients}
        has_protein_match = bool(user_protein_ids & recipe_ing_ids)

        # Lấy danh sách nguyên liệu người dùng đã có trong món này
        matched_ings = (
            db.session.query(Ingredient)
            .join(RecipeIngredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .filter(
                RecipeIngredient.recipe_id == recipe.id,
                RecipeIngredient.ingredient_id.in_(ingredient_ids),
            )
            .all()
        )

        # Lấy danh sách nguyên liệu còn thiếu (chỉ báo thiếu nguyên liệu chính, không đòi muối/nước mắm)
        missing_ings = (
            db.session.query(Ingredient)
            .join(RecipeIngredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .filter(
                RecipeIngredient.recipe_id == recipe.id,
                RecipeIngredient.ingredient_id.notin_(effective_ids),
                RecipeIngredient.ingredient_id.notin_(staple_ids),
                RecipeIngredient.is_optional == False,
            )
            .all()
        )

        results.append({
            # Nested recipe object
            "recipe": {
                "id": recipe.id,
                "name": recipe.name,
                "image_url": recipe.image_url,
                "difficulty": recipe.difficulty,
                "cook_time_min": recipe.cook_time_min,
                "avg_rating": round(recipe.avg_rating, 1),
                "rating_count": recipe.rating_count,
                "region": recipe.region,
                "tags": [t.name for t in recipe.tags],
                "is_saved": False,
            },
            # Flat fields
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "image_url": recipe.image_url,
            "difficulty": recipe.difficulty,
            "cook_time_min": recipe.cook_time_min,
            "avg_rating": round(recipe.avg_rating, 1),
            "region": recipe.region,
            "tags": [t.name for t in recipe.tags],
            "matched_ingredients": [f"{i.name} {i.emoji}" for i in matched_ings],
            "matched_count": matched_count,
            "total_required": total_required,
            "match_percent": match_percent,
            "missing_ingredients": [f"{i.name} {i.emoji}" for i in missing_ings],
            "has_protein_match": has_protein_match,
        })

    # Sắp xếp ưu tiên:
    # 1. Có khớp đạm chính lên trước
    # 2. match_percent cao hơn lên trước
    # 3. matched_count nhiều hơn lên trước
    results.sort(
        key=lambda x: (
            1 if x["has_protein_match"] else 0,
            x["match_percent"],
            x["matched_count"],
        ),
        reverse=True,
    )

    return results
