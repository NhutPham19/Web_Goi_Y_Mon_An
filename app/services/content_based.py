"""
app/services/content_based.py
Content-Based Filtering: gợi ý món ăn dựa trên sở thích user.
Dùng one-hot encoding cho Tags, Difficulty, Cook time + Cosine Similarity.
"""
from datetime import datetime, timezone, timedelta
import numpy as np


def compute_recommendations(user_id: str, top_n: int = 10) -> list:
    """
    Điểm vào chính — được gọi từ route /api/recommendations.

    Logic:
    1. Check cache còn fresh không (< 1 giờ)
    2. Stale → chạy CBF (hoặc hybrid) → lưu cache
    3. Trả về danh sách recipe dict từ cache
    """
    from flask import current_app
    from app import db
    from app.models.meal_plan import RecommendationCache
    from app.models.recipe import Recipe
    from app.models.user import UserPreference

    cache_ttl = current_app.config.get("RECOMMENDATION_CACHE_TTL", 3600)
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=cache_ttl)

    # Kiểm tra cache
    cached = (
        db.session.query(RecommendationCache)
        .filter(
            RecommendationCache.user_id == user_id,
            RecommendationCache.generated_at >= cutoff,
        )
        .order_by(RecommendationCache.score.desc())
        .limit(top_n)
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

    # Cache stale → tính toán lại
    prefs = UserPreference.query.filter_by(user_id=user_id).all()

    if not prefs:
        # Cold start: trả về popular
        return _popular_recipes(top_n)

    recipe_ids_with_scores = _run_cbf(user_id, prefs, top_n)
    _save_cache(user_id, recipe_ids_with_scores, algorithm="cbf")

    recipes = Recipe.query.filter(
        Recipe.id.in_([rid for rid, _ in recipe_ids_with_scores])
    ).all()
    recipe_map = {r.id: r for r in recipes}

    return [
        recipe_map[rid].to_dict_list()
        for rid, _ in recipe_ids_with_scores
        if rid in recipe_map
    ]


def _run_cbf(user_id: str, prefs: list, top_n: int) -> list:
    """
    Chạy Content-Based Filtering.

    Returns:
        List of (recipe_id, score) sorted by score DESC
    """
    from sklearn.metrics.pairwise import cosine_similarity
    from app.models.recipe import Recipe, Tag
    from app import db

    # Lấy tất cả tags để build feature space
    all_tags = Tag.query.order_by(Tag.id).all()
    tag_name_to_idx = {t.name: i for i, t in enumerate(all_tags)}
    tag_name_lower_to_idx = {t.name.lower(): i for i, t in enumerate(all_tags)}
    difficulties = {"easy": 0, "medium": 1, "hard": 2}
    regions_order = ["mien_bac", "mien_trung", "mien_nam", "quoc_te"]

    # Feature dimension: len(tags) + 3 (difficulty) + 4 (region) + 1 (cook_time normalized)
    feature_dim = len(all_tags) + 3 + 4 + 1

    # Build recipe feature matrix
    recipes = Recipe.query.filter_by(is_published=True).all()
    if not recipes:
        return []

    recipe_features = []
    recipe_ids = []

    for recipe in recipes:
        vec = np.zeros(feature_dim)

        # Tag one-hot
        for tag in recipe.tags:
            if tag.name in tag_name_to_idx:
                vec[tag_name_to_idx[tag.name]] = 1.0

        # Difficulty one-hot (offset: len(all_tags))
        diff_idx = len(all_tags) + difficulties.get(recipe.difficulty, 1)
        vec[diff_idx] = 1.0

        # Region one-hot (offset: len(all_tags) + 3)
        if recipe.region and recipe.region in regions_order:
            region_idx = len(all_tags) + 3 + regions_order.index(recipe.region)
            vec[region_idx] = 1.0

        # Cook time normalized (0-1, max=180 phút)
        vec[-1] = min(recipe.cook_time_min, 180) / 180.0

        recipe_features.append(vec)
        recipe_ids.append(recipe.id)

    if not recipe_features:
        return []

    recipe_matrix = np.array(recipe_features)

    # --- Build user preference vector ---
    user_vec = np.zeros(feature_dim)

    # Mapping taste preference sang tag name
    taste_to_tag = {
        "spicy": "cay",
        "mild": "thanh đạm",
        "sweet": "ngọt",
        "salty": "mặn",
        "sour": "chua",
        "vegetarian": "chay",
        "healthy": "healthy",
    }

    # Mapping diet preference sang tag name
    diet_to_tag = {
        "vegetarian": "chay",
        "vegan": "chay",
        "quick": "nhanh",
        "fast": "nhanh",
        "healthy": "healthy",
        "low_fat": "ít dầu",
        "ít dầu": "ít dầu",
    }

    for pref in prefs:
        pref_type = pref.pref_type
        pref_value = pref.pref_value

        if pref_type == "taste":
            tag_name = taste_to_tag.get(pref_value, pref_value)
            # Tìm trong tag_name_to_idx (case-sensitive) rồi fallback lowercase
            if tag_name in tag_name_to_idx:
                user_vec[tag_name_to_idx[tag_name]] = 1.5  # boost
            elif tag_name.lower() in tag_name_lower_to_idx:
                user_vec[tag_name_lower_to_idx[tag_name.lower()]] = 1.5

        elif pref_type == "diet":
            tag_name = diet_to_tag.get(pref_value, pref_value)
            if tag_name in tag_name_to_idx:
                user_vec[tag_name_to_idx[tag_name]] = 1.5
            elif tag_name.lower() in tag_name_lower_to_idx:
                user_vec[tag_name_lower_to_idx[tag_name.lower()]] = 1.5

        elif pref_type == "region":
            # Boost chiều vùng miền tương ứng
            region_map = {
                "mien_bac": "mien_bac",
                "mien_trung": "mien_trung",
                "mien_nam": "mien_nam",
                "quoc_te": "quoc_te",
                # Miền Bắc/Nam/Trung tag trong bảng tags
                "Miền Bắc": "mien_bac",
                "Miền Trung": "mien_trung",
                "Miền Nam": "mien_nam",
            }
            region_key = region_map.get(pref_value, pref_value)
            if region_key in regions_order:
                region_offset = len(all_tags) + 3 + regions_order.index(region_key)
                user_vec[region_offset] = 2.0  # boost mạnh hơn
            # Đồng thời boost tag vùng miền nếu có
            tag_name_map = {
                "mien_bac": "Miền Bắc",
                "mien_trung": "Miền Trung",
                "mien_nam": "Miền Nam",
            }
            tag_name = tag_name_map.get(pref_value, pref_value)
            if tag_name in tag_name_to_idx:
                user_vec[tag_name_to_idx[tag_name]] = 2.0

        elif pref_type == "serving_size":
            try:
                serving_size = int(pref_value)
                # Nếu serving nhỏ (<= 2), ưu tiên món nhanh
                if serving_size <= 2:
                    for tag_key in ["nhanh", "dưới 30 phút"]:
                        if tag_key in tag_name_to_idx:
                            user_vec[tag_name_to_idx[tag_key]] = 1.0
            except ValueError:
                pass

    if user_vec.sum() == 0:
        return _popular_recipe_ids(top_n)

    # Cosine similarity
    user_vec_2d = user_vec.reshape(1, -1)
    similarities = cosine_similarity(user_vec_2d, recipe_matrix)[0]

    # Lấy index có similarity cao nhất
    top_indices = np.argsort(similarities)[::-1][:top_n]

    return [
        (recipe_ids[i], float(similarities[i]))
        for i in top_indices
        if similarities[i] > 0
    ]


def _save_cache(user_id: str, recipe_scores: list, algorithm: str = "cbf"):
    """Lưu kết quả gợi ý vào bảng recommendation_cache."""
    from app import db
    from app.models.meal_plan import RecommendationCache

    # Xóa cache cũ của user (chỉ xóa cùng algorithm)
    RecommendationCache.query.filter_by(user_id=user_id, algorithm=algorithm).delete()

    for recipe_id, score in recipe_scores:
        cache_entry = RecommendationCache(
            user_id=user_id,
            recipe_id=int(recipe_id),
            score=float(score),
            algorithm=algorithm,
        )
        db.session.add(cache_entry)

    db.session.commit()


def _popular_recipes(top_n: int) -> list:
    """Fallback: trả về danh sách món ăn phổ biến nhất."""
    from app.models.recipe import Recipe
    recipes = (
        Recipe.query
        .filter(Recipe.is_published == True)  # noqa
        .order_by(Recipe.avg_rating.desc(), Recipe.rating_count.desc())
        .limit(top_n)
        .all()
    )
    return [r.to_dict_list() for r in recipes]


def _popular_recipe_ids(top_n: int) -> list:
    """Trả về (recipe_id, score) của món phổ biến."""
    from app.models.recipe import Recipe
    recipes = (
        Recipe.query
        .filter(Recipe.is_published == True)  # noqa
        .order_by(Recipe.avg_rating.desc())
        .limit(top_n)
        .all()
    )
    return [(r.id, r.avg_rating / 5.0) for r in recipes]
