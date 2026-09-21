# 🍳 Kế Hoạch Backend — Hệ Thống Gợi Ý & Công Thức Nấu Ăn Thông Minh
> **TVU 2026 · Dự án kiểm thử**
> Backend: Claude · Frontend/UI: Antigravity (toàn quyền thiết kế)
> Cập nhật lần cuối: 2026-09-21

---

## 📌 Nguyên tắc vận hành (đọc trước khi làm gì)

- **Backend = REST API JSON** — Claude xây, Antigravity gọi
- **Không UptimeRobot, không GitHub Actions ping** — server tự sleep khi không dùng, chấp nhận cold start
- **Tách Render account** — dự án này dùng account riêng, không đụng 750h của dự án chính
- **Tách Supabase project** — dùng project riêng biệt trong cùng account hoặc account khác
- **Frontend do Antigravity toàn quyền** — Claude không đụng HTML/CSS/JS, chỉ expose API sạch
- **Làm từng task nhỏ, không làm lớt phớt** — hoàn thành task trước mới sang task sau
- **Mọi thứ đọc từ `.env`** — không hardcode key nào trong code

---

## 🗺️ Tổng quan kiến trúc

```
[Antigravity Frontend]
        │  HTTP requests (JSON)
        ▼
[Flask REST API — Claude]
        │
        ├── /api/auth/...
        ├── /api/recipes/...
        ├── /api/search/...
        ├── /api/recommendations/...
        ├── /api/ratings/...
        ├── /api/meal-plans/...
        └── /api/admin/...
        │
        ▼
[Supabase PostgreSQL]     [Cloudinary]
```

---

## 📁 Cấu trúc thư mục dự án

```
nauAn-backend/
├── app/
│   ├── __init__.py          # App factory, đăng ký blueprints
│   ├── models/              # SQLAlchemy models (1 file per table group)
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── ingredient.py
│   │   ├── rating.py
│   │   └── meal_plan.py
│   ├── routes/              # Blueprint handlers
│   │   ├── auth.py
│   │   ├── recipes.py
│   │   ├── search.py
│   │   ├── recommendations.py
│   │   ├── ratings.py
│   │   ├── meal_plans.py
│   │   └── admin.py
│   ├── services/            # Business logic tách khỏi routes
│   │   ├── content_based.py
│   │   ├── collaborative.py
│   │   ├── ingredient_search.py
│   │   └── cloudinary_service.py
│   └── utils/
│       ├── response.py      # Helper format JSON response đồng nhất
│       └── decorators.py    # JWT decorators, role check
├── config.py                # Đọc .env, cấu hình app
├── app.py                   # Entry point
├── requirements.txt
├── Procfile                 # web: gunicorn app:app
├── .env                     # KHÔNG commit
├── .gitignore
└── README.md
```

---

## ⚙️ Contract API — Định dạng chuẩn

Mọi response đều theo format sau để Antigravity dễ handle:

```json
// Thành công
{
  "success": true,
  "data": { ... },
  "message": "OK"
}

// Thất bại
{
  "success": false,
  "error": "Mô tả lỗi rõ ràng",
  "code": 400
}

// Danh sách có phân trang
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 85,
    "total_pages": 8
  }
}
```

**Auth:** JWT token gửi trong header `Authorization: Bearer <token>`

**CORS:** Cho phép tất cả origin trong môi trường dev, thu hẹp khi deploy.

---

---

# 🔨 TASK LIST — Backend

> Mỗi task = 1 đơn vị công việc hoàn chỉnh, test được độc lập.
> Hoàn thành task → đánh dấu ✅ → mới sang task tiếp theo.

---

## PHASE 1 — Khung xương (Không có cái này, không làm được gì khác)

---

### TASK 1.1 — Khởi tạo dự án & cấu hình môi trường
**Mục tiêu:** Có 1 Flask app chạy được, kết nối được Supabase.

**Việc cần làm:**
- [ ] Tạo repo GitHub mới (private)
- [ ] Tạo virtualenv, install Flask, SQLAlchemy, psycopg2, python-dotenv, Flask-CORS
- [ ] Tạo `.gitignore` (bao gồm `.env`, `__pycache__`, `*.pyc`)
- [ ] Tạo `.env` với các biến:
  ```
  DATABASE_URL=postgresql://...supabase...
  SECRET_KEY=random_string_dai_30_ky_tu
  CLOUDINARY_CLOUD_NAME=
  CLOUDINARY_API_KEY=
  CLOUDINARY_API_SECRET=
  FLASK_ENV=development
  ```
