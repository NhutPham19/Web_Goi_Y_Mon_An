"""
scripts/seed_additional_recipes.py
Bổ sung 18-19 công thức món ăn Việt Nam chất lượng cao cho các nguyên liệu đạm bị thiếu:
- Thịt bò xay (id 31)
- Cá basa (id 45)
- Cá thu (id 46)
- Sò huyết (id 49)
- Ngao / nghêu (id 50)
- Thịt vịt (id 30)
- Thịt gà (id 29)
- Trứng gà (id 40)
- Trứng vịt (id 41)
- Cá diêu hồng (id 51)
- Mực (id 47)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.recipe import Recipe, Tag, Step
from app.models.ingredient import Ingredient, RecipeIngredient

ADDITIONAL_RECIPES = [
    {
        "name": "Bò bằm xào hành tây cà chua",
        "description": "Thịt bò xay xào cùng cà chua và hành tây ngọt mềm, sốt đậm đà rưới cơm nóng cực kỳ đưa cơm và dễ làm.",
        "difficulty": "easy",
        "cook_time_min": 15,
        "prep_time_min": 10,
        "servings": 3,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "dễ nấu", "Miền Nam", "mặn"],
        "ingredients": [
            {"name": "Thịt bò xay", "quantity": 300, "unit": "g"},
            {"name": "Cà chua", "quantity": 2, "unit": "quả"},
            {"name": "Hành tây", "quantity": 1, "unit": "củ"},
            {"name": "Tỏi", "quantity": 3, "unit": "tép"},
            {"name": "Hành lá", "quantity": 2, "unit": "nhánh"},
            {"name": "Dầu ăn", "quantity": 2, "unit": "muỗng canh"},
            {"name": "Nước mắm", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Tiêu đen", "quantity": 0.5, "unit": "muỗng cà phê"},
        ],
        "steps": [
            {"step_number": 1, "description": "Ướp thịt bò xay với 1 muỗng cà phê hạt nêm, chút tiêu và tỏi băm trong 10 phút.", "duration_min": 10},
            {"step_number": 2, "description": "Cà chua bổ múi cau, hành tây thái múi cau nhỏ. Hành lá cắt khúc.", "duration_min": 5},
            {"step_number": 3, "description": "Phi thơm tỏi băm với dầu ăn trên chảo nóng, cho thịt bò xay vào xào săn với lửa lớn rồi trút ra đĩa.", "duration_min": 3},
            {"step_number": 4, "description": "Cho tiếp cà chua và hành tây vào chảo xào chín mềm, nêm nước mắm và chút đường cho vừa vị.", "duration_min": 4},
            {"step_number": 5, "description": "Trút thịt bò vào đảo nhanh tay cùng hành lá trong 1 phút, rắc tiêu đen rồi tắt bếp.", "duration_min": 2}
        ]
    },
    {
        "name": "Cháo thịt bò bằm gừng tươi",
        "description": "Bát cháo nóng hổi sánh mịn, thịt bò xay béo ngọt quyện cùng vị ấm nồng của gừng tươi và hành hoa giải cảm tuyệt vời.",
        "difficulty": "easy",
        "cook_time_min": 25,
        "prep_time_min": 10,
        "servings": 2,
        "region": "mien_bac",
        "image_url": "https://images.unsplash.com/photo-1541832676-9b763b0239ab?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "healthy", "dễ nấu", "ăn sáng", "Miền Bắc"],
        "ingredients": [
            {"name": "Thịt bò xay", "quantity": 200, "unit": "g"},
            {"name": "Gạo tẻ", "quantity": 100, "unit": "g"},
            {"name": "Gừng", "quantity": 1, "unit": "củ"},
            {"name": "Hành lá", "quantity": 3, "unit": "nhánh"},
            {"name": "Nước mắm", "quantity": 1, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Tiêu đen", "quantity": 0.5, "unit": "muỗng cà phê"},
        ],
        "steps": [
            {"step_number": 1, "description": "Gạo vo sạch, cho vào nồi với 800ml nước ninh nhừ thành cháo trắng.", "duration_min": 15},
            {"step_number": 2, "description": "Gừng cạo vỏ thái sợi mảnh, hành lá rửa sạch thái nhỏ.", "duration_min": 3},
            {"step_number": 3, "description": "Ướp thịt bò xay với chút nước mắm, hạt nêm và gừng thái sợi.", "duration_min": 5},
            {"step_number": 4, "description": "Khi cháo nhừ, thả thịt bò xay vào khuấy đều tay cho thịt tơi và chín đều trong 3-4 phút.", "duration_min": 4},
            {"step_number": 5, "description": "Múc cháo ra tô, rắc hành hoa và tiêu xay lên trên, thưởng thức khi còn nóng ấm.", "duration_min": 2}
        ]
    },
    {
        "name": "Cá basa kho tộ nước dừa",
        "description": "Cá basa béo ngậy được kho kẹo trong niêu đất với nước dừa tươi, màu cánh gián bắt mắt, cay nồng ớt hiểm đậm chất Nam Bộ.",
        "difficulty": "medium",
        "cook_time_min": 30,
        "prep_time_min": 15,
        "servings": 4,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800&auto=format&fit=crop&q=80",
        "tags": ["mặn", "cay", "Miền Nam", "dễ nấu"],
        "ingredients": [
            {"name": "Cá basa", "quantity": 500, "unit": "g"},
            {"name": "Nước dừa tươi", "quantity": 150, "unit": "ml"},
            {"name": "Ớt đỏ", "quantity": 3, "unit": "trái"},
            {"name": "Tỏi", "quantity": 4, "unit": "tép"},
            {"name": "Hành lá", "quantity": 2, "unit": "nhánh"},
            {"name": "Nước mắm", "quantity": 3, "unit": "muỗng canh"},
            {"name": "Đường thốt nốt", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Tiêu đen", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Dầu ăn", "quantity": 1, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Cá basa rửa sạch với muối và giấm để khử tanh, cắt khúc vừa ăn để ráo.", "duration_min": 10},
            {"step_number": 2, "description": "Ướp cá với nước mắm, đường thốt nốt, hạt tiêu, tỏi băm và ớt hiểm đập dập khoảng 15 phút.", "duration_min": 15},
            {"step_number": 3, "description": "Thắng nước màu: Cho 1 muỗng đường và chút dầu ăn vào tộ đun nhỏ lửa đến khi có màu cánh gián đẹp.", "duration_min": 3},
            {"step_number": 4, "description": "Cho từng khúc cá vào tộ chiên sơ hai mặt cho săn và bám đều màu caramel.", "duration_min": 5},
            {"step_number": 5, "description": "Đổ nước dừa tươi vào xâm xấp mặt cá, đun sôi rồi hạ lửa riu riu kho 20 phút đến khi nước sốt sánh lại, rắc hành hoa và tiêu.", "duration_min": 20}
        ]
    },
    {
        "name": "Cá basa chiên sốt cà chua",
        "description": "Khúc cá basa chiên vàng giòn rụm bên ngoài, ngấm đều sốt cà chua chua ngọt mặn mà, rất được lòng trẻ nhỏ và gia đình.",
        "difficulty": "easy",
        "cook_time_min": 20,
        "prep_time_min": 10,
        "servings": 3,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "dễ nấu", "chua", "ngọt", "Miền Nam"],
        "ingredients": [
            {"name": "Cá basa", "quantity": 400, "unit": "g"},
            {"name": "Cà chua", "quantity": 3, "unit": "quả"},
            {"name": "Bột chiên giòn", "quantity": 50, "unit": "g"},
            {"name": "Tỏi", "quantity": 3, "unit": "tép"},
            {"name": "Hành lá", "quantity": 2, "unit": "nhánh"},
            {"name": "Nước mắm", "quantity": 2, "unit": "muỗng canh"},
            {"name": "Đường trắng", "quantity": 1, "unit": "muỗng canh"},
            {"name": "Dầu ăn", "quantity": 100, "unit": "ml"},
        ],
        "steps": [
            {"step_number": 1, "description": "Cá basa cắt miếng vừa ăn, thấm khô nước rồi lăn nhẹ qua một lớp mỏng bột chiên giòn.", "duration_min": 5},
            {"step_number": 2, "description": "Đun nóng chảo dầu, thả cá vào chiên vàng giòn hai mặt rồi vớt ra giấy thấm dầu.", "duration_min": 8},
            {"step_number": 3, "description": "Phi thơm tỏi băm, cho cà chua băm nhỏ vào xào nhuyễn cùng nước mắm và đường tạo thành sốt sánh.", "duration_min": 5},
            {"step_number": 4, "description": "Xếp cá ra đĩa, rưới đều sốt cà chua nóng sốt lên trên và trang trí hành ngò rí.", "duration_min": 2}
        ]
    },
    {
        "name": "Cá thu sốt cà chua thì là",
        "description": "Món ăn đặc trưng đất Bắc với lát cá thu rán vàng thơm bùi, sốt cà chua sánh đỏ quyện cùng hương thơm độc đáo của hành thì là.",
        "difficulty": "easy",
        "cook_time_min": 20,
        "prep_time_min": 10,
        "servings": 3,
        "region": "mien_bac",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "dễ nấu", "Miền Bắc", "chua"],
        "ingredients": [
            {"name": "Cá thu", "quantity": 400, "unit": "g"},
            {"name": "Cà chua", "quantity": 3, "unit": "quả"},
            {"name": "Hành lá", "quantity": 3, "unit": "nhánh"},
            {"name": "Tỏi", "quantity": 3, "unit": "tép"},
            {"name": "Nước mắm", "quantity": 2, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Tiêu đen", "quantity": 0.5, "unit": "muỗng cà phê"},
            {"name": "Dầu ăn", "quantity": 3, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Lát cá thu rửa sạch, thấm khô, ướp chút muối tiêu 10 phút.", "duration_min": 10},
            {"step_number": 2, "description": "Rán cá trên chảo dầu nóng cho bề mặt vàng xém thơm rồi vớt ra.", "duration_min": 7},
            {"step_number": 3, "description": "Phi thơm tỏi băm, xào cà chua chín mềm thành nước sốt đậm đà nêm nước mắm hạt nêm.", "duration_min": 5},
            {"step_number": 4, "description": "Cho cá thu vào om cùng sốt cà chua trên lửa nhỏ trong 5 phút cho thấm gia vị.", "duration_min": 5},
            {"step_number": 5, "description": "Cho hành lá cắt khúc vào đảo nhẹ rồi tắt bếp, dùng nóng với cơm.", "duration_min": 2}
        ]
    },
    {
        "name": "Cá thu kho tiêu nghệ",
        "description": "Khúc cá thu chắc thịt kho ngấm vị cay ấm nồng của tiêu sọ và màu vàng óng ả từ nghệ tươi, ăn với cơm trắng mùa mưa thì tuyệt hảo.",
        "difficulty": "medium",
        "cook_time_min": 30,
        "prep_time_min": 10,
        "servings": 3,
        "region": "mien_trung",
        "image_url": "https://images.unsplash.com/photo-1580476262798-bddd9f4b7369?w=800&auto=format&fit=crop&q=80",
        "tags": ["mặn", "cay", "Miền Trung", "dễ nấu"],
        "ingredients": [
            {"name": "Cá thu", "quantity": 400, "unit": "g"},
            {"name": "Bột nghệ", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Tiêu đen", "quantity": 1.5, "unit": "muỗng cà phê"},
            {"name": "Ớt đỏ", "quantity": 3, "unit": "trái"},
            {"name": "Tỏi", "quantity": 3, "unit": "tép"},
            {"name": "Nước mắm", "quantity": 2.5, "unit": "muỗng canh"},
            {"name": "Đường trắng", "quantity": 1, "unit": "muỗng canh"},
            {"name": "Dầu ăn", "quantity": 2, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Cá thu sơ chế sạch, để ráo nước hoàn toàn.", "duration_min": 5},
            {"step_number": 2, "description": "Ướp cá với nước mắm, bột nghệ, tiêu đen giã dập, ớt và tỏi băm trong 15 phút.", "duration_min": 15},
            {"step_number": 3, "description": "Chiên sơ cá thu cho mặt cá săn lại giúp thịt cá giữ độ dai ngon khi kho.", "duration_min": 5},
            {"step_number": 4, "description": "Thêm nước ấm và nước ướp cá vào nồi, kho trên lửa nhỏ liu riu 20 phút đến khi nước cạn sền sệt.", "duration_min": 20},
            {"step_number": 5, "description": "Rắc thêm tiêu đen tươi xay nhuyễn lên bề mặt và tắt bếp.", "duration_min": 1}
        ]
    },
    {
        "name": "Sò huyết xào me chua ngọt",
        "description": "Sò huyết béo bùi thấm đẫm trong lớp sốt me sánh mịn chua chua ngọt ngọt, the cay tỏi ớt thơm lừng món nhậu nức tiếng.",
        "difficulty": "easy",
        "cook_time_min": 15,
        "prep_time_min": 15,
        "servings": 2,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "chua", "cay", "ngọt", "Miền Nam", "tiệc"],
        "ingredients": [
            {"name": "Sò huyết", "quantity": 500, "unit": "g"},
            {"name": "Me (tamarind)", "quantity": 50, "unit": "g"},
            {"name": "Tỏi", "quantity": 5, "unit": "tép"},
            {"name": "Ớt đỏ", "quantity": 2, "unit": "trái"},
            {"name": "Đường trắng", "quantity": 2, "unit": "muỗng canh"},
            {"name": "Nước mắm", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Dầu ăn", "quantity": 2, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Sò huyết chà rửa thật sạch bùn đất bên ngoài vỏ, để ráo.", "duration_min": 10},
            {"step_number": 2, "description": "Dầm me với nửa chén nước ấm, lọc qua rây lấy nước cốt me sánh đặc.", "duration_min": 5},
            {"step_number": 3, "description": "Phi thật nhiều tỏi băm thơm vàng trong chảo dầu, vớt một nửa tỏi phi ra để riêng.", "duration_min": 3},
            {"step_number": 4, "description": "Cho nước cốt me, đường, nước mắm, ớt băm vào chảo đun sôi lăn tăn thành sốt me sệt.", "duration_min": 3},
            {"step_number": 5, "description": "Cho sò huyết vào xào với lửa lớn trong 3-4 phút đến khi sò vừa hé miệng thì tắt bếp, rắc tỏi phi lên trên.", "duration_min": 4}
        ]
    },
    {
        "name": "Sò huyết nướng muối ớt",
        "description": "Sò huyết tươi ngọt béo ngậy được phủ lớp muối ớt cay xè thơm nức mũi, giữ trọn vị ngọt tự nhiên của biển cả.",
        "difficulty": "easy",
        "cook_time_min": 10,
        "prep_time_min": 10,
        "servings": 2,
        "region": "mien_trung",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "cay", "Miền Trung", "tiệc", "dễ nấu"],
        "ingredients": [
            {"name": "Sò huyết", "quantity": 500, "unit": "g"},
            {"name": "Ớt đỏ", "quantity": 4, "unit": "trái"},
            {"name": "Tỏi", "quantity": 3, "unit": "tép"},
            {"name": "Muối", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Dầu ăn", "quantity": 1, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Rửa sạch sò huyết bằng bàn chải để loại bỏ hoàn toàn cát bẩn bám trên vỏ.", "duration_min": 8},
            {"step_number": 2, "description": "Giã nhuyễn ớt đỏ cùng muối hột và chút dầu ăn để làm hỗn hợp muối ớt phết.", "duration_min": 4},
            {"step_number": 3, "description": "Cho sò huyết lên vỉ nướng hoặc chảo gang nướng trên lửa lớn đến khi sò hé miệng.", "duration_min": 5},
            {"step_number": 4, "description": "Phết sốt muối ớt lên ruột sò nướng thêm 1 phút cho ngấm đều và thưởng thức ngay.", "duration_min": 2}
        ]
    },
    {
        "name": "Nghêu hấp sả ớt",
        "description": "Nghêu tươi ngọt nước hấp cùng sả đập dập thơm lừng, ớt cay nồng ấm bụng, nước nghêu ngọt thanh húp xì xụp cực đã.",
        "difficulty": "easy",
        "cook_time_min": 10,
        "prep_time_min": 10,
        "servings": 3,
        "region": "mien_trung",
        "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "cay", "dễ nấu", "Miền Trung", "healthy"],
        "ingredients": [
            {"name": "Ngao (nghêu)", "quantity": 800, "unit": "g"},
            {"name": "Sả", "quantity": 5, "unit": "cây"},
            {"name": "Ớt đỏ", "quantity": 3, "unit": "trái"},
            {"name": "Gừng", "quantity": 1, "unit": "củ"},
            {"name": "Nước mắm", "quantity": 1, "unit": "muỗng canh"},
            {"name": "Đường trắng", "quantity": 1, "unit": "muỗng cà phê"},
        ],
        "steps": [
            {"step_number": 1, "description": "Ngâm nghêu với nước vo gạo và vài lát ớt trong 30 phút để nhả hết cát, rửa sạch lại.", "duration_min": 10},
            {"step_number": 2, "description": "Sả rửa sạch đập dập cắt khúc ngắn. Gừng gọt vỏ thái sợi. Ớt cắt lát.", "duration_min": 5},
            {"step_number": 3, "description": "Lót một lớp sả và gừng dưới đáy nồi, đổ nghêu vào, thêm chút nước mắm, đường và nửa chén nước nhỏ.", "duration_min": 2},
            {"step_number": 4, "description": "Đậy nắp đun lửa lớn trong 5-7 phút đến khi nghêu mở hết miệng thì đảo đều rồi tắt bếp ngay.", "duration_min": 6}
        ]
    },
    {
        "name": "Canh nghêu nấu chua dứa cà chua",
        "description": "Tô canh nghêu thanh mát với vị chua dịu của dứa và cà chua, nước dùng ngọt đậm đà từ nghêu tươi giúp giải nhiệt mùa hè.",
        "difficulty": "easy",
        "cook_time_min": 15,
        "prep_time_min": 10,
        "servings": 4,
        "region": "mien_bac",
        "image_url": "https://images.unsplash.com/photo-1541832676-9b763b0239ab?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "chua", "healthy", "dễ nấu", "Miền Bắc"],
        "ingredients": [
            {"name": "Ngao (nghêu)", "quantity": 600, "unit": "g"},
            {"name": "Cà chua", "quantity": 2, "unit": "quả"},
            {"name": "Dứa (thơm)", "quantity": 0.5, "unit": "quả"},
            {"name": "Hành lá", "quantity": 2, "unit": "nhánh"},
            {"name": "Ớt đỏ", "quantity": 1, "unit": "trái"},
            {"name": "Nước mắm", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
        ],
        "steps": [
            {"step_number": 1, "description": "Nghêu rửa sạch, luộc với 600ml nước cho hé miệng. Vớt nghêu lấy thịt, chắt lấy nước luộc trong.", "duration_min": 8},
            {"step_number": 2, "description": "Cà chua bổ múi cau, dứa thái lát mỏng vừa ăn. Hành ngò thái nhỏ.", "duration_min": 4},
            {"step_number": 3, "description": "Phi thơm hành tím, xào cà chua và dứa cho thơm rồi đổ nước luộc nghêu vào đun sôi.", "duration_min": 4},
            {"step_number": 4, "description": "Nêm nước mắm hạt nêm cho vừa miệng, thả thịt nghêu vào nấu thêm 1 phút rồi rắc hành lá tắt bếp.", "duration_min": 2}
        ]
    },
    {
        "name": "Vịt kho gừng sả ớt",
        "description": "Thịt vịt béo ngậy được kho săn đượm vị gừng ấm và sả phi giòn, khử sạch mùi vịt, màu cánh gián quyến rũ ăn tốn cơm vô cùng.",
        "difficulty": "medium",
        "cook_time_min": 35,
        "prep_time_min": 15,
        "servings": 4,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
        "tags": ["mặn", "cay", "Miền Nam", "dễ nấu"],
        "ingredients": [
            {"name": "Thịt vịt", "quantity": 600, "unit": "g"},
            {"name": "Gừng", "quantity": 2, "unit": "củ"},
            {"name": "Sả", "quantity": 3, "unit": "cây"},
            {"name": "Ớt đỏ", "quantity": 2, "unit": "trái"},
            {"name": "Tỏi", "quantity": 4, "unit": "tép"},
            {"name": "Nước mắm", "quantity": 3, "unit": "muỗng canh"},
            {"name": "Nước tương (xì dầu)", "quantity": 1, "unit": "muỗng canh"},
            {"name": "Đường thốt nốt", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Tiêu đen", "quantity": 1, "unit": "muỗng cà phê"},
        ],
        "steps": [
            {"step_number": 1, "description": "Thịt vịt chặt miếng vừa ăn, dùng gừng giã dập và rượu trắng chà xát thật kỹ để khử mùi hôi, rửa sạch để ráo.", "duration_min": 10},
            {"step_number": 2, "description": "Ướp vịt với nước mắm, nước tương, đường thốt nốt, hạt tiêu, một nửa gừng thái sợi và sả băm trong 20 phút.", "duration_min": 20},
            {"step_number": 3, "description": "Phi thơm tỏi, sả và gừng thái sợi còn lại trong chảo nóng đến khi thơm lừng.", "duration_min": 3},
            {"step_number": 4, "description": "Cho thịt vịt vào xào săn với lửa lớn cho mỡ vịt tươm ra và miếng thịt thấm đều vị caramel.", "duration_min": 7},
            {"step_number": 5, "description": "Đổ chút nước sôi xăm xắp mặt thịt, đậy nắp kho liu riu trong 20 phút đến khi nước sốt keo sánh lại, rắc tiêu ớt.", "duration_min": 20}
        ]
    },
    {
        "name": "Gà kho sả ớt đậm vị",
        "description": "Thịt gà ta săn chắc vàng ươm ngấm đẫm hương sả băm giòn và ớt cay nồng, món ăn kinh điển trong mâm cơm gia đình Việt.",
        "difficulty": "easy",
        "cook_time_min": 25,
        "prep_time_min": 10,
        "servings": 4,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "mặn", "cay", "Miền Nam", "dễ nấu"],
        "ingredients": [
            {"name": "Thịt gà", "quantity": 500, "unit": "g"},
            {"name": "Sả", "quantity": 4, "unit": "cây"},
            {"name": "Ớt đỏ", "quantity": 3, "unit": "trái"},
            {"name": "Tỏi", "quantity": 4, "unit": "tép"},
            {"name": "Nước mắm", "quantity": 2.5, "unit": "muỗng canh"},
            {"name": "Đường trắng", "quantity": 1, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Dầu ăn", "quantity": 2, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Thịt gà rửa sạch chặt miếng vừa ăn. Sả ớt và tỏi băm nhuyễn.", "duration_min": 8},
            {"step_number": 2, "description": "Ướp gà với 1 muỗng mắm, hạt nêm, chút đường và 1/2 lượng sả ớt băm trong 15 phút.", "duration_min": 15},
            {"step_number": 3, "description": "Đun nóng dầu ăn, phi vàng thơm lượng sả tỏi băm còn lại rồi trút gà vào đảo đều tay trên lửa lớn cho săn.", "duration_min": 5},
            {"step_number": 4, "description": "Nêm thêm mắm và đường tạo màu caramel vàng ươm, đậy nắp om nhỏ lửa trong 15 phút đến khi gà chín mềm đậm vị.", "duration_min": 15}
        ]
    },
    {
        "name": "Canh chua gà nấu me thanh mát",
        "description": "Sự kết hợp độc đáo giữa thịt gà mềm ngọt và vị chua thanh tao từ me chín, cà chua mọng nước giúp bữa cơm thêm ngon miệng dễ tiêu.",
        "difficulty": "easy",
        "cook_time_min": 20,
        "prep_time_min": 10,
        "servings": 4,
        "region": "mien_trung",
        "image_url": "https://images.unsplash.com/photo-1541832676-9b763b0239ab?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "chua", "healthy", "Miền Trung", "dễ nấu"],
        "ingredients": [
            {"name": "Thịt gà", "quantity": 400, "unit": "g"},
            {"name": "Me (tamarind)", "quantity": 40, "unit": "g"},
            {"name": "Cà chua", "quantity": 2, "unit": "quả"},
            {"name": "Hành tây", "quantity": 0.5, "unit": "củ"},
            {"name": "Ớt đỏ", "quantity": 1, "unit": "trái"},
            {"name": "Ngò rí (rau mùi)", "quantity": 2, "unit": "nhánh"},
            {"name": "Nước mắm", "quantity": 2, "unit": "muỗng canh"},
            {"name": "Đường trắng", "quantity": 1, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Thịt gà chặt miếng vừa ăn. Cà chua bổ múi cau, me dầm nước ấm lấy nước cốt chua thanh.", "duration_min": 8},
            {"step_number": 2, "description": "Xào săn thịt gà với chút hành tím và nước mắm cho thơm.", "duration_min": 4},
            {"step_number": 3, "description": "Đổ 800ml nước vào đun sôi, hớt bọt, cho nước cốt me và cà chua vào nấu chín trong 10 phút.", "duration_min": 10},
            {"step_number": 4, "description": "Nêm gia vị vừa vị chua ngọt thanh nhẹ, múc ra bát rắc rau ngò và vài lát ớt cay.", "duration_min": 2}
        ]
    },
    {
        "name": "Cá diêu hồng chiên xù sốt chua ngọt",
        "description": "Cá diêu hồng giòn rụm màu vàng ruộm, kết hợp sốt cà chua dứa sánh mịn chua ngọt kích thích vị giác tuyệt đối.",
        "difficulty": "medium",
        "cook_time_min": 25,
        "prep_time_min": 15,
        "servings": 4,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800&auto=format&fit=crop&q=80",
        "tags": ["dưới 30 phút", "chua", "ngọt", "dễ nấu", "Miền Nam"],
        "ingredients": [
            {"name": "Cá diêu hồng", "quantity": 700, "unit": "g"},
            {"name": "Bột chiên giòn", "quantity": 80, "unit": "g"},
            {"name": "Cà chua", "quantity": 2, "unit": "quả"},
            {"name": "Dứa (thơm)", "quantity": 0.25, "unit": "quả"},
            {"name": "Hành lá", "quantity": 2, "unit": "nhánh"},
            {"name": "Tỏi", "quantity": 3, "unit": "tép"},
            {"name": "Nước mắm", "quantity": 2, "unit": "muỗng canh"},
            {"name": "Dầu ăn", "quantity": 150, "unit": "ml"},
        ],
        "steps": [
            {"step_number": 1, "description": "Cá diêu hồng làm sạch, khứa vẩy ca rô hai bên thân, để ráo rồi áo một lớp bột chiên giòn mỏng.", "duration_min": 10},
            {"step_number": 2, "description": "Đun nóng nhiều dầu trong chảo sâu lòng, chiên cá chín vàng giòn rụm cả 2 mặt rồi vớt ra đĩa.", "duration_min": 12},
            {"step_number": 3, "description": "Làm sốt: Phi tỏi băm, xào nhuyễn cà chua và dứa băm hạt lựu, nêm mắm đường cho sánh mịn chua ngọt.", "duration_min": 5},
            {"step_number": 4, "description": "Rưới đều nước sốt lên thân cá chiên giòn và thưởng thức ngay khi còn nóng giòn.", "duration_min": 2}
        ]
    },
    {
        "name": "Trứng chiên thịt bằm nấm mèo",
        "description": "Trứng gà đánh xốp chiên vàng ruộm, nhân thịt bằm béo mềm quyện mộc nhĩ giòn sần sật và hành hoa thơm nức mũi.",
        "difficulty": "easy",
        "cook_time_min": 10,
        "prep_time_min": 10,
        "servings": 3,
        "region": "mien_bac",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "dễ nấu", "Miền Bắc", "mặn"],
        "ingredients": [
            {"name": "Trứng gà", "quantity": 3, "unit": "quả"},
            {"name": "Thịt lợn (heo)", "quantity": 150, "unit": "g"},
            {"name": "Mộc nhĩ (nấm mèo)", "quantity": 20, "unit": "g"},
            {"name": "Hành lá", "quantity": 2, "unit": "nhánh"},
            {"name": "Nước mắm", "quantity": 1, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Tiêu đen", "quantity": 0.5, "unit": "muỗng cà phê"},
            {"name": "Dầu ăn", "quantity": 2, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Mộc nhĩ ngâm nước ấm cho nở mềm, rửa sạch rồi thái sợi nhỏ li ti. Thịt heo băm nhuyễn.", "duration_min": 8},
            {"step_number": 2, "description": "Đập trứng vào tô, cho thịt bằm, mộc nhĩ, hành hoa, nước mắm, hạt nêm và tiêu xay vào đánh đều.", "duration_min": 3},
            {"step_number": 3, "description": "Đun nóng chảo dầu, đổ hỗn hợp trứng vào tráng đều chảo, hạ lửa vừa đậy nắp cho chín mềm bên trong.", "duration_min": 4},
            {"step_number": 4, "description": "Lật mặt trứng chiên vàng xém thơm lừng cả 2 mặt rồi múc ra đĩa cắt miếng vừa ăn.", "duration_min": 3}
        ]
    },
    {
        "name": "Canh cà chua trứng đậu phụ",
        "description": "Món canh mây quốc dân nhẹ bụng, thanh mát với nước dùng chua ngọt từ cà chua, trứng kéo sợi bồng bềnh và đậu phụ mềm mịn.",
        "difficulty": "easy",
        "cook_time_min": 10,
        "prep_time_min": 5,
        "servings": 3,
        "region": "mien_bac",
        "image_url": "https://images.unsplash.com/photo-1541832676-9b763b0239ab?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "healthy", "dễ nấu", "chua", "Miền Bắc"],
        "ingredients": [
            {"name": "Trứng gà", "quantity": 2, "unit": "quả"},
            {"name": "Cà chua", "quantity": 2, "unit": "quả"},
            {"name": "Đậu phụ (tofu)", "quantity": 2, "unit": "bìa"},
            {"name": "Hành lá", "quantity": 2, "unit": "nhánh"},
            {"name": "Nước mắm", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Dầu ăn", "quantity": 1, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Cà chua bổ múi cau. Đậu phụ cắt miếng vuông nhỏ. Trứng gà đánh tan trong chén.", "duration_min": 4},
            {"step_number": 2, "description": "Phi thơm đầu hành lá với chút dầu ăn, xào cà chua chín mềm tạo màu đỏ tự nhiên.", "duration_min": 3},
            {"step_number": 3, "description": "Đổ 600ml nước vào đun sôi, nêm nước mắm và hạt nêm cho vừa miệng rồi thả đậu phụ vào.", "duration_min": 3},
            {"step_number": 4, "description": "Hạ nhỏ lửa, từ từ rót trứng vào nồi đồng thời khuấy nhẹ theo một chiều tạo vân mây đẹp mắt.", "duration_min": 2},
            {"step_number": 5, "description": "Rắc hành hoa thái nhỏ, tiêu xay lên rồi tắt bếp ngay.", "duration_min": 1}
        ]
    },
    {
        "name": "Mực xào chua ngọt cần tây dứa",
        "description": "Mực tươi giòn sần sật xào cùng dứa chua ngọt, cà chua mọng nước và hành tây thơm giòn, màu sắc rực rỡ bắt mắt.",
        "difficulty": "easy",
        "cook_time_min": 15,
        "prep_time_min": 10,
        "servings": 3,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800&auto=format&fit=crop&q=80",
        "tags": ["nhanh", "dưới 30 phút", "chua", "ngọt", "dễ nấu", "Miền Nam"],
        "ingredients": [
            {"name": "Mực", "quantity": 400, "unit": "g"},
            {"name": "Dứa (thơm)", "quantity": 0.5, "unit": "quả"},
            {"name": "Cà chua", "quantity": 2, "unit": "quả"},
            {"name": "Hành tây", "quantity": 0.5, "unit": "củ"},
            {"name": "Tỏi", "quantity": 3, "unit": "tép"},
            {"name": "Nước mắm", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Hạt nêm", "quantity": 1, "unit": "muỗng cà phê"},
            {"name": "Tiêu đen", "quantity": 0.5, "unit": "muỗng cà phê"},
            {"name": "Dầu ăn", "quantity": 2, "unit": "muỗng canh"},
        ],
        "steps": [
            {"step_number": 1, "description": "Mực làm sạch, khứa vảy rồng cắt miếng vừa ăn, chần nhanh qua nước sôi có gừng đập dập rồi vớt ra ngâm nước đá cho giòn.", "duration_min": 6},
            {"step_number": 2, "description": "Dứa thái lát mỏng, cà chua và hành tây bổ múi cau.", "duration_min": 4},
            {"step_number": 3, "description": "Phi thơm tỏi băm, cho mực vào xào nhanh tay trên lửa lớn trong 1 phút rồi trút ra đĩa riêng.", "duration_min": 2},
            {"step_number": 4, "description": "Cho dứa, cà chua và hành tây vào chảo xào chín tới, nêm mắm và hạt nêm cho vừa miệng.", "duration_min": 3},
            {"step_number": 5, "description": "Trút mực trở lại chảo đảo đều nhanh tay trong 1 phút, rắc tiêu xay và hành lá tắt bếp.", "duration_min": 2}
        ]
    },
    {
        "name": "Trứng vịt kho thịt ba chỉ kiểu truyền thống",
        "description": "Thịt ba chỉ béo ngậy mềm tan kết hợp cùng quả trứng vịt ngấm đều nước dừa thơm béo và màu cánh gián nâu óng, chuẩn vị Tết sum vầy.",
        "difficulty": "medium",
        "cook_time_min": 40,
        "prep_time_min": 15,
        "servings": 4,
        "region": "mien_nam",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
        "tags": ["mặn", "ngọt", "Miền Nam", "tiệc"],
        "ingredients": [
            {"name": "Trứng vịt", "quantity": 4, "unit": "quả"},
            {"name": "Ba chỉ heo", "quantity": 400, "unit": "g"},
            {"name": "Nước dừa tươi", "quantity": 250, "unit": "ml"},
            {"name": "Tỏi", "quantity": 4, "unit": "tép"},
            {"name": "Ớt đỏ", "quantity": 2, "unit": "trái"},
            {"name": "Nước mắm", "quantity": 3, "unit": "muỗng canh"},
            {"name": "Đường thốt nốt", "quantity": 1.5, "unit": "muỗng canh"},
            {"name": "Tiêu đen", "quantity": 1, "unit": "muỗng cà phê"},
        ],
        "steps": [
            {"step_number": 1, "description": "Trứng vịt luộc chín, bóc sạch vỏ. Ba chỉ heo cắt khối vuông 3-4cm chần sơ qua nước sôi.", "duration_min": 12},
            {"step_number": 2, "description": "Ướp thịt heo với nước mắm, đường thốt nốt, tỏi ớt băm và tiêu xay trong 20 phút.", "duration_min": 20},
            {"step_number": 3, "description": "Xào thịt trên chảo cho săn lại và mỡ trong veo.", "duration_min": 5},
            {"step_number": 4, "description": "Đổ nước dừa tươi vào nồi ngập thịt, đun sôi rồi vớt bọt, hạ nhỏ lửa kho liu riu 20 phút.", "duration_min": 20},
            {"step_number": 5, "description": "Thả trứng vịt vào kho cùng thêm 15-20 phút đến khi thịt mềm rục và trứng ngấm màu nâu cánh gián tuyệt đẹp.", "duration_min": 15}
        ]
    }
]


def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Bắt đầu nạp bổ sung các công thức món ăn còn thiếu...")
        created = 0
        skipped = 0
        errors = 0

        tag_map = {t.name: t for t in Tag.query.all()}
        ing_map = {i.name: i for i in Ingredient.query.all()}

        for recipe_data in ADDITIONAL_RECIPES:
            name = recipe_data["name"]

            # Kiểm tra xem món đã có chưa
            existing = Recipe.query.filter_by(name=name).first()
            if existing:
                skipped += 1
                print(f"  ⏭️ Đã có: {name}")
                continue

            try:
                recipe = Recipe(
                    name=name,
                    description=recipe_data.get("description", ""),
                    difficulty=recipe_data.get("difficulty", "medium"),
                    cook_time_min=recipe_data.get("cook_time_min", 25),
                    prep_time_min=recipe_data.get("prep_time_min", 10),
                    servings=recipe_data.get("servings", 3),
                    region=recipe_data.get("region"),
                    is_published=True,
                    image_url=recipe_data.get("image_url"),
                )
                db.session.add(recipe)
                db.session.flush()

                # Gắn tags
                for tag_name in recipe_data.get("tags", []):
                    tag = tag_map.get(tag_name)
                    if tag:
                        recipe.tags.append(tag)
                    else:
                        new_tag = Tag(name=tag_name, color="#4CAF50")
                        db.session.add(new_tag)
                        db.session.flush()
                        tag_map[tag_name] = new_tag
                        recipe.tags.append(new_tag)

                # Gắn ingredients
                for ing_data in recipe_data.get("ingredients", []):
                    ing_name = ing_data["name"]
                    ingredient = ing_map.get(ing_name)
                    if not ingredient:
                        print(f"  ⚠️ Nguyên liệu không tìm thấy: '{ing_name}' trong món '{name}'")
                        continue

                    ri = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=float(ing_data.get("quantity", 1)),
                        unit=ing_data.get("unit") or ingredient.unit,
                        is_optional=False,
                    )
                    db.session.add(ri)

                # Gắn steps
                for step_data in recipe_data.get("steps", []):
                    step = Step(
                        recipe_id=recipe.id,
                        step_number=int(step_data.get("step_number", 1)),
                        description=step_data.get("description", ""),
                        image_url=None,
                        duration_min=step_data.get("duration_min"),
                    )
                    db.session.add(step)

                db.session.commit()
                created += 1
                print(f"  ✅ Đã thêm [{created}]: {name}")

            except Exception as e:
                db.session.rollback()
                errors += 1
                print(f"  ❌ Lỗi khi thêm '{name}': {e}")

        print(f"\n{'='*50}")
        print("🎉 Hoàn tất nạp bổ sung công thức món ăn!")
        print(f"   Đã thêm mới   : {created} món")
        print(f"   Đã có sẵn     : {skipped} món")
        print(f"   Lỗi           : {errors} món")
        print(f"   Tổng món trong DB : {Recipe.query.count()} món")
        print(f"{'='*50}")


if __name__ == "__main__":
    seed()
