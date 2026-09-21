"""
app/routes/meal_plans.py
Blueprint: meal_plans_bp
Endpoints:
  GET    /api/meal-plans?week_start=2026-09-21
  POST   /api/meal-plans
  DELETE /api/meal-plans/:id
  GET    /api/meal-plans/shopping-list?week_start=2026-09-21
  GET    /api/users/me/saved
  POST   /api/users/me/saved
  DELETE /api/users/me/saved/:recipe_id
"""
from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func

from app import db
from app.models.meal_plan import MealPlan, SavedRecipe
from app.models.recipe import Recipe
from app.models.ingredient import RecipeIngredient, Ingredient
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required_custom

meal_plans_bp = Blueprint("meal_plans", __name__)

VALID_MEAL_TYPES = ("breakfast", "lunch", "dinner")


# ─── MEAL PLANS ──────────────────────────────────────────────────────────────

@meal_plans_bp.route("/meal-plans", methods=["GET"])
@jwt_required_custom
def get_meal_plan():
    """
    GET /api/meal-plans?week_start=2026-09-21
    Trả về thực đơn tuần của user.
    """
    user_id = get_jwt_identity()
    week_start_str = request.args.get("week_start", "")

    try:
        week_start = date.fromisoformat(week_start_str) if week_start_str else date.today()
    except ValueError:
        return error_response("week_start không hợp lệ, dùng định dạng YYYY-MM-DD", 400)

    plans = (
        MealPlan.query
        .filter_by(user_id=user_id, week_start=week_start)
        .order_by(MealPlan.day_of_week, MealPlan.meal_type)
        .all()
    )

    # Nhóm theo ngày cho Antigravity dễ render
    plan_by_day = {}
    for plan in plans:
        day = plan.day_of_week
        if day not in plan_by_day:
            plan_by_day[day] = []
        plan_by_day[day].append(plan.to_dict())

    return success_response(data={
        "week_start": week_start.isoformat(),
        "days": plan_by_day,
    })


@meal_plans_bp.route("/meal-plans", methods=["POST"])
@jwt_required_custom
def add_to_meal_plan():
    """
    POST /api/meal-plans
    Body: { "week_start": "2026-09-21", "day_of_week": 1, "meal_type": "lunch", "recipe_id": 15 }
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    week_start_str = data.get("week_start", "")
    day_of_week = data.get("day_of_week")
    meal_type = data.get("meal_type", "")
    recipe_id = data.get("recipe_id")

    # Validation
    try:
        week_start = date.fromisoformat(week_start_str)
    except (ValueError, TypeError):
        return error_response("week_start không hợp lệ (YYYY-MM-DD)", 400)

    if day_of_week is None or not isinstance(day_of_week, int) or day_of_week < 0 or day_of_week > 6:
        return error_response("day_of_week phải là số từ 0 đến 6", 400)

    if meal_type not in VALID_MEAL_TYPES:
        return error_response(f"meal_type phải là {VALID_MEAL_TYPES}", 400)

    if not recipe_id:
        return error_response("recipe_id là bắt buộc", 400)

    recipe = Recipe.query.get(recipe_id)
    if not recipe or not recipe.is_published:
        return error_response("Công thức không tồn tại", 404)

    plan = MealPlan(
        user_id=user_id,
        week_start=week_start,
        day_of_week=day_of_week,
        meal_type=meal_type,
        recipe_id=recipe_id,
    )
    db.session.add(plan)
    db.session.commit()

    return success_response(data=plan.to_dict(), message="Đã thêm vào thực đơn", status_code=201)


@meal_plans_bp.route("/meal-plans/<int:plan_id>", methods=["DELETE"])
@jwt_required_custom
def remove_from_meal_plan(plan_id):
    """DELETE /api/meal-plans/:id"""
    user_id = get_jwt_identity()
    plan = MealPlan.query.filter_by(id=plan_id, user_id=user_id).first()
    if not plan:
        return error_response("Không tìm thấy mục thực đơn này", 404)

    db.session.delete(plan)
    db.session.commit()
    return success_response(message="Đã xóa khỏi thực đơn")


@meal_plans_bp.route("/meal-plans/shopping-list", methods=["GET"])
@jwt_required_custom
def get_shopping_list():
    """
    GET /api/meal-plans/shopping-list?week_start=2026-09-21
    Tổng hợp nguyên liệu cần mua trong tuần.
    """
    user_id = get_jwt_identity()
    week_start_str = request.args.get("week_start", "")

    try:
        week_start = date.fromisoformat(week_start_str) if week_start_str else date.today()
    except ValueError:
        return error_response("week_start không hợp lệ", 400)

    # Lấy tất cả recipe_id trong tuần
    plans = MealPlan.query.filter_by(user_id=user_id, week_start=week_start).all()
    recipe_ids = [p.recipe_id for p in plans]

    if not recipe_ids:
        return success_response(data={
            "week_start": week_start.isoformat(),
            "ingredients": [],
        })

    # Aggregate: SUM quantity theo ingredient, nhóm theo (ingredient_id, unit)
    rows = (
        db.session.query(
            RecipeIngredient.ingredient_id,
            RecipeIngredient.unit,
            func.sum(RecipeIngredient.quantity).label("total_quantity"),
        )
        .filter(RecipeIngredient.recipe_id.in_(recipe_ids))
        .filter(RecipeIngredient.is_optional == False)  # noqa
        .group_by(RecipeIngredient.ingredient_id, RecipeIngredient.unit)
        .all()
    )

    # Lấy thông tin ingredient
    shopping_list = []
    for row in rows:
        ing = Ingredient.query.get(row.ingredient_id)
        if ing:
            shopping_list.append({
                "ingredient_id": ing.id,
                "name": ing.name,
                "emoji": ing.emoji,
                "total_quantity": round(row.total_quantity, 2),
                "unit": row.unit,
            })

    # Sort theo tên
    shopping_list.sort(key=lambda x: x["name"])

    return success_response(data={
        "week_start": week_start.isoformat(),
        "ingredients": shopping_list,
    })


# ─── SAVED RECIPES ────────────────────────────────────────────────────────────

@meal_plans_bp.route("/users/me/saved", methods=["GET"])
@jwt_required_custom
def get_saved_recipes():
    """GET /api/users/me/saved"""
    user_id = get_jwt_identity()
    saved = SavedRecipe.query.filter_by(user_id=user_id).order_by(SavedRecipe.saved_at.desc()).all()
    return success_response(data=[s.to_dict() for s in saved])


@meal_plans_bp.route("/users/me/saved", methods=["POST"])
@jwt_required_custom
def save_recipe():
    """POST /api/users/me/saved — Body: { "recipe_id": 15 }"""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    recipe_id = data.get("recipe_id")

    if not recipe_id:
        return error_response("recipe_id là bắt buộc", 400)

    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    existing = SavedRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if existing:
        return error_response("Bạn đã lưu công thức này rồi", 409)

    saved = SavedRecipe(user_id=user_id, recipe_id=recipe_id)
    db.session.add(saved)
    db.session.commit()

    return success_response(data=saved.to_dict(), message="Đã lưu công thức", status_code=201)


@meal_plans_bp.route("/users/me/saved/<int:recipe_id>", methods=["DELETE"])
@jwt_required_custom
def unsave_recipe(recipe_id):
    """DELETE /api/users/me/saved/:recipe_id"""
    user_id = get_jwt_identity()
    saved = SavedRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if not saved:
        return error_response("Không tìm thấy công thức đã lưu", 404)

    db.session.delete(saved)
    db.session.commit()
    return success_response(message="Đã bỏ lưu công thức")