- [ ] Viết `config.py` đọc `.env`
- [ ] Viết `app.py` — app factory cơ bản
- [ ] Test: `flask run` → `http://localhost:5000/api/health` trả về `{"status": "ok"}`
- [ ] Tạo Supabase project riêng (không dùng chung với dự án khác)
- [ ] Kết nối thử SQLAlchemy → Supabase thành công

**Output khi xong:** App chạy local, ping health check OK, kết nối DB OK.

---

### TASK 1.2 — Thiết kế & tạo Database Schema
**Mục tiêu:** Toàn bộ 12 bảng được tạo trên Supabase, đúng quan hệ.

**Các bảng cần tạo (theo thứ tự phụ thuộc):**

```sql
-- Nhóm 1: Độc lập
users
ingredients
tags

-- Nhóm 2: Phụ thuộc nhóm 1
user_preferences        (FK → users)
recipes                 (bảng trung tâm)

-- Nhóm 3: Quan hệ nhiều-nhiều
recipe_ingredients      (FK → recipes, ingredients)
recipe_tags             (FK → recipes, tags)
ingredient_substitutes  (FK → ingredients × 2)

-- Nhóm 4: User activity
steps                   (FK → recipes)
ratings                 (FK → users, recipes)
view_history            (FK → users, recipes)
meal_plans              (FK → users, recipes)
```

**Chi tiết từng bảng:**

```sql
users (id UUID PK, email UNIQUE, password_hash, full_name, role ENUM('user','admin'), created_at)

user_preferences (id, user_id FK, pref_type VARCHAR, pref_value VARCHAR)
-- pref_type: 'diet' | 'taste' | 'allergy' | 'serving_size'
-- pref_value: 'vegetarian' | 'spicy' | 'peanut' | '4'

ingredients (id, name UNIQUE, category VARCHAR, unit VARCHAR, emoji VARCHAR, calories_per_100g FLOAT)

tags (id, name UNIQUE, color VARCHAR)
-- color: hex code để Antigravity render badge màu

recipes (
  id, name, description, image_url, difficulty ENUM('easy','medium','hard'),
  cook_time_min INT, prep_time_min INT, servings INT,
  avg_rating FLOAT DEFAULT 0, rating_count INT DEFAULT 0,
  is_published BOOLEAN DEFAULT false, created_by FK → users,
  created_at, updated_at
)

recipe_ingredients (id, recipe_id FK, ingredient_id FK, quantity FLOAT, unit VARCHAR, is_optional BOOLEAN DEFAULT false)

recipe_tags (recipe_id FK, tag_id FK, PRIMARY KEY(recipe_id, tag_id))

steps (id, recipe_id FK, step_number INT, description TEXT, image_url VARCHAR, duration_min INT)

ratings (id, user_id FK, recipe_id FK, score INT CHECK(1-5), review_text TEXT, created_at, UNIQUE(user_id, recipe_id))

view_history (id, user_id FK, recipe_id FK, viewed_at TIMESTAMP, duration_sec INT)

meal_plans (id, user_id FK, week_start DATE, day_of_week INT(0-6), meal_type ENUM('breakfast','lunch','dinner'), recipe_id FK)

ingredient_substitutes (id, ingredient_id FK, substitute_id FK, note VARCHAR)
```

**Việc cần làm:**
- [ ] Viết SQLAlchemy models cho tất cả bảng
- [ ] Tạo migration (dùng `flask db init/migrate/upgrade` với Flask-Migrate)
- [ ] Chạy migration lên Supabase
- [ ] Verify bảng đã tạo đúng trong Supabase dashboard

**Output khi xong:** 12 bảng tồn tại trên Supabase với đúng quan hệ FK.

---

### TASK 1.3 — Auth API (Đăng ký / Đăng nhập / Phân quyền)
**Mục tiêu:** Antigravity có thể đăng ký, đăng nhập, nhận JWT token.

**Endpoints:**
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me          (cần token)
POST /api/auth/logout      (client xóa token, server blacklist optional)
```

**Chi tiết:**

```
POST /api/auth/register
Body: { "email": "...", "password": "...", "full_name": "..." }
- Validate email format, password >= 8 ký tự
- Hash password bằng bcrypt
- Tạo user với role = 'user'
- Trả về JWT token + user info (không có password)

