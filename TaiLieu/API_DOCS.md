# 📖 API Documentation — Hệ Thống Nấu Ăn Thông Minh

> **Version:** 1.0  
> **Backend:** Flask REST API (Python)  
> **Database:** Supabase PostgreSQL  
> **Image Storage:** Cloudinary  
> **Auth:** JWT Bearer Token (7 ngày)  

---

## 🌐 Base URL

| Môi trường | URL |
|---|---|
| Local Development | `http://localhost:5000` |
| Production (Render) | `https://[app-name].onrender.com` *(cập nhật sau khi deploy)* |

---

## 🔐 Authentication

Tất cả endpoint có ghi `(cần token)` đều yêu cầu header sau:

```
Authorization: Bearer <access_token>
```

**Quy trình:**
1. `POST /api/auth/register` hoặc `POST /api/auth/login` → nhận `token`
2. Lưu token (localStorage hoặc memory)
3. Gửi token trong mọi request cần xác thực

---

## 📐 Response Format Chuẩn

Mọi response đều tuân thủ format thống nhất:

```json
// Thành công (single item)
{
  "success": true,
  "data": { ... },
  "message": "Mô tả kết quả (optional)"
}

// Thành công (danh sách có phân trang)
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

// Thất bại / lỗi
{
  "success": false,
  "error": "Mô tả lỗi chi tiết",
  "code": 400
}
```

**HTTP Status Codes:**
| Code | Ý nghĩa |
|---|---|
| 200 | OK |
| 201 | Created thành công |
| 400 | Bad Request (body sai) |
| 401 | Unauthorized (thiếu/sai token) |
| 403 | Forbidden (không đủ quyền admin) |
| 404 | Not Found |
| 409 | Conflict (đã tồn tại) |
| 500 | Internal Server Error |

---

## 🔑 AUTHENTICATION API

### `POST /api/auth/register` — Đăng ký
```json
// Request Body
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Nguyễn Văn A"
}

// Response 201
{
  "success": true,
  "data": {
    "token": "eyJ...",
    "user": {
      "id": "uuid-...",
      "email": "user@example.com",
      "full_name": "Nguyễn Văn A",
      "role": "user",
      "created_at": "2026-09-21T11:00:00Z"
    }
  },
  "message": "Đăng ký thành công"
}
```

### `POST /api/auth/login` — Đăng nhập
```json
// Request Body
{
  "email": "user@example.com",
  "password": "password123"
}

// Response 200
{
  "success": true,
  "data": {
    "token": "eyJ...",
    "user": { ... }
  }
}
```

### `GET /api/auth/me` — Thông tin user hiện tại *(cần token)*
```json
// Response 200
{
  "success": true,
  "data": {
    "id": "uuid-...",
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "role": "user",
    "preferences": [
      { "pref_type": "taste", "pref_value": "spicy" }
    ]
  }
}
```

### `POST /api/auth/logout` — Đăng xuất *(cần token)*
```json
// Response 200
{ "success": true, "message": "Đăng xuất thành công" }
```

---

## 👤 USER PREFERENCES API

### `GET /api/auth/users/me/preferences` *(cần token)*
```json
// Response 200
{
  "success": true,
  "data": [
    { "pref_type": "diet", "pref_value": "vegetarian" },
    { "pref_type": "taste", "pref_value": "spicy" }
  ]
}
```

### `POST /api/auth/users/me/preferences` *(cần token)*

> ⚠️ **Upsert:** Thao tác này XÓA toàn bộ sở thích cũ và thay bằng danh sách mới.

```json
// Request Body
{
  "preferences": [
    { "pref_type": "diet",         "pref_value": "vegetarian" },
    { "pref_type": "taste",        "pref_value": "spicy" },
    { "pref_type": "taste",        "pref_value": "salty" },
    { "pref_type": "allergy",      "pref_value": "peanut" },
    { "pref_type": "serving_size", "pref_value": "2" }
  ]
}
```

**Giá trị hợp lệ:**
| pref_type | pref_value |
|---|---|
| `diet` | `vegetarian`, `vegan`, `quick` |
| `taste` | `spicy`, `sweet`, `salty`, `healthy` |
| `allergy` | `peanut`, `seafood`, `gluten` |
| `serving_size` | `"1"`, `"2"`, `"4"`, `"6"` |

---

## 🍽️ RECIPES API

