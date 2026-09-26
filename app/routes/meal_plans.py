"""
app/routes/meal_plans.py
Blueprint: meal_plans_bp
Endpoints:
  GET    /api/meal-plans?week_start=2026-09-21
  POST   /api/meal-plans
  DELETE /api/meal-plans/:id
  GET    /api/meal-plans/shopping-list?week_start=2026-09-21
  GET    /api/users/me/saved
  POST   /api/users/me/saved                    (Body: {recipe_id})
  POST   /api/users/me/saved/:recipe_id         (alias từ Frontend - recipe_id in URL)
  DELETE /api/users/me/saved/:recipe_id
"""
from datetime import date, timedelta
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
    week_start_str = request.args.get("week_start") or request.args.get("start_date") or ""

    try:
        target_date = date.fromisoformat(week_start_str) if week_start_str else date.today()
        # Chuẩn hóa về Thứ 2 đầu tuần (0=Monday) để luôn khớp với week_start khi thêm món
        week_start = target_date - timedelta(days=target_date.weekday())
    except ValueError:
        return error_response("week_start hoặc start_date không hợp lệ, dùng định dạng YYYY-MM-DD", 400)

    plans = (
        MealPlan.query
        .filter_by(user_id=user_id, week_start=week_start)
        .order_by(MealPlan.day_of_week, MealPlan.meal_type)
        .all()
    )

    # Trả về flat array với field `date` để Frontend dùng plans.map(...)
    result = []
    for plan in plans:
        plan_dict = plan.to_dict()
        # Tính trường `date` từ week_start + day_of_week
        item_date = week_start + timedelta(days=plan.day_of_week)
        plan_dict["date"] = item_date.isoformat()
        result.append(plan_dict)

    return success_response(data=result)


@meal_plans_bp.route("/meal-plans", methods=["POST"])
@jwt_required_custom
def add_to_meal_plan():
    """
    POST /api/meal-plans
    Body hỗ trợ 2 format:
      1. Frontend format: { "date": "2026-09-24", "meal_type": "lunch", "recipe_id": 15, "servings": 2 }
      2. Backend native:  { "week_start": "2026-09-21", "day_of_week": 3, "meal_type": "lunch", "recipe_id": 15 }
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    meal_type = data.get("meal_type", "")
    recipe_id = data.get("recipe_id")
    servings = data.get("servings")

    # Xác định week_start và day_of_week từ 'date' hoặc 'week_start'+'day_of_week'
    if "date" in data:
        # Frontend gửi date trực tiếp → tính week_start (Monday) và day_of_week
        try:
            item_date = date.fromisoformat(str(data["date"]))
        except (ValueError, TypeError):
            return error_response("date không hợp lệ (YYYY-MM-DD)", 400)
        # week_start = Monday của tuần đó (weekday() 0=Mon, 6=Sun)
        week_start = item_date - timedelta(days=item_date.weekday())
        day_of_week = item_date.weekday()  # 0=Mon, 6=Sun
    else:
        # Backend native format
        week_start_str = data.get("week_start", "")
        day_of_week = data.get("day_of_week")

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

    plan_dict = plan.to_dict()
    # Tính trường `date` để Frontend dùng
    item_date = week_start + timedelta(days=day_of_week)
    plan_dict["date"] = item_date.isoformat()

    return success_response(data=plan_dict, message="Đã thêm vào thực đơn", status_code=201)


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
    week_start_str = request.args.get("week_start") or request.args.get("start_date") or ""

    try:
        target_date = date.fromisoformat(week_start_str) if week_start_str else date.today()
        week_start = target_date - timedelta(days=target_date.weekday())
    except ValueError:
        return error_response("week_start hoặc start_date không hợp lệ, dùng định dạng YYYY-MM-DD", 400)

    # Lấy tất cả recipe_id trong tuần
    plans = MealPlan.query.filter_by(user_id=user_id, week_start=week_start).all()
    recipe_ids = [p.recipe_id for p in plans]

    if not recipe_ids:
        return success_response(data=[])

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

    # Sort theo tên và trả về flat array (Frontend gọi shoppingList.map(...))
    shopping_list.sort(key=lambda x: x["name"])
    return success_response(data=shopping_list)


# ─── SAVED RECIPES ────────────────────────────────────────────────────────────

@meal_plans_bp.route("/users/me/saved", methods=["GET"])
@jwt_required_custom
def get_saved_recipes():
    """
    GET /api/users/me/saved
    Trả về danh sách Recipe objects (flat) với is_saved=True.
    SavedRecipesPage.tsx dùng res.data.map((r) => ({...r, is_saved: true}))
    và truyền thẳng vào <RecipeCard recipe={r} />, nên cần trả về Recipe shape.
    """
    user_id = get_jwt_identity()
    saved = SavedRecipe.query.filter_by(user_id=user_id).order_by(SavedRecipe.saved_at.desc()).all()

    result = []
    for s in saved:
        if s.recipe:
            recipe_dict = s.recipe.to_dict_list()
            recipe_dict["is_saved"] = True
            recipe_dict["saved_at"] = s.saved_at.isoformat() if s.saved_at else None
            result.append(recipe_dict)

    return success_response(data=result)


@meal_plans_bp.route("/users/me/saved", methods=["POST"])
@jwt_required_custom
def save_recipe():
    """POST /api/users/me/saved — Body: { "recipe_id": 15 }"""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    recipe_id = data.get("recipe_id")
    return _do_save_recipe(user_id, recipe_id)


@meal_plans_bp.route("/users/me/saved/<int:recipe_id>", methods=["POST"])
@jwt_required_custom
def save_recipe_by_id(recipe_id):
    """
    POST /api/users/me/saved/:recipe_id  ← alias được Frontend gọi
    recipe_id lấy từ URL path.
    """
    user_id = get_jwt_identity()
    return _do_save_recipe(user_id, recipe_id)


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


# ─── SHARED LOGIC ─────────────────────────────────────────────────────────────

def _do_save_recipe(user_id: str, recipe_id):
    """Xử lý logic lưu recipe — dùng chung cho cả 2 route."""
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
