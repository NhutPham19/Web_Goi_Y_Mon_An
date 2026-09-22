"""
scripts/download_authentic_recipes.py
Tự động tải 61 ảnh món ăn chất lượng cao về lưu trữ cục bộ tại frontend/public/recipes/{id}.jpg
Đồng thời cập nhật trường image_url trong Supabase Database thành đường dẫn nội bộ: /recipes/{id}.jpg
"""
import sys
import os
import urllib.request
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.recipe import Recipe
from scripts.update_recipe_images import RECIPE_IMAGES, DEFAULT_IMAGE

TARGET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "recipes"))

def download_and_sync():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"📁 Thư mục lưu ảnh: {TARGET_DIR}")

    app = create_app()
    with app.app_context():
        recipes = Recipe.query.order_by(Recipe.id).all()
        total = len(recipes)
        success_count = 0
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

        print(f"🚀 Bắt đầu tải và đồng bộ {total} món ăn...")

        for r in recipes:
            img_url = RECIPE_IMAGES.get(r.name, r.image_url or DEFAULT_IMAGE)
            file_name = f"{r.id}.jpg"
            file_path = os.path.join(TARGET_DIR, file_name)

            try:
                # Tải ảnh về
                req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as response:
                    content = response.read()
                    with open(file_path, "wb") as f:
                        f.write(content)
                
                size_kb = len(content) / 1024
                # Cập nhật đường dẫn nội bộ trong DB
                r.image_url = f"/recipes/{file_name}"
                success_count += 1
                print(f"[{r.id:02d}/{total}] ✅ {r.name} -> /recipes/{file_name} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"[{r.id:02d}/{total}] ❌ Lỗi {r.name}: {e}")
            
            time.sleep(0.1)

        db.session.commit()
        print(f"\n🎉 HOÀN THÀNH: Đã lưu {success_count}/{total} ảnh nội bộ vào frontend/public/recipes/ và cập nhật Supabase!")

if __name__ == "__main__":
    download_and_sync()
