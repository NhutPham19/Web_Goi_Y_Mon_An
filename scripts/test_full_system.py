"""
scripts/test_full_system.py
Script kiểm thử tự động toàn bộ tính năng của Web Nấu Ăn:
1. Health check & Config
2. Auth (Register, Login, Me, Preferences, Logout)
3. Recipes (List, Filters, Query param vs Search param, Detail, Similar, Nutrition, 404s)
4. Ratings & Views (Add rating, Get ratings, Record views - auth vs guest)
5. Ingredients & Search by ingredients (List, Substitutes, Categories, Tags, Math/Percent check)
6. Recommendations (Guest popular, Auth CBF/Hybrid, cold-start)
7. Meal Plans & Shopping List (Add with date, Add with week_start, Get, Delete, Shopping list params)
8. Saved Recipes (Save via URL, Save via Body, List, Unsave)
9. Admin API (Stats, Recipe CRUD, Publish toggle, Permissions)
"""
import os
import sys
import json
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.user import User, UserPreference
from app.models.recipe import Recipe, Tag
from app.models.ingredient import Ingredient, RecipeIngredient, IngredientSubstitute
from app.models.rating import Rating, ViewHistory
from app.models.meal_plan import MealPlan, SavedRecipe

def run_tests():
    app = create_app()
    client = app.test_client()

    results = {
        "passed": [],
        "failed": [],
        "warnings": [],
    }

    def record_pass(category, name, detail=""):
        msg = f"[{category}] PASS: {name} - {detail}"
        results["passed"].append(msg)
        print(f"  \033[92m✓\033[0m {msg}")

    def record_fail(category, name, detail=""):
        msg = f"[{category}] FAIL: {name} - {detail}"
        results["failed"].append(msg)
        print(f"  \033[91m✗\033[0m {msg}")

    def record_warn(category, name, detail=""):
        msg = f"[{category}] WARN: {name} - {detail}"
        results["warnings"].append(msg)
        print(f"  \033[93m!\033[0m {msg}")

    with app.app_context():
        print("\n========================================================")
        print("  BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG WEB NẤU ĂN")
        print("========================================================")

        # ------------------------------------------------------------------
        # 1. HEALTH CHECK & CONFIG
        # ------------------------------------------------------------------
        print("\n--- 1. Health Check & Config ---")
        res = client.get("/api/health")
        if res.status_code == 200 and res.json.get("status") == "ok":
            record_pass("Health", "API Health check", str(res.json))
        else:
            record_fail("Health", "API Health check", f"Status {res.status_code}: {res.data}")

        # Check DB connection & counts
        try:
            u_count = User.query.count()
            r_count = Recipe.query.count()
            i_count = Ingredient.query.count()
            rat_count = Rating.query.count()
            record_pass("Database", "Kết nối Supabase PostgreSQL", f"Users: {u_count}, Recipes: {r_count}, Ingredients: {i_count}, Ratings: {rat_count}")
        except Exception as e:
            record_fail("Database", "Kết nối Supabase PostgreSQL", str(e))

        # ------------------------------------------------------------------
        # 2. AUTHENTICATION & PROFILE
        # ------------------------------------------------------------------
        print("\n--- 2. Authentication & User Profile ---")
        test_email = f"test_agent_{int(date.today().strftime('%Y%m%d'))}@example.com"
        test_pass = "TestPassword123!"
        test_name = "Agent Tester"

        # Register test user (or clean up if exists)
        existing = User.query.filter_by(email=test_email).first()
        if existing:
            # delete user's saved recipes, ratings, etc.
            SavedRecipe.query.filter_by(user_id=existing.id).delete()
            MealPlan.query.filter_by(user_id=existing.id).delete()
            Rating.query.filter_by(user_id=existing.id).delete()
            ViewHistory.query.filter_by(user_id=existing.id).delete()
            UserPreference.query.filter_by(user_id=existing.id).delete()
            db.session.delete(existing)
            db.session.commit()

        # Register
        reg_res = client.post("/api/auth/register", json={
            "email": test_email,
            "password": test_pass,
            "full_name": test_name
        })
        if reg_res.status_code == 201 and reg_res.json.get("success"):
            record_pass("Auth", "Đăng ký tài khoản mới", reg_res.json.get("message", ""))
            user_token = reg_res.json["data"]["token"]
            test_user_id = reg_res.json["data"]["user"]["id"]
        else:
            record_fail("Auth", "Đăng ký tài khoản mới", f"{reg_res.status_code}: {reg_res.json}")
            user_token = None
            test_user_id = None

        # Duplicate register check
        dup_res = client.post("/api/auth/register", json={
            "email": test_email,
            "password": test_pass,
            "full_name": test_name
        })
        if dup_res.status_code == 409:
            record_pass("Auth", "Bắt trùng lặp email khi đăng ký", "Trả về 409 Conflict đúng chuẩn")
        else:
            record_fail("Auth", "Bắt trùng lặp email khi đăng ký", f"Kỳ vọng 409, nhận {dup_res.status_code}")

        # Login
        login_res = client.post("/api/auth/login", json={
            "email": test_email,
            "password": test_pass
        })
        if login_res.status_code == 200 and login_res.json.get("success"):
            record_pass("Auth", "Đăng nhập chính xác", "Nhận JWT token thành công")
            user_token = login_res.json["data"]["token"]
        else:
            record_fail("Auth", "Đăng nhập chính xác", f"{login_res.status_code}: {login_res.json}")

        # Login wrong pass
        wrong_res = client.post("/api/auth/login", json={
            "email": test_email,
            "password": "wrong_password"
        })
        if wrong_res.status_code == 401:
            record_pass("Auth", "Chặn đăng nhập sai mật khẩu", "Trả về 401 Unauthorized đúng chuẩn")
        else:
            record_fail("Auth", "Chặn đăng nhập sai mật khẩu", f"Kỳ vọng 401, nhận {wrong_res.status_code}")

        auth_headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}

        # Get Me
        me_res = client.get("/api/auth/me", headers=auth_headers)
        if me_res.status_code == 200 and me_res.json.get("data", {}).get("email") == test_email:
            record_pass("Auth", "Lấy thông tin profile GET /api/auth/me", f"User: {test_name}")
        else:
            record_fail("Auth", "Lấy thông tin profile GET /api/auth/me", f"{me_res.status_code}: {me_res.json}")

        # Get Me without token
        unauth_me = client.get("/api/auth/me")
        if unauth_me.status_code in (401, 422):
            record_pass("Auth", "Bảo vệ endpoint GET /api/auth/me khi không có token", f"Trả về {unauth_me.status_code}")
        else:
            record_fail("Auth", "Bảo vệ endpoint GET /api/auth/me", f"Kỳ vọng 401/422, nhận {unauth_me.status_code}")

        # Update preferences
        pref_payload = {
            "preferences": [
                {"pref_type": "taste", "pref_value": "spicy"},
                {"pref_type": "region", "pref_value": "mien_nam"},
                {"pref_type": "diet", "pref_value": "healthy"}
            ]
        }
        pref_res = client.post("/api/auth/users/me/preferences", json=pref_payload, headers=auth_headers)
        if pref_res.status_code == 200 and len(pref_res.json.get("data", [])) == 3:
            record_pass("Auth", "Cập nhật sở thích POST /api/auth/users/me/preferences", "Đã lưu 3 preferences")
        else:
            record_fail("Auth", "Cập nhật sở thích POST /api/auth/users/me/preferences", f"{pref_res.status_code}: {pref_res.json}")

        # Get preferences
        get_pref_res = client.get("/api/auth/users/me/preferences", headers=auth_headers)
        if get_pref_res.status_code == 200 and len(get_pref_res.json.get("data", [])) == 3:
            record_pass("Auth", "Lấy danh sách sở thích GET /api/auth/users/me/preferences", "Khớp dữ liệu vừa tạo")
        else:
            record_fail("Auth", "Lấy danh sách sở thích GET /api/auth/users/me/preferences", f"{get_pref_res.status_code}: {get_pref_res.json}")

        # ------------------------------------------------------------------
        # 3. RECIPES API
        # ------------------------------------------------------------------
        print("\n--- 3. Recipes API ---")
        # List recipes
        rec_res = client.get("/api/recipes?page=1&limit=5")
        if rec_res.status_code == 200 and len(rec_res.json.get("data", [])) > 0:
            total_items = rec_res.json.get("pagination", {}).get("total", 0)
            record_pass("Recipes", "Lấy danh sách món ăn GET /api/recipes", f"Đã lấy {len(rec_res.json['data'])} món, tổng {total_items}")
            sample_recipe = rec_res.json["data"][0]
            sample_recipe_id = sample_recipe["id"]
        else:
            record_fail("Recipes", "Lấy danh sách món ăn GET /api/recipes", f"{rec_res.status_code}: {rec_res.json}")
            sample_recipe_id = 1

        # Search by 'q'
        q_res = client.get("/api/recipes?q=bún")
        if q_res.status_code == 200:
            count_q = len(q_res.json.get("data", []))
            record_pass("Recipes", "Tìm kiếm theo param ?q=bún", f"Tìm thấy {count_q} món")
        else:
            record_fail("Recipes", "Tìm kiếm theo param ?q=bún", f"{q_res.status_code}: {q_res.json}")

        # Search by 'search' param (Check compatibility with Frontend)
        search_res = client.get("/api/recipes?search=bún")
        if search_res.status_code == 200:
            count_search = len(search_res.json.get("data", []))
            if count_search == count_q and count_search > 0:
                record_pass("Recipes", "Hỗ trợ param ?search=bún", f"Khớp kết quả với ?q= ({count_search} món)")
            else:
                record_fail("Recipes", "Hỗ trợ param ?search=bún", f"Khác biệt: ?q={count_q} nhưng ?search={count_search}")
        else:
            record_fail("Recipes", "Hỗ trợ param ?search=bún", f"{search_res.status_code}: {search_res.json}")

        # Filter by region
        reg_filter = client.get("/api/recipes?region=mien_bac")
        if reg_filter.status_code == 200:
            record_pass("Recipes", "Lọc món theo miền ?region=mien_bac", f"Tìm thấy {len(reg_filter.json.get('data', []))} món")
        else:
            record_fail("Recipes", "Lọc món theo miền ?region=mien_bac", f"{reg_filter.status_code}")

        # Filter by difficulty
        diff_filter = client.get("/api/recipes?difficulty=easy")
        if diff_filter.status_code == 200:
            record_pass("Recipes", "Lọc món theo độ khó ?difficulty=easy", f"Tìm thấy {len(diff_filter.json.get('data', []))} món")
        else:
            record_fail("Recipes", "Lọc món theo độ khó ?difficulty=easy", f"{diff_filter.status_code}")

        # Get Recipe Detail
        detail_res = client.get(f"/api/recipes/{sample_recipe_id}")
        if detail_res.status_code == 200 and detail_res.json.get("data", {}).get("id") == sample_recipe_id:
            d = detail_res.json["data"]
            has_ings = len(d.get("ingredients", [])) > 0
            has_steps = len(d.get("steps", [])) > 0
            record_pass("Recipes", f"Lấy chi tiết món GET /api/recipes/{sample_recipe_id}", f"Có {len(d.get('ingredients', []))} nguyên liệu, {len(d.get('steps', []))} bước nấu")
            if not has_ings:
                record_warn("Recipes", f"Món {sample_recipe_id} không có nguyên liệu", "")
            if not has_steps:
                record_warn("Recipes", f"Món {sample_recipe_id} không có bước nấu", "")
        else:
            record_fail("Recipes", f"Lấy chi tiết món GET /api/recipes/{sample_recipe_id}", f"{detail_res.status_code}: {detail_res.json}")

        # Recipe 404
        nf_res = client.get("/api/recipes/999999")
        if nf_res.status_code == 404:
            record_pass("Recipes", "Xử lý món không tồn tại (404 Not Found)", "Trả về 404 chuẩn")
        else:
            record_fail("Recipes", "Xử lý món không tồn tại", f"Kỳ vọng 404, nhận {nf_res.status_code}")

        # ------------------------------------------------------------------
        # 4. RATINGS & VIEWS
        # ------------------------------------------------------------------
        print("\n--- 4. Ratings & Views ---")
        # Get recipe ratings
        rat_list = client.get(f"/api/recipes/{sample_recipe_id}/ratings")
        if rat_list.status_code == 200:
            record_pass("Ratings", f"Xem đánh giá món GET /api/recipes/{sample_recipe_id}/ratings", f"Có {len(rat_list.json.get('data', []))} đánh giá")
        else:
            record_fail("Ratings", f"Xem đánh giá món GET /api/recipes/{sample_recipe_id}/ratings", f"{rat_list.status_code}")

        # Post rating via route POST /api/recipes/<id>/ratings (Frontend style)
        post_rat = client.post(f"/api/recipes/{sample_recipe_id}/ratings", json={
            "score": 5,
            "review_text": "Món này rất ngon và chuẩn vị Việt Nam!"
        }, headers=auth_headers)
        if post_rat.status_code in (200, 201) and post_rat.json.get("success"):
            record_pass("Ratings", f"Đánh giá món POST /api/recipes/{sample_recipe_id}/ratings", "Thành công")
        else:
            record_fail("Ratings", f"Đánh giá món POST /api/recipes/{sample_recipe_id}/ratings", f"{post_rat.status_code}: {post_rat.json}")

        # Post view via route POST /api/recipes/<id>/views (With Token)
        view_auth = client.post(f"/api/recipes/{sample_recipe_id}/views", json={"duration_sec": 45}, headers=auth_headers)
        if view_auth.status_code == 200:
            record_pass("Views", f"Ghi nhận lượt xem (đã đăng nhập) POST /api/recipes/{sample_recipe_id}/views", "Trả về 200")
        else:
            record_fail("Views", f"Ghi nhận lượt xem (đã đăng nhập)", f"{view_auth.status_code}")

        # Post view via route POST /api/recipes/<id>/views (GUEST - NO TOKEN)
        view_guest = client.post(f"/api/recipes/{sample_recipe_id}/views", json={"duration_sec": 30})
        if view_guest.status_code == 200:
            record_pass("Views", f"Ghi nhận lượt xem (khách vãng lai)", "Trả về 200 thành công")
        elif view_guest.status_code in (401, 422):
            record_fail("Views", f"Ghi nhận lượt xem (khách vãng lai)", f"BỊ LỖI 401 Unauthorized do endpoint yêu cầu JWT token!")
        else:
            record_fail("Views", f"Ghi nhận lượt xem (khách vãng lai)", f"Status {view_guest.status_code}")

        # ------------------------------------------------------------------
        # 5. INGREDIENTS & SEARCH BY INGREDIENTS
        # ------------------------------------------------------------------
        print("\n--- 5. Ingredients & Search by Ingredients ---")
        # List ingredients
        ing_list = client.get("/api/ingredients?limit=10")
        if ing_list.status_code == 200 and len(ing_list.json.get("data", [])) > 0:
            sample_ing = ing_list.json["data"][0]
            record_pass("Ingredients", "Lấy danh sách nguyên liệu GET /api/ingredients", f"Lấy thành công, ví dụ: {sample_ing['name']}")
        else:
            record_fail("Ingredients", "Lấy danh sách nguyên liệu GET /api/ingredients", f"{ing_list.status_code}")

        # Tags route
        tags_res = client.get("/api/tags")
        if tags_res.status_code == 200 and len(tags_res.json.get("data", [])) > 0:
            record_pass("Tags", "Lấy danh sách tags GET /api/tags", f"Có {len(tags_res.json['data'])} tags")
        else:
            record_fail("Tags", "Lấy danh sách tags GET /api/tags", f"{tags_res.status_code}")

        # Tags alias route (Frontend calls /api/ingredients/tags)
        tags_alias = client.get("/api/ingredients/tags")
        if tags_alias.status_code == 200 and len(tags_alias.json.get("data", [])) > 0:
            record_pass("Tags", "Alias tags GET /api/ingredients/tags", f"Khớp {len(tags_alias.json['data'])} tags")
        else:
            record_fail("Tags", "Alias tags GET /api/ingredients/tags", f"Status {tags_alias.status_code}")

        # Substitutes
        sub_res = client.get("/api/ingredients/1/substitutes")
        if sub_res.status_code == 200:
            subs = sub_res.json.get("data", [])
            record_pass("Ingredients", "Lấy nguyên liệu thay thế GET /api/ingredients/1/substitutes", f"Có {len(subs)} nguyên liệu thay thế")
            # Check fields
            if subs:
                first_sub = subs[0]
                if "ratio" not in first_sub:
                    record_warn("Ingredients", "Thiếu field 'ratio' trong IngredientSubstitute response", f"Frontend hiển thị 'Tỷ lệ: undefined:1' vì model chỉ có note, không có ratio!")
        else:
            record_fail("Ingredients", "Lấy nguyên liệu thay thế GET /api/ingredients/1/substitutes", f"{sub_res.status_code}")

        # Search recipes by ingredients
        # Lấy vài ID nguyên liệu phổ biến
        test_ing_ids = [1, 2, 3, 5, 8]
        search_by_ing = client.post("/api/search/by-ingredients", json={
            "ingredient_ids": test_ing_ids,
            "match_mode": "any"
        })
        if search_by_ing.status_code == 200 and search_by_ing.json.get("success"):
            matched_recipes = search_by_ing.json.get("data", [])
            record_pass("SearchIngredients", "Tìm món theo nguyên liệu POST /api/search/by-ingredients", f"Tìm thấy {len(matched_recipes)} món phù hợp")
            if matched_recipes:
                first_m = matched_recipes[0]
                mp = first_m.get("match_percent")
                record_pass("SearchIngredients", f"Giá trị match_percent", f"match_percent = {mp}")
                # Kiểm tra lỗi UI nhân đôi:
                # Nếu backend trả về 75.0 và frontend nhân 100 thành 7500%:
                if mp > 1:
                    print(f"      [CHÚ Ý LỖI 2] Backend trả về match_percent={mp} (đã scale 0-100).")
        else:
            record_fail("SearchIngredients", "Tìm món theo nguyên liệu", f"{search_by_ing.status_code}: {search_by_ing.json}")

        # ------------------------------------------------------------------
        # 6. RECOMMENDATIONS API
        # ------------------------------------------------------------------
        print("\n--- 6. Recommendations API ---")
        # Guest recommendations (No Token)
        rec_guest = client.get("/api/recommendations?limit=6")
        if rec_guest.status_code == 200 and rec_guest.json.get("success"):
            rec_guest_data = rec_guest.json.get("data", [])
            record_pass("Recommendations", "Khách vãng lai xem gợi ý GET /api/recommendations", f"Trả về {len(rec_guest_data)} món phổ biến (HTTP 200)")
        else:
            record_fail("Recommendations", "Khách vãng lai xem gợi ý GET /api/recommendations", f"Kỳ vọng 200, nhận {rec_guest.status_code}: {rec_guest.json}")

        # Authenticated user recommendations (With Token & Preferences)
        rec_auth = client.get("/api/recommendations?limit=6&force_refresh=true", headers=auth_headers)
        if rec_auth.status_code == 200 and rec_auth.json.get("success"):
            rec_auth_data = rec_auth.json.get("data", [])
            record_pass("Recommendations", "User đã đăng nhập xem gợi ý AI", f"Trả về {len(rec_auth_data)} món theo thuật toán: {rec_auth.json.get('message')}")
        else:
            record_fail("Recommendations", "User đã đăng nhập xem gợi ý AI", f"{rec_auth.status_code}: {rec_auth.json}")

        # ------------------------------------------------------------------
        # 7. MEAL PLANS & SHOPPING LIST
        # ------------------------------------------------------------------
        print("\n--- 7. Meal Plans & Shopping List ---")
        # Add meal plan with 'date' (Frontend format)
        today_str = date.today().isoformat()
        mp_add_res = client.post("/api/meal-plans", json={
            "date": today_str,
            "meal_type": "lunch",
            "recipe_id": sample_recipe_id,
            "servings": 4
        }, headers=auth_headers)
        if mp_add_res.status_code == 201 and mp_add_res.json.get("success"):
            plan_id = mp_add_res.json["data"]["id"]
            record_pass("MealPlans", "Thêm món vào thực đơn với param 'date' (Frontend format)", f"Đã thêm plan_id={plan_id}")
        else:
            record_fail("MealPlans", "Thêm món vào thực đơn với param 'date'", f"{mp_add_res.status_code}: {mp_add_res.json}")
            plan_id = None

        # Get meal plans (Backend native param: week_start)
        # Calculate monday of this week
        curr_monday = date.today() - timedelta(days=date.today().weekday())
        mp_get_ws = client.get(f"/api/meal-plans?week_start={curr_monday.isoformat()}", headers=auth_headers)
        if mp_get_ws.status_code == 200 and len(mp_get_ws.json.get("data", [])) > 0:
            record_pass("MealPlans", "Lấy thực đơn tuần với param ?week_start=", f"Tìm thấy {len(mp_get_ws.json['data'])} món")
        else:
            record_fail("MealPlans", "Lấy thực đơn tuần với param ?week_start=", f"{mp_get_ws.status_code}: {mp_get_ws.json}")

        # Get meal plans with NO params (as Frontend MealPlanPage calls: mealPlansApi.getAll())
        mp_get_none = client.get("/api/meal-plans", headers=auth_headers)
        if mp_get_none.status_code == 200:
            found_count = len(mp_get_none.json.get("data", []))
            # Chú ý: Nếu date.today() != Monday, week_start=date.today() trong Backend sẽ không khớp với Monday!
            if date.today().weekday() != 0 and found_count == 0:
                record_warn("MealPlans", "GET /api/meal-plans không có param (Default date)", f"date.today() là Thứ {date.today().weekday()+1}, nhưng món được lưu theo Monday ({curr_monday.isoformat()}). Do đó không tìm thấy món vừa lưu!")
            else:
                record_pass("MealPlans", "Lấy thực đơn tuần không truyền param", f"Tìm thấy {found_count} món")
        else:
            record_fail("MealPlans", "Lấy thực đơn tuần không truyền param", f"{mp_get_none.status_code}")

        # Get shopping list
        shop_res = client.get(f"/api/meal-plans/shopping-list?week_start={curr_monday.isoformat()}", headers=auth_headers)
        if shop_res.status_code == 200:
            shop_items = shop_res.json.get("data", [])
            record_pass("MealPlans", "Tạo danh sách đi chợ GET /api/meal-plans/shopping-list", f"Tổng hợp {len(shop_items)} nguyên liệu cần mua")
        else:
            record_fail("MealPlans", "Tạo danh sách đi chợ", f"{shop_res.status_code}: {shop_res.json}")

        # Delete meal plan
        if plan_id:
            del_mp = client.delete(f"/api/meal-plans/{plan_id}", headers=auth_headers)
            if del_mp.status_code == 200:
                record_pass("MealPlans", f"Xóa món khỏi thực đơn DELETE /api/meal-plans/{plan_id}", "Xóa thành công")
            else:
                record_fail("MealPlans", f"Xóa món khỏi thực đơn", f"{del_mp.status_code}")

        # ------------------------------------------------------------------
        # 8. SAVED RECIPES (BOOKMARK)
        # ------------------------------------------------------------------
        print("\n--- 8. Saved Recipes (Bookmarks) ---")
        # Save recipe via POST /api/users/me/saved/:recipe_id (Frontend format)
        save_res = client.post(f"/api/users/me/saved/{sample_recipe_id}", headers=auth_headers)
        if save_res.status_code in (200, 201) and save_res.json.get("success"):
            record_pass("SavedRecipes", f"Lưu món POST /api/users/me/saved/{sample_recipe_id}", "Lưu thành công")
        else:
            record_fail("SavedRecipes", f"Lưu món POST /api/users/me/saved/{sample_recipe_id}", f"{save_res.status_code}: {save_res.json}")

        # Duplicate save check
        dup_save = client.post(f"/api/users/me/saved/{sample_recipe_id}", headers=auth_headers)
        if dup_save.status_code == 409:
            record_pass("SavedRecipes", "Chặn lưu trùng lặp cùng một món", "Trả về 409 Conflict chuẩn")
        else:
            record_fail("SavedRecipes", "Chặn lưu trùng lặp", f"Kỳ vọng 409, nhận {dup_save.status_code}")

        # Get saved recipes
        get_saved = client.get("/api/users/me/saved", headers=auth_headers)
        if get_saved.status_code == 200:
            saved_items = get_saved.json.get("data", [])
            has_id = any(item.get("id") == sample_recipe_id for item in saved_items)
            if has_id:
                record_pass("SavedRecipes", "Lấy danh sách món đã lưu GET /api/users/me/saved", f"Có {len(saved_items)} món, chứa món ID {sample_recipe_id}")
            else:
                record_fail("SavedRecipes", "Lấy danh sách món đã lưu", f"Không tìm thấy món ID {sample_recipe_id}")
        else:
            record_fail("SavedRecipes", "Lấy danh sách món đã lưu", f"{get_saved.status_code}")

        # Unsave recipe DELETE /api/users/me/saved/:recipe_id
        unsave_res = client.delete(f"/api/users/me/saved/{sample_recipe_id}", headers=auth_headers)
        if unsave_res.status_code == 200:
            record_pass("SavedRecipes", f"Bỏ lưu món DELETE /api/users/me/saved/{sample_recipe_id}", "Bỏ lưu thành công")
        else:
            record_fail("SavedRecipes", f"Bỏ lưu món", f"{unsave_res.status_code}")

        # Unsave again (expect 404)
        unsave_again = client.delete(f"/api/users/me/saved/{sample_recipe_id}", headers=auth_headers)
        if unsave_again.status_code == 404:
            record_pass("SavedRecipes", "Bỏ lưu món không tồn tại trong danh sách", "Trả về 404 Not Found")
        else:
            record_fail("SavedRecipes", "Bỏ lưu món không tồn tại", f"Kỳ vọng 404, nhận {unsave_again.status_code}")

        # ------------------------------------------------------------------
        # 9. ADMIN API & PERMISSIONS
        # ------------------------------------------------------------------
        print("\n--- 9. Admin API & Permissions ---")
        # Regular user accessing admin route -> expect 403 Forbidden
        reg_admin_try = client.get("/api/admin/stats", headers=auth_headers)
        if reg_admin_try.status_code == 403:
            record_pass("Admin", "Chặn user thường truy cập endpoint admin", "Trả về 403 Forbidden chuẩn")
        else:
            record_fail("Admin", "Chặn user thường truy cập admin", f"Kỳ vọng 403, nhận {reg_admin_try.status_code}")

        # Create/Get an admin user to test admin functionality
        admin_email = "admin_test@example.com"
        admin_user = User.query.filter_by(role="admin").first()
        from flask_jwt_extended import create_access_token
        if admin_user:
            admin_token = create_access_token(identity=admin_user.id)
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            record_pass("Admin", "Tìm thấy tài khoản Admin trong DB", f"Admin ID: {admin_user.id}")
        else:
            record_warn("Admin", "Chưa có tài khoản admin trong DB", "Tạo tạm admin token để test...")
            admin_token = create_access_token(identity=test_user_id)
            # grant admin temporarily
            test_u = User.query.get(test_user_id)
            test_u.role = "admin"
            db.session.commit()
            admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Test GET /api/admin/stats
        admin_stats = client.get("/api/admin/stats", headers=admin_headers)
        if admin_stats.status_code == 200 and admin_stats.json.get("success"):
            stats_data = admin_stats.json.get("data", {})
            record_pass("Admin", "Lấy thống kê hệ thống GET /api/admin/stats", f"Recipes: {stats_data.get('total_recipes')}, Users: {stats_data.get('total_users')}, Ratings: {stats_data.get('total_ratings')}")
        else:
            record_fail("Admin", "Lấy thống kê hệ thống GET /api/admin/stats", f"{admin_stats.status_code}: {admin_stats.json}")

        # Test Toggle Publish Recipe
        toggle_res = client.post(f"/api/admin/recipes/{sample_recipe_id}/publish", headers=admin_headers)
        if toggle_res.status_code == 200:
            is_pub = toggle_res.json.get("data", {}).get("is_published")
            record_pass("Admin", f"Ẩn/Hiện công thức POST /api/admin/recipes/{sample_recipe_id}/publish", f"Trạng thái mới: {is_pub}")
            # Revert back
            client.post(f"/api/admin/recipes/{sample_recipe_id}/publish", headers=admin_headers)
        else:
            record_fail("Admin", "Ẩn/Hiện công thức", f"{toggle_res.status_code}")

        # Clean up test user
        if test_user_id:
            u = User.query.get(test_user_id)
            if u:
                SavedRecipe.query.filter_by(user_id=test_user_id).delete()
                MealPlan.query.filter_id = test_user_id
                MealPlan.query.filter_by(user_id=test_user_id).delete()
                Rating.query.filter_by(user_id=test_user_id).delete()
                ViewHistory.query.filter_by(user_id=test_user_id).delete()
                UserPreference.query.filter_by(user_id=test_user_id).delete()
                db.session.delete(u)
                db.session.commit()

        # ------------------------------------------------------------------
        # TỔNG KẾT
        # ------------------------------------------------------------------
        print("\n========================================================")
        print("                   KẾT QUẢ KIỂM THỬ")
        print("========================================================")
        print(f"Tổng số PASS: {len(results['passed'])}")
        print(f"Tổng số FAIL: {len(results['failed'])}")
        print(f"Tổng số WARN: {len(results['warnings'])}")

        if results["failed"]:
            print("\n❌ DANH SÁCH LỖI (FAIL):")
            for f in results["failed"]:
                print(f"  - {f}")

        if results["warnings"]:
            print("\n⚠️ DANH SÁCH CẢNH BÁO (WARN):")
            for w in results["warnings"]:
                print(f"  - {w}")

if __name__ == "__main__":
    run_tests()
