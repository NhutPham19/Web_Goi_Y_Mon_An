import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { recipesApi } from '@/api/recipes';
import { mealPlansApi } from '@/api/mealPlans';
import { Recipe } from '@/types';
import { CookingTimer } from '@/components/recipes/CookingTimer';
import { SubstituteModal } from '@/components/recipes/SubstituteModal';
import { useAuth } from '@/context/AuthContext';
import { 
  Clock, 
  Users, 
  Star, 
  Bookmark, 
  CalendarPlus, 
  ArrowLeft, 
  Check, 
  Sparkles, 
  ChefHat, 
  HelpCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

export const RecipeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated } = useAuth();

  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [servingsScale, setServingsScale] = useState(4);

  // Substitute modal
  const [subModalOpen, setSubModalOpen] = useState(false);
  const [activeIngredientId, setActiveIngredientId] = useState<number | null>(null);
  const [activeIngredientName, setActiveIngredientName] = useState('');

  // Rating input
  const [userRating, setUserRating] = useState(5);
  const [reviewText, setReviewText] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);

  // Meal Plan quick add
  const [addingMealPlan, setAddingMealPlan] = useState(false);

  useEffect(() => {
    if (!id) return;

    const fetchRecipe = async () => {
      setLoading(true);
      try {
        const res = await recipesApi.getById(id);
        if (res.success && res.data) {
          setRecipe(res.data);
          setServingsScale(res.data.servings || 4);
          setIsSaved(res.data.is_saved || false);
          // Fire-and-forget view history recording
          recipesApi.recordView(res.data.id);
        }
      } catch {
        toast.error('Không tìm thấy món ăn này');
      } finally {
        setLoading(false);
      }
    };

    fetchRecipe();
  }, [id]);

  const handleToggleSave = async () => {
    if (!isAuthenticated || !recipe) {
      toast.error('Vui lòng đăng nhập để lưu món ăn!');
      return;
    }
    try {
      if (isSaved) {
        await recipesApi.unsaveRecipe(recipe.id);
        setIsSaved(false);
        toast.info(`Đã bỏ lưu món ${recipe.name}`);
      } else {
        await recipesApi.saveRecipe(recipe.id);
        setIsSaved(true);
        toast.success(`Đã thêm ${recipe.name} vào danh sách yêu thích! ❤️`);
      }
    } catch {
      toast.error('Có lỗi xảy ra');
    }
  };

  const handleRate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated || !recipe) {
      toast.error('Vui lòng đăng nhập để gửi đánh giá!');
      return;
    }
    setSubmittingRating(true);
    try {
      const res = await recipesApi.rate(recipe.id, userRating, reviewText);
      if (res.success) {
        toast.success('Cảm ơn bạn đã đánh giá món ăn! ⭐');
        setReviewText('');
        // Refresh recipe rating
        const updated = await recipesApi.getById(recipe.id);
        if (updated.success && updated.data) setRecipe(updated.data);
      }
    } catch {
      toast.error('Có lỗi khi gửi đánh giá');
    } finally {
      setSubmittingRating(false);
    }
  };

  const handleQuickAddMealPlan = async () => {
    if (!isAuthenticated || !recipe) {
      toast.error('Vui lòng đăng nhập để lập thực đơn!');
      return;
    }
    setAddingMealPlan(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      await mealPlansApi.add(today, 'lunch', recipe.id, servingsScale);
      toast.success(`Đã xếp ${recipe.name} vào thực đơn trưa hôm nay! 📅`);
    } catch {
      toast.error('Có lỗi khi thêm vào thực đơn');
    } finally {
      setAddingMealPlan(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-neutral-500">Đang tải công thức nấu ăn...</p>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
        <h2 className="text-xl font-bold">Không tìm thấy món ăn</h2>
        <Link to="/" className="text-brand-600 text-sm font-semibold hover:underline mt-2 inline-block">
          ← Quay lại trang chủ
        </Link>
      </div>
    );
  }

  const baseServings = recipe.servings || 4;
  const ratio = servingsScale / baseServings;

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl space-y-10">
      {/* Back button */}
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-neutral-500 hover:text-brand-600 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Quay lại danh sách món ăn</span>
      </Link>

      {/* HERO BANNER */}
      <div className="relative rounded-3xl overflow-hidden bg-white border border-slate-200/80 shadow-sm">
        <div className="relative aspect-21/9 md:aspect-16/7 w-full overflow-hidden bg-slate-900">
          <img
            src={recipe.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'}
            alt={recipe.name}
            className="w-full h-full object-cover opacity-90"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-black/10" />

          {/* Floating actions on image */}
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <button
              onClick={handleToggleSave}
              className={`p-3 rounded-full backdrop-blur-md transition shadow-md ${
                isSaved
                  ? 'bg-rose-500 text-white hover:bg-rose-600 scale-105'
                  : 'bg-white/80 text-neutral-800 hover:bg-white'
              }`}
              title={isSaved ? 'Bỏ lưu' : 'Lưu món ăn'}
            >
              <Bookmark className={`w-5 h-5 ${isSaved ? 'fill-current' : ''}`} />
            </button>
          </div>

          {/* Hero text overlay */}
          <div className="absolute bottom-6 inset-x-6 text-white space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              {recipe.tags?.map((t) => (
                <span
                  key={t.id}
                  className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-white/20 backdrop-blur-md text-white"
                >
                  #{t.name}
                </span>
              ))}
            </div>
            <h1 className="text-2xl sm:text-4xl font-black font-heading tracking-tight">
              {recipe.name}
            </h1>
            <p className="text-xs sm:text-sm text-neutral-200 line-clamp-2 max-w-3xl">
              {recipe.description}
            </p>
          </div>
        </div>

        {/* Quick Meta Strip */}
        <div className="p-6 grid grid-cols-2 sm:grid-cols-4 gap-4 bg-orange-50/40 border-t border-neutral-100 text-neutral-700 text-xs font-medium">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-orange-100 text-brand-700">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <span className="block text-neutral-400 text-[10px] uppercase">Thời gian nấu</span>
              <span className="font-bold text-sm text-neutral-900">{recipe.cook_time_min} phút</span>
              <span className="text-[10px] text-neutral-500 ml-1">(Chuẩn bị {recipe.prep_time_min}p)</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-100 text-amber-700">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <span className="block text-neutral-400 text-[10px] uppercase">Khẩu phần chuẩn</span>
              <span className="font-bold text-sm text-neutral-900">{recipe.servings} người ăn</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-100 text-emerald-700">
              <ChefHat className="w-5 h-5" />
            </div>
            <div>
              <span className="block text-neutral-400 text-[10px] uppercase">Độ khó</span>
              <span className="font-bold text-sm text-neutral-900 capitalize">
                {recipe.difficulty === 'easy' ? 'Dễ' : recipe.difficulty === 'medium' ? 'Vừa' : 'Khó'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-rose-100 text-rose-700">
              <Star className="w-5 h-5 fill-rose-500 text-rose-500" />
            </div>
            <div>
              <span className="block text-neutral-400 text-[10px] uppercase">Đánh giá</span>
              <span className="font-bold text-sm text-neutral-900">
                {recipe.avg_rating ? recipe.avg_rating.toFixed(1) : '5.0'} / 5.0
              </span>
              <span className="text-[10px] text-neutral-500 ml-1">({recipe.rating_count || 12} lượt)</span>
            </div>
          </div>
        </div>
      </div>

      {/* BODY CONTENT: INGREDIENTS & STEPS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LEFT COLUMN: INGREDIENTS CHECKLIST (1 col) */}
        <div className="lg:col-span-1 space-y-6">
          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-neutral-900 font-heading">
                Nguyên Liệu
              </h2>
              {/* Servings scale buttons */}
              <div className="flex items-center gap-1 bg-neutral-100 p-1 rounded-xl">
                {[2, 4, 6].map((num) => (
                  <button
                    key={num}
                    onClick={() => setServingsScale(num)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                      servingsScale === num
                        ? 'bg-white text-brand-600 shadow-xs'
                        : 'text-neutral-500 hover:text-neutral-900'
                    }`}
                  >
                    {num} người
                  </button>
                ))}
              </div>
            </div>

            {/* List */}
            <div className="divide-y divide-neutral-100 text-sm">
              {recipe.ingredients?.map((item) => {
                const scaledQuantity = Math.round(item.quantity * ratio * 10) / 10;
                return (
                  <div key={item.ingredient_id} className="py-2.5 flex items-center justify-between group">
                    <div className="flex items-center gap-2">
                      <span className="text-base">{item.emoji || '🌿'}</span>
                      <span className="font-medium text-neutral-800">{item.name}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="font-bold text-brand-600 text-xs">
                        {scaledQuantity} {item.unit}
                      </span>
                      {/* Substitute button */}
                      <button
                        onClick={() => {
                          setActiveIngredientId(item.ingredient_id);
                          setActiveIngredientName(item.name);
                          setSubModalOpen(true);
                        }}
                        className="p-1 rounded-md text-neutral-300 hover:text-amber-500 hover:bg-amber-50 transition"
                        title="Xem nguyên liệu thay thế"
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Add to Meal Plan Button */}
            <button
              onClick={handleQuickAddMealPlan}
              disabled={addingMealPlan}
              className="w-full py-3 rounded-2xl bg-orange-100 hover:bg-orange-200 text-brand-800 text-xs font-bold transition flex items-center justify-center gap-2"
            >
              <CalendarPlus className="w-4 h-4 text-brand-600" />
              <span>Xếp món này vào Thực Đơn Tuần</span>
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: COOKING STEPS & TIMER (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-sm space-y-6">
            <h2 className="text-lg font-bold text-neutral-900 font-heading">
              Các Bước Chế Biến Chi Tiết
            </h2>

            <div className="space-y-6">
              {recipe.steps?.map((step) => (
                <div
                  key={step.step_number}
                  className="flex gap-4 p-4 rounded-2xl bg-neutral-50/70 border border-neutral-100"
                >
                  {/* Step number badge */}
                  <div className="w-8 h-8 rounded-xl bg-brand-600 text-white font-bold text-sm flex items-center justify-center shrink-0 shadow-xs">
                    {step.step_number}
                  </div>

                  {/* Step details */}
                  <div className="flex-1 space-y-3">
                    <p className="text-sm text-neutral-700 leading-relaxed">
                      {step.description}
                    </p>

                    {/* Integrated Cooking Timer if duration is set */}
                    {step.duration_min && step.duration_min > 0 && (
                      <CookingTimer
                        initialMinutes={step.duration_min}
                        stepTitle={`Bước ${step.step_number}: Hẹn giờ ${step.duration_min} phút`}
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* RATING & REVIEW FORM */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-neutral-900 font-heading">
              Đánh Giá & Trải Nghiệm Món Ăn Này
            </h3>
            <form onSubmit={handleRate} className="space-y-3">
              {/* Star selector */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-neutral-500">Chấm điểm:</span>
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      type="button"
                      key={star}
                      onClick={() => setUserRating(star)}
                      className="p-1 hover:scale-110 transition"
                    >
                      <Star
                        className={`w-5 h-5 ${
                          star <= userRating
                            ? 'text-amber-400 fill-amber-400'
                            : 'text-neutral-300'
                        }`}
                      />
                    </button>
                  ))}
                </div>
                <span className="text-xs font-bold text-amber-600 ml-2">
                  {userRating === 5 ? 'Tuyệt vời!' : userRating === 4 ? 'Rất ngon' : 'Khá ổn'}
                </span>
              </div>

              {/* Review input */}
              <textarea
                rows={2}
                placeholder="Chia sẻ cảm nhận hoặc bí quyết nấu món này của bạn..."
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                className="w-full p-3 rounded-xl border border-neutral-200 text-xs focus:outline-none focus:border-brand-500"
              />

              <div className="text-right">
                <button
                  type="submit"
                  disabled={submittingRating}
                  className="px-6 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-xs transition"
                >
                  {submittingRating ? 'Đang gửi...' : 'Gửi Đánh Giá'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Substitute Modal */}
      <SubstituteModal
        ingredientId={activeIngredientId}
        ingredientName={activeIngredientName}
        isOpen={subModalOpen}
        onClose={() => setSubModalOpen(false)}
      />
    </div>
  );
};
