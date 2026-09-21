"""
scripts/data/ingredients_data.py
Danh sách 100 nguyên liệu phổ biến trong ẩm thực Việt Nam.
Format: (name, category, unit, emoji, calories_per_100g)
"""

INGREDIENTS = [
    # ─── RÂU CỦ (rau_cu) ─────────────────────────────────────────────────────
    ("Cà rốt", "rau_cu", "g", "🥕", 41),
    ("Cà chua", "rau_cu", "g", "🍅", 18),
    ("Hành tây", "rau_cu", "g", "🧅", 40),
    ("Hành lá", "rau_cu", "g", "🌿", 32),
    ("Tỏi", "rau_cu", "g", "🧄", 149),
    ("Gừng", "rau_cu", "g", "🫚", 80),
    ("Ớt đỏ", "rau_cu", "g", "🌶️", 40),
    ("Ớt xanh", "rau_cu", "g", "🌶️", 27),
    ("Khoai tây", "rau_cu", "g", "🥔", 77),
    ("Bắp cải", "rau_cu", "g", "🥬", 25),
    ("Rau muống", "rau_cu", "g", "🌿", 22),
    ("Cải xanh", "rau_cu", "g", "🥬", 32),
    ("Khổ qua (mướp đắng)", "rau_cu", "g", "🥒", 17),
    ("Bí đỏ", "rau_cu", "g", "🎃", 26),
    ("Bí xanh", "rau_cu", "g", "🥒", 14),
    ("Đậu cô ve", "rau_cu", "g", "🫘", 31),
    ("Đậu bắp (đậu tây)", "rau_cu", "g", "🫑", 33),
    ("Ngò rí (rau mùi)", "rau_cu", "g", "🌿", 23),
    ("Sả", "rau_cu", "g", "🌾", 99),
    ("Củ sen", "rau_cu", "g", "🌸", 74),
    ("Su su", "rau_cu", "g", "🥒", 16),
    ("Cà tím", "rau_cu", "g", "🍆", 25),
    ("Nấm rơm", "rau_cu", "g", "🍄", 22),
    ("Nấm đông cô (shiitake)", "rau_cu", "g", "🍄", 34),
    ("Rau ngổ", "rau_cu", "g", "🌿", 18),
    ("Giá đỗ", "rau_cu", "g", "🌱", 30),

    # ─── THỊT (thit) ──────────────────────────────────────────────────────────
    ("Thịt bò", "thit", "g", "🥩", 250),
    ("Thịt lợn (heo)", "thit", "g", "🥩", 242),
    ("Thịt gà", "thit", "g", "🍗", 165),
    ("Thịt vịt", "thit", "g", "🦆", 201),
    ("Thịt bò xay", "thit", "g", "🥩", 254),
    ("Sườn heo", "thit", "g", "🥩", 290),
    ("Giò sống", "thit", "g", "🥩", 195),
    ("Chả lụa", "thit", "g", "🌭", 220),
    ("Ba chỉ heo", "thit", "g", "🥓", 518),
    ("Lòng heo", "thit", "g", "🫀", 143),
    ("Xương bò", "thit", "g", "🦴", 50),
    ("Xương heo", "thit", "g", "🦴", 45),
    ("Thịt cua", "thit", "g", "🦀", 87),
    ("Trứng gà", "sua_trung", "quả", "🥚", 155),
    ("Trứng vịt", "sua_trung", "quả", "🥚", 185),

    # ─── HẢI SẢN (hai_san) ────────────────────────────────────────────────────
    ("Tôm sú", "hai_san", "g", "🦐", 99),
    ("Tôm thẻ", "hai_san", "g", "🦐", 95),
    ("Cá lóc", "hai_san", "g", "🐟", 91),
    ("Cá basa", "hai_san", "g", "🐠", 90),
    ("Cá thu", "hai_san", "g", "🐟", 144),
    ("Mực", "hai_san", "g", "🦑", 92),
    ("Cua biển", "hai_san", "g", "🦀", 87),
    ("Sò huyết", "hai_san", "g", "🦪", 77),
    ("Ngao (nghêu)", "hai_san", "g", "🦪", 74),
    ("Cá diêu hồng", "hai_san", "g", "🐟", 97),

    # ─── GIA VỊ (gia_vi) ──────────────────────────────────────────────────────
    ("Muối", "gia_vi", "muỗng cà phê", "🧂", 0),
    ("Đường trắng", "gia_vi", "g", "🍬", 387),
    ("Đường thốt nốt", "gia_vi", "g", "🍯", 383),
    ("Nước mắm", "gia_vi", "ml", "🫙", 35),
    ("Nước tương (xì dầu)", "gia_vi", "ml", "🫗", 60),
    ("Dầu ăn", "gia_vi", "ml", "🫙", 884),
    ("Dầu mè", "gia_vi", "ml", "🫙", 884),
    ("Giấm", "gia_vi", "ml", "🫙", 21),
    ("Hắc xì dầu", "gia_vi", "ml", "🫗", 70),
    ("Tương hoisin", "gia_vi", "ml", "🫙", 220),
    ("Tương ớt", "gia_vi", "ml", "🌶️", 93),
    ("Mắm ruốc", "gia_vi", "g", "🫙", 167),
    ("Mắm tôm", "gia_vi", "g", "🫙", 90),
    ("Bột ngọt (mì chính)", "gia_vi", "g", "🧂", 0),
    ("Hạt nêm", "gia_vi", "g", "🧂", 0),
    ("Tiêu đen", "gia_vi", "g", "🫚", 251),
    ("Bột nghệ", "gia_vi", "g", "🌿", 354),
    ("Bột ớt", "gia_vi", "g", "🌶️", 282),
    ("Quế", "gia_vi", "g", "🪵", 247),
    ("Hoa hồi", "gia_vi", "g", "⭐", 337),

    # ─── BỘT & ĐƯỜNG (bot_duong) ──────────────────────────────────────────────
    ("Bột mì đa dụng", "bot_duong", "g", "🌾", 364),
    ("Bột gạo", "bot_duong", "g", "🌾", 366),
    ("Bột năng (tapioca)", "bot_duong", "g", "🌾", 357),
    ("Bột chiên giòn", "bot_duong", "g", "🌾", 340),
    ("Bột nở", "bot_duong", "muỗng cà phê", "🧁", 53),

    # ─── NGŨ CỐC & MÌ (bot_duong) ──────────────────────────────────────────
    ("Gạo tẻ", "bot_duong", "g", "🍚", 130),
    ("Gạo nếp", "bot_duong", "g", "🍚", 340),
    ("Bánh phở (sợi tươi)", "bot_duong", "g", "🍜", 135),
    ("Bún tươi", "bot_duong", "g", "🍜", 108),
    ("Mì trứng (sợi khô)", "bot_duong", "g", "🍝", 380),
    ("Miến dong", "bot_duong", "g", "🍜", 341),

    # ─── SỮA & TRỨNG (sua_trung) ──────────────────────────────────────────────
    ("Sữa tươi", "sua_trung", "ml", "🥛", 61),
    ("Nước cốt dừa", "sua_trung", "ml", "🥥", 230),
    ("Bơ lạt", "sua_trung", "g", "🧈", 717),
    ("Phô mai (cream cheese)", "sua_trung", "g", "🧀", 342),

    # ─── TRÁI CÂY (trai_cay) ──────────────────────────────────────────────────
    ("Dứa (thơm)", "trai_cay", "g", "🍍", 50),
    ("Chuối", "trai_cay", "quả", "🍌", 89),
    ("Xoài", "trai_cay", "g", "🥭", 60),
    ("Chanh", "trai_cay", "quả", "🍋", 29),
    ("Cà chua bi", "trai_cay", "g", "🍅", 18),

    # ─── ĐỒ KHÔ (do_kho) ──────────────────────────────────────────────────────
    ("Đậu phụ (tofu)", "do_kho", "g", "🍱", 76),
    ("Đậu hũ non", "do_kho", "g", "🍱", 55),
    ("Đậu phộng (lạc)", "do_kho", "g", "🥜", 567),
    ("Mộc nhĩ (nấm mèo)", "do_kho", "g", "🍄", 35),
    ("Nước dùng (stock) gà", "do_kho", "ml", "🍲", 15),
    ("Nước dừa tươi", "do_kho", "ml", "🥥", 19),
    ("Me (tamarind)", "do_kho", "g", "🫙", 239),
    ("Sả khô", "do_kho", "g", "🌾", 99),
]

