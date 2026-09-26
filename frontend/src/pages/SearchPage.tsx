import React, { useEffect, useState, useRef } from 'react';
import { ingredientsApi } from '@/api/ingredients';
import { Ingredient, SearchByIngredientResult } from '@/types';
import { MorphSVG } from '@/components/animations/MorphSVG';
import { RecipeCard } from '@/components/recipes/RecipeCard';
import { 
  Search, 
  Sparkles, 
  Check, 
  X, 
  AlertCircle, 
  Flame,
  ChefHat,
  Clock,
  Filter,
  CheckCircle2,
  ArrowDownCircle,
  RotateCcw
} from 'lucide-react';
import { toast } from 'sonner';

// Các gia vị cơ bản bếp nào cũng có -> Không cần bắt người dùng tick chọn
const PANTRY_STAPLE_NAMES = [
  'muối',
  'đường trắng',
  'đường thốt nốt',
  'nước mắm',
  'dầu ăn',
  'bột ngọt (mì chính)',
  'hạt nêm',
  'tiêu đen',
  'nước tương (xì dầu)',
  'gạo tẻ',
];

export const SearchPage: React.FC = () => {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('thit');
  const [filterQuery, setFilterQuery] = useState('');
  
  const [results, setResults] = useState<SearchByIngredientResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Ref cuộn mượt xuống phần kết quả
  const resultsSectionRef = useRef<HTMLDivElement>(null);

  const categories = [
    { id: 'thit', label: 'Thịt & Trứng', icon: '🥩' },
    { id: 'hai_san', label: 'Hải sản & Trứng', icon: '🦐' },
    { id: 'rau_cu', label: 'Rau củ tươi', icon: '🥕' },
    { id: 'gia_vi', label: 'Gia vị đặc biệt', icon: '🧄' },
    { id: 'do_kho', label: 'Bún, Miến & Khác', icon: '🍜' },
    { id: 'all', label: 'Tất cả', icon: '🧺' },
  ];

  useEffect(() => {
    const loadIngredients = async () => {
      try {
        const res = await ingredientsApi.getAll();
        if (res.success && res.data) {
          setIngredients(res.data);
        }
      } catch (err) {
        console.error('Failed to load ingredients', err);
      }
    };
    loadIngredients();
  }, []);

  const toggleIngredient = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const scrollToResults = () => {
    setTimeout(() => {
      if (resultsSectionRef.current) {
        resultsSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 150);
  };

  const handleSearch = async () => {
    if (selectedIds.length === 0) {
      toast.error('Vui lòng chọn ít nhất 1 nguyên liệu đang có trong bếp!');
      return;
    }

    setIsSearching(true);
    setHasSearched(true);
    try {
      const res = await ingredientsApi.searchByIngredients(selectedIds, 0.1);
      if (res.success && res.data) {
        setResults(res.data);
        toast.success(`Đã tìm thấy ${res.data.length} món ăn phù hợp!`);
        scrollToResults();
      } else {
        setResults([]);
      }
    } catch {
      toast.error('Có lỗi khi tìm kiếm');
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const clearAll = () => {
    setSelectedIds([]);
    setResults([]);
    setHasSearched(false);
  };

  // Lọc nguyên liệu theo Category thông minh
  const isPantryStaple = (name: string) =>
    PANTRY_STAPLE_NAMES.some((s) => name.toLowerCase().includes(s));

  const isEgg = (name: string) => name.toLowerCase().includes('trứng');

  const filteredIngredients = ingredients.filter((ing) => {
    const nameLower = ing.name.toLowerCase();

    // Ẩn các gia vị cơ bản để người dùng không phải chọn rườm rà
    if (isPantryStaple(nameLower)) return false;

    // Lọc theo Tab Category
    let matchCategory = false;
    if (activeCategory === 'thit') {
      // Nhóm Thịt & Trứng
      matchCategory = ing.category === 'thit' || isEgg(nameLower);
    } else if (activeCategory === 'hai_san') {
      // Nhóm Hải sản & Trứng
      matchCategory = ing.category === 'hai_san' || isEgg(nameLower);
    } else if (activeCategory === 'rau_cu') {
      matchCategory = ing.category === 'rau_cu';
    } else if (activeCategory === 'gia_vi') {
      matchCategory = ['gia_vi', 'nuoc_sot'].includes(ing.category);
    } else if (activeCategory === 'do_kho') {
      matchCategory = ['do_kho', 'bot_duong', 'hat', 'khac'].includes(ing.category) && !isEgg(nameLower);
    } else {
      matchCategory = true;
    }

    const matchQuery = nameLower.includes(filterQuery.toLowerCase());
    return matchCategory && matchQuery;
  });

  const displayedResults = results;

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-100 text-brand-700 text-xs font-semibold">
          <span className="text-base">🥕</span>
          <span>Tính năng độc quyền "Có gì nấu nấy"</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-neutral-900 font-heading">
          Tủ Lạnh Nhà Bạn Đang Có Gì?
        </h1>
        <p className="text-sm text-neutral-600">
          Chỉ cần chọn <strong>Thịt</strong> hoặc <strong>Hải sản</strong> (kèm trứng) và <strong>Rau củ</strong>, hệ thống tự động kết hợp gia vị sẵn có để gợi ý ngay những món ngon nhất!
        </p>
      </div>

      {/* PANTRY STAPLES NOTIFICATION BADGE */}
      <div className="p-3.5 rounded-2xl bg-amber-50/80 border border-amber-200/70 flex items-center gap-3 text-xs text-amber-900 shadow-2xs">
        <span className="text-xl shrink-0">🧂</span>
        <div className="leading-relaxed">
          <strong>Bếp nhà bạn đã có sẵn gia vị cơ bản:</strong> Nước mắm, Muối, Đường, Tiêu, Dầu ăn, Hạt nêm.
          <span className="text-amber-800 ml-1">
            Bạn không cần chọn các gia vị này, hãy tập trung chọn <strong>Đạm chính</strong> và <strong>Rau củ</strong> nhé!
          </span>
        </div>
      </div>

      {/* INGREDIENTS SELECTOR PANEL */}
      <div className="rounded-3xl bg-white border border-slate-200/80 shadow-sm p-6 space-y-6">
        {/* Top Control Bar: Search & Categories */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Categories Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`flex items-center gap-1.5 px-3.5 py-2.5 rounded-2xl text-xs font-bold transition ${
                  activeCategory === cat.id
                    ? 'bg-brand-500 text-white shadow-sm'
                    : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200/80'
                }`}
              >
                <span>{cat.icon}</span>
                <span>{cat.label}</span>
              </button>
            ))}
          </div>

          {/* Search box for ingredients */}
          <div className="relative w-full md:w-64">
            <Search className="w-4 h-4 text-neutral-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Gõ tìm nguyên liệu..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-neutral-200 text-xs focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>

        {/* Selected ingredients preview pills */}
        {selectedIds.length > 0 && (
          <div className="p-4 rounded-2xl bg-orange-50/70 border border-orange-200/60 flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-brand-800 mr-2 flex items-center gap-1">
              <Check className="w-3.5 h-3.5 text-brand-600" />
              Đã chọn ({selectedIds.length}):
            </span>
            {selectedIds.map((id) => {
              const ing = ingredients.find((i) => i.id === id);
              if (!ing) return null;
              return (
                <span
                  key={id}
                  onClick={() => toggleIngredient(id)}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-brand-200 text-brand-900 text-xs font-semibold shadow-2xs cursor-pointer hover:bg-rose-50 hover:border-rose-200 hover:text-rose-600 transition"
                  title="Bấm để xóa"
                >
                  <span>{ing.emoji}</span>
                  <span>{ing.name}</span>
                  <X className="w-3 h-3 text-neutral-400" />
                </span>
              );
            })}
            <button
              onClick={clearAll}
              className="text-xs text-neutral-400 hover:text-rose-600 underline ml-auto transition"
            >
              Xóa hết
            </button>
          </div>
        )}

        {/* Ingredients Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5 max-h-84 overflow-y-auto pr-1">
          {filteredIngredients.map((ing) => {
            const isSelected = selectedIds.includes(ing.id);
            return (
              <button
                key={ing.id}
                onClick={() => toggleIngredient(ing.id)}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-2xl border text-left text-xs transition-all ${
                  isSelected
                    ? 'bg-brand-500 border-brand-600 text-white shadow-sm font-semibold scale-102'
                    : 'bg-white border-neutral-200/80 text-neutral-700 hover:border-brand-300 hover:bg-orange-50/30'
                }`}
              >
                <span className="text-lg">{ing.emoji}</span>
                <span className="truncate flex-1 font-medium">{ing.name}</span>
              </button>
            );
          })}
        </div>

        {/* Search CTA */}
        <div className="pt-4 border-t border-neutral-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-neutral-500">
            Mẹo: Chỉ cần chọn <span className="font-semibold text-neutral-800">1 loại Thịt hoặc Cá/Tôm</span> + <span className="font-semibold text-neutral-800">1 loại Rau</span> là có thể tìm ra hàng loạt món ngon!
          </div>

          <button
            onClick={handleSearch}
            disabled={isSearching || selectedIds.length === 0}
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 to-amber-500 text-white font-bold text-sm shadow-md shadow-orange-500/20 hover:shadow-lg transition hover:-translate-y-0.5 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isSearching ? (
              <>
                <MorphSVG size={22} color="#ffffff" />
                <span>AI đang tìm công thức...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 fill-white" />
                <span>Tìm món nấu được ngay ({selectedIds.length} nguyên liệu)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* SEARCH RESULTS SECTION */}
      {hasSearched && (
        <section ref={resultsSectionRef} id="results-section" className="space-y-6 pt-6 animate-fade-in-up scroll-mt-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-xs">
            <div>
              <div className="flex items-center gap-2">
                <ChefHat className="w-5 h-5 text-brand-600" />
                <h2 className="text-2xl font-bold text-neutral-900 font-heading">
                  Kết Quả Món Ăn Nấu Được
                </h2>
              </div>
              <p className="text-xs text-neutral-500 mt-1">
                Ưu tiên các món có nguyên liệu đạm chính & độ khớp cao nhất
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-orange-100 text-brand-700 font-bold text-xs">
                {results.length} món phù hợp
              </span>
            </div>
          </div>

          {results.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-3xl border border-neutral-100 p-8">
              <AlertCircle className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-neutral-800">Không tìm thấy món phù hợp với các nguyên liệu đã chọn</h3>
              <p className="text-sm text-neutral-500 mt-1">
                Hãy thử chọn thêm nguyên liệu đạm chính hoặc rau củ khác để nhận gợi ý nấu ăn nhé!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((resItem) => {
                const percent = Math.min(100, Math.max(0, Math.round(resItem.match_percent)));
                return (
                  <div
                    key={resItem.recipe.id}
                    className="flex flex-col rounded-3xl bg-white border border-slate-200/80 shadow-sm overflow-hidden hover:shadow-xl transition"
                  >
                    {/* Top card */}
                    <RecipeCard recipe={resItem.recipe} />

                    {/* Matching ingredients Breakdown */}
                    <div className="p-4 bg-orange-50/50 border-t border-orange-100 space-y-3">
                      {/* Percent Bar */}
                      <div>
                        <div className="flex items-center justify-between text-xs font-semibold mb-1">
                          <span className="text-brand-800 flex items-center gap-1">
                            <Flame className="w-3.5 h-3.5 text-brand-600" />
                            Độ khớp nguyên liệu:
                          </span>
                          <span className="text-brand-700 font-bold">{percent}%</span>
                        </div>
                        <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-brand-500 to-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: `${percent}%` }}
                          />
                        </div>
                      </div>

                      {/* Ingredients tags */}
                      <div className="space-y-1.5 text-xs">
                        {/* Matched */}
                        {resItem.matched_ingredients.length > 0 && (
                          <div className="flex flex-wrap items-center gap-1">
                            <span className="text-emerald-700 font-semibold text-[11px]">Đã có:</span>
                            {resItem.matched_ingredients.map((name, i) => (
                              <span
                                key={i}
                                className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[11px] font-medium"
                              >
                                ✓ {name}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Missing */}
                        {resItem.missing_ingredients.length > 0 ? (
                          <div className="flex flex-wrap items-center gap-1 pt-1">
                            <span className="text-amber-700 font-semibold text-[11px]">Cần thêm:</span>
                            {resItem.missing_ingredients.map((name, i) => (
                              <span
                                key={i}
                                className="px-2 py-0.5 rounded-md bg-amber-100/80 text-amber-900 text-[11px]"
                              >
                                + {name}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <div className="text-[11px] text-emerald-600 font-semibold flex items-center gap-1 pt-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Bạn đã có đủ nguyên liệu để nấu ngay!
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}

      {/* FLOATING STICKY BAR KHI ĐÃ CHỌN NGUYÊN LIỆU */}
      {selectedIds.length > 0 && !isSearching && (
        <div className="fixed bottom-6 inset-x-0 z-40 flex justify-center px-4 pointer-events-none animate-fade-in-up">
          <div className="pointer-events-auto bg-neutral-900/90 backdrop-blur-md text-white px-5 py-3 rounded-2xl shadow-xl border border-neutral-700 flex items-center gap-4">
            <span className="text-xs font-semibold">
              Đã chọn <span className="text-brand-400 font-bold">{selectedIds.length}</span> nguyên liệu
            </span>
            <button
              onClick={handleSearch}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-brand-500 to-amber-500 text-white font-bold text-xs hover:opacity-95 transition flex items-center gap-1.5 shadow-xs"
            >
              <span>{hasSearched ? 'Xem kết quả' : 'Tìm món ngay'}</span>
              <ArrowDownCircle className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
