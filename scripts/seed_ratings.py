"""
scripts/seed_ratings.py
Tạo synthetic ratings (đánh giá giả lập) để phục vụ demo Collaborative Filtering.

Logic sinh ratings hợp lý:
  - Nhóm user "thích cay" → rate cao món có tag "cay"
  - Nhóm user "ăn chay" → rate cao món có tag "chay"
  - Nhóm user "miền Nam" → rate cao món Miền Nam
  - Nhóm user "healthy" → rate cao món healthy / ít dầu
  - Random noise nhẹ để dữ liệu không quá lý tưởng

Cách chạy:
    python scripts/seed_ratings.py

Điều kiện:
  - Phải có ít nhất 10 users và 10 recipes trong DB.
  - Cần thêm user test qua API /api/auth/register trước khi chạy.
"""
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.rating import Rating
from sqlalchemy import func

# Profile: mỗi profile định nghĩa 1 loại user và tag ưa thích
USER_PROFILES = [
    {"name": "Thích cay", "boost_tags": {"cay"}, "avoid_tags": {"chay"}, "base_score": 4},
    {"name": "Ăn chay", "boost_tags": {"chay", "healthy", "ít dầu"}, "avoid_tags": set(), "base_score": 4},
    {"name": "Yêu miền Nam", "boost_tags": {"Miền Nam"}, "avoid_tags": set(), "base_score": 4},
    {"name": "Yêu miền Bắc", "boost_tags": {"Miền Bắc"}, "avoid_tags": set(), "base_score": 4},
    {"name": "Yêu miền Trung", "boost_tags": {"Miền Trung"}, "avoid_tags": set(), "base_score": 4},
    {"name": "Ăn healthy", "boost_tags": {"healthy", "ít dầu", "chay"}, "avoid_tags": {"tiệc"}, "base_score": 4},
    {"name": "Ăn tiệc", "boost_tags": {"tiệc", "Miền Nam"}, "avoid_tags": {"ít dầu"}, "base_score": 4},
    {"name": "Bận rộn / nhanh", "boost_tags": {"nhanh", "dưới 30 phút", "dễ nấu"}, "avoid_tags": set(), "base_score": 4},
    {"name": "Bình dân", "boost_tags": set(), "avoid_tags": set(), "base_score": 3},
    {"name": "Sành ăn", "boost_tags": {"tiệc", "cay"}, "avoid_tags": set(), "base_score": 5},
]

TARGET_RATINGS = 500  # Mục tiêu tổng số ratings cần có trong DB


def _calc_score(recipe, profile: dict) -> int:
    """Tính điểm đánh giá dựa trên profile + random noise."""
    recipe_tag_names = {t.name for t in recipe.tags}
    base = profile["base_score"]

    # Boost nếu recipe có tag ưa thích
    boost = len(recipe_tag_names & profile["boost_tags"])
    if boost > 0:
        base = min(5, base + boost)

    # Penalty nếu có tag tránh
    penalty = len(recipe_tag_names & profile["avoid_tags"])
    if penalty > 0:
        base = max(1, base - penalty)

    # Random noise ±1
    noise = random.choice([-1, -1, 0, 0, 0, 1, 1])
    score = max(1, min(5, base + noise))
    return score


def seed():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        recipes = Recipe.query.filter_by(is_published=True).all()

        if len(users) < 2:
            print("⚠️  Cần ít nhất 2 users trong DB.")
            print("   Tạo users qua: POST /api/auth/register")
            return

        if len(recipes) < 10:
            print("⚠️  Cần ít nhất 10 recipes. Hãy chạy seed_recipes.py trước.")
            return

        existing_count = Rating.query.count()
        print(f"📊 Hiện có {existing_count} ratings trong DB.")

        if existing_count >= TARGET_RATINGS:
            print(f"✅ Đã đủ {TARGET_RATINGS}+ ratings. Không cần thêm.")
            return

        need = TARGET_RATINGS - existing_count
        created = 0
        skipped = 0

        print(f"🌱 Cần tạo thêm ~{need} ratings synthetic...")

        # Gán mỗi user 1 profile ngẫu nhiên
        user_profile_map = {}
        for user in users:
            user_profile_map[user.id] = random.choice(USER_PROFILES)

        # Mỗi user rate ~60-80% số recipes
        random.shuffle(recipes)
        for user in users:
            profile = user_profile_map[user.id]

            # Lấy recipes user chưa rate
            rated_ids = {r.recipe_id for r in Rating.query.filter_by(user_id=user.id).all()}
            unrated = [r for r in recipes if r.id not in rated_ids]

            # Rate 60-80% trong số đó
            sample_size = int(len(unrated) * random.uniform(0.55, 0.80))
            sampled = random.sample(unrated, min(sample_size, len(unrated)))

            for recipe in sampled:
                if created >= need:
                    break

                score = _calc_score(recipe, profile)
                rating = Rating(
                    user_id=user.id,
                    recipe_id=recipe.id,
                    score=score,
                    review_text=None,
                )
                db.session.add(rating)
                created += 1

            if created >= need:
                break

        db.session.commit()

        # Cập nhật avg_rating trên tất cả recipes
        print("🔄 Cập nhật avg_rating trên tất cả recipes...")
        for recipe in recipes:
            result = db.session.query(
                func.avg(Rating.score).label("avg"),
                func.count(Rating.id).label("cnt"),
            ).filter(Rating.recipe_id == recipe.id).one()
            recipe.avg_rating = round(float(result.avg or 0), 2)
            recipe.rating_count = result.cnt or 0
        db.session.commit()

        total = Rating.query.count()
        print(f"\n{'='*50}")
        print(f"🎉 Hoàn tất seed ratings!")
        print(f"   Đã tạo mới : {created} ratings")
        print(f"   Tổng trong DB  : {total} ratings")
        print(f"   CF có thể train: {'✅ Sẵn sàng' if total >= 200 else f'⏳ Cần thêm {200 - total} ratings'}")
        print(f"{'='*50}")


if __name__ == "__main__":
    seed()
