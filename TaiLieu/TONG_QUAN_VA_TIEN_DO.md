# 📋 TỔNG QUAN DỰ ÁN & TIẾN ĐỘ THỰC HIỆN

> **Dự án:** Hệ Thống Gợi Ý & Công Thức Nấu Ăn Thông Minh (TVU 2026)  
> **Cập nhật:** 2026-09-21  
> **Backend:** Claude  
> **Frontend:** Antigravity  

---

## 🌳 CÂY THƯ MỤC DỰ ÁN (ĐÃ SẮP XẾP CHUẨN)

```
Web_NauAn/
├── TaiLieu/                           # 📚 Tài liệu dự án
│   ├── KEHOACH_BACKEND_NauAn.md       # Kế hoạch chi tiết 6 Phase
│   ├── CLAUDE_INSTRUCTION.md          # System prompt dành cho Claude
│   ├── SKILL_FRONTEND_DESIGN.md       # Hướng dẫn thiết kế UI cho Antigravity
│   ├── API_DOCS.md                    # ✅ Tài liệu API đầy đủ cho Antigravity
│   └── TONG_QUAN_VA_TIEN_DO.md        # File này
│
├── app/                               # ⚙️ Source code Flask API
│   ├── __init__.py                    # App Factory, đăng ký Blueprints & CORS
│   ├── models/                        # 12 ORM Models SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py                    # User, UserPreference
│   │   ├── recipe.py                  # Recipe, Step, Tag, recipe_tags
│   │   ├── ingredient.py              # Ingredient, RecipeIngredient, IngredientSubstitute
│   │   ├── rating.py                  # Rating, ViewHistory
│   │   └── meal_plan.py               # MealPlan, SavedRecipe, RecommendationCache
│   ├── routes/                        # Flask Blueprints
│   │   ├── __init__.py
│   │   ├── auth.py                    # Register, Login, Me, Logout, Preferences
│   │   ├── recipes.py                 # CRUD công thức, filter, upload ảnh
│   │   ├── ingredients.py             # Danh sách nguyên liệu, tags, substitutes
│   │   ├── search.py                  # Tìm món theo nguyên liệu có sẵn
│   │   ├── recommendations.py         # ✅ HYBRID CBF 60% + CF 40%
│   │   ├── ratings.py                 # Đánh giá sao, lịch sử xem
│   │   ├── meal_plans.py              # Thực đơn tuần, shopping list
│   │   └── admin.py                   # Stats, quản trị tags/nguyên liệu
│   ├── services/                      # Business Logic & Machine Learning
│   │   ├── __init__.py
│   │   ├── ingredient_search.py       # Thuật toán so khớp nguyên liệu
│   │   ├── content_based.py           # CBF: TF-IDF + Cosine Similarity
│   │   ├── collaborative.py           # CF: SVD Matrix Factorization
│   │   └── cloudinary_service.py      # Upload & transform ảnh
│   └── utils/
│       ├── __init__.py
│       ├── response.py                # JSON response format chuẩn
│       └── decorators.py              # @jwt_required_custom, @admin_required
│
├── scripts/                           # 🌱 Scripts nạp dữ liệu
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ingredients_data.py        # 100 nguyên liệu, 15 tags, 15 substitutes
│   │   └── recipes_data.py            # ✅ 80 món ăn Việt Nam 3 miền
│   ├── seed_ingredients.py            # Seed nguyên liệu, tags, substitutes
│   ├── seed_recipes.py                # ✅ Seed 80 công thức vào DB
│   └── seed_ratings.py                # ✅ Seed 500 synthetic ratings cho CF
│
├── .env.example                       # Mẫu biến môi trường
├── .gitignore
├── Procfile                           # web: gunicorn app:app
├── requirements.txt
└── app.py                             # Entry point Flask
```

---

## ✅ BÁO CÁO TIẾN ĐỘ TASK

### PHASE 1 — Khung xương (100% hoàn thành)
| Task | Nội dung | Trạng thái |
|---|---|:---:|
| Task 1.1 | Khởi tạo dự án, config Flask, Supabase | ✅ |
| Task 1.2 | 12 bảng SQLAlchemy Models + quan hệ FK | ✅ |
| Task 1.3 | Auth API (Register, Login, Me, Preferences) + JWT + bcrypt | ✅ |