### `GET /api/recipes` — Danh sách công thức (public)
```
Query Parameters:
  ?page=1          (mặc định 1)
  ?limit=12        (mặc định 12, tối đa 50)
  ?tag=cay         (lọc theo tag name)
  ?difficulty=easy (easy | medium | hard)
  ?region=mien_nam (mien_nam | mien_bac | mien_trung | quoc_te)
  ?q=bún bò        (tìm theo tên công thức)
  ?published=true  (mặc định true)
```

```json
// Response 200
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Bún bò Huế",
      "image_url": "https://res.cloudinary.com/xxx/...",
      "difficulty": "hard",
      "cook_time_min": 180,
      "prep_time_min": 30,
      "servings": 6,
      "avg_rating": 4.3,
      "rating_count": 12,
      "region": "mien_trung",
      "tags": ["Miền Trung", "cay", "mặn"],
      "ingredient_count": 10,
      "is_published": true
    }
  ],
  "pagination": { "page": 1, "limit": 12, "total": 80, "total_pages": 7 }
}
```

### `GET /api/recipes/:id` — Chi tiết công thức (public)
```json
// Response 200
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Bún bò Huế",
    "description": "Bún bò Huế đậm đà...",
    "image_url": "https://res.cloudinary.com/...",
    "difficulty": "hard",
    "cook_time_min": 180,
    "prep_time_min": 30,
    "servings": 6,
    "avg_rating": 4.3,
    "rating_count": 12,
    "region": "mien_trung",
    "is_published": true,
    "tags": [
      { "id": 3, "name": "Miền Trung", "color": "#AB47BC" }
    ],
    "ingredients": [
      {
        "ingredient_id": 5,
        "name": "Thịt bò",
        "emoji": "🥩",
        "quantity": 400,
        "unit": "g",
        "is_optional": false
      }
    ],
    "steps": [
      {
        "step_number": 1,
        "description": "Hầm xương bò...",
        "image_url": null,
        "duration_min": 180
      }
    ]
  }
}
```

### `POST /api/admin/recipes` — Tạo công thức *(admin)*
```json
// Request Body
{
  "name": "Tên món ăn",
  "description": "Mô tả ngắn...",
  "difficulty": "medium",
  "cook_time_min": 60,
  "prep_time_min": 20,
  "servings": 4,
  "region": "mien_nam",
  "tag_ids": [1, 3],
  "ingredients": [
    { "ingredient_id": 5, "quantity": 500, "unit": "g", "is_optional": false }
  ],
  "steps": [
    { "step_number": 1, "description": "...", "duration_min": 30 }
  ]
}
```

### `PUT /api/admin/recipes/:id` — Cập nhật công thức *(admin)*
> Body giống POST, chỉ gửi fields muốn thay đổi.

### `DELETE /api/admin/recipes/:id` — Xóa công thức *(admin)*
```json
{ "success": true, "message": "Đã xóa thành công" }
```

### `POST /api/admin/recipes/:id/image` — Upload ảnh *(admin)*
```
Content-Type: multipart/form-data
Body: file (image file)
```
```json
// Response 200
{
  "success": true,
  "data": {
    "image_url": "https://res.cloudinary.com/.../w_800,h_600,c_fill/...",
    "thumbnail_url": "https://res.cloudinary.com/.../w_400,h_300,c_fill/..."
  }
}
```

### `POST /api/admin/recipes/:id/publish` — Toggle Published *(admin)*
```json
{ "success": true, "data": { "is_published": true }, "message": "Công thức đã xuất bản" }
```

---

## 🥕 INGREDIENTS & TAGS API

### `GET /api/ingredients` — Danh sách nguyên liệu (public)
```
Query: ?category=rau_cu  ?q=cà  ?page=1  ?limit=100
```

**Danh sách categories:**
`rau_cu` | `thit` | `hai_san` | `gia_vi` | `bot_duong` | `trai_cay` | `sua_trung` | `do_kho`

```json
// Response 200
{
  "success": true,
  "data": [
    { "id": 1, "name": "Cà rốt", "category": "rau_cu", "unit": "g", "emoji": "🥕", "calories_per_100g": 41 }
  ]
}
```

### `GET /api/ingredients/:id` — Chi tiết nguyên liệu (public)
```json
{ "success": true, "data": { "id": 1, "name": "Cà rốt", ... } }
```

### `GET /api/ingredients/:id/substitutes` — Nguyên liệu thay thế (public)
```json
{
  "success": true,
  "data": {
    "ingredient": { "id": 10, "name": "Bơ lạt", "emoji": "🧈" },
    "substitutes": [
      { "id": 11, "name": "Dầu ăn", "emoji": "🫙", "note": "Dùng 3/4 lượng bơ" }
    ]
  }
}
```

