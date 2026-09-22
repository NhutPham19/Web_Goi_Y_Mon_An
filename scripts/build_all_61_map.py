import os
import re
import urllib.request
import urllib.parse
import json
import time

# 1. Start with the verified list
VERIFIED = {
    # Flagged by user in screenshot:
    56: "https://i.ytimg.com/vi/r1nHxOdGXRU/hqdefault.jpg", # Cá diêu hồng hấp gừng
    50: "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/07/X%C3%B4i_g%E1%BA%A5c.JPG/960px-X%C3%B4i_g%E1%BA%A5c.JPG", # Xôi gấc
    57: "https://tiki.vn/blog/wp-content/uploads/2023/10/U3RVg0Zy2vjdTkm_dEr9C73K-U80JBuWIxgXP18dXnKhfXb3oj8k3tQFsnsr9ZIPigPlT4UN39xDeL0tUlmNxw3TQNfSHdGnK-pL6VyeZB5FWcsYfzloWWGDnHaE1nvAKNSKNLTqTCFJg-9iLxyQhiY.jpg", # Mực xào sa tế
    19: "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8b/B%C3%BAn_ch%E1%BA%A3_Th%E1%BB%A5y_Khu%C3%AA.jpg/960px-B%C3%BAn_ch%E1%BA%A3_Th%E1%BB%A5y_Khu%C3%AA.jpg", # Bún chả Hà Nội
    58: "https://i.ytimg.com/vi/3eY5Rdv7j2w/hqdefault.jpg", # Cháo cá lóc rau ngổ
    54: "https://i.ytimg.com/vi/APs76-va_Dw/hqdefault.jpg", # Sườn xào chua ngọt

    # Wiki verified dishes
    1: "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b0/C%C6%A1m_T%E1%BA%A5m%2C_Da_Nang%2C_Vietnam.jpg/960px-C%C6%A1m_T%E1%BA%A5m%2C_Da_Nang%2C_Vietnam.jpg",
    2: "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ec/H%E1%BB%A7_ti%E1%BA%BFu_nam_vang_gi%C3%B2_4.jpg/960px-H%E1%BB%A7_ti%E1%BA%BFu_nam_vang_gi%C3%B2_4.jpg",
    3: "https://upload.wikimedia.org/wikipedia/commons/a/a0/Canhchua2.jpg",
    5: "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a5/B%C3%A1nh_x%C3%A8o_with_n%C6%B0%E1%BB%9Bc_m%E1%BA%AFm.jpg/960px-B%C3%A1nh_x%C3%A8o_with_n%C6%B0%E1%BB%9Bc_m%E1%BA%AFm.jpg",
    6: "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/03/Summer_roll.jpg/960px-Summer_roll.jpg",
    8: "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/78/Product_Shots_of_Food-Bo_Luc_Lac.jpg/960px-Product_Shots_of_Food-Bo_Luc_Lac.jpg",
    13: "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/47/Bun_thit_nuong.jpg/960px-Bun_thit_nuong.jpg",
    21: "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a7/Banh_cuon.jpg/960px-Banh_cuon.jpg",
    24: "https://upload.wikimedia.org/wikipedia/commons/6/6b/Cha_gio.jpg",
    26: "https://upload.wikimedia.org/wikipedia/commons/3/37/B%C3%BAn_%E1%BB%91c.jpg",
    31: "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/59/Bun_Bo_Nam_Bo.jpg/960px-Bun_Bo_Nam_Bo.jpg",
    33: "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/00/Bun-Bo-Hue-from-Huong-Giang-2011.jpg/960px-Bun-Bo-Hue-from-Huong-Giang-2011.jpg",
    34: "https://upload.wikimedia.org/wikipedia/commons/d/d3/B%C3%A1nh_b%C3%A8o.jpg",
    35: "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/df/Mi_Quang_1A_Danang.jpg/960px-Mi_Quang_1A_Danang.jpg",
    36: "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/18/Cao_l%E1%BA%A7u_%28144854_994%29.jpg/960px-Cao_l%E1%BA%A7u_%28144854_994%29.jpg",
    61: "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/47/Bun_thit_nuong.jpg/960px-Bun_thit_nuong.jpg",
}