POST /api/auth/login
Body: { "email": "...", "password": "..." }
- Verify password hash
- Trả về JWT token (expire 7 ngày) + user info

GET /api/auth/me
Header: Authorization: Bearer <token>
- Decode token, trả về user hiện tại
```

**Packages cần thêm:** `Flask-JWT-Extended`, `bcrypt`

**Việc cần làm:**
- [ ] Install Flask-JWT-Extended, bcrypt
- [ ] Viết `utils/decorators.py`: `@jwt_required`, `@admin_required`
- [ ] Viết `routes/auth.py` với 3 endpoints
- [ ] Test: register → nhận token → dùng token gọi /me → nhận user info
- [ ] Test: sai password → trả 401 đúng format

**Output khi xong:** Postman/curl gọi được register, login, nhận token hợp lệ.

---

---

## PHASE 2 — Core Content (Dữ liệu công thức)

---

### TASK 2.1 — Ingredients & Tags API
**Mục tiêu:** Có API để seed và lấy danh sách nguyên liệu, tags.

**Endpoints:**
```
GET  /api/ingredients              (public — Antigravity dùng cho search filter)
GET  /api/ingredients?category=rau_cu
GET  /api/tags                     (public)
POST /api/admin/ingredients        (admin only)
POST /api/admin/tags               (admin only)
```

**Chi tiết response nguyên liệu:**
```json
{
  "id": 1,
  "name": "Cà rốt",
  "category": "rau_cu",
  "unit": "g",
  "emoji": "🥕",
  "calories_per_100g": 41
}
```

**Việc cần làm:**
- [ ] Viết routes cho ingredients và tags
- [ ] Viết script seed data: `scripts/seed_ingredients.py` (~100 nguyên liệu với emoji)
- [ ] Viết script seed tags: cay, chay, nhanh, tiệc, ăn sáng, ít dầu, dễ nấu, Miền Nam, Miền Bắc, Miền Trung...
- [ ] Chạy seed lên Supabase
- [ ] Test GET /api/ingredients → list đúng

**Output khi xong:** 100 nguyên liệu + ~15 tags tồn tại trong DB, API trả về đúng.

---

### TASK 2.2 — Recipes CRUD API (Admin)
**Mục tiêu:** Admin tạo/sửa/xóa công thức đầy đủ (tên, mô tả, ảnh URL, bước nấu, nguyên liệu, tags).

**Endpoints:**
```
GET    /api/recipes                   (public, có phân trang + filter)
GET    /api/recipes/:id               (public)
POST   /api/admin/recipes             (admin — tạo mới)
PUT    /api/admin/recipes/:id         (admin — cập nhật)
DELETE /api/admin/recipes/:id         (admin — xóa)
POST   /api/admin/recipes/:id/image   (admin — upload ảnh lên Cloudinary)
```

**Chi tiết GET /api/recipes:**
```
Query params:
  ?page=1&limit=12
  ?tag=cay
  ?difficulty=easy
  ?q=bún bò           (tìm theo tên)
  ?published=true

