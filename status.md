# 📊 BÁO CÁO TIẾN ĐỘ DỰ ÁN (PROJECT STATUS)
> **Dự án:** Hệ Thống Gợi Ý & Công Thức Nấu Ăn Thông Minh (TVU 2026)  
> **Repository:** [https://github.com/NhutPham19/Web_Goi_Y_Mon_An](https://github.com/NhutPham19/Web_Goi_Y_Mon_An) (Branch: `main`)  
> **Cập nhật:** 2026-09-22  
> **Người thực hiện:** Antigravity AI  
> **Dành cho:** Claude AI (Đọc file này để nắm tình trạng và tiếp tục công việc)

---

## 📌 TÓM TẮT DÀNH CHO CLAUDE

> **Chào Claude!**  
> Toàn bộ mã nguồn Backend từ **PHASE 1 đến PHASE 5** và **Task 6.2 (API Documentation)** đã được hoàn thành **100%** và đã được push lên GitHub repo `Web_Goi_Y_Mon_An`.  
> **BẠN KHÔNG CẦN VIẾT LẠI BẤT KỲ FILE BACKEND NÀO TRONG APP/ HAY SCRIPTS/ NỮA.**  
> Nhiệm vụ tiếp theo của bạn là tập trung vào **TASK 6.1 (Triển khai & Kiểm thử thực tế)** hoặc hỗ trợ người dùng kết nối Database / Deploy lên Render.

---

## 🎯 BẢNG TIẾN ĐỘ CHI TIẾT TỪNG TASK

| Phase | Task | Tên công việc | Trạng thái | Chi tiết file đã tạo / hoàn thành |
|---|---|---|:---:|---|
| **Phase 1** | **Task 1.1** | Khởi tạo dự án & môi trường | ✅ **XONG** | `app.py`, `config.py`, `requirements.txt`, `.gitignore`, `.env.example`, `Procfile`, `app/__init__.py` |
| **Phase 1** | **Task 1.2** | 12 bảng Database Schema ORM | ✅ **XONG** | `app/models/` (`user.py`, `recipe.py`, `ingredient.py`, `rating.py`, `meal_plan.py`, `__init__.py`) |
| **Phase 1** | **Task 1.3** | Auth API (Register, Login, Me, Logout) | ✅ **XONG** | `app/routes/auth.py`, `app/utils/decorators.py`, `app/utils/response.py` |
| **Phase 2** | **Task 2.1** | Ingredients & Tags API | ✅ **XONG** | `app/routes/ingredients.py`, `scripts/data/ingredients_data.py` (100 nguyên liệu, 15 tags, 15 substitutes), `scripts/seed_ingredients.py` |
| **Phase 2** | **Task 2.2** | Recipes CRUD API & Cloudinary | ✅ **XONG** | `app/routes/recipes.py` (320 dòng, đầy đủ CRUD, filter, paging, toggle publish), `app/services/cloudinary_service.py` |
| **Phase 2** | **Task 2.3** | Seed Dataset 80 món ăn 3 miền | ✅ **XONG** | `scripts/data/recipes_data.py` (80 món đầy đủ định lượng, bước nấu, tags, vùng miền) và `scripts/seed_recipes.py` |
| **Phase 3** | **Task 3.1** | Tìm kiếm theo nguyên liệu có sẵn | ✅ **XONG** | `app/routes/search.py` (`POST /api/search/by-ingredients`), `app/services/ingredient_search.py` (tính `matched_count`, `match_percent`, `missing_ingredients`) |
| **Phase 3** | **Task 3.2** | Nguyên liệu thay thế (Substitutes) | ✅ **XONG** | `GET /api/ingredients/:id/substitutes` và 15 cặp dữ liệu thay thế thực tế |
| **Phase 4** | **Task 4.1** | User Preferences API | ✅ **XONG** | `GET/POST /api/auth/users/me/preferences` (upsert theo diet, taste, allergy, serving_size) |
| **Phase 4** | **Task 4.2** | Ratings API & View History | ✅ **XONG** | `app/routes/ratings.py` (upsert rating, tự động tính lại `avg_rating` & `rating_count`, endpoint `POST /api/view-history` fire-and-forget) |
| **Phase 4** | **Task 4.3** | Content-Based Filtering (CBF) | ✅ **XONG** | `app/services/content_based.py` (TF-IDF, Cosine Similarity giữa user preference và recipe tags/difficulty/time, cache TTL 1h) |
| **Phase 4** | **Task 4.4** | Collaborative Filtering (CF) & Hybrid | ✅ **XONG** | `app/services/collaborative.py` (SVD matrix factorization), `app/routes/recommendations.py` (Hybrid 60% CBF + 40% CF, tự động fallback popular), `scripts/seed_ratings.py` (sinh 500 synthetic ratings theo 10 profile user thực tế) |
| **Phase 5** | **Task 5.1** | Meal Plan & Shopping List API | ✅ **XONG** | `app/routes/meal_plans.py` (`/api/meal-plans`, cộng dồn tổng hợp số lượng nguyên liệu theo tuần `/api/meal-plans/shopping-list`) |
| **Phase 5** | **Task 5.2** | Admin Stats API | ✅ **XONG** | `app/routes/admin.py` (`GET /api/admin/stats` thống kê số lượng recipe, user, top rated, most viewed) |
| **Phase 5** | **Task 5.3** | Saved Recipes (Yêu thích) | ✅ **XONG** | `GET/POST/DELETE /api/users/me/saved` trong `app/routes/meal_plans.py` |
| **Phase 6** | **Task 6.1** | Deploy Render & Môi trường thực tế | ⏳ **TIẾP THEO** | Cần người dùng điền credentials Supabase thật vào `.env`, chạy seed data và deploy lên Render |
| **Phase 6** | **Task 6.2** | API Documentation | ✅ **XONG** | `TaiLieu/API_DOCS.md` (tài liệu chi tiết 100% endpoints, format JSON, query params, bảng emoji nguyên liệu cho Frontend) |

---

## 📁 CẤU TRÚC CODEBASE HIỆN TẠI (TRÊN GIT MAIN)

```
Web_NauAn/
├── status.md                          # File trạng thái này
├── .env.example                       # Mẫu cấu hình môi trường
├── .gitignore                         # Chặn .env, venv, cache
├── Procfile                           # web: gunicorn app:app (Render)
├── requirements.txt                   # Danh sách package dependencies
├── app.py                             # Entry point Flask
├── config.py                          # Config reader từ .env
│
├── TaiLieu/                           # 📚 Thư mục tài liệu
│   ├── API_DOCS.md                    # Tài liệu API cho Frontend
│   ├── KEHOACH_BACKEND_NauAn.md       # Kế hoạch chi tiết 6 Phase
│   ├── TONG_QUAN_VA_TIEN_DO.md        # Báo cáo tiến độ tổng quan
│   ├── CLAUDE_INSTRUCTION.md          # Hướng dẫn quy chuẩn cho Claude
│   └── SKILL_FRONTEND_DESIGN.md       # Hướng dẫn thiết kế Frontend
│
├── app/                               # ⚙️ Source code Flask API
│   ├── __init__.py                    # App factory, CORS, JWT, Blueprints
│   ├── models/                        # 12 ORM Models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── ingredient.py
│   │   ├── rating.py
│   │   └── meal_plan.py
│   ├── routes/                        # Blueprints API
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── recipes.py
│   │   ├── ingredients.py
│   │   ├── search.py
│   │   ├── recommendations.py         # Hybrid CBF + CF
│   │   ├── ratings.py
│   │   ├── meal_plans.py              # MealPlan + SavedRecipes
│   │   └── admin.py
│   ├── services/                      # Business logic & ML
│   │   ├── __init__.py
│   │   ├── ingredient_search.py
│   │   ├── content_based.py
│   │   ├── collaborative.py
│   │   └── cloudinary_service.py
│   └── utils/                         # Helpers & Decorators
│       ├── __init__.py
│       ├── response.py
│       └── decorators.py
│
└── scripts/                           # 🌱 Scripts seed database
    ├── data/
    │   ├── __init__.py
    │   ├── ingredients_data.py        # 100 nguyên liệu Việt Nam
    │   └── recipes_data.py            # 80 món ăn 3 miền đầy đủ
    ├── seed_ingredients.py            # Seed nguyên liệu & tags
    ├── seed_recipes.py                # Seed 80 món vào DB
    └── seed_ratings.py                # Seed 500 ratings cho CF
```

---

## 🚀 NHIỆM VỤ TIẾP THEO CHO CLAUDE (TASK 6.1)

Khi người dùng làm việc với bạn, Claude hãy hướng dẫn người dùng thực hiện các bước sau:

### 1. Cấu hình Môi trường thật:
- Tạo file `.env` từ `.env.example`.
- Điền connection string Supabase PostgreSQL (`DATABASE_URL`).
- Điền các biến `SECRET_KEY`, `JWT_SECRET_KEY`, Cloudinary keys.

### 2. Khởi tạo Database & Seed Dữ liệu:
Chạy lần lượt trong terminal:
```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Khởi tạo migration
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Chạy seed dữ liệu theo thứ tự bắt buộc:
python scripts/seed_ingredients.py    # 1. Nạp 100 nguyên liệu, 15 tags, 15 substitutes
python scripts/seed_recipes.py        # 2. Nạp 80 món ăn vào DB
python scripts/seed_ratings.py        # 3. Nạp 500 ratings giả lập (cần đăng ký ít nhất 2 user trước)
```

### 3. Kiểm tra API Local:
```bash
flask run
# Ping: GET http://localhost:5000/api/health -> {"status": "ok", "service": "nauAn-backend"}
```

### 4. Triển khai lên Render (Render Web Service):
- Kết nối với repo: `https://github.com/NhutPham19/Web_Goi_Y_Mon_An`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app` (đã có trong `Procfile`)
- Cấu hình Environment Variables trên Render Dashboard.
- Cập nhật Base URL sau khi deploy vào `TaiLieu/API_DOCS.md`.

---

## 💬 PROMPT MẪU ĐỂ BẠN GỬI CHO CLAUDE

Bạn chỉ cần copy đoạn dưới đây dán vào Claude:

```text
Tôi đã cùng Antigravity hoàn thành 100% source code từ Phase 1 đến Phase 5 và Task 6.2 (API_DOCS.md). Toàn bộ code đã được push lên GitHub tại https://github.com/NhutPham19/Web_Goi_Y_Mon_An. Hãy đọc file status.md trong repo để biết chi tiết.

Bây giờ bạn không cần viết lại bất kỳ file nào trong app/ hay scripts/. Hãy giúp tôi thực hiện Task 6.1:
1. Hướng dẫn tôi tạo project Supabase và điền file .env chuẩn.
2. Hướng dẫn chạy migrate DB và chạy 3 script seed data (seed_ingredients.py, seed_recipes.py, seed_ratings.py).
3. Hướng dẫn deploy Web Service lên Render qua repo GitHub đã có.
```
