# 📊 BÁO CÁO TIẾN ĐỘ DỰ ÁN (PROJECT STATUS)
> **Dự án:** Hệ Thống Gợi Ý & Công Thức Nấu Ăn Thông Minh (TVU 2026)  
> **Repository:** [https://github.com/NhutPham19/Web_Goi_Y_Mon_An](https://github.com/NhutPham19/Web_Goi_Y_Mon_An) (Branch: `main`)  
> **Cập nhật:** 2026-09-22  
> **Người cập nhật:** Antigravity AI  
> **Dành cho:** Claude AI & User

---

## 📌 TÓM TẮT DÀNH CHO CLAUDE

> **Chào Claude!**  
> Hệ thống Backend đã hoàn thành 100% các models ORM và kết nối thành công với database **Supabase PostgreSQL** thật (61 công thức món ăn, 99 nguyên liệu, 15 tags, 489 ratings).  
> Giao diện Frontend bằng React/TypeScript cũng đã được xây dựng hoàn tất.  
> 
> **Nhiệm vụ của bạn hiện tại:**  
> Đọc kỹ file **[`TaiLieu/CLAUDE_INSTRUCTION.md`](./TaiLieu/CLAUDE_INSTRUCTION.md)** để nắm danh sách các lỗi Backend cần sửa, bao gồm:
> 1. Sửa `config.py` (`ProductionConfig.init_app` & chuẩn hóa URI `postgresql://`).
> 2. Sửa thuật toán AI Recommendations (cho phép optional JWT cho khách vãng lai, sửa CBF cho vùng miền & vị giác).
> 3. Bổ sung các Route Alias (`POST /api/users/me/saved/<id>`, `POST /api/recipes/<id>/ratings`, `POST /api/recipes/<id>/views`, v.v.).
> 4. Chuẩn hóa hình ảnh món Việt chuẩn xác trong `scripts/update_recipe_images.py` và chạy cập nhật lên database.
> 5. **CHỪA LẠI ĐÚNG 2 LỖI** theo hướng dẫn trong `CLAUDE_INSTRUCTION.md` để user thử nghiệm Agent AI kiểm thử tự động.
> 
> *Sau khi Claude hoàn thành và push code Backend lên Git, Antigravity AI sẽ tiếp quản và sửa toàn bộ phần Frontend + đóng gói Docker.*

---

## 🎯 BẢNG TIẾN ĐỘ CHI TIẾT TỪNG PHẦN

| Hạng mục | Thành phần | Trạng thái | Chi tiết | Phụ trách |
|---|---|:---:|---|:---:|
| **Database & ORM** | 12 bảng PostgreSQL | ✅ **HOÀN THÀNH** | Đã kết nối Supabase, migration và nạp 61 món, 99 nguyên liệu, 489 ratings | Claude |
| **REST API Backend** | Flask Blueprints | ⚠️ **CẦN SỬA** | 8 blueprints cơ bản đã chạy, cần sửa route alias, JWT optional, config.py | Claude |
| **Hệ thống AI / ML** | CBF + CF Hybrid | ⚠️ **CẦN SỬA** | Cần sửa logic vùng miền/vị giác CBF và kích hoạt CF | Claude |
| **Dữ liệu Hình ảnh** | 61 món ăn 3 miền | ⚠️ **CẦN SỬA** | Cần cập nhật link ảnh món Việt chuẩn xác thay thế ảnh salad/ramen | Claude |
| **Frontend Web App** | React 19 + Vite | ⏳ **CHỜ BACKEND** | Giao diện đã xong, chờ Claude xong Backend sẽ sửa contract mismatch | Antigravity |
| **Kiểm thử tự động** | AI Testing Agent | ⏳ **CHỜ SỬA** | Đã chọn và chừa lại 2 lỗi (Lỗi param search & Lỗi nhân đôi %) để agent test | User & Agent |
| **Đóng gói Docker** | Multi-container Compose | ⏳ **BƯỚC CUỐI** | Dockerfile Backend, Frontend Nginx, docker-compose.yml | Antigravity |

---

## 📁 CẤU TRÚC CODEBASE HIỆN TẠI

```
Web_NauAn/
├── status.md                          # File trạng thái dự án
├── .env.example                       # Mẫu cấu hình môi trường
├── .gitignore                         # Chặn .env, venv, node_modules, cache
├── Procfile                           # Gunicorn entrypoint
├── requirements.txt                   # Danh sách package Python
├── app.py                             # Entry point Flask
├── config.py                          # Config reader từ .env
│
├── TaiLieu/                           # 📚 Tài liệu cốt lõi (Đã dọn dẹp gọn gàng)
│   ├── CLAUDE_INSTRUCTION.md          # 👉 HƯỚNG DẪN CHI TIẾT DÀNH CHO CLAUDE
│   └── API_DOCS.md                    # Đặc tả đầy đủ 100% REST API Endpoints
│
├── app/                               # ⚙️ Source code Flask API
│   ├── models/                        # 12 ORM Models
│   ├── routes/                        # Blueprints API
│   ├── services/                      # Business logic & ML (CBF, CF, Cloudinary)
│   └── utils/                         # Helpers & Decorators
│
├── frontend/                          # 🎨 Mã nguồn Frontend (React + Vite + Tailwind)
│   ├── src/                           # Components, Pages, APIs, Types
│   ├── package.json
│   └── vite.config.ts
│
├── migrations/                        # Thư mục Flask-Migrate
└── scripts/                           # 🌱 Scripts seed & cập nhật database
    ├── data/                          # Dữ liệu nguyên liệu & công thức món ăn
    ├── seed_ingredients.py
    ├── seed_recipes.py
    ├── seed_ratings.py
    └── update_recipe_images.py        # Script cập nhật ảnh món ăn
```