Response data mỗi recipe (list view):
{
  "id": 1,
  "name": "Bún bò Huế",
  "image_url": "https://res.cloudinary.com/.../w_400,h_300,c_fill/bun-bo.jpg",
  "difficulty": "medium",
  "cook_time_min": 90,
  "avg_rating": 4.3,
  "rating_count": 12,
  "tags": ["cay", "Miền Trung"],
  "ingredient_count": 15
}
```

**Chi tiết GET /api/recipes/:id (detail view):**
```json
{
  "id": 1,
  "name": "Bún bò Huế",
  "description": "...",
  "image_url": "...",
  "difficulty": "medium",
  "cook_time_min": 90,
  "prep_time_min": 30,
  "servings": 4,
  "avg_rating": 4.3,
  "rating_count": 12,
  "tags": [{"id": 1, "name": "cay", "color": "#FF4444"}],
  "ingredients": [
    {
      "ingredient_id": 5,
      "name": "Thịt bò",
      "emoji": "🥩",
      "quantity": 500,
      "unit": "g",
      "is_optional": false
    }
  ],
  "steps": [
    {
      "step_number": 1,
      "description": "Luộc xương trong 30 phút...",
      "image_url": null,
      "duration_min": 30
    }
  ]
}
```

**POST /api/admin/recipes body:**
```json
{
  "name": "Bún bò Huế",
  "description": "...",
  "difficulty": "medium",
  "cook_time_min": 90,
  "prep_time_min": 30,
  "servings": 4,
  "tag_ids": [1, 3],
  "ingredients": [
    {"ingredient_id": 5, "quantity": 500, "unit": "g", "is_optional": false}
  ],
  "steps": [
    {"step_number": 1, "description": "...", "duration_min": 30}
  ]
}
```

**Việc cần làm:**
- [ ] Viết `routes/recipes.py` với tất cả endpoints
- [ ] Viết `services/cloudinary_service.py` — nhận file, upload, trả URL transformation
- [ ] Logic filter + pagination trong GET /api/recipes
- [ ] Admin guard trên POST/PUT/DELETE
- [ ] Test: tạo công thức → lấy detail → update → xóa
- [ ] Test: filter theo tag, difficulty, search tên

**Output khi xong:** Admin có thể CRUD đầy đủ 1 công thức qua API.

---

### TASK 2.3 — Seed Dataset (~80 món ăn)
**Mục tiêu:** Có đủ data để ML hoạt động và demo được.

**Danh sách ưu tiên seed (theo độ phổ biến):**

Nhóm miền Nam (30 món):
- Hủ tiếu Nam Vang, Cơm tấm sườn bì chả, Bánh mì thịt, Canh chua cá lóc,
  Thịt kho tàu, Lẩu mắm, Bánh xèo, Gỏi cuốn, Chả giò, Bún mắm,
  Cơm chiên dương châu, Canh khổ qua, Mì Quảng, Bánh canh cua,
  Lẩu thái, Cá kho tộ, Thịt bò lúc lắc, Gà chiên mắm, Tôm rang muối,
  Cà ri gà, Bún thịt nướng, Chè bà ba, Bánh bèo, Súp cua, Heo quay,
  Vịt nấu chao, Ếch xào sả ớt, Cháo lòng, Bánh tằm bì, Nem nướng

Nhóm miền Bắc (25 món):
- Phở bò, Phở gà, Bún chả Hà Nội, Bún thang, Bánh cuốn, Chả cá Lã Vọng,
  Bún ốc, Cháo sườn, Giò thủ, Nem Hà Nội (nem rán), Xôi xéo,
  Bún riêu, Miến gà, Canh bún, Thịt đông, Ô mai, Cơm rang dưa bò,
  Bánh gối, Bánh đúc nóng, Lẩu cua đồng, Xôi gấc, Chè hạt sen,
  Rươi rang, Bún bò Nam Bộ (dù tên có Nam Bộ nhưng phổ biến Bắc), Ốc luộc

Nhóm miền Trung (25 món):
- Bún bò Huế, Bánh bèo Huế, Bánh nậm, Bánh lọc, Cơm hến,
  Bún thịt nướng Huế, Mì Quảng Đà Nẵng, Bánh mì Hội An, Cao lầu,
  Bánh đập, Cơm gà Hội An, Bánh tráng cuốn thịt heo, Bê thui,
  Mắm tôm chua, Chè bắp Hội An, Bánh căn, Nem lụi, Bánh ướt,
  Tré Huế, Vả trộn, Cơm âm phủ, Bún sứa, Bánh ram ít, Bánh bột lọc trần, Chả ram tôm đất

**Script seed:** Viết `scripts/seed_recipes.py` nhập data từ Python dict/JSON.

**Mỗi món cần có đầy đủ:**
- Tên, mô tả ngắn (~2 câu)
- Nguyên liệu với số lượng (ít nhất 5 nguyên liệu/món)
- Độ khó, thời gian nấu
- Tags (ít nhất 2 tags/món)
- Các bước nấu cơ bản (ít nhất 3 bước/món)
- `image_url` để null trước, cập nhật sau khi có ảnh Cloudinary

**Việc cần làm:**
- [ ] Tạo file data `scripts/data/recipes_data.py` (~80 món đầy đủ fields)
- [ ] Viết `scripts/seed_recipes.py` đọc data và insert vào DB
- [ ] Chạy seed — verify trên Supabase
- [ ] Tạo tài khoản admin thủ công trong DB
- [ ] Test: GET /api/recipes → trả về 80 món, phân trang đúng

**Output khi xong:** 80 món ăn đầy đủ trong DB, ML có đủ data để train.

---

---

## PHASE 3 — Tính năng tìm kiếm theo nguyên liệu

---

### TASK 3.1 — Search by Ingredients API
**Mục tiêu:** Người dùng chọn nguyên liệu, nhận danh sách công thức nấu được.

**Đây là tính năng kỹ thuật đặc trưng nhất — cần làm cẩn thận.**

**Endpoint:**
```
POST /api/search/by-ingredients
Body: {
  "ingredient_ids": [1, 5, 12, 23],
  "match_mode": "any"   // "any" = có ít nhất 1, "all" = phải có tất cả
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "recipe_id": 15,
      "recipe_name": "Trứng chiên cà chua",
      "image_url": "...",
      "difficulty": "easy",
      "cook_time_min": 15,
      "avg_rating": 4.5,
      "matched_ingredients": ["Trứng 🥚", "Cà chua 🍅"],
      "matched_count": 2,
      "total_required": 5,
      "match_percent": 40,
      "missing_ingredients": ["Hành lá 🌿", "Dầu ăn 🫚", "Muối 🧂"]
    }
  ]
}
```
*Sắp xếp theo `matched_count` DESC — món dùng nhiều nguyên liệu người dùng có nhất lên đầu.*

**Logic SQL:**
```sql
-- Core query
SELECT
  r.id,
  r.name,
  COUNT(ri.ingredient_id) AS matched_count,
  (SELECT COUNT(*) FROM recipe_ingredients WHERE recipe_id = r.id AND is_optional = false) AS total_required
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
WHERE ri.ingredient_id = ANY(:ingredient_ids)
  AND r.is_published = true
