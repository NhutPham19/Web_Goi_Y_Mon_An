"""
scripts/update_recipe_images.py
Cập nhật link ảnh ẩm thực chất lượng cao (Unsplash HD Food Photography)
cho toàn bộ 61 món ăn trong Database Supabase.
"""
import sys
import os

sys.path.insert(0, r"e:\FILE hoc nam 4\ChuyenNganh_ThuNghiem\Web_NauAn")

from app import create_app, db
from app.models.recipe import Recipe

RECIPE_IMAGES = {
    # Miền Nam
    "Cơm tấm sườn bì chả": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "Hủ tiếu Nam Vang": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "Canh chua cá lóc": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",
    "Thịt kho tàu": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "Bánh xèo miền Nam": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80",
    "Gỏi cuốn tôm thịt": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
    "Cá kho tộ": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?auto=format&fit=crop&w=800&q=80",
    "Thịt bò lúc lắc": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",
    "Gà chiên mắm tỏi": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=800&q=80",
    "Tôm rang muối sả ớt": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",
    "Cà ri gà khoai tây": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?auto=format&fit=crop&w=800&q=80",
    "Lẩu mắm": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",
    "Bún thịt nướng": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    "Canh khổ qua nhồi thịt": "https://images.unsplash.com/photo-1604152135912-04a022e23696?auto=format&fit=crop&w=800&q=80",
    "Vịt nấu chao": "https://images.unsplash.com/photo-1514944298352-f6745129037c?auto=format&fit=crop&w=800&q=80",
    "Cơm chiên dương châu": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=800&q=80",
    "Lẩu thái hải sản": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    
    # Miền Bắc
    "Phở bò truyền thống": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80",
    "Bún chả Hà Nội": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    "Bún riêu cua": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80",
    "Bánh cuốn nhân thịt nấm": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
    "Xôi xéo": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80",
    "Miến gà": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "Nem rán Hà Nội": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "Cháo sườn heo": "https://images.unsplash.com/photo-1511690656952-34342bb7c2f2?auto=format&fit=crop&w=800&q=80",
    "Bún ốc": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "Giò thủ": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "Phở gà": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80",
    "Lẩu cua đồng": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",
    "Cơm rang dưa bò": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=800&q=80",
    "Bún bò Nam Bộ": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    "Bánh mì trứng ốp la": "https://images.unsplash.com/photo-1626804475297-41608ea09aeb?auto=format&fit=crop&w=800&q=80",

    # Miền Trung
    "Bún bò Huế": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80",
    "Bánh bèo Huế": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?auto=format&fit=crop&w=800&q=80",
    "Mì Quảng": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "Cao lầu Hội An": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    "Cơm hến Huế": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "Bánh nậm": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?auto=format&fit=crop&w=800&q=80",
    "Bánh lọc trần tôm thịt": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?auto=format&fit=crop&w=800&q=80",
    "Cơm gà Hội An": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "Nem lụi Huế": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",
    "Bánh căn Phan Rang": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80",
    "Bánh mì Hội An": "https://images.unsplash.com/photo-1626804475297-41608ea09aeb?auto=format&fit=crop&w=800&q=80",
    "Bánh ướt Quảng Nam": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
    "Bún sứa Nha Trang": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "Bánh đập Hội An": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80",
    "Vả trộn Huế": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
    
    # Món quen thuộc hàng ngày
    "Đậu hũ sốt cà chua": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "Canh rau muống tôm": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",
    "Xôi gấc": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80",
    "Súp cua thịt ghẹ": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",
    "Chả giò miền Nam": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "Nộm hoa chuối tôm thịt": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
    "Sườn xào chua ngọt": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "Canh bí đỏ nấu tôm": "https://images.unsplash.com/photo-1604152135912-04a022e23696?auto=format&fit=crop&w=800&q=80",
    "Cá diêu hồng hấp gừng": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?auto=format&fit=crop&w=800&q=80",
    "Mực xào sa tế": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",
    "Cháo cá lóc rau ngổ": "https://images.unsplash.com/photo-1511690656952-34342bb7c2f2?auto=format&fit=crop&w=800&q=80",
    "Trứng chiên cà chua": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "Tôm sú hấp bia gừng": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",
    "Bún thịt nướng Huế": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"

def run():
    app = create_app()
    with app.app_context():
        recipes = Recipe.query.all()
        updated = 0
        for r in recipes:
            img = RECIPE_IMAGES.get(r.name, DEFAULT_IMAGE)
            r.image_url = img
            updated += 1
        db.session.commit()
        print(f"🎉 Đã cập nhật ảnh HD thành công cho {updated}/{len(recipes)} món ăn trên Supabase!")

if __name__ == "__main__":
    run()
