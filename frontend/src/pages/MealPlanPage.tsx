import React, { useEffect, useState } from 'react';
import { mealPlansApi } from '@/api/mealPlans';
import { MealPlanItem, ShoppingListItem } from '@/types';
import { useAuth } from '@/context/AuthContext';
import { 
  CalendarDays, 
  ShoppingBag, 
  Trash2, 
  Plus, 
  CheckSquare, 
  Square, 
  Utensils, 
  Clock, 
  Sparkles,
  Printer
} from 'lucide-react';
import { toast } from 'sonner';
import { Link } from 'react-router-dom';

export const MealPlanPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [plans, setPlans] = useState<MealPlanItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Shopping list modal
  const [shoppingList, setShoppingList] = useState<ShoppingListItem[]>([]);
  const [showShoppingList, setShowShoppingList] = useState(false);
  const [loadingShoppingList, setLoadingShoppingList] = useState(false);
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  const daysOfWeek = [
    { key: 'mon', label: 'Thứ 2' },
    { key: 'tue', label: 'Thứ 3' },
    { key: 'wed', label: 'Thứ 4' },
    { key: 'thu', label: 'Thứ 5' },
    { key: 'fri', label: 'Thứ 6' },
    { key: 'sat', label: 'Thứ 7' },
    { key: 'sun', label: 'Chủ Nhật' },
  ];

  const fetchPlans = async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const res = await mealPlansApi.getAll();
      if (res.success && res.data) {
        setPlans(res.data);
      }
    } catch {
      toast.error('Không thể tải thực đơn tuần');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, [isAuthenticated]);

  const handleDelete = async (id: number) => {
    try {
      await mealPlansApi.remove(id);
      setPlans((prev) => prev.filter((p) => p.id !== id));
      toast.success('Đã xóa món khỏi thực đơn');
    } catch {
      toast.error('Không thể xóa món');
    }
  };

  const handleGenerateShoppingList = async () => {
    if (!isAuthenticated) {
      toast.error('Vui lòng đăng nhập để tạo danh sách đi chợ!');
      return;
    }
    setLoadingShoppingList(true);
    setShowShoppingList(true);
    try {
      const res = await mealPlansApi.getShoppingList();
      if (res.success && res.data) {
        setShoppingList(res.data);
      }
    } catch {
      toast.error('Không thể tổng hợp danh sách đi chợ');
    } finally {
      setLoadingShoppingList(false);
    }
  };

  const toggleCheckItem = (id: number) => {
    setCheckedItems((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-20 text-center max-w-md">
        <div className="w-16 h-16 rounded-3xl bg-orange-100 text-brand-600 flex items-center justify-center mx-auto mb-4">
          <CalendarDays className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-neutral-900 font-heading">
          Lập Kế Hoạch Bữa Ăn Tuần
        </h2>
        <p className="text-sm text-neutral-500 mt-2 leading-relaxed">
          Đăng nhập ngay để tự động phân bổ bữa ăn trong tuần và tự động tạo danh sách đi chợ thông minh (tổng hợp khối lượng thịt, rau, gia vị)!
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Quản lý bữa ăn gia đình
          </div>
          <h1 className="text-3xl font-black text-neutral-900 font-heading">
            Thực Đơn Tuần & Danh Sách Đi Chợ
          </h1>
          <p className="text-xs text-neutral-500 mt-1">
            Đã lên kế hoạch cho <span className="font-bold text-brand-600">{plans.length}</span> món ăn
          </p>
        </div>

        {/* Generate Shopping list button */}
        <button
          onClick={handleGenerateShoppingList}
          className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold text-sm shadow-md shadow-emerald-600/20 hover:shadow-lg transition hover:-translate-y-0.5 flex items-center gap-2"
        >
          <ShoppingBag className="w-4 h-4" />
          <span>Tạo Danh Sách Đi Chợ Tự Động</span>
        </button>
      </div>

      {/* SCHEDULE CARDS */}
      {loading ? (
        <div className="py-20 text-center text-sm text-neutral-400">Đang tải lịch ăn uống...</div>
      ) : plans.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-neutral-100 p-8">
          <CalendarDays className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-neutral-800">Chưa có món nào trong thực đơn tuần</h3>
          <p className="text-sm text-neutral-500 mt-1">
            Hãy khám phá các công thức nấu ăn và bấm "Xếp món này vào Thực Đơn Tuần"!
          </p>
          <Link
            to="/"
            className="mt-4 px-5 py-2.5 inline-block text-xs font-semibold text-white bg-brand-600 rounded-xl hover:bg-brand-700 transition"
          >
            Khám phá món ngon ngay
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((item) => (
            <div
              key={item.id}
              className="p-5 rounded-3xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between hover:shadow-md transition"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
                    {item.date} • {item.meal_type === 'breakfast' ? 'Bữa Sáng' : item.meal_type === 'lunch' ? 'Bữa Trưa' : 'Bữa Tối'}
                  </span>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="text-neutral-400 hover:text-rose-600 p-1 rounded-lg transition"
                    title="Xóa món này"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex gap-3">
                  <img
                    src={item.recipe?.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'}
                    alt={item.recipe?.name}
                    className="w-20 h-20 rounded-2xl object-cover"
                  />
                  <div>
                    <Link
                      to={`/recipes/${item.recipe?.id}`}
                      className="font-bold text-sm text-neutral-900 hover:text-brand-600 transition font-heading line-clamp-1"
                    >
                      {item.recipe?.name}
                    </Link>
                    <p className="text-xs text-neutral-500 mt-1 flex items-center gap-1">
                      <Clock className="w-3 h-3 text-brand-500" />
                      <span>{item.recipe?.cook_time_min} phút</span>
                      <span>• {item.servings} người ăn</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SHOPPING LIST MODAL */}
      {showShoppingList && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in-up">
          <div className="relative w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl border border-neutral-100 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-neutral-100">
              <div className="flex items-center gap-2">
                <div className="p-2.5 rounded-xl bg-emerald-100 text-emerald-700">
                  <ShoppingBag className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-neutral-900 font-heading">
                    Danh Sách Đi Chợ Tổng Hợp
                  </h3>
                  <p className="text-xs text-neutral-500">
                    Đã cộng dồn khối lượng tất cả nguyên liệu cho tuần này
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowShoppingList(false)}
                className="text-neutral-400 hover:text-neutral-700 p-1"
              >
                ✕
              </button>
            </div>

            {/* Content list */}
            <div className="flex-1 overflow-y-auto py-4 divide-y divide-neutral-100">
              {loadingShoppingList ? (
                <div className="py-12 text-center text-sm text-neutral-400">
                  Đang cộng dồn nguyên liệu...
                </div>
              ) : shoppingList.length === 0 ? (
                <div className="py-12 text-center text-sm text-neutral-500">
                  Chưa có nguyên liệu nào cần mua. Hãy thêm món vào thực đơn trước nhé!
                </div>
              ) : (
                shoppingList.map((item) => {
                  const isDone = !!checkedItems[item.ingredient_id];
                  return (
                    <div
                      key={item.ingredient_id}
                      onClick={() => toggleCheckItem(item.ingredient_id)}
                      className="py-3 px-2 flex items-center justify-between cursor-pointer hover:bg-neutral-50 rounded-xl transition"
                    >
                      <div className="flex items-center gap-3">
                        {isDone ? (
                          <CheckSquare className="w-5 h-5 text-emerald-600" />
                        ) : (
                          <Square className="w-5 h-5 text-neutral-300" />
                        )}
                        <span className="text-lg">{item.emoji || '🛒'}</span>
                        <span
                          className={`text-sm font-medium ${
                            isDone ? 'line-through text-neutral-400' : 'text-neutral-800'
                          }`}
                        >
                          {item.name}
                        </span>
                      </div>
                      <span className="font-bold text-brand-600 text-xs">
                        {Math.round(item.total_quantity * 10) / 10} {item.unit}
                      </span>
                    </div>
                  );
                })
              )}
            </div>

            <div className="pt-4 border-t border-neutral-100 flex items-center justify-between">
              <span className="text-xs text-neutral-400">
                Tip: Tích chọn để đánh dấu nguyên liệu đã mua xong.
              </span>
              <button
                onClick={() => setShowShoppingList(false)}
                className="px-5 py-2 rounded-xl bg-brand-600 text-white text-xs font-semibold shadow-xs"
              >
                Xong
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