GROUP BY r.id
ORDER BY matched_count DESC;
```

**Việc cần làm:**
- [ ] Viết `services/ingredient_search.py` với hàm `search_by_ingredients(ingredient_ids, match_mode)`
- [ ] Tính `match_percent`, lấy `missing_ingredients` cho từng kết quả
- [ ] Viết route `POST /api/search/by-ingredients`
- [ ] Test: chọn [trứng, cà chua] → trả về các món dùng 2 nguyên liệu này, sort đúng

**Output khi xong:** Chọn nguyên liệu → nhận danh sách công thức hợp lệ, sort đúng thứ tự.

---

### TASK 3.2 — Ingredient Substitutes API
**Mục tiêu:** Tra cứu nguyên liệu thay thế khi thiếu một nguyên liệu.

**Endpoint:**
```
GET /api/ingredients/:id/substitutes
```

**Response:**
```json
{
  "ingredient": {"id": 10, "name": "Bơ", "emoji": "🧈"},
  "substitutes": [
    {"id": 11, "name": "Dầu ăn", "emoji": "🫚", "note": "Dùng 3/4 lượng bơ"},
    {"id": 12, "name": "Margarine", "emoji": "🧈", "note": "Tỷ lệ 1:1"}
  ]
}
```

**Việc cần làm:**
- [ ] Viết route `GET /api/ingredients/:id/substitutes`
- [ ] Seed dữ liệu substitutes vào bảng `ingredient_substitutes` (~30 cặp phổ biến):
  - Bơ → Dầu ăn, Margarine
  - Nước mắm → Muối + Đường
  - Sữa tươi → Sữa đặc pha loãng, Nước cốt dừa
  - Đường → Mật ong (giảm 25%)
  - Bột mì → Bột gạo (cho món gluten-free)
  - ...
- [ ] Test GET → trả về substitutes đúng

**Output khi xong:** Gọi API với ingredient_id → nhận danh sách thay thế.

---

---

## PHASE 4 — Recommendation System (ML)

---

### TASK 4.1 — User Preferences & Profile API
**Mục tiêu:** Người dùng lưu sở thích, hệ thống lưu vào DB cho ML dùng.

**Endpoints:**
```
GET  /api/users/me/preferences       (cần token)
POST /api/users/me/preferences       (lưu/update sở thích)
```

**Body POST:**
```json
{
  "preferences": [
    {"pref_type": "diet", "pref_value": "vegetarian"},
    {"pref_type": "taste", "pref_value": "spicy"},
    {"pref_type": "taste", "pref_value": "salty"},
    {"pref_type": "allergy", "pref_value": "peanut"},
    {"pref_type": "serving_size", "pref_value": "2"}
  ]
}
```

**Logic:** Upsert — xóa preferences cũ của user, insert batch mới.

**Việc cần làm:**
- [ ] Viết routes cho preferences
- [ ] Test: lưu preferences → GET lại → đúng

**Output khi xong:** Người dùng có thể cập nhật sở thích, data lưu vào DB.

---

### TASK 4.2 — Rating API & View History
**Mục tiêu:** Thu thập feedback để làm input cho ML.

**Endpoints:**
```
POST /api/ratings                    (cần token)
GET  /api/recipes/:id/ratings        (public)
POST /api/view-history               (cần token — gọi tự động khi xem recipe)
```

**POST /api/ratings body:**
```json
{
  "recipe_id": 15,
  "score": 4,
  "review_text": "Ngon, nhưng hơi mặn một chút"
}
```

**Logic sau khi insert rating:**
- Recalculate `avg_rating` và `rating_count` trên bảng `recipes`
- Trigger flag "cần re-train ML" (đơn giản: set column `ml_stale = true` trong bảng settings)

**Việc cần làm:**
- [ ] Viết routes cho ratings (POST, GET list)
- [ ] Auto-update avg_rating trên recipes sau mỗi rating mới
- [ ] Viết route POST /api/view-history (nhẹ, fire-and-forget)
- [ ] Test: rate món → avg_rating trên recipe cập nhật đúng

**Output khi xong:** Người dùng rate được, avg_rating cập nhật realtime.

---

### TASK 4.3 — Content-Based Filtering (CBF)
**Mục tiêu:** Gợi ý món ăn dựa trên sở thích người dùng — không cần data rating.

**Cơ chế:**
1. Mỗi recipe được vector hóa từ tags + difficulty + cook_time
2. User profile được vector hóa từ preferences
3. Cosine Similarity tính độ tương đồng recipe-user
4. Top N recipe tương đồng nhất → gợi ý

**File:** `services/content_based.py`

```python
# Pseudocode cấu trúc
def build_recipe_features(recipes) -> DataFrame:
    # Tạo feature matrix: mỗi row = 1 recipe, mỗi col = 1 tag/feature
    # Dùng TfidfVectorizer hoặc one-hot encoding

