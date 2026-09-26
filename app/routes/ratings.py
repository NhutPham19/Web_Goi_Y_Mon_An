"""
app/routes/ratings.py
Blueprint: ratings_bp
Endpoints:
  POST /api/ratings                          (cần token) — gốc, vẫn giữ
  GET  /api/recipes/:id/ratings              (public)
  POST /api/recipes/:id/ratings             (cần token) — alias từ Frontend
  POST /api/view-history                     (cần token) — fire and forget
  POST /api/recipes/:id/views               (cần token) — alias từ Frontend
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func

from app import db
from app.models.rating import Rating, ViewHistory
from app.models.recipe import Recipe
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import jwt_required_custom

ratings_bp = Blueprint("ratings", __name__)


@ratings_bp.route("/ratings", methods=["POST"])
@jwt_required_custom
def create_rating():
    """
    POST /api/ratings
    Body: { "recipe_id": 15, "score": 4, "review_text": "Ngon!" }
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    return _do_create_rating(user_id, data)


@ratings_bp.route("/recipes/<int:recipe_id>/ratings", methods=["GET"])
def get_recipe_ratings(recipe_id):
    """
    GET /api/recipes/:id/ratings
    Query: ?page=1&limit=10
    """
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(50, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        page, limit = 1, 10

    query = Rating.query.filter_by(recipe_id=recipe_id).order_by(Rating.created_at.desc())
    total = query.count()
    ratings = query.offset((page - 1) * limit).limit(limit).all()

    return paginated_response(
        data=[r.to_dict() for r in ratings],
        total=total,
        page=page,
        limit=limit,
    )


@ratings_bp.route("/recipes/<int:recipe_id>/ratings", methods=["POST"])
@jwt_required_custom
def create_rating_for_recipe(recipe_id):
    """
    POST /api/recipes/:id/ratings    ← alias được Frontend gọi
    Body: { "score": 4, "review_text": "Ngon!" }
    recipe_id lấy từ URL path thay vì body.
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    # Inject recipe_id từ URL vào data
    data["recipe_id"] = recipe_id
    return _do_create_rating(user_id, data)


@ratings_bp.route("/view-history", methods=["POST"])
def record_view():
    """
    POST /api/view-history
    Body: { "recipe_id": 15, "duration_sec": 120 }
    Fire-and-forget: luôn trả 200, hỗ trợ cả khách vãng lai (optional JWT).
    """
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        user_id = None
    data = request.get_json(silent=True) or {}
    return _do_record_view(user_id, data.get("recipe_id"), data.get("duration_sec"))


@ratings_bp.route("/recipes/<int:recipe_id>/views", methods=["POST"])
def record_view_for_recipe(recipe_id):
    """
    POST /api/recipes/:id/views    ← alias được Frontend gọi
    Body: { "duration_sec": 120 }  (recipe_id lấy từ URL)
    Fire-and-forget: luôn trả 200, hỗ trợ cả khách vãng lai (optional JWT).
    """
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        user_id = None
    data = request.get_json(silent=True) or {}
    return _do_record_view(user_id, recipe_id, data.get("duration_sec"))


# ─── SHARED LOGIC ──────────────────────────────────────────────────────────────

def _do_create_rating(user_id: str, data: dict):
    """Xử lý logic upsert rating — dùng chung cho cả 2 route POST rating."""
    recipe_id = data.get("recipe_id")
    score = data.get("score")
    review_text = str(data.get("review_text", "") or "").strip()

    # Validation
    if not recipe_id:
        return error_response("recipe_id là bắt buộc", 400)

    if score is None:
        return error_response("score là bắt buộc", 400)

    try:
        score = int(score)
    except (TypeError, ValueError):
        return error_response("score phải là số nguyên từ 1 đến 5", 400)

    if score < 1 or score > 5:
        return error_response("score phải là số nguyên từ 1 đến 5", 400)

    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    # Upsert rating (user chỉ rate 1 lần / recipe)
    existing = Rating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    is_new = existing is None

    if existing:
        existing.score = score
        existing.review_text = review_text or existing.review_text
        rating = existing
    else:
        rating = Rating(
            user_id=user_id,
            recipe_id=recipe_id,
            score=score,
            review_text=review_text or None,
        )
        db.session.add(rating)

    db.session.flush()

    # Cập nhật avg_rating và rating_count trên bảng recipes
    _update_recipe_rating_stats(recipe_id)

    db.session.commit()

    return success_response(
        data=rating.to_dict(),
        message="Đánh giá thành công",
        status_code=201 if is_new else 200,
    )


def _do_record_view(user_id: str, recipe_id, duration_sec):
    """Xử lý logic ghi view history — dùng chung cho cả 2 route POST view."""
    if recipe_id and user_id:
        try:
            vh = ViewHistory(
                user_id=user_id,
                recipe_id=int(recipe_id),
                duration_sec=int(duration_sec) if duration_sec else None,
            )
            db.session.add(vh)
            db.session.commit()
        except Exception:
            db.session.rollback()

    return success_response(message="OK")


# ─── HELPER ──────────────────────────────────────────────────────────────────

def _update_recipe_rating_stats(recipe_id: int):
    """
    Tính lại avg_rating và rating_count cho recipe.
    Gọi sau mỗi lần insert/update Rating.
    """
    result = db.session.query(
        func.avg(Rating.score).label("avg"),
        func.count(Rating.id).label("cnt"),
    ).filter(Rating.recipe_id == recipe_id).one()

    recipe = Recipe.query.get(recipe_id)
    if recipe:
        recipe.avg_rating = round(float(result.avg or 0), 2)
        recipe.rating_count = result.cnt or 0
