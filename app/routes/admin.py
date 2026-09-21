"""
app/routes/admin.py
Blueprint: admin_bp
Endpoints:
  GET  /api/admin/stats
  POST /api/admin/ingredients
  POST /api/admin/tags
"""
from flask import Blueprint, request
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.recipe import Recipe, Tag
from app.models.ingredient import Ingredient, IngredientSubstitute
from app.models.rating import Rating, ViewHistory
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """GET /api/admin/stats"""
    total_recipes = Recipe.query.count()
    published_recipes = Recipe.query.filter_by(is_published=True).count()
    total_users = User.query.count()
    total_ratings = Rating.query.count()
    total_views = ViewHistory.query.count()

    # Top 5 rated
    top_rated = (
        Recipe.query
        .filter(Recipe.is_published == True, Recipe.rating_count >= 1)  # noqa
        .order_by(Recipe.avg_rating.desc(), Recipe.rating_count.desc())
        .limit(5)
        .all()
    )

    # Most viewed (join với view_history)
    most_viewed_rows = (
        db.session.query(
            Recipe,
            func.count(ViewHistory.id).label("view_count"),
        )
        .join(ViewHistory, Recipe.id == ViewHistory.recipe_id)
        .filter(Recipe.is_published == True)  # noqa
        .group_by(Recipe.id)
        .order_by(func.count(ViewHistory.id).desc())
        .limit(5)
        .all()
    )

    # Recent ratings
    recent_ratings = (
        Rating.query
        .order_by(Rating.created_at.desc())
        .limit(10)
        .all()
    )

    return success_response(data={
        "total_recipes": total_recipes,
        "published_recipes": published_recipes,
        "draft_recipes": total_recipes - published_recipes,
        "total_users": total_users,
        "total_ratings": total_ratings,
        "total_views": total_views,
        "top_rated_recipes": [r.to_dict_list() for r in top_rated],
        "most_viewed_recipes": [
            {**r.to_dict_list(), "view_count": vc}
            for r, vc in most_viewed_rows
        ],
        "recent_ratings": [r.to_dict() for r in recent_ratings],
    })


@admin_bp.route("/ingredients", methods=["POST"])
@admin_required
def create_ingredient():
    """
    POST /api/admin/ingredients
    Body: { "name": "Cà rốt", "category": "rau_cu", "unit": "g", "emoji": "🥕", "calories_per_100g": 41 }
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return error_response("Tên nguyên liệu là bắt buộc", 400)

    if Ingredient.query.filter_by(name=name).first():
        return error_response("Nguyên liệu đã tồn tại", 409)

    ing = Ingredient(
        name=name,
        category=data.get("category", "khac"),
        unit=data.get("unit", "g"),
        emoji=data.get("emoji", "🥗"),
        calories_per_100g=data.get("calories_per_100g"),
    )
    db.session.add(ing)
    db.session.commit()

    return success_response(data=ing.to_dict(), message="Tạo nguyên liệu thành công", status_code=201)


@admin_bp.route("/tags", methods=["POST"])
@admin_required
def create_tag():
    """
    POST /api/admin/tags
    Body: { "name": "cay", "color": "#FF4444" }
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    color = (data.get("color") or "#607D8B").strip()

    if not name:
        return error_response("Tên tag là bắt buộc", 400)

    if Tag.query.filter_by(name=name).first():
        return error_response("Tag đã tồn tại", 409)

    tag = Tag(name=name, color=color)
    db.session.add(tag)
    db.session.commit()

    return success_response(data=tag.to_dict(), message="Tạo tag thành công", status_code=201)


@admin_bp.route("/ingredients/<int:ingredient_id>/substitutes", methods=["POST"])
@admin_required
def add_substitute(ingredient_id):
    """
    POST /api/admin/ingredients/:id/substitutes
    Body: { "substitute_id": 11, "note": "Dùng 3/4 lượng bơ" }
    """
    ing = Ingredient.query.get(ingredient_id)
    if not ing:
        return error_response("Nguyên liệu không tồn tại", 404)

    data = request.get_json(silent=True) or {}
    substitute_id = data.get("substitute_id")
    note = data.get("note", "")

    if not substitute_id:
        return error_response("substitute_id là bắt buộc", 400)

    sub_ing = Ingredient.query.get(substitute_id)
    if not sub_ing:
        return error_response("Nguyên liệu thay thế không tồn tại", 404)

    sub = IngredientSubstitute(
        ingredient_id=ingredient_id,
        substitute_id=substitute_id,
        note=note or None,
    )
    db.session.add(sub)
    db.session.commit()

    return success_response(
        data=sub.to_dict(),
        message="Đã thêm nguyên liệu thay thế",
        status_code=201,
    )
