"""
app/services/cloudinary_service.py
Upload và xử lý ảnh trên Cloudinary.
"""
import cloudinary
import cloudinary.uploader
from flask import current_app


def init_cloudinary():
    """Khởi tạo Cloudinary với credentials từ config."""
    cloudinary.config(
        cloud_name=current_app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=current_app.config.get("CLOUDINARY_API_KEY"),
        api_secret=current_app.config.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def upload_recipe_image(file_obj, recipe_id: int, slot: int = 1) -> dict:
    """
    Upload ảnh công thức lên Cloudinary.
    
    Args:
        file_obj: File object từ request.files
        recipe_id: ID của recipe (dùng làm public_id)
        slot: Slot 1 (ảnh chính) hoặc Slot 2 (ảnh dự phòng)
    
    Returns:
        {
            "url": "https://res.cloudinary.com/.../recipe_xxx_slot1.jpg",
            "thumbnail_url": "https://res.cloudinary.com/.../w_400,h_300,.../recipe_xxx_slot1.jpg",
            "public_id": "nauan/recipes/recipe_15_slot1"
        }
    
    Raises:
        Exception nếu upload thất bại
    """
    init_cloudinary()

    public_id = f"nauan/recipes/recipe_{recipe_id}_slot{slot}"

    result = cloudinary.uploader.upload(
        file_obj,
        public_id=public_id,
        overwrite=True,
        resource_type="image",
        transformation=[
            {"width": 1200, "height": 900, "crop": "limit", "quality": "auto:good"},
        ],
    )

    # URL gốc
    original_url = result.get("secure_url", "")

    # URL thumbnail (400x300, crop fill) cho list view
    # Cloudinary transformation inline vào URL
    thumbnail_url = _build_transformation_url(original_url, "w_400,h_300,c_fill,q_auto")

    return {
        "url": original_url,
        "thumbnail_url": thumbnail_url,
        "public_id": result.get("public_id", ""),
    }


def delete_image(public_id: str) -> bool:
    """Xóa ảnh khỏi Cloudinary theo public_id."""
    init_cloudinary()
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception:
        return False


def _build_transformation_url(original_url: str, transformation: str) -> str:
    """
    Chèn transformation vào Cloudinary URL.
    
    Ví dụ:
        original:    https://res.cloudinary.com/demo/image/upload/v123/sample.jpg
        transformed: https://res.cloudinary.com/demo/image/upload/w_400,h_300,c_fill/v123/sample.jpg
    """
    if "/image/upload/" not in original_url:
        return original_url
    return original_url.replace("/image/upload/", f"/image/upload/{transformation}/", 1)
