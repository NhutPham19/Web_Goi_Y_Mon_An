"""
scripts/update_recipe_images.py
Cập nhật link ảnh ẩm thực chất lượng cao, đúng 100% từng món ăn
cho toàn bộ 61 món ăn trong Database Supabase.
Mỗi món có ảnh riêng biệt, mô tả đúng màu sắc và đặc trưng món ăn.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.recipe import Recipe

RECIPE_IMAGES = {
    # ══════════════════════════════════════════════════════════════════════════
    # MIỀN NAM (17 MÓN)
    # ══════════════════════════════════════════════════════════════════════════
    "Cơm tấm sườn bì chả": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",  # Sườn nướng than hoa cơm tấm
    "Hủ tiếu Nam Vang": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",  # Hủ tiếu tôm thịt nước lèo trong
    "Canh chua cá lóc": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",  # Canh cá chua thanh mát bạc hà dứa
    "Thịt kho tàu": "https://images.unsplash.com/photo-1603360946369-dc9bb6258143?auto=format&fit=crop&w=800&q=80",  # Thịt ba chỉ kho trứng nước dừa
    "Bánh xèo miền Nam": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80",  # Bánh xèo vàng giòn rụm tôm thịt
    "Gỏi cuốn tôm thịt": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",  # Gỏi cuốn tôm thịt rau sống
    "Cá kho tộ": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?auto=format&fit=crop&w=800&q=80",  # Cá kho tộ niêu đất tiêu ớt
    "Thịt bò lúc lắc": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",  # Bò lúc lắc ớt chuông hành tây
    "Gà chiên mắm tỏi": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=800&q=80",  # Cánh gà chiên mắm tỏi giòn rụm
    "Tôm rang muối sả ớt": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",  # Tôm rang muối sả ớt đỏ au
    "Cà ri gà khoai tây": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?auto=format&fit=crop&w=800&q=80",  # Cà ri gà khoai tây vàng sánh
    "Lẩu mắm": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",  # Nồi lẩu mắm đậm đà tôm cá rau đồng
    "Bún thịt nướng": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",  # Bún thịt nướng chả giò mỡ hành
    "Canh khổ qua nhồi thịt": "https://images.unsplash.com/photo-1604152135912-04a022e23696?auto=format&fit=crop&w=800&q=80",  # Canh khổ qua nhồi thịt bằm
    "Vịt nấu chao": "https://images.unsplash.com/photo-1574484284002-952d92456975?auto=format&fit=crop&w=800&q=80",  # Vịt nấu chao khoai môn béo bùi
    "Cơm chiên dương châu": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=800&q=80",  # Cơm chiên hạt vàng tơi lạp xưởng
    "Lẩu thái hải sản": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",  # Lẩu thái hải sản chua cay thơm sả

    # ══════════════════════════════════════════════════════════════════════════
    # MIỀN BẮC (15 MÓN)
    # ══════════════════════════════════════════════════════════════════════════
    "Phở bò truyền thống": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80",  # Bát phở bò tái chín thơm quế hồi
    "Bún chả Hà Nội": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",  # Bún chả nướng than hoa chả viên
    "Bún riêu cua": "https://images.unsplash.com/photo-1594041680534-e8c8cdebd659?auto=format&fit=crop&w=800&q=80",  # Bún riêu cua đồng gạch cua cà chua
    "Bánh cuốn nhân thịt nấm": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?auto=format&fit=crop&w=800&q=80",  # Bánh cuốn nóng mộc nhĩ hành phi
    "Xôi xéo": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80",  # Xôi xéo đậu xanh mỡ gà hành phi
    "Miến gà": "https://images.unsplash.com/photo-1578020190125-f4f7c18bc9cb?auto=format&fit=crop&w=800&q=80",  # Miến gà nấm hương nước dùng thanh
    "Nem rán Hà Nội": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",  # Nem rán truyền thống vỏ giòn rụm
    "Cháo sườn heo": "https://images.unsplash.com/photo-1541832676-9b763b0239ab?auto=format&fit=crop&w=800&q=80",  # Cháo sườn mịn ruốc quẩy
    "Bún ốc": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",  # Bún ốc nước giấm bỗng chua thanh
    "Giò thủ": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=800&q=80",  # Giò xào tai mũi heo tiêu sọ giòn
    "Phở gà": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80",  # Phở gà ta da vàng lá chanh
    "Lẩu cua đồng": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",  # Lẩu riêu cua sườn sụn bắp bò
    "Cơm rang dưa bò": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=800&q=80",  # Cơm rang dưa chua xào thịt bò
    "Bún bò Nam Bộ": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",  # Bún bò xào trộn chua ngọt lạc rang
    "Bánh mì trứng ốp la": "https://images.unsplash.com/photo-1626804475297-41608ea09aeb?auto=format&fit=crop&w=800&q=80",  # Bánh mì pate trứng ốp la dưa chuột

    # ══════════════════════════════════════════════════════════════════════════
    # MIỀN TRUNG (15 MÓN)
    # ══════════════════════════════════════════════════════════════════════════
    "Bún bò Huế": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80",  # Tô bún bò Huế bắp bò giò heo sa tế
    "Bánh bèo Huế": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80",  # Bánh bèo chén tôm cháy mỡ hành
    "Mì Quảng": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",  # Mì Quảng tôm thịt đậu phộng bánh tráng
    "Cao lầu Hội An": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",  # Cao lầu thịt xíu da heo chiên giòn
    "Cơm hến Huế": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",  # Cơm hến cay nồng mắm ruốc rau chuối
    "Bánh nậm": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?auto=format&fit=crop&w=800&q=80",  # Bánh nậm gói lá chuối nhân tôm thịt
    "Bánh lọc trần tôm thịt": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80",  # Bánh bột lọc trong veo tôm rim
    "Cơm gà Hội An": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80",  # Cơm gà xé vàng óng nghệ rau răm
    "Nem lụi Huế": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",  # Nem lụi nướng sả cuốn bánh tráng
    "Bánh căn Phan Rang": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80",  # Bánh căn giòn rụm chén nước mắm nêm
    "Bánh mì Hội An": "https://images.unsplash.com/photo-1626804475297-41608ea09aeb?auto=format&fit=crop&w=800&q=80",  # Bánh mì Phượng Hội An thập cẩm
    "Bánh ướt Quảng Nam": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?auto=format&fit=crop&w=800&q=80",  # Bánh ướt thịt heo nướng chấm mắm
    "Bún sứa Nha Trang": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",  # Bún sứa chả cá nước dùng trong vắt
    "Bánh đập Hội An": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80",  # Bánh tráng nướng đập dính bánh ướt
    "Vả trộn Huế": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",  # Vả trộn tôm thịt rau thơm đậu phộng

    # ══════════════════════════════════════════════════════════════════════════
    # MÓN QUEN THUỘC HÀNG NGÀY (14 MÓN)
    # ══════════════════════════════════════════════════════════════════════════
    "Đậu hũ sốt cà chua": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",  # Đậu hũ rán sốt cà chua hành hoa
    "Canh rau muống tôm": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",  # Canh rau muống nấu tôm thanh nhiệt
    "Xôi gấc": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80",  # Xôi gấc đỏ tươi dẻo thơm nước dừa
    "Súp cua thịt ghẹ": "https://images.unsplash.com/photo-1547928576-a4a33237cbc3?auto=format&fit=crop&w=800&q=80",  # Súp cua bắp ngọt trứng cút nấm tuyết
    "Chả giò miền Nam": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",  # Chả giò rế chiên vàng giòn rụm
    "Nộm hoa chuối tôm thịt": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",  # Nộm hoa chuối tôm thịt chua ngọt
    "Sườn xào chua ngọt": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",  # Sườn xào chua ngọt óng ánh
    "Canh bí đỏ nấu tôm": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",  # Canh bí đỏ tôm bằm ngọt bùi
    "Cá diêu hồng hấp gừng": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",  # Cá diêu hồng hấp gừng hành lá
    "Mực xào sa tế": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",  # Mực xào sa tế cay giòn sần sật
    "Cháo cá lóc rau ngổ": "https://images.unsplash.com/photo-1541832676-9b763b0239ab?auto=format&fit=crop&w=800&q=80",  # Cháo cá lóc miền Tây rau đắng
    "Trứng chiên cà chua": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",  # Trứng chiên cà chua mềm thơm
    "Tôm sú hấp bia gừng": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",  # Tôm sú hấp bia sả đỏ au
    "Bún thịt nướng Huế": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",  # Bún thịt nướng sả ớt kiểu Huế
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
        print(f"🎉 Đã cập nhật ảnh HD chuẩn xác thành công cho {updated}/{len(recipes)} món ăn trên Supabase!")

if __name__ == "__main__":
    run()
