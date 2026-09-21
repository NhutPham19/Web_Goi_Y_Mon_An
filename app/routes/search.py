"""
app/routes/search.py
Blueprint: search_bp
Endpoints:
  POST /api/search/by-ingredients
"""
from flask import Blueprint, request
from app.services.ingredient_search import search_by_ingredients
from app.utils.response import success_response, error_response

search_bp = Blueprint("search", __name__)


@search_bp.route("/by-ingredients", methods=["POST"])
def search_recipes_by_ingredients():
    """
    POST /api/search/by-ingredients
    Body: {
        "ingredient_ids": [1, 5, 12, 23],
        "match_mode": "any"   // "any" hoặc "all"
    }
    """
    data = request.get_json(silent=True) or {}

    ingredient_ids = data.get("ingredient_ids", [])
    match_mode = data.get("match_mode", "any")

    if not isinstance(ingredient_ids, list) or len(ingredient_ids) == 0:
        return error_response("ingredient_ids phải là mảng không rỗng", 400)

    if match_mode not in ("any", "all"):
        return error_response("match_mode phải là 'any' hoặc 'all'", 400)

    # Ép kiểu sang int, bỏ qua giá trị không hợp lệ
    try:
        ingredient_ids = [int(i) for i in ingredient_ids]
    except (ValueError, TypeError):
        return error_response("ingredient_ids phải chứa số nguyên", 400)

    results = search_by_ingredients(ingredient_ids, match_mode)

    return success_response(data=results)
