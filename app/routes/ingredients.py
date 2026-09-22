"""
app/routes/ingredients.py
Blueprint: ingredients_bp
Endpoints:
  GET  /api/ingredients               (public)
  GET  /api/ingredients/:id           (public)
  GET  /api/ingredients/:id/substitutes (public)
  GET  /api/tags                      (public)
  GET  /api/ingredients/tags          (public) — alias từ Frontend
  POST /api/admin/ingredients         → trong admin.py
  POST /api/admin/tags                → trong admin.py
"""
from flask import Blueprint, request
from app.models.ingredient import Ingredient, IngredientSubstitute
from app.models.recipe import Tag
from app.utils.response import success_response, error_response, paginated_response

ingredients_bp = Blueprint("ingredients", __name__)

VALID_CATEGORIES = [
    "rau_cu", "thit", "hai_san", "gia_vi", "bot_duong",
    "nuoc_sot", "trai_cay", "sua_trung", "hat", "do_kho", "khac",
]


# ─── INGREDIENTS ─────────────────────────────────────────────────────────────

@ingredients_bp.route("/ingredients", methods=["GET"])
def list_ingredients():
    """
    GET /api/ingredients
    Query: ?category=rau_cu&q=cà&page=1&limit=50
    """
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(100, max(1, int(request.args.get("limit", 100))))
    except ValueError:
        page, limit = 1, 100

    query = Ingredient.query.order_by(Ingredient.name)

    if category and category in VALID_CATEGORIES:
        query = query.filter(Ingredient.category == category)

    if q:
        query = query.filter(Ingredient.name.ilike(f"%{q}%"))

    total = query.count()
    ingredients = query.offset((page - 1) * limit).limit(limit).all()

    return paginated_response(
        data=[ing.to_dict() for ing in ingredients],
        total=total,
        page=page,
        limit=limit,
    )


@ingredients_bp.route("/ingredients/<int:ingredient_id>", methods=["GET"])
def get_ingredient(ingredient_id):
    """GET /api/ingredients/:id"""
    ingredient = Ingredient.query.get(ingredient_id)
    if not ingredient:
        return error_response("Nguyên liệu không tồn tại", 404)
    return success_response(data=ingredient.to_dict())


@ingredients_bp.route("/ingredients/<int:ingredient_id>/substitutes", methods=["GET"])
def get_substitutes(ingredient_id):
    """
    GET /api/ingredients/:id/substitutes
    Trả về danh sách nguyên liệu thay thế.
    """
    ingredient = Ingredient.query.get(ingredient_id)
    if not ingredient:
        return error_response("Nguyên liệu không tồn tại", 404)

    substitutes = IngredientSubstitute.query.filter_by(
        ingredient_id=ingredient_id
    ).all()

    # Trả về mảng substitutes trực tiếp (SubstituteModal.tsx dùng setSubstitutes(res.data))
    # ingredient info được đặt trong message để debug nếu cần
    return success_response(
        data=[s.to_dict() for s in substitutes],
        message=f"Nguyên liệu thay thế cho: {ingredient.name}",
    )


# ─── TAGS ────────────────────────────────────────────────────────────────────

@ingredients_bp.route("/tags", methods=["GET"])
def list_tags():
    """GET /api/tags — Trả về tất cả tags."""
    tags = Tag.query.order_by(Tag.name).all()
    return success_response(data=[t.to_dict() for t in tags])


@ingredients_bp.route("/ingredients/tags", methods=["GET"])
def list_tags_alias():
    """GET /api/ingredients/tags — Alias để Frontend có thể gọi."""
    return list_tags()