RECIPES = [
    (1, "Cơm tấm sườn bì chả"),
    (2, "Hủ tiếu Nam Vang"),
    (3, "Canh chua cá lóc"),
    (4, "Thịt kho tàu"),
    (5, "Bánh xèo miền Nam"),
    (6, "Gỏi cuốn tôm thịt"),
    (7, "Cá kho tộ"),
    (8, "Thịt bò lúc lắc"),
    (9, "Gà chiên mắm tỏi"),
    (10, "Tôm rang muối sả ớt"),
    (11, "Cà ri gà khoai tây"),
    (12, "Lẩu mắm miền Tây"),
    (13, "Bún thịt nướng"),
    (14, "Canh khổ qua nhồi thịt"),
    (15, "Vịt nấu chao"),
    (16, "Cơm chiên dương châu"),
    (17, "Lẩu thái hải sản"),
    (18, "Phở bò truyền thống"),
    (19, "Bún chả Hà Nội"),
    (20, "Bún riêu cua"),
    (21, "Bánh cuốn nhân thịt nấm"),
    (22, "Xôi xéo"),
    (23, "Miến gà"),
    (24, "Nem rán Hà Nội"),
    (25, "Cháo sườn heo"),
    (26, "Bún ốc"),
    (27, "Giò thủ"),
    (28, "Phở gà"),
    (29, "Lẩu cua đồng"),
    (30, "Cơm rang dưa bò"),
    (31, "Bún bò Nam Bộ"),
    (32, "Bánh mì trứng ốp la"),
    (33, "Bún bò Huế"),
    (34, "Bánh bèo Huế"),
    (35, "Mì Quảng"),
    (36, "Cao lầu Hội An"),
    (37, "Cơm hến Huế"),
    (38, "Bánh nậm"),
    (39, "Bánh lọc trần tôm thịt"),
    (40, "Cơm gà Hội An"),
    (41, "Nem lụi Huế"),
    (42, "Bánh căn Phan Rang"),
    (43, "Bánh mì Hội An"),
    (44, "Bánh ướt Quảng Nam"),
    (45, "Bún sứa Nha Trang"),
    (46, "Bánh đập Hội An"),
    (47, "Vả trộn Huế"),
    (48, "Đậu hũ sốt cà chua"),
    (49, "Canh rau muống tôm"),
    (50, "Xôi gấc"),
    (51, "Súp cua thịt ghẹ"),
    (52, "Chả giò miền Nam"),
    (53, "Nộm hoa chuối tôm thịt"),
    (54, "Sườn xào chua ngọt"),
    (55, "Canh bí đỏ nấu tôm"),
    (56, "Cá diêu hồng hấp gừng"),
    (57, "Mực xào sa tế"),
    (58, "Cháo cá lóc rau ngổ"),
    (59, "Trứng chiên cà chua"),
    (60, "Tôm sú hấp bia gừng"),
    (61, "Bún thịt nướng Huế")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def search_yt_top(q):
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        vids = list(dict.fromkeys(re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)))
        if vids:
            return f"https://i.ytimg.com/vi/{vids[0]}/hqdefault.jpg"
    return None

final_map = {}
for rid, name in RECIPES:
    if rid in VERIFIED:
        final_map[rid] = VERIFIED[rid]
        print(f"[{rid:02d}] {name} (PRE-SET) -> {final_map[rid][:60]}...")
    else:
        # Search YouTube recipe video
        search_query = f"{name} cách nấu món ngon mỗi ngày"
        try:
            yt_url = search_yt_top(search_query)
            if yt_url:
                final_map[rid] = yt_url
                print(f"[{rid:02d}] {name} (YT) -> {yt_url}")
            else:
                print(f"[{rid:02d}] {name} -> NOT FOUND")
        except Exception as e:
            print(f"[{rid:02d}] {name} -> Error {e}")
        time.sleep(0.3)

with open('scripts/all_61_map.json', 'w', encoding='utf-8') as f:
    json.dump(final_map, f, ensure_ascii=False, indent=2)

print(f"\nCompleted! Total recipes mapped: {len(final_map)}/61")
