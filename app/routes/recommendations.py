"""
app/routes/recommendations.py
Blueprint: recommendations_bp
Endpoint:
  GET /api/recommendations?limit=10   (cần token)

Logic:
  - Nếu DB có >= 200 ratings → Hybrid CBF (60%) + CF (40%)
  - Nếu < 200 ratings → CBF thuần
  - User mới (không có preferences) → Popular recipes (cold-start fallback)
"""
from flask import Blueprint, request, current_app
from flask_jwt_extended import get_jwt_identity

from app import db
from app.models.rating import Rating
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required_custom

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/recommendations", methods=["GET"])
@jwt_required_custom
def get_recommendations():
    """
    GET /api/recommendations?limit=10&force_refresh=false
    Query params:
      limit: số lượng gợi ý (mặc định 10, tối đa 20)
      force_refresh: "true" để bỏ qua cache và tính lại ngay
    """
    user_id = get_jwt_identity()

    try:
        limit = min(20, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        limit = 10

    force_refresh = request.args.get("force_refresh", "false").lower() == "true"

    try:
        cf_min = current_app.config.get("CF_MIN_RATINGS", 200)
        total_ratings = Rating.query.count()
        use_cf = total_ratings >= cf_min

        if use_cf:
            recipes = _hybrid_recommendations(user_id, limit, force_refresh)
            algo = "hybrid_cbf_cf"
        else:
            from app.services.content_based import compute_recommendations
            if force_refresh:
                # Xóa cache cũ trước khi tính lại
                _clear_user_cache(user_id)
            recipes = compute_recommendations(user_id, top_n=limit)
            algo = "cbf"

        return success_response(
            data=recipes,
            message=f"Gợi ý theo thuật toán: {algo} ({total_ratings} ratings)"
        )

    except Exception as e:
        current_app.logger.error(f"[Recommendations] Error for user {user_id}: {e}")
        return _fallback_popular(limit)


def _hybrid_recommendations(user_id: str, limit: int, force_refresh: bool = False) -> list:
    """
    Kết hợp CBF (60%) và Collaborative Filtering (40%).
    Trả về top `limit` công thức không trùng lặp.
    """
    from app.services.content_based import compute_recommendations, _run_cbf, _save_cache
    from app.services.collaborative import compute_cf_recommendations
    from app.models.recipe import Recipe
    from app.models.user import UserPreference
    from app.models.meal_plan import RecommendationCache
    from datetime import datetime, timezone, timedelta

    # Check cache hybrid
    if not force_refresh:
        cache_ttl = current_app.config.get("RECOMMENDATION_CACHE_TTL", 3600)
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=cache_ttl)
        cached = (
            db.session.query(RecommendationCache)
            .filter(
                RecommendationCache.user_id == user_id,
                RecommendationCache.algorithm == "hybrid",
                RecommendationCache.generated_at >= cutoff,
            )
            .order_by(RecommendationCache.score.desc())
            .limit(limit)
            .all()
        )
        if cached:
            recipe_ids = [c.recipe_id for c in cached]
            recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
            recipe_map = {r.id: r for r in recipes}
            return [
                recipe_map[c.recipe_id].to_dict_list()
                for c in cached
                if c.recipe_id in recipe_map
            ]

    # Tính CBF scores
    prefs = UserPreference.query.filter_by(user_id=user_id).all()
    cbf_results = {}
    if prefs:
        cbf_raw = _run_cbf(user_id, prefs, top_n=limit * 2)
        for recipe_id, score in cbf_raw:
            cbf_results[recipe_id] = score

    # Tính CF scores
    cf_results = {}
    cf_raw = compute_cf_recommendations(user_id, top_n=limit * 2)
    for recipe_id, score in cf_raw:
        # Normalize CF score: predict CF từ scale 1-5 → normalize về 0-1
        cf_results[recipe_id] = (score - 1) / 4.0

    # Merge: hybrid = 0.6*CBF + 0.4*CF
    all_ids = set(cbf_results.keys()) | set(cf_results.keys())
    hybrid_scores = {}
    for rid in all_ids:
        cbf_s = cbf_results.get(rid, 0.0)
        cf_s = cf_results.get(rid, 0.0)
        hybrid_scores[rid] = 0.6 * cbf_s + 0.4 * cf_s

    if not hybrid_scores:
        return _fallback_popular_list(limit)

    # Sort và lấy top N
    top_ids = sorted(hybrid_scores, key=lambda x: hybrid_scores[x], reverse=True)[:limit]

    # Lưu cache hybrid
    _clear_user_cache(user_id, algorithm="hybrid")
    from app.models.meal_plan import RecommendationCache
    for rid in top_ids:
        db.session.add(RecommendationCache(
            user_id=user_id,
            recipe_id=rid,
            score=hybrid_scores[rid],
            algorithm="hybrid",
        ))
    db.session.commit()

    # Lấy recipe objects
    recipes = Recipe.query.filter(Recipe.id.in_(top_ids)).all()
    recipe_map = {r.id: r for r in recipes}
    return [
        recipe_map[rid].to_dict_list()
        for rid in top_ids
        if rid in recipe_map
    ]


def _clear_user_cache(user_id: str, algorithm: str = None):
    """Xóa recommendation cache của user."""
    from app.models.meal_plan import RecommendationCache
    q = RecommendationCache.query.filter_by(user_id=user_id)
    if algorithm:
        q = q.filter_by(algorithm=algorithm)
    q.delete()
    db.session.commit()


def _fallback_popular(limit: int):
    """Response fallback popular khi có lỗi."""
    return success_response(
        data=_fallback_popular_list(limit),
        message="Hiển thị các món ăn phổ biến"
    )


def _fallback_popular_list(limit: int) -> list:
    """Lấy list món ăn phổ biến nhất."""
    from app.models.recipe import Recipe
    recipes = (
        Recipe.query
        .filter(Recipe.is_published == True)  # noqa
        .order_by(Recipe.avg_rating.desc(), Recipe.rating_count.desc())
        .limit(limit)
        .all()
    )
    return [r.to_dict_list() for r in recipes]