### PHASE 2 — Core Content (100% hoàn thành)
| Task | Nội dung | Trạng thái |
|---|---|:---:|
| Task 2.1 | Ingredients & Tags API + dataset 100 nguyên liệu + seed script | ✅ |
| Task 2.2 | Recipes CRUD API đầy đủ + Cloudinary upload | ✅ |
| Task 2.3 | Seed dataset 80 món ăn Việt Nam 3 miền + seed_recipes.py | ✅ |

### PHASE 3 — Tìm kiếm theo nguyên liệu (100% hoàn thành)
| Task | Nội dung | Trạng thái |
|---|---|:---:|
| Task 3.1 | `POST /api/search/by-ingredients` + thuật toán matched_count, match_percent | ✅ |
| Task 3.2 | `GET /api/ingredients/:id/substitutes` + seed 15 cặp thay thế | ✅ |

### PHASE 4 — Recommendation ML (100% hoàn thành)
| Task | Nội dung | Trạng thái |
|---|---|:---:|
| Task 4.1 | User Preferences API (GET/POST upsert) | ✅ |
| Task 4.2 | Ratings API + auto-update avg_rating + View History | ✅ |
| Task 4.3 | Content-Based Filtering (TF-IDF + Cosine Similarity) + cache TTL 1h | ✅ |
| Task 4.4 | Collaborative Filtering (SVD) + Hybrid CBF 60%+CF 40% + seed_ratings.py | ✅ |

### PHASE 5 — Tính năng mở rộng (90% hoàn thành)
| Task | Nội dung | Trạng thái |
|---|---|:---:|
| Task 5.1 | Meal Plan API + Shopping List aggregate | ✅ |
| Task 5.2 | Admin Stats API | ✅ |
| Task 5.3 | Saved Recipes API | ✅ |

### PHASE 6 — Deploy & Hoàn thiện (30%)
| Task | Nội dung | Trạng thái |
|---|---|:---:|
| Task 6.1 | Deploy lên Render | ⏳ Chưa deploy |
| Task 6.2 | API Documentation cho Antigravity | ✅ `TaiLieu/API_DOCS.md` |

---

## 🚀 BƯỚC TIẾP THEO: DEPLOY LÊN SUPABASE + RENDER

### Bước 1: Thiết lập Supabase
1. Tạo project Supabase mới tại [supabase.com](https://supabase.com)
2. Vào **Settings → Database → Connection string (URI)** → copy `DATABASE_URL`
3. Tạo file `.env` từ `.env.example`, điền `DATABASE_URL`

### Bước 2: Chạy migrations và seed data (local)
```bash
# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Cài thư viện
pip install -r requirements.txt

# Khởi tạo Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed dữ liệu (theo thứ tự)
python scripts/seed_ingredients.py    # 1. Seed nguyên liệu & tags
python scripts/seed_recipes.py        # 2. Seed 80 món ăn
python scripts/seed_ratings.py        # 3. Seed synthetic ratings (cần user trước)

# Test local
flask run
# → http://localhost:5000/api/health
```

### Bước 3: Tạo tài khoản admin
```sql
-- Chạy trực tiếp trong Supabase SQL editor:
UPDATE users SET role = 'admin' WHERE email = 'your_email@example.com';
```

### Bước 4: Deploy lên Render
1. Push code lên GitHub (private repo)
2. Tạo **Render account mới** (tách biệt)
3. New Web Service → Connect repo
4. Set Environment Variables từ `.env.example`
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app` (đã có Procfile)

---

## 🧪 TEST NHANH CÁC API CHÍNH

```bash
BASE=http://localhost:5000

# Health check
curl $BASE/api/health

# Register
curl -X POST $BASE/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345678","full_name":"Test User"}'

# Login & lưu token
TOKEN=$(curl -s -X POST $BASE/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345678"}' | python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# Danh sách công thức
curl "$BASE/api/recipes?page=1&limit=5"

# Tìm theo nguyên liệu
curl -X POST $BASE/api/search/by-ingredients \
  -H "Content-Type: application/json" \
  -d '{"ingredient_ids":[1,2,3],"match_mode":"any"}'

# Gợi ý cá nhân hóa
curl $BASE/api/recommendations?limit=5 \
  -H "Authorization: Bearer $TOKEN"
```
