"""
app/routes/recipes.py
Blueprint: recipes_bp
Endpoints:
  GET    /api/recipes                  (public, phân trang + filter)
  GET    /api/recipes/:id              (public, chi tiết)
  POST   /api/admin/recipes            (admin)
  PUT    /api/admin/recipes/:id        (admin)
  DELETE /api/admin/recipes/:id        (admin)
  POST   /api/admin/recipes/:id/image  (admin, upload Cloudinary)
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app import db
from app.models.recipe import Recipe, Step, Tag
from app.models.ingredient import Ingredient, RecipeIngredient
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import jwt_required_custom, admin_required

recipes_bp = Blueprint("recipes", __name__)

VALID_DIFFICULTIES = ("easy", "medium", "hard")


# ─── PUBLIC ENDPOINTS ─────────────────────────────────────────────────────────

@recipes_bp.route("/recipes", methods=["GET"])
def list_recipes():
    """
    GET /api/recipes
    Query params:
      ?page=1&limit=12
      ?tag=cay
      ?difficulty=easy
      ?q=bún bò
      ?published=true   (admin có thể xem cả unpublished)
      ?region=mien_nam
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(50, max(1, int(request.args.get("limit", 12))))
    except ValueError:
        page, limit = 1, 12

    tag_name = request.args.get("tag", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    # Hỗ trợ cả 'q' và 'search' parameter để tương thích hoàn toàn
    q = (request.args.get("q") or request.args.get("search") or "").strip()
    region = request.args.get("region", "").strip()
    published = request.args.get("published", "true").strip().lower()

    query = Recipe.query

    # Quản lý lọc theo trạng thái xuất bản
    if published == "all":
        pass  # Lấy tất cả (dành cho admin)
    elif published == "false":
        query = query.filter(Recipe.is_published == False)  # noqa: E712
    else:
        query = query.filter(Recipe.is_published == True)  # noqa: E712

    if tag_name:
        query = query.join(Recipe.tags).filter(Tag.name == tag_name)

    if difficulty and difficulty in VALID_DIFFICULTIES:
        query = query.filter(Recipe.difficulty == difficulty)

    if q:
        query = query.filter(Recipe.name.ilike(f"%{q}%"))

    if region:
        query = query.filter(Recipe.region == region)

    query = query.order_by(Recipe.avg_rating.desc(), Recipe.rating_count.desc())

    total = query.count()
    recipes = query.offset((page - 1) * limit).limit(limit).all()

    return paginated_response(
        data=[r.to_dict_list() for r in recipes],
        total=total,
        page=page,
        limit=limit,
    )


@recipes_bp.route("/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    """GET /api/recipes/:id — Chi tiết công thức kèm nguyên liệu và bước nấu."""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)
    if not recipe.is_published:
        # Chưa published — chỉ admin mới xem được (đơn giản hóa: trả 404)
        return error_response("Công thức không tồn tại", 404)
    return success_response(data=recipe.to_dict_detail())


# ─── ADMIN ENDPOINTS ──────────────────────────────────────────────────────────

@recipes_bp.route("/admin/recipes", methods=["POST"])
@admin_required
def create_recipe():
    """
    POST /api/admin/recipes
    Body: {
        "name": "...", "description": "...", "difficulty": "medium",
        "cook_time_min": 90, "prep_time_min": 30, "servings": 4,
        "region": "mien_trung", "tag_ids": [1, 3],
        "ingredients": [{"ingredient_id": 5, "quantity": 500, "unit": "g", "is_optional": false}],
        "steps": [{"step_number": 1, "description": "...", "duration_min": 30}]
    }
    """
    data = request.get_json(silent=True) or {}
    user_id = get_jwt_identity()

    # Validate bắt buộc
    name = (data.get("name") or "").strip()
    if not name:
        return error_response("Tên công thức là bắt buộc", 400)

    difficulty = data.get("difficulty", "medium")
    if difficulty not in VALID_DIFFICULTIES:
        return error_response(f"difficulty phải là {VALID_DIFFICULTIES}", 400)

    # Tạo recipe
    recipe = Recipe(
        name=name,
        description=data.get("description", ""),
        image_url=data.get("image_url", "/recipes/1.jpg"),
        backup_image_url=data.get("backup_image_url"),
        difficulty=difficulty,
        cook_time_min=int(data.get("cook_time_min", 30)),
        prep_time_min=int(data.get("prep_time_min", 15)),
        servings=int(data.get("servings", 4)),
        region=data.get("region"),
        is_published=bool(data.get("is_published", False)),
        created_by=user_id,
    )
    db.session.add(recipe)
    db.session.flush()  # Lấy recipe.id trước khi commit

    # Gắn tags
    _attach_tags(recipe, data.get("tag_ids", []))

    # Gắn nguyên liệu
    _attach_ingredients(recipe, data.get("ingredients", []))

    # Thêm các bước nấu
    _attach_steps(recipe, data.get("steps", []))

    db.session.commit()

    return success_response(
        data=recipe.to_dict_detail(),
        message="Tạo công thức thành công",
        status_code=201,
    )


@recipes_bp.route("/admin/recipes/<int:recipe_id>", methods=["GET"])
@admin_required
def get_admin_recipe(recipe_id):
    """GET /api/admin/recipes/:id — Lấy chi tiết công thức phục vụ chỉnh sửa (kể cả draft)."""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)
    return success_response(data=recipe.to_dict_detail())


@recipes_bp.route("/admin/recipes/<int:recipe_id>", methods=["PUT"])
@admin_required
def update_recipe(recipe_id):
    """PUT /api/admin/recipes/:id"""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    data = request.get_json(silent=True) or {}

    # Cập nhật các field đơn giản
    if "name" in data:
        recipe.name = (data["name"] or "").strip() or recipe.name
    if "description" in data:
        recipe.description = data["description"]
    if "difficulty" in data:
        if data["difficulty"] in VALID_DIFFICULTIES:
            recipe.difficulty = data["difficulty"]
    if "cook_time_min" in data:
        recipe.cook_time_min = int(data["cook_time_min"])
    if "prep_time_min" in data:
        recipe.prep_time_min = int(data["prep_time_min"])
    if "servings" in data:
        recipe.servings = int(data["servings"])
    if "region" in data:
        recipe.region = data["region"]
    if "is_published" in data:
        recipe.is_published = bool(data["is_published"])
    if "image_url" in data:
        recipe.image_url = data["image_url"]
    if "backup_image_url" in data:
        recipe.backup_image_url = data["backup_image_url"]

    # Cập nhật tags nếu có
    if "tag_ids" in data:
        recipe.tags.clear()
        _attach_tags(recipe, data["tag_ids"])

    # Cập nhật nguyên liệu nếu có
    if "ingredients" in data:
        RecipeIngredient.query.filter_by(recipe_id=recipe_id).delete()
        _attach_ingredients(recipe, data["ingredients"])

    # Cập nhật steps nếu có
    if "steps" in data:
        Step.query.filter_by(recipe_id=recipe_id).delete()
        _attach_steps(recipe, data["steps"])

    db.session.commit()

    return success_response(
        data=recipe.to_dict_detail(),
        message="Cập nhật thành công",
    )


@recipes_bp.route("/admin/recipes/<int:recipe_id>", methods=["DELETE"])
@admin_required
def delete_recipe(recipe_id):
    """DELETE /api/admin/recipes/:id"""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    db.session.delete(recipe)
    db.session.commit()

    return success_response(message=f"Đã xóa công thức '{recipe.name}'")


@recipes_bp.route("/admin/recipes/<int:recipe_id>/image", methods=["POST"])
@recipes_bp.route("/admin/recipes/<int:recipe_id>/images", methods=["POST"])
@admin_required
def upload_recipe_image(recipe_id):
    """
    POST /api/admin/recipes/:id/image hoặc /api/admin/recipes/:id/images
    Hỗ trợ cả tải file từ máy tính lẫn dán link ảnh trực tuyến.
    Tự động chuẩn hóa tên file tiếng Việt sang slug ASCII chống lỗi URL / cache.
    Hỗ trợ 2 slot: slot 1 (ảnh chính) và slot 2 (ảnh dự phòng).
    """
    import os
    import time
    from app.utils.slugify import generate_normalized_filename

    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    # Xác định slot (1: ảnh chính, 2: ảnh dự phòng)
    slot = 1
    raw_slot = request.form.get("slot") or request.args.get("slot") or (request.get_json(silent=True) or {}).get("slot")
    if str(raw_slot).strip().lower() in ["2", "slot2", "backup", "secondary"]:
        slot = 2

    saved_url = None

    # TH1: Tải file ảnh trực tiếp từ máy tính (hỗ trợ cả field name 'file' và 'image')
    uploaded_file = request.files.get("file") or request.files.get("image")
    if uploaded_file and uploaded_file.filename != "":
        ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif", "avif"}
        ext = uploaded_file.filename.rsplit(".", 1)[-1].lower() if "." in uploaded_file.filename else "jpg"
        if ext not in ALLOWED_EXTENSIONS:
            return error_response(f"Chỉ chấp nhận file ảnh: {ALLOWED_EXTENSIONS}", 400)

        # Chuẩn hóa tên file sạch không dấu tiếng Việt
        norm_filename = generate_normalized_filename(recipe.id, recipe.name, slot, ext)

        # 1. Thử upload lên Cloudinary nếu có credentials (ưu tiên cao cho Production Render/Cloud)
        from flask import current_app
        has_cloudinary = bool(
            current_app.config.get("CLOUDINARY_CLOUD_NAME") and
            current_app.config.get("CLOUDINARY_API_KEY") and
            current_app.config.get("CLOUDINARY_API_SECRET")
        )

        if has_cloudinary:
            try:
                from app.services.cloudinary_service import upload_recipe_image as upload_to_cloud
                uploaded_file.seek(0)
                cloud_res = upload_to_cloud(uploaded_file, recipe.id, slot=slot)
                if cloud_res and cloud_res.get("url"):
                    saved_url = cloud_res["url"]
            except Exception as e:
                current_app.logger.warning(f"Cloudinary upload failed: {e}. Falling back to local storage.")

        # 2. Nếu không dùng Cloudinary hoặc Cloudinary lỗi, lưu vào local disk
        if not saved_url:
            try:
                target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "recipes"))
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, norm_filename)
                uploaded_file.seek(0)
                uploaded_file.save(target_path)

                # Đồng bộ vào frontend/dist/recipes nếu thư mục build tồn tại
                dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist", "recipes"))
                if os.path.exists(dist_dir):
                    try:
                        import shutil
                        shutil.copy2(target_path, os.path.join(dist_dir, norm_filename))
                    except Exception:
                        pass

                saved_url = f"/recipes/{norm_filename}"
            except Exception as e:
                return error_response(f"Lỗi khi lưu file lên server: {str(e)}", 500)

    # TH2: Dán đường link ảnh trực tuyến (Image URL)
    elif request.form.get("image_url") or (request.get_json(silent=True) or {}).get("image_url"):
        input_url = (request.form.get("image_url") or (request.get_json(silent=True) or {}).get("image_url")).strip()
        if input_url:
            saved_url = input_url

    if not saved_url:
        return error_response("Vui lòng tải lên file ảnh hoặc nhập đường link ảnh", 400)

    # Cập nhật slot tương ứng
    if slot == 1:
        recipe.image_url = saved_url
    else:
        recipe.backup_image_url = saved_url

    db.session.commit()

    return success_response(
        data={
            "slot": slot,
            "image_url": recipe.image_url,
            "backup_image_url": recipe.backup_image_url,
        },
        message=f"Đã lưu ảnh cho Slot {slot} thành công"
    )


@recipes_bp.route("/admin/recipes/<int:recipe_id>/set-primary", methods=["POST"])
@admin_required
def set_primary_image(recipe_id):
    """
    POST /api/admin/recipes/:id/set-primary
    Hoán đổi ảnh giữa slot 1 và slot 2 (chọn ảnh nào làm ảnh chính hiển thị)
    Body: { "slot": 1 | 2 }
    """
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    data = request.get_json(silent=True) or {}
    slot = int(data.get("slot", 1))

    # Nếu chọn slot 2 làm ảnh chính và slot 2 có ảnh -> hoán đổi với slot 1
    if slot == 2 and recipe.backup_image_url:
        old_primary = recipe.image_url
        recipe.image_url = recipe.backup_image_url
        recipe.backup_image_url = old_primary
        db.session.commit()
    elif slot == 1 and recipe.image_url:
        pass

    return success_response(
        data={
            "image_url": recipe.image_url,
            "backup_image_url": recipe.backup_image_url,
        },
        message="Đã cập nhật ảnh chính (index) thành công"
    )


@recipes_bp.route("/admin/recipes/<int:recipe_id>/publish", methods=["POST"])
@admin_required
def publish_recipe(recipe_id):
    """POST /api/admin/recipes/:id/publish — Toggle published status."""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return error_response("Công thức không tồn tại", 404)

    recipe.is_published = not recipe.is_published
    db.session.commit()

    status = "đã xuất bản" if recipe.is_published else "đã ẩn"
    return success_response(
        data={"is_published": recipe.is_published},
        message=f"Công thức {status}",
    )


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _attach_tags(recipe, tag_ids: list):
    """Gắn tags vào recipe theo danh sách tag_ids."""
    for tag_id in tag_ids:
        tag = Tag.query.get(tag_id)
        if tag and tag not in recipe.tags:
            recipe.tags.append(tag)


def _attach_ingredients(recipe, ingredients: list):
    """Thêm RecipeIngredient records cho recipe."""
    for ing_data in ingredients:
        ingredient_id = ing_data.get("ingredient_id")
        if not ingredient_id:
            continue
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            continue
        ri = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient_id,
            quantity=float(ing_data.get("quantity", 1)),
            unit=ing_data.get("unit") or ingredient.unit,
            is_optional=bool(ing_data.get("is_optional", False)),
        )
        db.session.add(ri)


def _attach_steps(recipe, steps: list):
    """Thêm Step records cho recipe."""
    for step_data in steps:
        step = Step(
            recipe_id=recipe.id,
            step_number=int(step_data.get("step_number", 1)),
            description=step_data.get("description", ""),
            image_url=step_data.get("image_url"),
            duration_min=step_data.get("duration_min"),
        )
        db.session.add(step)
