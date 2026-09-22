import React, { useEffect, useState } from 'react';
import { recommendationsApi } from '@/api/recommendations';
import { Recipe } from '@/types';
import { RecipeCard } from '@/components/recipes/RecipeCard';
import { MorphSVG } from '@/components/animations/MorphSVG';
import { useAuth } from '@/context/AuthContext';
import { Sparkles, RefreshCw, Sliders, CheckCircle2, ShieldAlert } from 'lucide-react';
import { toast } from 'sonner';

export const RecommendPage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Preference filters
  const [taste, setTaste] = useState<'all' | 'spicy' | 'mild' | 'sweet'>('all');
  const [diet, setDiet] = useState<'all' | 'vegetarian' | 'healthy'>('all');
  const [region, setRegion] = useState<'all' | 'mien_bac' | 'mien_trung' | 'mien_nam'>('all');

  const fetchRecommendations = async (force = false) => {
    if (force) setRefreshing(true);
    else setLoading(true);

    try {
      const res = await recommendationsApi.getForMe(12, force);
      if (res.success && res.data) {
        setRecipes(res.data);
      }
    } catch {
      toast.error('Không thể tải gợi ý lúc này');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [isAuthenticated]);

  const handleApplyPreferences = async () => {
    if (!isAuthenticated) {
      toast.info('Đăng nhập để lưu khẩu vị cá nhân lâu dài nhé!');
      fetchRecommendations(true);
      return;
    }

    try {
      const prefs: Array<{ pref_type: string; pref_value: string }> = [];
      if (taste !== 'all') prefs.push({ pref_type: 'taste', pref_value: taste });
      if (diet !== 'all') prefs.push({ pref_type: 'diet', pref_value: diet });
      if (region !== 'all') prefs.push({ pref_type: 'region', pref_value: region });

      await recommendationsApi.updatePreferences(prefs);
      toast.success('Đã cập nhật hồ sơ khẩu vị thành công!');
      fetchRecommendations(true);
    } catch {
      toast.error('Có lỗi khi cập nhật khẩu vị');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-10">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-100 text-amber-800 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 fill-amber-600 text-amber-600" />
          <span>Thuật toán Hybrid Recommendation (CBF 60% + CF 40%)</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-neutral-900 font-heading">
          Gợi Ý Hôm Nay Dành Riêng Cho Bạn
        </h1>
        <p className="text-sm text-neutral-600">
          Hệ thống phân tích điểm tương đồng nội dung món ăn kết hợp hành vi đánh giá từ cộng đồng để đề xuất các món ăn chuẩn gu bạn nhất.
        </p>
      </div>

      {/* PREFERENCES ADJUSTER */}
      <div className="rounded-3xl bg-gradient-to-r from-orange-50/70 via-amber-50/70 to-orange-50/70 border border-orange-200/80 p-6 shadow-xs space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-brand-600" />
            <h3 className="font-bold text-sm text-neutral-800 font-heading">
              Tùy Chỉnh Khẩu Vị Hiện Tại
            </h3>
          </div>
          <button
            onClick={() => fetchRecommendations(true)}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-neutral-200 text-xs font-medium text-neutral-700 hover:bg-neutral-50 shadow-2xs transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-brand-500' : ''}`} />
            <span>Làm mới gợi ý</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Taste */}
          <div>
            <label className="block text-xs font-semibold text-neutral-600 mb-1.5">Vị giác</label>
            <div className="flex flex-wrap gap-1.5">
              {[
                { id: 'all', label: 'Tất cả' },
                { id: 'spicy', label: '🌶️ Cay nồng' },
                { id: 'mild', label: '🍲 Thanh đạm' },
                { id: 'sweet', label: '🍯 Ngọt ngào' },
              ].map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setTaste(opt.id as any)}
                  className={`px-3 py-1.5 rounded-xl text-xs transition ${
                    taste === opt.id
                      ? 'bg-brand-600 text-white font-semibold'
                      : 'bg-white text-neutral-600 border border-neutral-200 hover:bg-neutral-50'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Diet */}
          <div>
            <label className="block text-xs font-semibold text-neutral-600 mb-1.5">Chế độ ăn</label>
            <div className="flex flex-wrap gap-1.5">
              {[
                { id: 'all', label: 'Bình thường' },
                { id: 'vegetarian', label: '🥗 Ăn chay' },
                { id: 'healthy', label: '🥑 Ít dầu mỡ' },
              ].map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setDiet(opt.id as any)}
                  className={`px-3 py-1.5 rounded-xl text-xs transition ${
                    diet === opt.id
                      ? 'bg-emerald-600 text-white font-semibold'
                      : 'bg-white text-neutral-600 border border-neutral-200 hover:bg-neutral-50'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Region */}
          <div>
            <label className="block text-xs font-semibold text-neutral-600 mb-1.5">Vùng miền</label>
            <div className="flex flex-wrap gap-1.5">
              {[
                { id: 'all', label: 'Cả 3 miền' },
                { id: 'mien_bac', label: 'Miền Bắc' },
                { id: 'mien_trung', label: 'Miền Trung' },
                { id: 'mien_nam', label: 'Miền Nam' },
              ].map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setRegion(opt.id as any)}
                  className={`px-3 py-1.5 rounded-xl text-xs transition ${
                    region === opt.id
                      ? 'bg-amber-600 text-white font-semibold'
                      : 'bg-white text-neutral-600 border border-neutral-200 hover:bg-neutral-50'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-2 text-right">
          <button
            onClick={handleApplyPreferences}
            className="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-xs transition"
          >
            Lưu khẩu vị & Gợi ý lại
          </button>
        </div>
      </div>

      {/* RECOMMENDATIONS GRID */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-500" />
            <h2 className="text-2xl font-bold text-neutral-900 font-heading">
              {isAuthenticated ? `Món Dành Riêng Cho ${user?.full_name}` : 'Món Ăn Được Yêu Thích Nhất'}
            </h2>
          </div>
        </div>

        {loading ? (
          <div className="py-24 text-center">
            <MorphSVG size={64} color="#ea580c" className="mx-auto mb-4" />
            <p className="text-sm font-medium text-neutral-600">AI đang tính toán điểm tương thích...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {recipes.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