# ─── TAGS DATA ────────────────────────────────────────────────────────────────

TAGS = [
    # Hương vị
    ("cay", "#FF4444"),
    ("ngọt", "#FF8C00"),
    ("mặn", "#4A90D9"),
    ("chua", "#F7B731"),

    # Chế độ ăn
    ("chay", "#4CAF50"),
    ("ít dầu", "#81C784"),
    ("healthy", "#2E7D32"),

    # Thời gian
    ("nhanh", "#03A9F4"),
    ("dưới 30 phút", "#00BCD4"),

    # Vùng miền
    ("Miền Nam", "#FF7043"),
    ("Miền Bắc", "#5C6BC0"),
    ("Miền Trung", "#AB47BC"),

    # Bữa ăn
    ("ăn sáng", "#FFA726"),
    ("tiệc", "#EC407A"),
    ("dễ nấu", "#26A69A"),
]

# ─── INGREDIENT SUBSTITUTES ───────────────────────────────────────────────────
# Format: (ingredient_name, substitute_name, note)

SUBSTITUTES = [
    ("Bơ lạt", "Dầu ăn", "Dùng 3/4 lượng bơ (75ml dầu thay 100g bơ)"),
    ("Bơ lạt", "Nước cốt dừa", "Dùng tỷ lệ 1:1 cho bánh ngọt"),
    ("Nước mắm", "Nước tương (xì dầu)", "Dùng cùng lượng, thêm chút muối"),
    ("Nước mắm", "Muối", "1 muỗng nước mắm = 1/4 muỗng muối"),
    ("Sữa tươi", "Nước cốt dừa", "Tỷ lệ 1:1, món sẽ có vị dừa nhẹ"),
    ("Đường trắng", "Đường thốt nốt", "Tỷ lệ 1:1, vị ngọt tự nhiên hơn"),
    ("Bột mì đa dụng", "Bột gạo", "Tỷ lệ 1:1, thích hợp cho món chiên giòn"),
    ("Bột năng (tapioca)", "Bột gạo", "Tỷ lệ 1:1 cho làm đặc sốt"),
    ("Giấm", "Chanh", "Nước cốt 1 quả chanh = 2 muỗng canh giấm"),
    ("Tương hoisin", "Tương ớt", "Thêm chút đường để bù vị ngọt"),
    ("Mắm ruốc", "Mắm tôm", "Tỷ lệ 1:1, mắm tôm đặc hơn cần pha loãng"),
    ("Nấm đông cô (shiitake)", "Nấm rơm", "Tỷ lệ 1:1, hương vị nhẹ hơn"),
    ("Gạo nếp", "Gạo tẻ", "Kết quả kém dẻo hơn, không thay được 100%"),
    ("Dầu mè", "Dầu ăn", "Dùng 1/2 lượng vì dầu mè đậm mùi hơn"),
    ("Đậu phụ (tofu)", "Đậu hũ non", "Tofu non mềm hơn, hợp cho canh và hấp"),
]