def build_user_vector(user_preferences) -> array:
    # Convert preferences sang vector cùng chiều với recipe features

def compute_cbf_recommendations(user_id, top_n=10) -> list:
    # 1. Lấy user preferences từ DB
    # 2. Build user vector
    # 3. Compute cosine_similarity(user_vector, recipe_matrix)
    # 4. Sort, filter bỏ món user đã xem/rate
    # 5. Return top_n recipe_ids
    
def cache_recommendations(user_id, recipe_ids):
    # Lưu kết quả vào bảng recommendation_cache trong DB
```

**Bảng cache cần thêm:**
```sql
recommendation_cache (
  user_id UUID FK,
  recipe_id INT FK,
  score FLOAT,
  algorithm VARCHAR,  -- 'cbf' | 'cf' | 'hybrid'
  generated_at TIMESTAMP,
  PRIMARY KEY(user_id, recipe_id)
)
```

**Endpoint:**
```
GET /api/recommendations?limit=10    (cần token)
```

**Logic endpoint:**
1. Check cache còn fresh không (< 1 giờ)
2. Nếu stale → chạy lại CBF → update cache
3. Trả về từ cache

**Việc cần làm:**
- [ ] Tạo bảng `recommendation_cache` trên Supabase
- [ ] Install scikit-learn
- [ ] Viết `services/content_based.py` đầy đủ
- [ ] Viết route GET /api/recommendations
- [ ] Test: user có preferences → gọi /recommendations → nhận list hợp lý
- [ ] Test: user mới (chưa có preferences) → trả về popular recipes thay thế

**Output khi xong:** Người dùng có preferences → nhận gợi ý phù hợp sở thích.

---

### TASK 4.4 — Collaborative Filtering (CF) — Làm sau khi có đủ ratings
**Mục tiêu:** Gợi ý dựa trên người dùng có sở thích tương tự.

> ⚠️ **Điều kiện bắt đầu task này:** Phải có ít nhất 200 ratings thật hoặc synthetic trong DB.

**Cơ chế:**
1. Xây ma trận User × Recipe (giá trị = rating score)
2. Dùng SVD (Matrix Factorization) từ scikit-surprise
3. Predict rating của user với những món chưa xem
4. Top N món có predicted rating cao nhất → gợi ý

**File:** `services/collaborative.py`

```python
def train_cf_model(ratings_df) -> model:
    # Dùng scikit-surprise SVD
    # Train trên toàn bộ ratings hiện có
    # Serialize model với joblib

