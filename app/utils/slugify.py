"""
app/utils/slugify.py
Hàm chuẩn hóa chuỗi và tên file tiếng Việt sang slug ASCII không dấu, an toàn tuyệt đối cho URL và Web/Nginx.
"""
import re
import time

def slugify_vietnamese(text: str) -> str:
    """Chuyển đổi chuỗi tiếng Việt có dấu thành slug không dấu dạng kebab-case."""
    if not text:
        return "mon-an"
    text = text.lower().strip()
    replacements = {
        'đ': 'd', 'Đ': 'd',
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text or "mon-an"

def generate_normalized_filename(recipe_id: int, recipe_name: str, slot: int, extension: str = "jpg") -> str:
    """
    Tạo tên file chuẩn hóa: {recipe_id}_{slug}_slot{slot}_{timestamp}.{ext}
    Ví dụ: 56_ca-dieu-hong-hap-gung_slot1_1727088999.jpg
    """
    slug = slugify_vietnamese(recipe_name)
    timestamp = int(time.time())
    ext = extension.lstrip(".").lower() or "jpg"
    return f"{recipe_id}_{slug}_slot{slot}_{timestamp}.{ext}"
