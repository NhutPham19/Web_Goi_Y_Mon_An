import React, { useEffect, useState } from 'react';
import { recipesApi } from '@/api/recipes';
import { Recipe } from '@/types';
import { RecipeCard } from '@/components/recipes/RecipeCard';
import { useAuth } from '@/context/AuthContext';
import { Bookmark, Heart, Utensils } from 'lucide-react';
import { Link } from 'react-router-dom';

export const SavedRecipesPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSaved = async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const res = await recipesApi.getSaved();
      if (res.success && res.data) {
        const list = res.data.map((r: any) => {
          const item = r.recipe ? { ...r.recipe, is_saved: true } : { ...r, is_saved: true };
          return item;
        });
        setRecipes(list);
      }
    } catch {
      setRecipes([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, [isAuthenticated]);

  const handleSavedChange = (recipeId: number, isSaved: boolean) => {
    if (!isSaved) {
      setRecipes((prev) => prev.filter((r) => r.id !== recipeId));
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-20 text-center max-w-md">
        <div className="w-16 h-16 rounded-3xl bg-rose-100 text-rose-600 flex items-center justify-center mx-auto mb-4">
          <Heart className="w-8 h-8 fill-rose-500" />
        </div>
        <h2 className="text-2xl font-bold text-neutral-900 font-heading">
          Món Ăn Yêu Thích Của Bạn
        </h2>
        <p className="text-sm text-neutral-500 mt-2">
          Vui lòng đăng nhập để xem lại các công thức nấu ăn đã lưu vào bộ sưu tập cá nhân.
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div>
        <div className="inline-flex items-center gap-1.5 text-xs font-bold text-rose-700 bg-rose-100 px-3 py-1 rounded-full uppercase tracking-wider mb-2">
          <Heart className="w-3.5 h-3.5 fill-rose-600" /> Bộ sưu tập cá nhân
        </div>
        <h1 className="text-3xl font-black text-neutral-900 font-heading">
          Công Thức Đã Lưu
        </h1>
        <p className="text-xs text-neutral-500 mt-1">
          Bạn đang lưu trữ <span className="font-bold text-rose-600">{recipes.length}</span> món ăn
        </p>
      </div>

      {loading ? (
        <div className="py-20 text-center text-sm text-neutral-400">Đang tải công thức đã lưu...</div>
      ) : recipes.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-neutral-100 p-8">
          <Bookmark className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-neutral-800">Chưa có công thức nào được lưu</h3>
          <p className="text-sm text-neutral-500 mt-1">
            Bấm vào biểu tượng bookmark trên thẻ món ăn để lưu lại và xem lại bất cứ lúc nào!
          </p>
          <Link
            to="/"
            className="mt-4 px-5 py-2.5 inline-block text-xs font-semibold text-white bg-brand-600 rounded-xl hover:bg-brand-700 transition"
          >
            Khám phá món ngon
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} onSavedChange={handleSavedChange} />
          ))}
        </div>
      )}
    </div>
  );
};
