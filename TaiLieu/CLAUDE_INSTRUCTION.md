# 🤖 HƯỚNG DẪN DÀNH CHO CLAUDE (CLAUDE INSTRUCTION)
## Dự án: Hệ Thống Gợi Ý & Công Thức Nấu Ăn Thông Minh (TVU 2026)
> **Cập nhật:** 2026-09-22  
> **Người biên soạn:** Antigravity AI  
> **Người thực hiện:** Claude AI (Senior Backend Engineer)  
> **Trạng thái:** Backend đã có 12 models ORM, kết nối Supabase PostgreSQL thành công (61 món, 99 nguyên liệu, 489 ratings). Frontend (React/TypeScript) đã xây dựng xong giao diện.

---

## 📌 1. PHÂN CÔNG VAI TRÒ & QUY TRÌNH HỢP TÁC

- **Claude AI (Backend)**: Chịu trách nhiệm sửa toàn bộ các lỗi logic Backend, cấu hình `config.py`, thuật toán gợi ý AI (CBF + CF), bổ sung route alias để khớp với Frontend, và cập nhật link ảnh món ăn chuẩn vào database.
- **Antigravity AI (Frontend)**: Sau khi Claude sửa xong Backend và commit lên Git, Antigravity sẽ tiến hành sửa toàn bộ các điểm crash/mismatch trên giao diện React (SearchPage, MealPlanPage, SubstituteModal, SavedRecipesPage, v.v.).

---

## ⚠️ 2. QUY ĐỊNH BẮT BUỘC: CHỪA LẠI ĐÚNG 2 LỖI CHO AI KIỂM THỬ CỦA USER

> **LƯU Ý CỰC KỲ QUAN TRỌNG:**  
> Người dùng đang thử nghiệm hệ thống Agent AI kiểm thử tự động (Testing Agent). Do đó, bạn **PHẢI CHỪA LẠI ĐÚNG 2 LỖI SAU ĐÂY, TUYỆT ĐỐI KHÔNG SỬA**:
> 
> 1. **Lỗi 1 (API Param Mismatch)**: Trong route `GET /api/recipes` (`app/routes/recipes.py`), giữ nguyên việc đọc param `q = request.args.get("q")`. **KHÔNG ĐƯỢC** thêm hỗ trợ đọc `request.args.get("search")` (để Frontend gửi param `search` sẽ không lọc được tên món, dành cho AI kiểm thử bắt lỗi).
> 2. **Lỗi 2 (Tỷ lệ % độ khớp)**: Trong `app/services/ingredient_search.py`, giữ nguyên `match_percent` trả về giá trị đã nhân 100 (ví dụ `75.0`). Frontend đang nhân tiếp 100 thành `7500%`, đây là lỗi logic UI dành cho AI kiểm thử quét DOM.

---

## 🛠️ 3. DANH SÁCH CHI TIẾT CÁC TASK BACKEND CLAUDE CẦN SỬA

### Task 3.1: Sửa file `config.py`
1. **Lỗi `ProductionConfig.init_app`**:
   - Trong `ProductionConfig`, xóa dòng gọi `Config.init_app(app)` (vì class `Config` không có method này). Thay bằng `pass`.
2. **Lỗi prefix `postgres://` của SQLAlchemy 2.0+**:
   - Trong `Config.SQLALCHEMY_DATABASE_URI`: Khi lấy `DATABASE_URL` từ biến môi trường, nếu chuỗi bắt đầu bằng `postgres://`, hãy replace thành `postgresql://` để tránh lỗi `NoSuchModuleError` trên Render/Heroku/Supabase:
   ```python
   db_url = os.environ.get("DATABASE_URL", "")
   if db_url.startswith("postgres://"):
       db_url = db_url.replace("postgres://", "postgresql://", 1)
   SQLALCHEMY_DATABASE_URI = db_url
   ```

---

### Task 3.2: Sửa và Kích hoạt Chế độ AI Gợi Ý (`app/routes/recommendations.py` & `app/services/content_based.py`)

