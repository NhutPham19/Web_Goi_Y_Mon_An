"""
scripts/seed_recipes.py
Nạp dữ liệu ~80 công thức món ăn Việt Nam vào Database.

Cách chạy:
    python scripts/seed_recipes.py

Lưu ý:
    - Phải chạy seed_ingredients.py trước để có Tags và Ingredients trong DB.
    - Script chỉ insert món chưa có trong DB (dựa trên tên, tránh duplicate).
    - Sau khi seed xong, tự động publish tất cả các món.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.recipe import Recipe, Tag, Step
from app.models.ingredient import Ingredient, RecipeIngredient
from scripts.data.recipes_data import RECIPES


def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Bắt đầu seed Công thức...")
        created = 0
        skipped = 0
        errors = 0

        # Cache tags và ingredients để tránh query N+1
        tag_map = {t.name: t for t in Tag.query.all()}
        ing_map = {i.name: i for i in Ingredient.query.all()}

        if not tag_map:
            print("⚠️  Chưa có Tags trong DB. Hãy chạy seed_ingredients.py trước!")
            return

        if not ing_map:
            print("⚠️  Chưa có Ingredients trong DB. Hãy chạy seed_ingredients.py trước!")
            return

        for recipe_data in RECIPES:
            name = recipe_data["name"]

            # Bỏ qua nếu đã tồn tại
            if Recipe.query.filter_by(name=name).first():
                skipped += 1
                continue

            try:
                # Tạo recipe object
                recipe = Recipe(
                    name=name,
                    description=recipe_data.get("description", ""),
                    difficulty=recipe_data.get("difficulty", "medium"),
                    cook_time_min=recipe_data.get("cook_time_min", 30),
                    prep_time_min=recipe_data.get("prep_time_min", 15),
                    servings=recipe_data.get("servings", 4),
                    region=recipe_data.get("region"),
                    is_published=recipe_data.get("is_published", True),
                    image_url=None,  # Cập nhật sau khi có ảnh Cloudinary
                )
                db.session.add(recipe)
                db.session.flush()  # Lấy recipe.id ngay

                # Gắn Tags
                for tag_name in recipe_data.get("tags", []):
                    tag = tag_map.get(tag_name)
                    if tag:
                        recipe.tags.append(tag)
                    else:
                        # Tạo tag mới nếu chưa có
                        new_tag = Tag(name=tag_name, color="#607D8B")
                        db.session.add(new_tag)
                        db.session.flush()
                        tag_map[tag_name] = new_tag
                        recipe.tags.append(new_tag)

                # Gắn Ingredients
                for ing_data in recipe_data.get("ingredients", []):
                    ing_name = ing_data["name"]
                    ingredient = ing_map.get(ing_name)
                    if not ingredient:
                        print(f"  ⚠️  Nguyên liệu không tìm thấy: '{ing_name}' (món: {name})")
                        continue

                    ri = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=float(ing_data.get("quantity", 1)),
                        unit=ing_data.get("unit") or ingredient.unit,
                        is_optional=bool(ing_data.get("is_optional", False)),
                    )
                    db.session.add(ri)

                # Thêm Steps
                for step_data in recipe_data.get("steps", []):
                    step = Step(
                        recipe_id=recipe.id,
                        step_number=int(step_data.get("step_number", 1)),
                        description=step_data.get("description", ""),
                        image_url=None,
                        duration_min=step_data.get("duration_min"),
                    )
                    db.session.add(step)

                db.session.commit()
                created += 1
                print(f"  ✅ [{created}] {name}")

            except Exception as e:
                db.session.rollback()
                errors += 1
                print(f"  ❌ Lỗi khi seed '{name}': {e}")

        print(f"\n{'='*50}")
        print(f"🎉 Hoàn tất seed công thức!")
        print(f"   Đã tạo mới : {created} món")
        print(f"   Bỏ qua (đã có): {skipped} món")
        print(f"   Lỗi        : {errors} món")
        print(f"   Tổng trong DB  : {Recipe.query.count()} món")
        print(f"{'='*50}")


if __name__ == "__main__":
    seed()