### `GET /api/tags` — Danh sách tags (public)
```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "cay", "color": "#FF4444" },
    { "id": 2, "name": "chay", "color": "#4CAF50" }
  ]
}
```

---

## 🔍 SEARCH API

### `POST /api/search/by-ingredients` — Tìm món theo nguyên liệu (public)
```json
// Request Body
{
  "ingredient_ids": [1, 5, 12, 23],
  "match_mode": "any"
}
```

- `match_mode: "any"` → Trả về món dùng ít nhất 1 nguyên liệu trong danh sách
- `match_mode: "all"` → Chỉ trả về món mà tất cả nguyên liệu bắt buộc đều có trong danh sách

```json
// Response 200
{
  "success": true,
  "data": [
    {
      "recipe_id": 15,
      "recipe_name": "Trứng chiên cà chua",
      "image_url": "...",
      "difficulty": "easy",
      "cook_time_min": 10,
      "avg_rating": 4.5,
      "tags": ["dễ nấu", "nhanh"],
      "matched_ingredients": ["Trứng gà 🥚", "Cà chua 🍅"],
      "matched_count": 2,
      "total_required": 5,
      "match_percent": 40.0,
      "missing_ingredients": ["Hành lá 🌿", "Dầu ăn 🫙", "Muối 🧂"]
    }
  ]
}
```
> 📌 Kết quả được sắp xếp theo `matched_count` giảm dần.

---

## ⭐ RATINGS API

### `POST /api/ratings` — Đánh giá công thức *(cần token)*
```json
// Request Body
{
  "recipe_id": 15,
  "score": 4,
  "review_text": "Ngon, nhưng hơi mặn một chút"
}
```
> ⚠️ Mỗi user chỉ rate 1 lần/recipe. Rate lại sẽ **cập nhật** rating cũ.  
> Sau khi rate, `avg_rating` và `rating_count` của recipe được cập nhật tự động.

### `GET /api/recipes/:id/ratings` — Danh sách đánh giá (public)
```
Query: ?page=1  ?limit=10
```
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": "uuid-...",
      "recipe_id": 15,
      "score": 4,
      "review_text": "Ngon!",
      "created_at": "2026-09-21T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

### `POST /api/view-history` — Ghi nhận lịch sử xem *(cần token)*
> 🔥 Fire-and-forget — gọi tự động khi user mở trang chi tiết recipe.

```json
// Request Body
{
  "recipe_id": 15,
  "duration_sec": 120
}
```

---

## 🤖 RECOMMENDATIONS API

### `GET /api/recommendations` *(cần token)*
```
Query: ?limit=10  ?force_refresh=false
```

**Logic thuật toán:**
- Có `preferences` + `>= 200 ratings` trong DB → **Hybrid CBF 60% + CF 40%**
- Có `preferences` + `< 200 ratings` → **Content-Based Filtering (CBF)**
- Không có `preferences` (user mới) → **Popular recipes** (cold-start fallback)
- Cache TTL: **1 giờ** (dùng `force_refresh=true` để tính lại ngay)

```json
// Response 200
{
  "success": true,
  "data": [
    {
      "id": 7,
      "name": "Bún bò Huế",
      "image_url": "...",
      "difficulty": "hard",
      "cook_time_min": 180,
      "avg_rating": 4.5,
      "tags": ["Miền Trung", "cay"],
      ...
    }
  ],
  "message": "Gợi ý theo thuật toán: cbf (85 ratings)"
}
```

---

## 📅 MEAL PLANS API