#### 1. Sửa endpoint `GET /api/recommendations` hỗ trợ khách vãng lai (Optional Auth):
- **Hiện tại**: Dùng `@jwt_required_custom`, khách chưa đăng nhập truy cập trang `/recommend` bị trả về `401 Unauthorized`.
- **Cần sửa**: Đổi sang cơ chế Optional JWT:
  ```python
  from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

  @recommendations_bp.route("/recommendations", methods=["GET"])
  def get_recommendations():
      # Kiểm tra token nếu có, không có thì user_id = None
      try:
          verify_jwt_in_request(optional=True)
          user_id = get_jwt_identity()
      except Exception:
          user_id = None

      # Nếu chưa login -> Trả về danh sách món phổ biến nhất (Popular recipes) với HTTP 200
      if not user_id:
          return success_response(
              data=_fallback_popular_list(limit),
              message="Gợi ý món ăn phổ biến dành cho khách"
          )
      ...
  ```

#### 2. Nâng cấp thuật toán CBF (`app/services/content_based.py`):
- **Xử lý Vùng miền (`region`)**:
  - Khi user có preference `pref_type == "region"`, hãy map sang tag vùng miền tương ứng (ví dụ: `mien_nam` $\rightarrow$ tag `"Miền Nam"`, `mien_bac` $\rightarrow$ tag `"Miền Bắc"`, `mien_trung` $\rightarrow$ tag `"Miền Trung"`), hoặc lọc/boost các recipe có `recipe.region == pref_value`.
- **Bổ sung Mapping khẩu vị**:
  - `taste_to_tag`: Bổ sung `"mild": "thanh đạm"`, `"sweet": "ngọt"`, `"spicy": "cay"`.
  - `diet_to_tag`: Bổ sung `"healthy": "healthy"`, `"ít dầu": "ít dầu"`, `"vegetarian": "chay"`.
- Đảm bảo nếu người dùng thiết lập khẩu vị thì vector `user_vec` được tính toán chuẩn xác, không bị rỗng (`sum == 0`).

#### 3. Xử lý Collaborative Filtering (CF) (`app/services/collaborative.py`):
- Thư viện `scikit-surprise` thường gặp lỗi compile C++ trên Windows. Nếu không cài được `surprise`, bạn có thể triển khai ma trận SVD thuần túy bằng `scipy.sparse.linalg.svds` hoặc `sklearn.decomposition.TruncatedSVD` trên ma trận User-Recipe rating, hoặc load mô hình dự phòng để nhánh CF (trọng số 40%) thực sự sinh ra điểm dự đoán thay vì trả về `[]`.

---

### Task 3.3: Bổ sung Route Alias để tương thích 100% với Frontend

Frontend đã được thiết kế sẵn các API call, để tránh gãy kết nối, Backend cần hỗ trợ các route alias sau:

1. **Lưu công thức nấu ăn (`app/routes/meal_plans.py`)**:
   - Hiện tại Backend chỉ có `POST /api/users/me/saved` (body `{ "recipe_id": 15 }`).
   - Frontend đang gọi: `POST /api/users/me/saved/<int:recipe_id>`.
   - **Giải pháp**: Thêm route alias:
     ```python
     @meal_plans_bp.route("/users/me/saved/<int:recipe_id>", methods=["POST"])
     @jwt_required_custom
     def save_recipe_by_id(recipe_id):
         # Gọi logic lưu recipe_id tương tự route POST /users/me/saved
     ```

2. **Đánh giá món ăn (`app/routes/ratings.py`)**:
   - Hiện tại Backend chỉ có `POST /api/ratings` và `GET /api/recipes/<int:recipe_id>/ratings`.
   - Frontend đang gọi: `POST /api/recipes/<int:recipe_id>/ratings` với body `{ "score": 5, "review_text": "..." }`.
   - **Giải pháp**: Mở thêm method `POST` trên route `/recipes/<int:recipe_id>/ratings`:
     ```python
     @ratings_bp.route("/recipes/<int:recipe_id>/ratings", methods=["GET", "POST"])
     def recipe_ratings(recipe_id):
         if request.method == "POST":
             # Lấy score, review_text từ body và user_id từ JWT -> Lưu rating
     ```