def compute_cf_recommendations(user_id, top_n=10) -> list:
    # Load model từ disk (hoặc re-train nếu stale)
    # Predict cho tất cả recipes user chưa xem
    # Return top_n
```

**Script seed synthetic ratings:**
```python
# scripts/seed_ratings.py
# Tạo ~500 ratings giả lập hợp lý:
# - User "thích cay" → rate cao các món cay
# - User "ăn chay" → rate cao các món chay
# Giúp CF hoạt động khi demo
```

**Cập nhật endpoint /api/recommendations:**
- Nếu `count(ratings) >= 200` → dùng hybrid CBF+CF (trọng số 60/40)
- Nếu < 200 → dùng CBF thuần

**Việc cần làm:**
- [ ] Install scikit-surprise
- [ ] Viết script seed 500 synthetic ratings
- [ ] Viết `services/collaborative.py`
- [ ] Update logic hybrid trong GET /api/recommendations
- [ ] Test: 2 user khác sở thích → nhận gợi ý khác nhau

**Output khi xong:** Gợi ý chính xác hơn, kết hợp CBF + CF.

---

---

## PHASE 5 — Tính năng mở rộng

---

### TASK 5.1 — Meal Plan API
**Mục tiêu:** Người dùng lập thực đơn theo tuần, xuất danh sách nguyên liệu cần mua.

**Endpoints:**
```
GET    /api/meal-plans?week_start=2026-09-21   (cần token)
POST   /api/meal-plans                          (thêm món vào lịch)
DELETE /api/meal-plans/:id                      (xóa khỏi lịch)
GET    /api/meal-plans/shopping-list?week_start=2026-09-21   (tổng hợp nguyên liệu)
```

**POST body:**
```json
{
  "week_start": "2026-09-21",
  "day_of_week": 1,
  "meal_type": "lunch",
  "recipe_id": 15
}
```

**GET shopping-list response:**
```json
{
  "week_start": "2026-09-21",
  "ingredients": [
    {"name": "Thịt bò", "emoji": "🥩", "total_quantity": 1000, "unit": "g"},
    {"name": "Cà rốt", "emoji": "🥕", "total_quantity": 500, "unit": "g"}
  ]
}
```
*Tổng hợp bằng cách cộng quantity của tất cả recipes trong tuần, nhóm theo ingredient.*

**Việc cần làm:**
- [ ] Viết routes meal-plans
- [ ] Logic aggregate shopping list (GROUP BY ingredient, SUM quantity)
- [ ] Test: thêm 3 món vào lịch → GET shopping list → tổng hợp đúng

---

### TASK 5.2 — Admin Stats API (Đơn giản)
**Mục tiêu:** Antigravity hiển thị vài con số thống kê cho admin dashboard.

**Endpoint:**
```
GET /api/admin/stats     (admin only)
```

**Response:**
```json
{
  "total_recipes": 80,
  "total_users": 45,
  "total_ratings": 312,
  "top_rated_recipes": [...],
  "most_viewed_recipes": [...],
  "recent_ratings": [...]
}
```

**Việc cần làm:**
- [ ] Viết route admin stats với các query đơn giản
- [ ] Test: gọi với admin token → nhận stats đúng

---

### TASK 5.3 — Saved Recipes (Yêu thích)
**Mục tiêu:** Người dùng lưu công thức yêu thích.

**Bảng thêm:**
```sql
saved_recipes (user_id FK, recipe_id FK, saved_at TIMESTAMP, PRIMARY KEY(user_id, recipe_id))
```

**Endpoints:**
```
GET    /api/users/me/saved          (cần token)
POST   /api/users/me/saved          body: {"recipe_id": 15}
DELETE /api/users/me/saved/:recipe_id
```

---

---

## PHASE 6 — Deploy & Hoàn thiện

---

### TASK 6.1 — Chuẩn bị Deploy lên Render
**Mục tiêu:** App chạy được trên Render với đầy đủ tính năng.

**Checklist:**
- [ ] Tạo `Procfile`: `web: gunicorn app:app`
- [ ] Update `requirements.txt`: `pip freeze > requirements.txt`
- [ ] Verify không có hardcode key nào trong code
- [ ] Test kết nối Supabase production từ local với URL production
- [ ] Tạo Render account **riêng** (email khác với dự án chính)
- [ ] Deploy lên Render, set Environment Variables đầy đủ
- [ ] Test tất cả endpoints trên production URL
- [ ] **KHÔNG** setup UptimeRobot → chấp nhận cold start

**Output khi xong:** API chạy trên `https://xxx.onrender.com`, tất cả endpoints hoạt động.

