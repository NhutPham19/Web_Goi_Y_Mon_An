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
  Utensils,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  CheckCircle2
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

interface CollectionItem {
  id: string;
  title: string;
  description: string;
  badge?: string;
  colSpan: string;
  filterType: 'region' | 'difficulty' | 'search' | 'all';
  value: string;
  icon: React.ReactNode;
  imageUrl: string;
}

const FEATURED_COLLECTIONS: CollectionItem[] = [
  {
    id: 'mien_nam',
    title: 'Đặc Sản Miền Nam Nồng Nàn',
    description: 'Cơm tấm sườn bì chả, Canh chua cá lóc, Cá kho tộ, Bánh xèo miền Tây đậm vị ngọt béo khó quên.',
    badge: 'Top Yêu Thích',
    colSpan: 'md:col-span-2',
    filterType: 'region',
    value: 'mien_nam',
    icon: <ChefHat className="w-4 h-4 text-orange-500" />,
    imageUrl: 'https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'mien_bac',
    title: 'Tinh Hoa Vị Bắc Thanh Tao',
    description: 'Phở bò Hà Nội, Bún chả nướng than hoa, Nem rán vàng ươm chuẩn phong vị Thăng Long.',
    badge: 'Truyền Thống',
    colSpan: 'md:col-span-1',
    filterType: 'region',
    value: 'mien_bac',
    icon: <Sparkles className="w-4 h-4 text-amber-500" />,
    imageUrl: 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'easy',
    title: 'Món Nhanh Dưới 30 Phút',
    description: 'Dành cho ngày bận rộn: Trứng chiên cà chua, Bò xào hành tây, Tôm rang mặn ngọt nhanh gọn.',
    badge: 'Tiện Lợi',
    colSpan: 'md:col-span-1',
    filterType: 'difficulty',
    value: 'easy',
    icon: <Clock className="w-4 h-4 text-emerald-500" />,
    imageUrl: 'https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'mien_trung',
    title: 'Đậm Đà Đất Miền Trung',
    description: 'Bún bò xứ Huế cay nồng, Mì Quảng tôm thịt đậm vị, Cao lầu Hội An trứ danh.',
    badge: 'Cay Nồng',
    colSpan: 'md:col-span-2',
    filterType: 'region',
    value: 'mien_trung',
    icon: <Flame className="w-4 h-4 text-rose-500" />,
    imageUrl: 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'canh',
    title: 'Món Canh Thanh Mát Giải Nhiệt',
    description: 'Canh chua cá lóc miền Tây, Canh nghêu dứa thì là chua dịu, Canh cà chua trứng thanh ngọt.',
    badge: 'Giải Nhiệt',
    colSpan: 'md:col-span-2',
    filterType: 'search',
    value: 'canh',
    icon: <Utensils className="w-4 h-4 text-teal-500" />,
    imageUrl: 'https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'kho',
    title: 'Món Kho Đậm Đà Hao Cơm',
    description: 'Thịt kho tàu nước dừa óng ả, Cá basa kho tộ béo ngậy, Cá thu kho tiêu thơm nức mũi.',
    badge: 'Hao Cơm',
    colSpan: 'md:col-span-1',
    filterType: 'search',
    value: 'kho',
    icon: <Flame className="w-4 h-4 text-amber-600" />,
    imageUrl: 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'xao',
    title: 'Xào & Chiên Giòn Rụm Hấp Dẫn',
    description: 'Mực xào cần tây sốt chua ngọt, Cá diêu hồng chiên xù vàng ruộm, Gà chiên nước mắm thơm lừng.',
    badge: 'Giòn Thơm',
    colSpan: 'md:col-span-1',
    filterType: 'search',
    value: 'xào',
    icon: <Sparkles className="w-4 h-4 text-yellow-500" />,
    imageUrl: 'https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 'chao',
    title: 'Cháo Dinh Dưỡng & Dễ Tiêu',
    description: 'Cháo sườn nóng hổi ấm bụng ngày mưa, Cháo thịt bò bằm gừng giải cảm bồi bổ sức khỏe.',
    badge: 'Thanh Nhẹ',
    colSpan: 'md:col-span-2',
    filterType: 'search',
    value: 'cháo',
    icon: <ChefHat className="w-4 h-4 text-emerald-600" />,
    imageUrl: 'https://images.unsplash.com/photo-1505253758473-96b3015f27eb?auto=format&fit=crop&w=800&q=80',
  },
];

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [activeCollection, setActiveCollection] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [limit] = useState(12);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    const fetchRecipes = async () => {
      setLoading(true);
      try {
        const params: any = { page, limit };
        if (selectedRegion !== 'all') params.region = selectedRegion;
        if (selectedDifficulty !== 'all') params.difficulty = selectedDifficulty;
        if (searchQuery.trim()) params.search = searchQuery.trim();

        const res = await recipesApi.getAll(params);
        if (res.success && res.data) {
          setRecipes(res.data);
          if (res.pagination) {
            setTotalPages(res.pagination.total_pages || 1);
            setTotalCount(res.pagination.total || 0);
          }
        }
      } catch (err) {
        console.error('Failed to load recipes', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecipes();
  }, [selectedRegion, selectedDifficulty, searchQuery, page]);

  const scrollToRecipes = () => {
    setTimeout(() => {
      const el = document.getElementById('recipes-section');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };

  const handleSelectCollection = (
    collectionId: string,
    filterType: 'region' | 'difficulty' | 'search' | 'all',
    value: string
  ) => {
    setActiveCollection(collectionId);
    setPage(1);

    if (filterType === 'region') {
      setSelectedRegion(value);
      setSelectedDifficulty('all');
      setSearchQuery('');
    } else if (filterType === 'difficulty') {
      setSelectedDifficulty(value);
      setSelectedRegion('all');
      setSearchQuery('');
    } else if (filterType === 'search') {
      setSearchQuery(value);
      setSelectedRegion('all');
      setSelectedDifficulty('all');
    } else {
      setSelectedRegion('all');
      setSelectedDifficulty('all');
      setSearchQuery('');
    }

    scrollToRecipes();
  };

  const resetAllFilters = () => {
    setActiveCollection('all');
    setSelectedRegion('all');
    setSelectedDifficulty('all');
    setSearchQuery('');
    setPage(1);
  };

  const handleRegionChange = (reg: string) => {
    setSelectedRegion(reg);
    setActiveCollection(reg === 'all' ? 'all' : reg);
    setPage(1);
  };

  const handleDifficultyChange = (diff: string) => {
    setSelectedDifficulty(diff);
    setActiveCollection(diff === 'all' ? 'all' : diff);
    setPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    scrollToRecipes();
  };

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
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-widest">
              <Compass className="w-3.5 h-3.5" /> Khám phá nhanh theo chủ đề
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold text-neutral-900 font-heading mt-1">
              Góc Ẩm Thực Chọn Lọc
            </h2>
            <p className="text-xs sm:text-sm text-neutral-500 mt-1">
              Nhấp vào chủ đề bất kỳ để lọc công thức và tự động cuộn đến danh sách món ăn phù hợp
            </p>
          </div>

          {activeCollection !== 'all' && (
            <button
              onClick={resetAllFilters}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-brand-600 bg-brand-50 hover:bg-brand-100 border border-brand-200 rounded-xl transition shadow-xs self-start sm:self-auto cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Xem tất cả (Bỏ lọc)</span>
            </button>
          )}
        </div>

        <BentoGrid className="max-w-7xl">
          {FEATURED_COLLECTIONS.map((item) => {
            const isSelected = activeCollection === item.id;
            return (
              <BentoGridItem
                key={item.id}
                title={item.title}
                description={item.description}
                badge={item.badge}
                className={`${item.colSpan} transition-all duration-300 relative group/bento ${
                  isSelected
                    ? 'ring-4 ring-brand-500/40 border-brand-500 bg-orange-50/20 shadow-xl scale-[1.01]'
                    : 'hover:border-brand-200 hover:shadow-lg'
                }`}
                onClick={() => handleSelectCollection(item.id, item.filterType, item.value)}
                icon={item.icon}
                header={
                  <div className="relative w-full h-full overflow-hidden rounded-xl">
                    <img
                      src={item.imageUrl}
                      alt={item.title}
                      className="w-full h-full object-cover group-hover/bento:scale-105 transition duration-500"
                    />
                    {isSelected && (
                      <div className="absolute inset-0 bg-brand-600/20 backdrop-blur-[1px] flex items-center justify-center">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-brand-600 text-white text-xs font-bold rounded-full shadow-lg">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Đang lọc danh sách
                        </span>
                      </div>
                    )}
                  </div>
                }
              />
            );
          })}
        </BentoGrid>
      </section>

      {/* RECIPES FILTER & LISTING */}
      <section id="recipes-section" className="container mx-auto px-4 pt-8">
        {/* Header & Filter Controls */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-neutral-200">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900 font-heading">
              Tất Cả Công Thức Nấu Ăn
            </h2>
            <p className="text-sm text-neutral-500 mt-1">
              Hiển thị <span className="font-bold text-brand-600">{recipes.length}</span> / {totalCount} món ăn chuẩn vị {totalPages > 1 && `(Trang ${page} / ${totalPages})`}
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
                  onClick={() => handleRegionChange(tab.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
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
              onChange={(e) => handleDifficultyChange(e.target.value)}
              className="px-3 py-2 rounded-xl bg-white border border-neutral-200 text-xs font-medium text-neutral-700 focus:outline-none focus:border-brand-500 cursor-pointer"
            >
              <option value="all">Độ khó: Tất cả</option>
              <option value="easy">Dễ nấu</option>
              <option value="medium">Trung bình</option>
              <option value="hard">Cầu kỳ / Khó</option>
            </select>
          </div>
        </div>

        {/* Active Filter Indicator */}
        {(activeCollection !== 'all' || selectedRegion !== 'all' || selectedDifficulty !== 'all' || searchQuery.trim()) && (
          <div className="flex items-center justify-between p-3.5 px-4 mb-6 bg-gradient-to-r from-orange-50 via-amber-50 to-orange-50 border border-orange-200/80 rounded-2xl shadow-xs animate-fade-in-up">
            <div className="flex items-center gap-2 text-xs sm:text-sm text-neutral-800 flex-wrap">
              <span className="inline-flex items-center gap-1 font-semibold text-brand-700">
                <Filter className="w-4 h-4 text-brand-500" />
                Đang lọc theo:
              </span>
              <span className="font-bold text-neutral-900 bg-white px-2.5 py-1 rounded-lg border border-orange-200 shadow-xs">
                {FEATURED_COLLECTIONS.find((c) => c.id === activeCollection)?.title ||
                  (selectedRegion !== 'all'
                    ? selectedRegion === 'mien_bac'
                      ? 'Đặc Sản Miền Bắc'
                      : selectedRegion === 'mien_trung'
                      ? 'Đặc Sản Miền Trung'
                      : 'Đặc Sản Miền Nam'
                    : '') ||
                  (selectedDifficulty !== 'all'
                    ? `Độ khó: ${selectedDifficulty === 'easy' ? 'Dễ nấu' : selectedDifficulty === 'medium' ? 'Trung bình' : 'Khó'}`
                    : '') ||
                  (searchQuery.trim() ? `Từ khóa: "${searchQuery}"` : 'Tùy chỉnh')}
              </span>
            </div>
            <button
              onClick={resetAllFilters}
              className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-brand-700 hover:text-brand-900 bg-white hover:bg-orange-100/60 rounded-xl border border-orange-200 transition shadow-xs whitespace-nowrap ml-2 cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Xóa bộ lọc</span>
            </button>
          </div>
        )}

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
                setPage(1);
              }}
              className="mt-4 px-4 py-2 text-xs font-semibold text-brand-600 bg-brand-50 rounded-xl hover:bg-brand-100 transition"
            >
              Đặt lại tất cả bộ lọc
            </button>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {recipes.map((recipe) => (
                <RecipeCard key={recipe.id} recipe={recipe} />
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="mt-12 flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-white rounded-2xl border border-neutral-200/80 shadow-xs">
                <span className="text-xs text-neutral-500">
                  Hiển thị trang <strong className="text-neutral-800">{page}</strong> / {totalPages} ({totalCount} món ăn)
                </span>

                <div className="flex items-center gap-1.5">
                  <button
                    disabled={page <= 1}
                    onClick={() => handlePageChange(page - 1)}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-neutral-200 text-xs font-semibold text-neutral-700 hover:bg-neutral-100 disabled:opacity-30 disabled:hover:bg-transparent transition"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Trước</span>
                  </button>

                  {Array.from({ length: totalPages }).map((_, idx) => {
                    const pageNum = idx + 1;
                    if (
                      pageNum === 1 ||
                      pageNum === totalPages ||
                      (pageNum >= page - 2 && pageNum <= page + 2)
                    ) {
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`w-8 h-8 rounded-xl text-xs font-bold transition ${
                            page === pageNum
                              ? 'bg-brand-600 text-white shadow-sm'
                              : 'text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    }
                    if (pageNum === page - 3 || pageNum === page + 3) {
                      return (
                        <span key={pageNum} className="text-neutral-400 text-xs px-1">
                          ...
                        </span>
                      );
                    }
                    return null;
                  })}

                  <button
                    disabled={page >= totalPages}
                    onClick={() => handlePageChange(page + 1)}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-neutral-200 text-xs font-semibold text-neutral-700 hover:bg-neutral-100 disabled:opacity-30 disabled:hover:bg-transparent transition"
                  >
                    <span>Sau</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
};
