import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { adminApi, AdminStats, CreateRecipePayload } from '@/api/admin';
import { recipesApi } from '@/api/recipes';
import { ingredientsApi } from '@/api/ingredients';
import { Recipe, Ingredient } from '@/types';
import { 
  Shield, 
  Search, 
  Plus, 
  Image as ImageIcon, 
  Star, 
  Upload, 
  Trash2, 
  Eye, 
  EyeOff, 
  Check, 
  RefreshCw, 
  ChefHat, 
  AlertCircle, 
  X, 
  ChevronLeft, 
  ChevronRight,
  ExternalLink,
  Layers,
  Sparkles,
  Link as LinkIcon
} from 'lucide-react';
import { toast } from 'sonner';
import { Link } from 'react-router-dom';

export const AdminPage: React.FC = () => {
  const { user, isAuthenticated, login } = useAuth();

  // Admin login fallback state
  const [adminEmail, setAdminEmail] = useState('admin@gmail.com');
  const [adminPassword, setAdminPassword] = useState('12345678');
  const [loggingIn, setLoggingIn] = useState(false);

  // Stats state
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);

  // Recipes list state
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loadingRecipes, setLoadingRecipes] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState<'all' | 'published' | 'draft'>('all');
  const [page, setPage] = useState(1);
  const [limit] = useState(12);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Ingredients for recipe creator
  const [availableIngredients, setAvailableIngredients] = useState<Ingredient[]>([]);

  // Image Management Modal State
  const [selectedRecipeForImage, setSelectedRecipeForImage] = useState<Recipe | null>(null);
  const [imageModalSlot, setImageModalSlot] = useState<1 | 2>(1);
  const [uploadMethod, setUploadMethod] = useState<'file' | 'url'>('file');
  const [inputUrl, setInputUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);

  // Create Recipe Modal State
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [creatingRecipe, setCreatingRecipe] = useState(false);
  const [newRecipe, setNewRecipe] = useState<{
    name: string;
    description: string;
    difficulty: 'easy' | 'medium' | 'hard';
    cook_time_min: number;
    prep_time_min: number;
    servings: number;
    region: string;
    is_published: boolean;
    image_url: string;
    backup_image_url: string;
    ingredients: { ingredient_id: number; quantity: number; unit: string }[];
    steps: { step_number: number; description: string }[];
  }>({
    name: '',
    description: '',
    difficulty: 'medium',
    cook_time_min: 30,
    prep_time_min: 15,
    servings: 4,
    region: 'mien_nam',
    is_published: true,
    image_url: '',
    backup_image_url: '',
    ingredients: [{ ingredient_id: 1, quantity: 200, unit: 'g' }],
    steps: [{ step_number: 1, description: '' }],
  });

  const isAdmin = isAuthenticated && user?.role === 'admin';

  // Load Admin Stats
  const fetchStats = async () => {
    try {
      setLoadingStats(true);
      const res = await adminApi.getStats();
      if (res.success && res.data) {
        setStats(res.data);
      }
    } catch (err) {
      console.error('Failed to load stats', err);
    } finally {
      setLoadingStats(false);
    }
  };

  // Load Recipes for Admin
  const fetchRecipes = async (targetPage = page) => {
    try {
      setLoadingRecipes(true);
      const params: any = {
        page: targetPage,
        limit,
        published: selectedStatus === 'published' ? 'true' : selectedStatus === 'draft' ? 'false' : 'all',
      };
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (selectedRegion !== 'all') params.region = selectedRegion;

      const res = await adminApi.getRecipes(params);
      if (res.success && res.data) {
        setRecipes(res.data);
        if (res.pagination) {
          setTotalPages(res.pagination.total_pages || 1);
          setTotalCount(res.pagination.total || 0);
        }
      }
    } catch (err) {
      console.error('Failed to load recipes', err);
      toast.error('Không thể tải danh sách công thức');
    } finally {
      setLoadingRecipes(false);
    }
  };

  // Load Ingredients
  const fetchIngredients = async () => {
    try {
      const res = await ingredientsApi.getAll();
      if (res.success && res.data) {
        setAvailableIngredients(res.data);
      }
    } catch (err) {
      console.error('Failed to load ingredients', err);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchStats();
      fetchRecipes(1);
      fetchIngredients();
    }
  }, [isAdmin, selectedRegion, selectedStatus]);

  // Handle Search Submit
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchRecipes(1);
  };

  // Handle Quick Admin Login
  const handleQuickLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingIn(true);
    try {
      const ok = await login(adminEmail, adminPassword);
      if (ok) {
        toast.success('Đăng nhập Quản trị viên thành công!');
      } else {
        toast.error('Sai email hoặc mật khẩu quản trị');
      }
    } catch {
      toast.error('Lỗi khi đăng nhập');
    } finally {
      setLoggingIn(false);
    }
  };

  // Toggle Published
  const handleTogglePublish = async (recipe: Recipe) => {
    try {
      const res = await adminApi.togglePublish(recipe.id);
      if (res.success) {
        toast.success(res.message || 'Cập nhật trạng thái thành công');
        setRecipes((prev) =>
          prev.map((r) => (r.id === recipe.id ? { ...r, is_published: res.data.is_published } : r))
        );
        fetchStats();
      }
    } catch {
      toast.error('Lỗi khi đổi trạng thái xuất bản');
    }
  };

  // Delete Recipe
  const handleDeleteRecipe = async (recipe: Recipe) => {
    if (!window.confirm(`Bạn có chắc muốn xóa món "${recipe.name}" không?`)) return;

    try {
      const res = await adminApi.deleteRecipe(recipe.id);
      if (res.success) {
        toast.success(`Đã xóa món ${recipe.name}`);
        fetchRecipes(page);
        fetchStats();
      }
    } catch {
      toast.error('Không thể xóa món ăn');
    }
  };

  // Set Primary Image (Swap Slot 2 with Slot 1)
  const handleSetPrimary = async (recipeId: number, slot: 1 | 2) => {
    try {
      const res = await adminApi.setPrimaryImage(recipeId, slot);
      if (res.success) {
        toast.success('⭐ Đã đặt ảnh làm ảnh chính (Index) thành công!');
        // Update state
        setRecipes((prev) =>
          prev.map((r) =>
            r.id === recipeId
              ? {
                  ...r,
                  image_url: res.data.image_url,
                  backup_image_url: res.data.backup_image_url,
                }
              : r
          )
        );
        if (selectedRecipeForImage && selectedRecipeForImage.id === recipeId) {
          setSelectedRecipeForImage({
            ...selectedRecipeForImage,
            image_url: res.data.image_url,
            backup_image_url: res.data.backup_image_url,
          });
        }
      }
    } catch {
      toast.error('Lỗi khi hoán đổi ảnh chính');
    }
  };

  // Open Image Manager Modal
  const openImageModal = (recipe: Recipe, defaultSlot: 1 | 2 = 1) => {
    setSelectedRecipeForImage(recipe);
    setImageModalSlot(defaultSlot);
    setInputUrl(defaultSlot === 1 ? recipe.image_url || '' : recipe.backup_image_url || '');
    setSelectedFile(null);
    setFilePreview(null);
  };

  // Handle Image File Select
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      const preview = URL.createObjectURL(file);
      setFilePreview(preview);
    }
  };

  // Submit Image Upload / URL
  const handleSaveImage = async () => {
    if (!selectedRecipeForImage) return;

    setUploadingImage(true);
    try {
      let res;
      if (uploadMethod === 'file') {
        if (!selectedFile) {
          toast.error('Vui lòng chọn một file ảnh từ máy tính');
          setUploadingImage(false);
          return;
        }
        res = await adminApi.uploadImageFile(selectedRecipeForImage.id, selectedFile, imageModalSlot);
      } else {
        if (!inputUrl.trim()) {
          toast.error('Vui lòng nhập đường link ảnh hợp lệ');
          setUploadingImage(false);
          return;
        }
        res = await adminApi.setImageUrl(selectedRecipeForImage.id, inputUrl.trim(), imageModalSlot);
      }

      if (res.success) {
        toast.success(res.message || `Đã lưu ảnh Slot ${imageModalSlot} thành công!`);
        // Update recipes state
        const updated = {
          ...selectedRecipeForImage,
          image_url: res.data.image_url,
          backup_image_url: res.data.backup_image_url,
        };
        setSelectedRecipeForImage(updated);
        setRecipes((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
        setSelectedFile(null);
        setFilePreview(null);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Có lỗi khi lưu ảnh');
    } finally {
      setUploadingImage(false);
    }
  };

  // Create Recipe Handlers
  const handleAddIngredientRow = () => {
    setNewRecipe((prev) => ({
      ...prev,
      ingredients: [
        ...prev.ingredients,
        { ingredient_id: availableIngredients[0]?.id || 1, quantity: 100, unit: 'g' },
      ],
    }));
  };

  const handleRemoveIngredientRow = (index: number) => {
    setNewRecipe((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index),
    }));
  };

  const handleAddStepRow = () => {
    setNewRecipe((prev) => ({
      ...prev,
      steps: [
        ...prev.steps,
        { step_number: prev.steps.length + 1, description: '' },
      ],
    }));
  };

  const handleRemoveStepRow = (index: number) => {
    setNewRecipe((prev) => ({
      ...prev,
      steps: prev.steps
        .filter((_, i) => i !== index)
        .map((s, idx) => ({ ...s, step_number: idx + 1 })),
    }));
  };

  const handleCreateRecipeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRecipe.name.trim()) {
      toast.error('Vui lòng nhập tên món ăn');
      return;
    }

    setCreatingRecipe(true);
    try {
      const payload: CreateRecipePayload = {
        name: newRecipe.name.trim(),
        description: newRecipe.description.trim(),
        difficulty: newRecipe.difficulty,
        cook_time_min: Number(newRecipe.cook_time_min),
        prep_time_min: Number(newRecipe.prep_time_min),
        servings: Number(newRecipe.servings),
        region: newRecipe.region,
        is_published: newRecipe.is_published,
        image_url: newRecipe.image_url.trim() || undefined,
        backup_image_url: newRecipe.backup_image_url.trim() || undefined,
        ingredients: newRecipe.ingredients.map((ing) => ({
          ingredient_id: Number(ing.ingredient_id),
          quantity: Number(ing.quantity),
          unit: ing.unit,
        })),
        steps: newRecipe.steps.filter((s) => s.description.trim()).map((s, i) => ({
          step_number: i + 1,
          description: s.description.trim(),
        })),
      };

      const res = await adminApi.createRecipe(payload);
      if (res.success) {
        toast.success(`🎉 Đã thêm thành công món "${res.data.name}"!`);
        setCreateModalOpen(false);
        fetchRecipes(1);
        fetchStats();
        // Reset form
        setNewRecipe({
          name: '',
          description: '',
          difficulty: 'medium',
          cook_time_min: 30,
          prep_time_min: 15,
          servings: 4,
          region: 'mien_nam',
          is_published: true,
          image_url: '',
          backup_image_url: '',
          ingredients: [{ ingredient_id: 1, quantity: 200, unit: 'g' }],
          steps: [{ step_number: 1, description: '' }],
        });
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Có lỗi khi tạo công thức');
    } finally {
      setCreatingRecipe(false);
    }
  };

  // If not admin, show login box
  if (!isAdmin) {
    return (
      <div className="container mx-auto px-4 py-16 max-w-md">
        <div className="bg-white rounded-3xl p-8 border border-neutral-200 shadow-xl text-center space-y-6">
          <div className="w-16 h-16 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center mx-auto shadow-inner">
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-neutral-900 font-heading">
              Cổng Quản Trị Hệ Thống
            </h1>
            <p className="text-sm text-neutral-500 mt-1">
              Vui lòng đăng nhập với tài khoản Admin để quản lý danh mục món ăn, hình ảnh và phân quyền.
            </p>
          </div>

          <form onSubmit={handleQuickLogin} className="space-y-4 text-left">
            <div>
              <label className="block text-xs font-semibold text-neutral-600 mb-1">
                Email Quản trị
              </label>
              <input
                type="email"
                value={adminEmail}
                onChange={(e) => setAdminEmail(e.target.value)}
                required
                className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-neutral-600 mb-1">
                Mật khẩu
              </label>
              <input
                type="password"
                value={adminPassword}
                onChange={(e) => setAdminPassword(e.target.value)}
                required
                className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100"
              />
            </div>

            <button
              type="submit"
              disabled={loggingIn}
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-xl shadow-md hover:from-purple-700 hover:to-indigo-700 transition disabled:opacity-50"
            >
              {loggingIn ? 'Đang xác thực...' : 'Đăng nhập Quản trị viên'}
            </button>
          </form>

          <p className="text-xs text-neutral-400">
            Tài khoản mặc định: <span className="font-mono text-neutral-600">admin@gmail.com</span> / <span className="font-mono text-neutral-600">12345678</span>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-8">
      {/* Top Banner & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 p-6 md:p-8 rounded-3xl text-white shadow-xl">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-medium border border-purple-400/30">
            <Shield className="w-3.5 h-3.5 text-purple-400" />
            <span>Khu vực Quản trị Bếp Thông Minh</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black font-heading tracking-tight">
            Quản Lý Công Thức & Chuẩn Hóa Hình Ảnh
          </h1>
          <p className="text-sm text-purple-200 max-w-2xl">
            Tùy chỉnh 2 ô hình ảnh (ảnh chính & dự phòng), tự động chuẩn hóa tên file tránh lỗi Unicode/dấu tiếng Việt, kiểm soát xuất bản và phân trang.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCreateModalOpen(true)}
            className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-brand-500 to-amber-500 hover:from-brand-600 hover:to-amber-600 text-white font-bold text-sm shadow-lg shadow-brand-500/30 transition hover:-translate-y-0.5"
          >
            <Plus className="w-4 h-4" />
            <span>Thêm Món Ăn Mới</span>
          </button>
          <button
            onClick={() => {
              fetchStats();
              fetchRecipes(page);
            }}
            title="Tải lại dữ liệu"
            className="p-3 rounded-2xl bg-white/10 hover:bg-white/20 text-white transition backdrop-blur-md"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* STATS OVERVIEW CARDS */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-neutral-100 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-orange-100 text-orange-600 flex items-center justify-center">
              <ChefHat className="w-6 h-6" />
            </div>
            <div>
              <span className="block text-2xl font-black text-neutral-800">{stats.total_recipes}</span>
              <span className="text-xs text-neutral-500 font-medium">Tổng số công thức</span>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-neutral-100 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
              <Check className="w-6 h-6" />
            </div>
            <div>
              <span className="block text-2xl font-black text-neutral-800">{stats.published_recipes}</span>
              <span className="text-xs text-neutral-500 font-medium">Đã xuất bản (Live)</span>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-neutral-100 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <span className="block text-2xl font-black text-neutral-800">{stats.draft_recipes}</span>
              <span className="text-xs text-neutral-500 font-medium">Bản nháp (Ẩn)</span>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-neutral-100 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <span className="block text-2xl font-black text-neutral-800">{stats.total_views}</span>
              <span className="text-xs text-neutral-500 font-medium">Lượt xem món</span>
            </div>
          </div>
        </div>
      )}

      {/* FILTER & SEARCH BAR */}
      <div className="bg-white p-4 rounded-2xl border border-neutral-200 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Search Form */}
          <form onSubmit={handleSearch} className="flex-1 flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <input
                type="text"
                placeholder="Tìm món theo tên hoặc từ khóa..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2.5 rounded-xl bg-neutral-900 text-white text-xs font-semibold hover:bg-neutral-800 transition"
            >
              Tìm kiếm
            </button>
          </form>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Region select */}
            <select
              value={selectedRegion}
              onChange={(e) => {
                setSelectedRegion(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2.5 rounded-xl border border-neutral-200 text-xs font-medium text-neutral-700 focus:outline-none"
            >
              <option value="all">Vùng miền: Tất cả</option>
              <option value="mien_bac">Miền Bắc</option>
              <option value="mien_trung">Miền Trung</option>
              <option value="mien_nam">Miền Nam</option>
              <option value="quoc_te">Quốc tế</option>
            </select>

            {/* Status select */}
            <select
              value={selectedStatus}
              onChange={(e: any) => {
                setSelectedStatus(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2.5 rounded-xl border border-neutral-200 text-xs font-medium text-neutral-700 focus:outline-none"
            >
              <option value="all">Trạng thái: Tất cả</option>
              <option value="published">Đang hiển thị</option>
              <option value="draft">Đang ẩn (Nháp)</option>
            </select>
          </div>
        </div>

        {/* Counter Info */}
        <div className="text-xs text-neutral-500 flex items-center justify-between border-t border-neutral-100 pt-3">
          <span>
            Tìm thấy <strong className="text-neutral-800">{totalCount}</strong> món ăn (Trang {page} / {totalPages})
          </span>
          <span className="italic text-neutral-400">
            * Mọi ảnh tải lên tự động được đổi tên chuẩn hóa ASCII chống lỗi font
          </span>
        </div>
      </div>

      {/* RECIPES TABLE & 2-SLOT IMAGE MANAGEMENT */}
      <div className="bg-white rounded-3xl border border-neutral-200 shadow-sm overflow-hidden">
        {loadingRecipes ? (
          <div className="py-20 text-center space-y-3">
            <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs text-neutral-500">Đang tải danh sách công thức...</p>
          </div>
        ) : recipes.length === 0 ? (
          <div className="py-16 text-center text-neutral-400">
            <AlertCircle className="w-10 h-10 mx-auto mb-2 text-neutral-300" />
            <p className="text-sm">Không tìm thấy món ăn nào phù hợp với bộ lọc</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-neutral-600">
              <thead className="bg-neutral-50 text-xs font-bold text-neutral-500 uppercase border-b border-neutral-200">
                <tr>
                  <th className="py-4 px-4 w-12">ID</th>
                  <th className="py-4 px-4">Tên Món Ăn</th>
                  <th className="py-4 px-4 min-w-[280px]">Quản Lý 2 Ô Ảnh (Chính & Dự Phòng)</th>
                  <th className="py-4 px-4">Vùng Miền</th>
                  <th className="py-4 px-4">Độ Khó</th>
                  <th className="py-4 px-4">Trạng Thái</th>
                  <th className="py-4 px-4 text-right">Thao Tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {recipes.map((recipe) => (
                  <tr key={recipe.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-mono text-xs font-bold text-neutral-400">
                      #{recipe.id}
                    </td>

                    {/* Recipe Title & Info */}
                    <td className="py-3 px-4">
                      <div className="font-semibold text-neutral-900 flex items-center gap-1.5">
                        <Link
                          to={`/recipes/${recipe.id}`}
                          className="hover:text-brand-600 transition"
                          title="Xem trên web"
                        >
                          {recipe.name}
                        </Link>
                        <ExternalLink className="w-3.5 h-3.5 text-neutral-400" />
                      </div>
                      <div className="text-xs text-neutral-400 mt-0.5 line-clamp-1 max-w-xs">
                        {recipe.description || 'Chưa có mô tả'}
                      </div>
                    </td>

                    {/* 2 IMAGE SLOTS DISPLAY */}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        {/* SLOT 1 (Primary / Index) */}
                        <div className="relative group border border-emerald-300/80 rounded-xl overflow-hidden w-28 h-20 bg-slate-100 flex-shrink-0 shadow-xs">
                          <img
                            src={recipe.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80'}
                            alt={`Slot 1: ${recipe.name}`}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.currentTarget.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80';
                            }}
                          />
                          <div className="absolute top-1 left-1 bg-emerald-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md shadow">
                            ⭐ Ảnh chính
                          </div>
                          {/* Hover action to change Slot 1 */}
                          <button
                            onClick={() => openImageModal(recipe, 1)}
                            className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white text-xs font-medium"
                          >
                            Đổi Slot 1
                          </button>
                        </div>

                        {/* SLOT 2 (Backup / Secondary) */}
                        <div className="relative group border border-amber-300/80 rounded-xl overflow-hidden w-28 h-20 bg-slate-100 flex-shrink-0 shadow-xs">
                          {recipe.backup_image_url ? (
                            <>
                              <img
                                src={recipe.backup_image_url}
                                alt={`Slot 2: ${recipe.name}`}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  e.currentTarget.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80';
                                }}
                              />
                              <div className="absolute top-1 left-1 bg-amber-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md shadow">
                                Dự phòng
                              </div>
                            </>
                          ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center text-neutral-400 text-[11px] p-2 text-center bg-neutral-50">
                              <ImageIcon className="w-4 h-4 mb-1 text-neutral-300" />
                              <span>Chưa có ảnh 2</span>
                            </div>
                          )}

                          {/* Hover actions for Slot 2 */}
                          <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition flex flex-col items-center justify-center gap-1 p-1">
                            <button
                              onClick={() => openImageModal(recipe, 2)}
                              className="text-[10px] text-white bg-white/20 hover:bg-white/30 px-2 py-0.5 rounded w-full text-center"
                            >
                              Đổi Slot 2
                            </button>
                            {recipe.backup_image_url && (
                              <button
                                onClick={() => handleSetPrimary(recipe.id, 2)}
                                title="Đưa ảnh dự phòng lên làm ảnh chính"
                                className="text-[10px] text-white bg-emerald-600 hover:bg-emerald-700 px-2 py-0.5 rounded w-full text-center font-bold flex items-center justify-center gap-1"
                              >
                                <Star className="w-2.5 h-2.5" /> Làm Index
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Quick action to open modal */}
                        <button
                          onClick={() => openImageModal(recipe, 1)}
                          className="px-2.5 py-1.5 text-xs text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-xl font-medium transition"
                        >
                          Chỉnh sửa ảnh
                        </button>
                      </div>
                    </td>

                    {/* Region */}
                    <td className="py-3 px-4">
                      <span className="capitalize text-xs font-medium text-neutral-600">
                        {recipe.region ? recipe.region.replace('_', ' ') : 'Chưa đặt'}
                      </span>
                    </td>

                    {/* Difficulty */}
                    <td className="py-3 px-4">
                      <span
                        className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          recipe.difficulty === 'easy'
                            ? 'bg-emerald-50 text-emerald-700'
                            : recipe.difficulty === 'medium'
                            ? 'bg-amber-50 text-amber-700'
                            : 'bg-rose-50 text-rose-700'
                        }`}
                      >
                        {recipe.difficulty === 'easy' ? 'Dễ' : recipe.difficulty === 'medium' ? 'Vừa' : 'Khó'}
                      </span>
                    </td>

                    {/* Published Status Toggle */}
                    <td className="py-3 px-4">
                      <button
                        onClick={() => handleTogglePublish(recipe)}
                        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition ${
                          recipe.is_published
                            ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200'
                            : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                        }`}
                      >
                        {recipe.is_published ? (
                          <>
                            <Eye className="w-3.5 h-3.5" /> Live
                          </>
                        ) : (
                          <>
                            <EyeOff className="w-3.5 h-3.5" /> Nháp
                          </>
                        )}
                      </button>
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDeleteRecipe(recipe)}
                        title="Xóa công thức"
                        className="p-2 text-neutral-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* PAGINATION BAR */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-neutral-100 flex flex-col sm:flex-row items-center justify-between gap-4">
            <span className="text-xs text-neutral-500">
              Trang <strong className="text-neutral-800">{page}</strong> trên tổng số{' '}
              <strong className="text-neutral-800">{totalPages}</strong> trang ({totalCount} món)
            </span>

            <div className="flex items-center gap-1.5">
              <button
                disabled={page <= 1}
                onClick={() => {
                  setPage(page - 1);
                  fetchRecipes(page - 1);
                }}
                className="px-3 py-1.5 rounded-xl border border-neutral-200 text-xs font-medium text-neutral-600 hover:bg-neutral-100 disabled:opacity-30 disabled:hover:bg-transparent"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              {Array.from({ length: totalPages }).map((_, idx) => {
                const pageNum = idx + 1;
                // Only show around current page
                if (
                  pageNum === 1 ||
                  pageNum === totalPages ||
                  (pageNum >= page - 2 && pageNum <= page + 2)
                ) {
                  return (
                    <button
                      key={pageNum}
                      onClick={() => {
                        setPage(pageNum);
                        fetchRecipes(pageNum);
                      }}
                      className={`w-8 h-8 rounded-xl text-xs font-semibold transition ${
                        page === pageNum
                          ? 'bg-purple-600 text-white shadow-sm'
                          : 'text-neutral-600 hover:bg-neutral-100 border border-neutral-200'
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
                onClick={() => {
                  setPage(page + 1);
                  fetchRecipes(page + 1);
                }}
                className="px-3 py-1.5 rounded-xl border border-neutral-200 text-xs font-medium text-neutral-600 hover:bg-neutral-100 disabled:opacity-30 disabled:hover:bg-transparent"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ────────────────────────────────────────────────────────── */}
      {/* MODAL 1: CHỈNH SỬA & CHUẨN HÓA 2 Ô HÌNH ẢNH */}
      {/* ────────────────────────────────────────────────────────── */}
      {selectedRecipeForImage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-6 space-y-6 shadow-2xl border border-neutral-200 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-start justify-between border-b border-neutral-100 pb-4">
              <div>
                <span className="text-xs font-bold text-purple-600 uppercase tracking-wider">
                  Quản lý hình ảnh
                </span>
                <h3 className="text-xl font-bold text-neutral-900 font-heading">
                  {selectedRecipeForImage.name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedRecipeForImage(null)}
                className="p-1 rounded-xl text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 2 Current Slots Preview */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Slot 1 Box */}
              <div
                className={`p-3 rounded-2xl border-2 transition ${
                  imageModalSlot === 1
                    ? 'border-purple-600 bg-purple-50/40'
                    : 'border-neutral-200 bg-neutral-50/60'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-emerald-700 flex items-center gap-1">
                    <Star className="w-3.5 h-3.5 fill-emerald-600 text-emerald-600" />
                    Slot 1 (Ảnh chính / Index)
                  </span>
                  <button
                    onClick={() => setImageModalSlot(1)}
                    className="text-[11px] font-semibold text-purple-700 underline"
                  >
                    Chọn sửa ô này
                  </button>
                </div>

                <div className="aspect-4/3 w-full rounded-xl overflow-hidden bg-slate-200 relative mb-2">
                  <img
                    src={selectedRecipeForImage.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80'}
                    alt="Slot 1"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="text-[10px] text-neutral-400 truncate" title={selectedRecipeForImage.image_url}>
                  {selectedRecipeForImage.image_url || 'Chưa thiết lập'}
                </div>
              </div>

              {/* Slot 2 Box */}
              <div
                className={`p-3 rounded-2xl border-2 transition ${
                  imageModalSlot === 2
                    ? 'border-purple-600 bg-purple-50/40'
                    : 'border-neutral-200 bg-neutral-50/60'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-amber-700 flex items-center gap-1">
                    <ImageIcon className="w-3.5 h-3.5 text-amber-600" />
                    Slot 2 (Ảnh dự phòng)
                  </span>
                  <button
                    onClick={() => setImageModalSlot(2)}
                    className="text-[11px] font-semibold text-purple-700 underline"
                  >
                    Chọn sửa ô này
                  </button>
                </div>

                <div className="aspect-4/3 w-full rounded-xl overflow-hidden bg-slate-200 relative mb-2">
                  {selectedRecipeForImage.backup_image_url ? (
                    <img
                      src={selectedRecipeForImage.backup_image_url}
                      alt="Slot 2"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center text-neutral-400 text-xs p-4 text-center">
                      <ImageIcon className="w-6 h-6 mb-1 text-neutral-300" />
                      <span>Trống - Thêm ảnh dự phòng tại đây</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between gap-1">
                  <span className="text-[10px] text-neutral-400 truncate flex-1" title={selectedRecipeForImage.backup_image_url}>
                    {selectedRecipeForImage.backup_image_url || 'Chưa thiết lập'}
                  </span>
                  {selectedRecipeForImage.backup_image_url && (
                    <button
                      onClick={() => handleSetPrimary(selectedRecipeForImage.id, 2)}
                      className="text-[10px] bg-emerald-600 text-white font-bold px-2 py-0.5 rounded shadow hover:bg-emerald-700 transition"
                    >
                      ⭐ Đặt làm chính
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Input Action Form */}
            <div className="p-4 bg-slate-50 rounded-2xl border border-neutral-200 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-neutral-700">
                  Cập nhật ảnh cho: <strong className="text-purple-700">Slot {imageModalSlot}</strong>
                </span>

                {/* Toggle Upload File vs Paste URL */}
                <div className="flex items-center gap-1 bg-neutral-200/80 p-0.5 rounded-lg text-xs">
                  <button
                    type="button"
                    onClick={() => setUploadMethod('file')}
                    className={`px-2.5 py-1 rounded-md font-medium transition ${
                      uploadMethod === 'file' ? 'bg-white shadow-xs font-semibold' : 'text-neutral-600'
                    }`}
                  >
                    Tải file lên
                  </button>
                  <button
                    type="button"
                    onClick={() => setUploadMethod('url')}
                    className={`px-2.5 py-1 rounded-md font-medium transition ${
                      uploadMethod === 'url' ? 'bg-white shadow-xs font-semibold' : 'text-neutral-600'
                    }`}
                  >
                    Nhập link URL
                  </button>
                </div>
              </div>

              {uploadMethod === 'file' ? (
                <div className="space-y-3">
                  <label className="border-2 border-dashed border-neutral-300 hover:border-purple-500 rounded-2xl p-6 flex flex-col items-center justify-center cursor-pointer transition bg-white group">
                    <Upload className="w-8 h-8 text-neutral-400 group-hover:text-purple-600 mb-2 transition" />
                    <span className="text-xs font-semibold text-neutral-700">
                      {selectedFile ? selectedFile.name : 'Chọn file ảnh từ máy tính (JPG, PNG, WebP)'}
                    </span>
                    <span className="text-[11px] text-neutral-400 mt-1">
                      File sẽ tự động được chuẩn hóa tên thành ASCII không dấu + timestamp
                    </span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>

                  {filePreview && (
                    <div className="flex items-center gap-3 p-2 bg-purple-50 rounded-xl border border-purple-200">
                      <img src={filePreview} alt="Preview" className="w-14 h-14 object-cover rounded-lg" />
                      <div className="text-xs text-neutral-600 flex-1">
                        <strong className="block text-neutral-800">Xem trước ảnh tải lên:</strong>
                        <span>Chuẩn bị lưu vào Slot {imageModalSlot}</span>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-2">
                  <label className="block text-xs font-semibold text-neutral-600">
                    Đường dẫn ảnh trực tuyến (Image URL)
                  </label>
                  <input
                    type="url"
                    value={inputUrl}
                    onChange={(e) => setInputUrl(e.target.value)}
                    placeholder="https://images.unsplash.com/..."
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-purple-500"
                  />
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedRecipeForImage(null)}
                  className="px-4 py-2 text-xs font-semibold text-neutral-600 hover:bg-neutral-200 rounded-xl transition"
                >
                  Đóng
                </button>
                <button
                  type="button"
                  disabled={uploadingImage}
                  onClick={handleSaveImage}
                  className="px-5 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-md transition disabled:opacity-50"
                >
                  {uploadingImage ? 'Đang lưu & chuẩn hóa...' : `Lưu vào Slot ${imageModalSlot}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────────────────────── */}
      {/* MODAL 2: TỰ TAY THÊM MÓN ĂN MỚI */}
      {/* ────────────────────────────────────────────────────────── */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl max-w-3xl w-full p-6 space-y-6 shadow-2xl border border-neutral-200 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-start justify-between border-b border-neutral-100 pb-4">
              <div>
                <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">
                  Thêm công thức mới
                </span>
                <h3 className="text-xl font-bold text-neutral-900 font-heading">
                  Nhập thông tin món ăn
                </h3>
              </div>
              <button
                onClick={() => setCreateModalOpen(false)}
                className="p-1 rounded-xl text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateRecipeSubmit} className="space-y-6">
              {/* Basic Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-neutral-700 mb-1">
                    Tên món ăn <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Ví dụ: Cá Bống Kho Tiêu, Bún Bò Huế..."
                    value={newRecipe.name}
                    onChange={(e) => setNewRecipe({ ...newRecipe, name: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-neutral-700 mb-1">
                    Mô tả món ăn
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Mô tả ngắn về hương vị, xuất xứ hoặc điểm đặc biệt..."
                    value={newRecipe.description}
                    onChange={(e) => setNewRecipe({ ...newRecipe, description: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-700 mb-1">Vùng miền</label>
                  <select
                    value={newRecipe.region}
                    onChange={(e) => setNewRecipe({ ...newRecipe, region: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
                  >
                    <option value="mien_bac">Miền Bắc</option>
                    <option value="mien_trung">Miền Trung</option>
                    <option value="mien_nam">Miền Nam</option>
                    <option value="quoc_te">Quốc Tế</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-700 mb-1">Độ khó</label>
                  <select
                    value={newRecipe.difficulty}
                    onChange={(e: any) => setNewRecipe({ ...newRecipe, difficulty: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
                  >
                    <option value="easy">Dễ nấu</option>
                    <option value="medium">Trung bình</option>
                    <option value="hard">Cầu kỳ / Khó</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-700 mb-1">
                    Thời gian chuẩn bị (phút)
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={newRecipe.prep_time_min}
                    onChange={(e) => setNewRecipe({ ...newRecipe, prep_time_min: Number(e.target.value) })}
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-700 mb-1">
                    Thời gian nấu (phút)
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={newRecipe.cook_time_min}
                    onChange={(e) => setNewRecipe({ ...newRecipe, cook_time_min: Number(e.target.value) })}
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-700 mb-1">
                    Khẩu phần (người)
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={newRecipe.servings}
                    onChange={(e) => setNewRecipe({ ...newRecipe, servings: Number(e.target.value) })}
                    className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div className="flex items-center gap-2 pt-6">
                  <input
                    type="checkbox"
                    id="is_published_checkbox"
                    checked={newRecipe.is_published}
                    onChange={(e) => setNewRecipe({ ...newRecipe, is_published: e.target.checked })}
                    className="w-4 h-4 text-brand-600 rounded"
                  />
                  <label htmlFor="is_published_checkbox" className="text-xs font-bold text-neutral-800">
                    Xuất bản công khai ngay lên web
                  </label>
                </div>
              </div>

              {/* 2 Image Slots Input */}
              <div className="p-4 bg-orange-50/60 rounded-2xl border border-orange-100 space-y-3">
                <h4 className="text-xs font-bold text-brand-800 uppercase flex items-center gap-1.5">
                  <ImageIcon className="w-4 h-4 text-brand-600" />
                  Đường Dẫn 2 Ô Hình Ảnh (Tùy chọn)
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-neutral-600 mb-1">
                      Ảnh chính (Slot 1 / Index)
                    </label>
                    <input
                      type="text"
                      placeholder="https://... hoặc /recipes/ten-anh.jpg"
                      value={newRecipe.image_url}
                      onChange={(e) => setNewRecipe({ ...newRecipe, image_url: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg border border-neutral-200 text-xs focus:outline-none focus:border-brand-500 bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-neutral-600 mb-1">
                      Ảnh dự phòng (Slot 2)
                    </label>
                    <input
                      type="text"
                      placeholder="https://... hoặc /recipes/ten-anh-2.jpg"
                      value={newRecipe.backup_image_url}
                      onChange={(e) => setNewRecipe({ ...newRecipe, backup_image_url: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg border border-neutral-200 text-xs focus:outline-none focus:border-brand-500 bg-white"
                    />
                  </div>
                </div>
                <p className="text-[10px] text-neutral-500">
                  * Sau khi tạo xong, bạn cũng có thể bấm "Chỉnh sửa ảnh" ở bảng để tải trực tiếp file từ máy tính lên.
                </p>
              </div>

              {/* Ingredients List */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-neutral-800 uppercase">
                    Nguyên Liệu Cần Có
                  </h4>
                  <button
                    type="button"
                    onClick={handleAddIngredientRow}
                    className="text-xs text-brand-600 font-semibold hover:underline flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Thêm nguyên liệu
                  </button>
                </div>

                <div className="space-y-2">
                  {newRecipe.ingredients.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <select
                        value={item.ingredient_id}
                        onChange={(e) => {
                          const val = Number(e.target.value);
                          setNewRecipe((prev) => ({
                            ...prev,
                            ingredients: prev.ingredients.map((ing, i) =>
                              i === idx ? { ...ing, ingredient_id: val } : ing
                            ),
                          }));
                        }}
                        className="flex-1 px-3 py-2 rounded-xl border border-neutral-200 text-xs focus:outline-none"
                      >
                        {availableIngredients.map((ing) => (
                          <option key={ing.id} value={ing.id}>
                            {ing.emoji} {ing.name} ({ing.unit})
                          </option>
                        ))}
                      </select>

                      <input
                        type="number"
                        placeholder="Số lượng"
                        value={item.quantity}
                        onChange={(e) => {
                          const val = Number(e.target.value);
                          setNewRecipe((prev) => ({
                            ...prev,
                            ingredients: prev.ingredients.map((ing, i) =>
                              i === idx ? { ...ing, quantity: val } : ing
                            ),
                          }));
                        }}
                        className="w-24 px-3 py-2 rounded-xl border border-neutral-200 text-xs focus:outline-none"
                      />

                      <input
                        type="text"
                        placeholder="Đơn vị"
                        value={item.unit}
                        onChange={(e) => {
                          const val = e.target.value;
                          setNewRecipe((prev) => ({
                            ...prev,
                            ingredients: prev.ingredients.map((ing, i) =>
                              i === idx ? { ...ing, unit: val } : ing
                            ),
                          }));
                        }}
                        className="w-20 px-3 py-2 rounded-xl border border-neutral-200 text-xs focus:outline-none"
                      />

                      {newRecipe.ingredients.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveIngredientRow(idx)}
                          className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Cooking Steps */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-neutral-800 uppercase">
                    Các Bước Thực Hiện
                  </h4>
                  <button
                    type="button"
                    onClick={handleAddStepRow}
                    className="text-xs text-brand-600 font-semibold hover:underline flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Thêm bước nấu
                  </button>
                </div>

                <div className="space-y-2">
                  {newRecipe.steps.map((st, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <span className="w-7 h-7 rounded-lg bg-neutral-200 text-neutral-700 flex items-center justify-center font-bold text-xs flex-shrink-0 mt-1">
                        {st.step_number}
                      </span>
                      <textarea
                        rows={2}
                        placeholder={`Mô tả bước ${st.step_number}...`}
                        value={st.description}
                        onChange={(e) => {
                          const val = e.target.value;
                          setNewRecipe((prev) => ({
                            ...prev,
                            steps: prev.steps.map((s, i) =>
                              i === idx ? { ...s, description: val } : s
                            ),
                          }));
                        }}
                        className="flex-1 px-3 py-2 rounded-xl border border-neutral-200 text-xs focus:outline-none"
                      />
                      {newRecipe.steps.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveStepRow(idx)}
                          className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg mt-1"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex justify-end gap-3 pt-4 border-t border-neutral-100">
                <button
                  type="button"
                  onClick={() => setCreateModalOpen(false)}
                  className="px-5 py-2.5 rounded-xl border border-neutral-200 text-xs font-semibold text-neutral-600 hover:bg-neutral-100"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={creatingRecipe}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-amber-500 text-white font-bold text-xs shadow-md hover:from-brand-700 hover:to-amber-600 disabled:opacity-50"
                >
                  {creatingRecipe ? 'Đang tạo món...' : 'Tạo Món Ăn'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