3. **Ghi nhận lượt xem (`app/routes/ratings.py`)**:
   - Hiện tại Backend chỉ có `POST /api/view-history`.
   - Frontend đang gọi: `POST /api/recipes/<int:recipe_id>/views`.
   - **Giải pháp**: Thêm route:
     ```python
     @ratings_bp.route("/recipes/<int:recipe_id>/views", methods=["POST"])
     def record_recipe_view(recipe_id):
         # Ghi nhận view (fire-and-forget, optional auth)
     ```

4. **Lấy danh sách Tags (`app/routes/ingredients.py`)**:
   - Hiện tại route là `/tags` (tức `GET /api/tags`).
   - Frontend đang gọi: `GET /api/ingredients/tags`.
   - **Giải pháp**: Thêm alias `@ingredients_bp.route("/ingredients/tags", methods=["GET"])` trỏ về hàm `list_tags`.

5. **Thêm món vào Thực đơn tuần (`app/routes/meal_plans.py`)**:
   - Trong `POST /api/meal-plans`: Frontend gửi `{ "date": "2026-09-22", "meal_type": "lunch", "recipe_id": 15, "servings": 4 }`.
   - Backend hiện tại bắt buộc phải có `week_start` và `day_of_week`.
   - **Giải pháp**: Nếu request có `date` (YYYY-MM-DD):
     ```python
     if "date" in data and not week_start_str:
         target_date = date.fromisoformat(data["date"])
         # Thứ 2 đầu tuần (0=Monday)
         week_start = target_date - timedelta(days=target_date.weekday())
         day_of_week = target_date.weekday()
     ```

---

### Task 3.4: Chuẩn hóa toàn bộ Hình Ảnh Món Ăn Việt Nam

1. Mở file `scripts/update_recipe_images.py`.
2. Thay thế toàn bộ các link ảnh không đúng (đĩa salad hoa quả, mì ramen Nhật, sườn BBQ Mỹ, sủi cảo Trung Hoa) bằng **link ảnh HD món ăn Việt Nam chuẩn xác 100%**:
   - *Cơm tấm sườn bì chả*: Đĩa cơm tấm sườn nướng than hoa, chả trứng, mỡ hành.
   - *Phở bò truyền thống*: Tô phở bò tái lăn nước dùng trong vắt, hành hoa.
   - *Bún chả Hà Nội*: Bát nước mắm chả miếng than hoa, đĩa bún sợi và rau sống.
   - *Canh chua cá lóc*: Tô canh chua cá lóc miền Tây với dọc mùng, cà chua, dứa.
   - *Thịt kho tàu*: Đĩa thịt ba chỉ kho trứng vịt nước dừa màu cánh gián.
   - *Bánh xèo miền Nam*: Chiếc bánh xèo giòn rụm màu vàng nghệ nhân tôm thịt giá đỗ.
   - *Bún bò Huế*: Tô bún bò sa tế cay nồng bắp bò giò heo.
   - *Hủ tiếu Nam Vang*: Tô hủ tiếu tôm thịt trứng cút nước lèo trong ngọt.
   - *Cá kho tộ*: Khúc cá kho tộ trong nồi đất sánh sệt ớt đỏ hành hoa.
3. Chạy script để cập nhật trực tiếp vào Supabase database:
   ```bash
   python scripts/update_recipe_images.py
   ```
4. Đảm bảo cập nhật tương tự trong `scripts/data/recipes_data.py`.

---

## 🧪 4. HƯỚNG DẪN KIỂM THỬ SAU KHI SỬA

Claude hãy chạy các lệnh sau để đảm bảo Backend chạy mượt mà:
```bash
# 1. Kiểm tra syntax toàn bộ backend
python -m compileall app scripts

# 2. Chạy cập nhật hình ảnh chuẩn lên Supabase
python scripts/update_recipe_images.py

# 3. Test API server
python app.py
```

Sau khi bạn hoàn thành toàn bộ công việc Backend, hãy cập nhật trạng thái vào `status.md` và push code lên GitHub repo `Web_Goi_Y_Mon_An`. **Antigravity AI sẽ tiếp nhận và sửa hoàn thiện Frontend ngay sau đó!**
