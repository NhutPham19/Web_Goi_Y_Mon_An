"""
scripts/seed_ingredients.py
Seed 100 nguyên liệu, 15 tags, và các cặp nguyên liệu thay thế vào Database.
Cách chạy:
    python scripts/seed_ingredients.py
"""
import sys
import os

# Thêm root vào sys.path để import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.ingredient import Ingredient, IngredientSubstitute
from app.models.recipe import Tag
from scripts.data.ingredients_data import INGREDIENTS, TAGS, SUBSTITUTES


def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Bắt đầu seed Tags...")
        tag_count = 0
        for name, color in TAGS:
            existing = Tag.query.filter_by(name=name).first()
            if not existing:
                db.session.add(Tag(name=name, color=color))
                tag_count += 1
        db.session.commit()
        print(f"✅ Đã thêm mới {tag_count} tags (Tổng: {Tag.query.count()})")

        print("🌱 Bắt đầu seed Nguyên liệu...")
        ing_count = 0
        for name, category, unit, emoji, calories in INGREDIENTS:
            existing = Ingredient.query.filter_by(name=name).first()
            if not existing:
                db.session.add(Ingredient(
                    name=name,
                    category=category,
                    unit=unit,
                    emoji=emoji,
                    calories_per_100g=calories,
                ))
                ing_count += 1
        db.session.commit()
        print(f"✅ Đã thêm mới {ing_count} nguyên liệu (Tổng: {Ingredient.query.count()})")

        print("🌱 Bắt đầu seed Nguyên liệu thay thế (Substitutes)...")
        sub_count = 0
        for ing_name, sub_name, note in SUBSTITUTES:
            orig = Ingredient.query.filter_by(name=ing_name).first()
            sub = Ingredient.query.filter_by(name=sub_name).first()
            if orig and sub:
                existing = IngredientSubstitute.query.filter_by(
                    ingredient_id=orig.id, substitute_id=sub.id
                ).first()
                if not existing:
                    db.session.add(IngredientSubstitute(
                        ingredient_id=orig.id,
                        substitute_id=sub.id,
                        note=note,
                    ))
                    sub_count += 1
        db.session.commit()
        print(f"✅ Đã thêm mới {sub_count} cặp thay thế (Tổng: {IngredientSubstitute.query.count()})")
        print("🎉 Hoàn tất seed dữ liệu nguyên liệu & tags!")


if __name__ == "__main__":
    seed()
