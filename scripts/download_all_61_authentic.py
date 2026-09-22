"""
scripts/download_all_61_authentic.py
Tải 61 ảnh món ăn Việt Nam chuẩn xác 100% về frontend/public/recipes/{id}.jpg
Đảm bảo độ phân giải cao (HD), mô tả đúng thực tế từng món ẩm thực truyền thống Việt Nam.
"""
import os
import sys
import json
import urllib.request
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.recipe import Recipe

TARGET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "recipes"))

# Tải bản đồ 61 món
MAP_FILE = os.path.join(os.path.dirname(__file__), "all_61_map.json")
with open(MAP_FILE, "r", encoding="utf-8") as f:
    recipe_map = json.load(f)

# Tinh chỉnh đặc thù cho các món để đảm bảo ảnh đẹp & độc lập nhất
recipe_map["43"] = "https://i.ytimg.com/vi/dyfYLlIuhmg/hqdefault.jpg"  # Bánh mì Phượng Hội An
recipe_map["61"] = "https://i.ytimg.com/vi/RC0MSWeDL0A/hqdefault.jpg"  # Bún thịt nướng kiểu Huế
recipe_map["58"] = "https://i.ytimg.com/vi/3eY5Rdv7j2w/hqdefault.jpg"  # Cháo cá lóc rau ngổ
recipe_map["57"] = "https://tiki.vn/blog/wp-content/uploads/2023/10/U3RVg0Zy2vjdTkm_dEr9C73K-U80JBuWIxgXP18dXnKhfXb3oj8k3tQFsnsr9ZIPigPlT4UN39xDeL0tUlmNxw3TQNfSHdGnK-pL6VyeZB5FWcsYfzloWWGDnHaE1nvAKNSKNLTqTCFJg-9iLxyQhiY.jpg" # Mực xào sa tế
recipe_map["56"] = "https://i.ytimg.com/vi/r1nHxOdGXRU/hqdefault.jpg"  # Cá diêu hồng hấp gừng
recipe_map["54"] = "https://i.ytimg.com/vi/APs76-va_Dw/hqdefault.jpg"  # Sườn xào chua ngọt
recipe_map["50"] = "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/07/X%C3%B4i_g%E1%BA%A5c.JPG/960px-X%C3%B4i_g%E1%BA%A5c.JPG" # Xôi gấc
recipe_map["19"] = "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8b/B%C3%BAn_ch%E1%BA%A3_Th%E1%BB%A5y_Khu%C3%AA.jpg/960px-B%C3%BAn_ch%E1%BA%A3_Th%E1%BB%A5y_Khu%C3%AA.jpg" # Bún chả

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_image(url):
    # Nếu là YouTube hqdefault, thử maxresdefault trước
    if "i.ytimg.com/vi/" in url and "hqdefault.jpg" in url:
        max_url = url.replace("hqdefault.jpg", "maxresdefault.jpg")
        try:
            req = urllib.request.Request(max_url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = resp.read()
                if len(data) > 5000: # Valid image
                    return data
        except Exception:
            pass # fallback to hqdefault

    # Tải URL gốc
    clean_url = url.split("?utm_")[0]
    req = urllib.request.Request(clean_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()

def run():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"📁 Thư mục lưu ảnh: {TARGET_DIR}")

    app = create_app()
    with app.app_context():
        recipes = Recipe.query.order_by(Recipe.id).all()
        total = len(recipes)
        success = 0
        failed = 0

        print(f"🚀 Bắt đầu tải và cập nhật {total} ảnh chuẩn xác 100%...")

        for r in recipes:
            str_id = str(r.id)
            img_url = recipe_map.get(str_id)
            if not img_url:
                print(f"[{r.id:02d}/{total}] ⚠️ Không có URL cho: {r.name}")
                failed += 1
                continue

            file_path = os.path.join(TARGET_DIR, f"{r.id}.jpg")

            try:
                data = download_image(img_url)
                with open(file_path, "wb") as f:
                    f.write(data)
                size_kb = len(data) / 1024
                # Cập nhật đường dẫn chuẩn vào database
                r.image_url = f"/recipes/{r.id}.jpg"
                success += 1
                print(f"[{r.id:02d}/{total}] ✅ {r.name} -> {r.id}.jpg ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"[{r.id:02d}/{total}] ❌ Lỗi {r.name}: {e}")
                failed += 1
            
            time.sleep(0.1)

        db.session.commit()
        print(f"\n🎉 HOÀN THÀNH: Đã lưu thành công {success}/{total} ảnh chuẩn vào thư mục frontend/public/recipes/ và cập nhật Supabase Database!")

if __name__ == "__main__":
    run()