### `GET /api/meal-plans` *(cần token)*
```
Query: ?week_start=2026-09-21
```
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "week_start": "2026-09-21",
      "day_of_week": 1,
      "meal_type": "lunch",
      "recipe": {
        "id": 15,
        "name": "Trứng chiên cà chua",
        "image_url": "...",
        "cook_time_min": 10
      }
    }
  ]
}
```

### `POST /api/meal-plans` *(cần token)*
```json
// Request Body
{
  "week_start": "2026-09-21",
  "day_of_week": 1,
  "meal_type": "lunch",
  "recipe_id": 15
}
```

**Giá trị hợp lệ:**
- `day_of_week`: 0 (Thứ 2) → 6 (Chủ Nhật)
- `meal_type`: `breakfast` | `lunch` | `dinner`

### `DELETE /api/meal-plans/:id` *(cần token)*
```json
{ "success": true, "message": "Đã xóa" }
```

### `GET /api/meal-plans/shopping-list` *(cần token)*
```
Query: ?week_start=2026-09-21
```
```json
{
  "success": true,
  "data": {
    "week_start": "2026-09-21",
    "ingredients": [
      { "name": "Thịt bò", "emoji": "🥩", "total_quantity": 1000, "unit": "g" },
      { "name": "Cà rốt", "emoji": "🥕", "total_quantity": 500, "unit": "g" }
    ]
  }
}
```
> Tổng hợp và cộng dồn số lượng tất cả nguyên liệu từ mọi bữa ăn trong tuần.

---

## ❤️ SAVED RECIPES API

### `GET /api/users/me/saved` *(cần token)*
```json
{ "success": true, "data": [ { "recipe_id": 15, "saved_at": "...", "recipe": { ... } } ] }
```

### `POST /api/users/me/saved` *(cần token)*
```json
// Request Body
{ "recipe_id": 15 }
```

### `DELETE /api/users/me/saved/:recipe_id` *(cần token)*
```json
{ "success": true, "message": "Đã xóa khỏi yêu thích" }
```

---

## 🔧 ADMIN API

### `GET /api/admin/stats` *(admin token)*
```json
{
  "success": true,
  "data": {
    "total_recipes": 80,
    "published_recipes": 78,
    "draft_recipes": 2,
    "total_users": 45,
    "total_ratings": 312,
    "total_views": 890,
    "top_rated_recipes": [ ... ],
    "most_viewed_recipes": [ { ..., "view_count": 45 } ],
    "recent_ratings": [ ... ]
  }
}
```

### `POST /api/admin/ingredients` *(admin)*
```json
{ "name": "Cà rốt", "category": "rau_cu", "unit": "g", "emoji": "🥕", "calories_per_100g": 41 }
```

### `POST /api/admin/tags` *(admin)*
```json
{ "name": "cay", "color": "#FF4444" }
```

### `POST /api/admin/ingredients/:id/substitutes` *(admin)*
```json
{ "substitute_id": 11, "note": "Dùng 3/4 lượng bơ" }
```

---

## 🩺 HEALTH CHECK

### `GET /api/health` — Kiểm tra server hoạt động (public)
```json
{ "status": "ok", "service": "nauAn-backend" }
```

---

## 🎨 EMOJI NGUYÊN LIỆU (Bảng tham chiếu cho Antigravity)

> Sử dụng field `emoji` từ API response, không hardcode phía Frontend.

| Category | Một số emoji phổ biến |
|---|---|
| Rau củ | 🥕🍅🧅🌿🧄🌶️🥔🥬🍆🍄🌱 |
| Thịt | 🥩🍗🦆🥓🦴🌭🫀 |
| Hải sản | 🦐🐟🐠🦑🦀🦪 |
| Gia vị | 🧂🫙🫗🌶️🌿⭐🪵 |
| Ngũ cốc & bột | 🍚🍜🍝🌾🧁 |
| Sữa & trứng | 🥚🥛🧈🧀🥥 |
| Trái cây | 🍍🍌🥭🍋🍅 |

---

## 📦 BIẾN MÔI TRƯỜNG (.env) — Cho Backend

```env
FLASK_ENV=development
SECRET_KEY=<random 32 chars>
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
JWT_SECRET_KEY=<random 32 chars khác>
CLOUDINARY_CLOUD_NAME=<your_cloud_name>
CLOUDINARY_API_KEY=<your_api_key>
CLOUDINARY_API_SECRET=<your_api_secret>
```

---

## ⚙️ THÔNG TIN TÍCH HỢP — Cho Antigravity Frontend

| Mục | Chi tiết |
|---|---|
| **Token Storage** | Lưu trong `localStorage` key `nau_an_token` |
| **Token Header** | `Authorization: Bearer <token>` |
| **Image Display** | Dùng `image_url` từ API response trực tiếp (Cloudinary URL đã được transform) |
| **Pagination** | Xử lý field `pagination.total_pages` để render số trang |
| **Error Handling** | Khi `success: false`, hiển thị field `error` ra UI |
| **Emoji** | Lấy từ field `emoji` trong response, KHÔNG hardcode |
| **Cold Start API** | `/api/recommendations` sẽ trả popular recipes khi user mới, không báo lỗi |