---

### TASK 6.2 — API Documentation cho Antigravity
**Mục tiêu:** Antigravity có đủ thông tin để gọi API mà không cần hỏi.

**Tạo file `API_DOCS.md`** liệt kê đầy đủ:
- Base URL
- Auth flow (register → login → gửi token trong header)
- Tất cả endpoints với method, params, request body, response mẫu
- Error codes và ý nghĩa
- Danh sách emoji cho từng nguyên liệu (để Antigravity dùng nhất quán)

**Việc cần làm:**
- [ ] Viết `API_DOCS.md` đầy đủ
- [ ] Share cho Antigravity

---

---

## 📊 Tóm tắt tiến độ

| Phase | Task | Ưu tiên | Phụ thuộc |
|---|---|---|---|
| 1 | 1.1 Khởi tạo dự án | 🔴 Bắt buộc | — |
| 1 | 1.2 Database Schema | 🔴 Bắt buộc | 1.1 |
| 1 | 1.3 Auth API | 🔴 Bắt buộc | 1.2 |
| 2 | 2.1 Ingredients & Tags | 🔴 Bắt buộc | 1.2 |
| 2 | 2.2 Recipes CRUD | 🔴 Bắt buộc | 2.1 |
| 2 | 2.3 Seed 80 món | 🔴 Bắt buộc | 2.2 |
| 3 | 3.1 Search by Ingredients | 🔴 Bắt buộc | 2.3 |
| 3 | 3.2 Ingredient Substitutes | 🟡 Nên có | 2.1 |
| 4 | 4.1 User Preferences | 🔴 Bắt buộc | 1.3 |
| 4 | 4.2 Ratings & View History | 🔴 Bắt buộc | 2.2 |
| 4 | 4.3 Content-Based Filtering | 🔴 Bắt buộc | 4.1 + 2.3 |
| 4 | 4.4 Collaborative Filtering | 🟡 Nên có | 4.2 (cần 200+ ratings) |
| 5 | 5.1 Meal Plan | 🟡 Nên có | 2.2 |
| 5 | 5.2 Admin Stats | 🟢 Tùy chọn | 2.2 |
| 5 | 5.3 Saved Recipes | 🟢 Tùy chọn | 1.3 |
| 6 | 6.1 Deploy Render | 🔴 Bắt buộc | Tất cả phase 1-4 |
| 6 | 6.2 API Docs | 🔴 Bắt buộc | 6.1 |

---

## 🔗 Thông tin cần sync với Antigravity

Trước khi Antigravity bắt đầu code frontend, cần thống nhất:

1. **Base URL** của API (sau khi deploy)
2. **Token storage** — Antigravity lưu JWT ở đâu (localStorage, cookie)
3. **Image display** — Antigravity dùng Cloudinary transformation URL trực tiếp từ `image_url` field
4. **Pagination** — Antigravity xử lý `pagination.total_pages` để render số trang
5. **Error handling** — Antigravity hiển thị `error` field khi `success: false`
6. **Emoji nguyên liệu** — Lấy từ field `emoji` trong response, không hardcode phía frontend

---

## 📦 Dependencies tổng hợp

```txt
Flask
Flask-CORS
Flask-JWT-Extended
Flask-Migrate
SQLAlchemy
psycopg2-binary
python-dotenv
bcrypt
cloudinary
scikit-learn
scikit-surprise
pandas
numpy
joblib
gunicorn
```

---

*File này là kế hoạch sống — cập nhật khi có thay đổi. Mỗi task hoàn thành đánh dấu [x] vào checkbox.*
