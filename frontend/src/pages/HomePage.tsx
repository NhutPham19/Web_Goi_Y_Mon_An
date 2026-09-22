import React, { useEffect, useState } from 'react';
import { recipesApi } from '@/api/recipes';
import { Recipe } from '@/types';
import { RecipeCard } from '@/components/recipes/RecipeCard';
import { BentoGrid, BentoGridItem } from '@/components/animations/BentoGrid';
import { MorphSVG } from '@/components/animations/MorphSVG';
import { GlowCard } from '@/components/animations/GlowCard';
import { 
  Search, 
  Sparkles, 
  Flame, 
  Clock, 
  ArrowRight, 
  Compass, 
  ChefHat, 
  Filter, 
  Utensils 
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

  useEffect(() => {
    const fetchRecipes = async () => {
      setLoading(true);
      try {
        const params: any = { limit: 24 };
        if (selectedRegion !== 'all') params.region = selectedRegion;
        if (selectedDifficulty !== 'all') params.difficulty = selectedDifficulty;
        if (searchQuery.trim()) params.search = searchQuery.trim();

        const res = await recipesApi.getAll(params);
        if (res.success && res.data) {
          setRecipes(res.data);
        }
      } catch (err) {
        console.error('Failed to load recipes', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecipes();
  }, [selectedRegion, selectedDifficulty, searchQuery]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  // Bento highlights
  const topRated = recipes.slice(0, 4);

  return (
    <div className="space-y-16 pb-16">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden pt-8 pb-16 md:pt-16 md:pb-24">
        {/* Background glow orbs */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-orange-100/60 via-amber-50/40 to-transparent blur-3xl -z-10" />

        <div className="container mx-auto px-4 text-center">
          {/* Animated Pill Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-orange-100/80 border border-orange-200 text-brand-700 text-xs font-semibold mb-6 shadow-xs animate-fade-in-up">
            <Sparkles className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
            <span>AI Đề Xuất Món Ăn Theo Khẩu Vị & Nguyên Liệu Có Sẵn</span>
          </div>

          <div className="flex flex-col items-center justify-center max-w-3xl mx-auto space-y-4">
            <div className="flex items-center gap-4">
              <MorphSVG size={52} color="#ea580c" />
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-neutral-900 tracking-tight font-heading">
                Hôm nay ăn gì? <br />
                <span className="bg-gradient-to-r from-brand-600 via-orange-500 to-amber-500 bg-clip-text text-transparent">
                  Để AI lo từ A đến Z!
                </span>
              </h1>
            </div>

            <p className="text-base sm:text-lg text-neutral-600 max-w-2xl leading-relaxed">
              Khám phá hơn 60 món ăn truyền thống 3 miền, tìm món nhanh từ nguyên liệu trong tủ lạnh và nhận thực đơn cá nhân hóa dựa trên học máy thông minh.
            </p>
          </div>

          {/* Quick Search Bar */}
          <form
            onSubmit={handleSearchSubmit}
            className="mt-8 max-w-xl mx-auto relative flex items-center shadow-lg shadow-orange-500/10 rounded-2xl bg-white border border-orange-200/80 p-1.5 focus-within:border-brand-500 transition"
          >
            <div className="pl-3.5 text-neutral-400">
              <Search className="w-5 h-5 text-brand-500" />
            </div>
            <input
              type="text"
              placeholder="Tìm món ngon: Phở bò, Canh chua, Bò lúc lắc..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2.5 text-sm bg-transparent focus:outline-none text-neutral-800 placeholder:text-neutral-400"
            />
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-amber-500 text-white text-sm font-semibold shadow-sm hover:shadow transition hover:-translate-y-0.5"
            >
              Tìm kiếm
            </button>
          </form>

          {/* Action Callouts */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/search-ingredients"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-2xl bg-white border border-neutral-200 text-neutral-800 text-sm font-semibold shadow-xs hover:border-brand-300 hover:shadow-md transition group"
            >
              <span className="text-lg">🥕</span>
              <span>Tìm món bằng nguyên liệu có sẵn</span>
              <ArrowRight className="w-4 h-4 text-brand-500 group-hover:translate-x-1 transition" />
            </Link>

            <Link
              to="/recommend"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 text-white text-sm font-semibold shadow-md shadow-orange-500/20 hover:shadow-lg transition group hover:-translate-y-0.5"
            >
              <Sparkles className="w-4 h-4 fill-white" />
              <span>Gợi ý khẩu vị hôm nay (AI)</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 21st.dev BENTO GRID DISCOVERY */}
      <section className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-widest">
              <Compass className="w-3.5 h-3.5" /> Khám phá nhanh
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold text-neutral-900 font-heading">
              Góc Ẩm Thực Chọn Lọc
            </h2>
          </div>
        </div>

        <BentoGrid className="max-w-7xl">
          <BentoGridItem
            title="Đặc Sản Miền Nam Nồng Nàn"
            description="Cơm tấm sườn bì chả, Canh chua cá lóc, Cá kho tộ, Bánh xèo miền Tây đậm vị ngọt béo."
            badge="Top Yêu Thích"
            className="md:col-span-2"
            onClick={() => setSelectedRegion('mien_nam')}
            icon={<ChefHat className="w-4 h-4 text-brand-500" />}
            header={
              <img
                src="https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80"
                alt="Miền Nam"
                className="w-full h-full object-cover"
              />
            }
          />

          <BentoGridItem
            title="Tinh Hoa Vị Bắc"
            description="Phở bò truyền thống, Bún chả than hoa nướng, Bún thang thanh tao."
            className="md:col-span-1"
            onClick={() => setSelectedRegion('mien_bac')}
            icon={<Sparkles className="w-4 h-4 text-amber-500" />}
            header={
              <img
                src="https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80"
                alt="Miền Bắc"
                className="w-full h-full object-cover"
              />
            }
          />

          <BentoGridItem
            title="Món Nhanh Dưới 30 Phút"
            description="Dành cho những ngày bận rộn: Trứng chiên cà chua, Bò xào, Tôm rang mặn ngọt."
            badge="Tiện Lợi"
            className="md:col-span-1"
            onClick={() => setSelectedDifficulty('easy')}
            icon={<Clock className="w-4 h-4 text-emerald-500" />}
            header={
              <img
                src="https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80"
                alt="Món Nhanh"
                className="w-full h-full object-cover"
              />
            }
          />

          <BentoGridItem
            title="Đậm Đà Đất Miền Trung"
            description="Bún bò xứ Huế cay nồng, Mì Quảng đậm vị tôm thịt, Cao lầu Hội An trứ danh."
            className="md:col-span-2"
            onClick={() => setSelectedRegion('mien_trung')}
            icon={<Flame className="w-4 h-4 text-rose-500" />}
            header={
              <img
                src="https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80"
                alt="Miền Trung"
                className="w-full h-full object-cover"
              />
            }
          />
        </BentoGrid>
      </section>

      {/* RECIPES FILTER & LISTING */}
      <section className="container mx-auto px-4 pt-8">
        {/* Header & Filter Controls */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-4 border-b border-neutral-200">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900 font-heading">
              Tất Cả Công Thức Nấu Ăn
            </h2>
            <p className="text-sm text-neutral-500 mt-1">
              Hiển thị <span className="font-bold text-brand-600">{recipes.length}</span> món ăn chuẩn vị
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Region filters */}
            <div className="flex items-center gap-1 bg-neutral-100 p-1 rounded-xl">
              {[
                { id: 'all', label: 'Tất cả' },
                { id: 'mien_bac', label: 'Miền Bắc' },
                { id: 'mien_trung', label: 'Miền Trung' },
                { id: 'mien_nam', label: 'Miền Nam' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setSelectedRegion(tab.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                    selectedRegion === tab.id
                      ? 'bg-white text-neutral-900 shadow-xs font-semibold'
                      : 'text-neutral-500 hover:text-neutral-800'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Difficulty dropdown/toggle */}
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-3 py-2 rounded-xl bg-white border border-neutral-200 text-xs font-medium text-neutral-700 focus:outline-none focus:border-brand-500"
            >
              <option value="all">Độ khó: Tất cả</option>
              <option value="easy">Dễ nấu</option>
              <option value="medium">Trung bình</option>
              <option value="hard">Cầu kỳ / Khó</option>
            </select>
          </div>
        </div>

        {/* Recipe Grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
              <div key={n} className="rounded-3xl bg-neutral-100 h-80 animate-pulse" />
            ))}
          </div>
        ) : recipes.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-3xl border border-neutral-100 p-8">
            <Utensils className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-neutral-800">Không tìm thấy món ăn phù hợp</h3>
            <p className="text-sm text-neutral-500 mt-1">
              Thử xóa bộ lọc hoặc tìm kiếm với từ khóa khác nhé!
            </p>
            <button
              onClick={() => {
                setSelectedRegion('all');
                setSelectedDifficulty('all');
                setSearchQuery('');
              }}
              className="mt-4 px-4 py-2 text-xs font-semibold text-brand-600 bg-brand-50 rounded-xl hover:bg-brand-100 transition"
            >
              Đặt lại tất cả bộ lọc
            </button>
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
