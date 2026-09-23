import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Recipe } from '@/types';
import { Clock, Flame, Star, Bookmark, ChefHat } from 'lucide-react';
import { recipesApi } from '@/api/recipes';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';

interface RecipeCardProps {
  recipe: Recipe;
  onSavedChange?: (recipeId: number, isSaved: boolean) => void;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, onSavedChange }) => {
  const { isAuthenticated } = useAuth();
  const [isSaved, setIsSaved] = useState(recipe.is_saved || false);
  const [saving, setSaving] = useState(false);

  const regionNames: Record<string, string> = {
    mien_bac: 'Miền Bắc',
    mien_trung: 'Miền Trung',
    mien_nam: 'Miền Nam',
    quoc_te: 'Quốc Tế',
  };

  const difficultyNames: Record<string, { label: string; color: string }> = {
    easy: { label: 'Dễ', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    medium: { label: 'Vừa', color: 'bg-amber-50 text-amber-700 border-amber-200' },
    hard: { label: 'Khó', color: 'bg-rose-50 text-rose-700 border-rose-200' },
  };

  const handleToggleSave = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      toast.error('Vui lòng đăng nhập để lưu món ăn yêu thích!');
      return;
    }

    setSaving(true);
    try {
      if (isSaved) {
        await recipesApi.unsaveRecipe(recipe.id);
        setIsSaved(false);
        toast.info(`Đã bỏ lưu món ${recipe.name}`);
        onSavedChange?.(recipe.id, false);
      } else {
        await recipesApi.saveRecipe(recipe.id);
        setIsSaved(true);
        toast.success(`Đã thêm ${recipe.name} vào danh sách yêu thích! ❤️`);
        onSavedChange?.(recipe.id, true);
      }
    } catch {
      toast.error('Có lỗi xảy ra khi lưu món');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Link
      to={`/recipes/${recipe.id}`}
      className="group flex flex-col rounded-3xl bg-white border border-slate-100 shadow-sm hover:shadow-xl hover:border-brand-200 transition-all duration-300 overflow-hidden hover:-translate-y-1.5"
    >
      {/* Thumbnail */}
      <div className="relative aspect-4/3 w-full overflow-hidden bg-slate-100">
        <img
          src={recipe.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'}
          alt={recipe.name}
          className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
          loading="lazy"
          onError={(e) => {
            const currentSrc = e.currentTarget.src;
            if (recipe.backup_image_url && !currentSrc.includes(recipe.backup_image_url)) {
              e.currentTarget.src = recipe.backup_image_url;
            } else {
              e.currentTarget.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80';
            }
          }}
        />

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20" />

        {/* Top Badges */}
        <div className="absolute top-3 inset-x-3 flex items-center justify-between">
          {recipe.region && (
            <span className="px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-md bg-white/90 text-neutral-800 shadow-xs">
              {regionNames[recipe.region] || recipe.region}
            </span>
          )}

          <button
            onClick={handleToggleSave}
            disabled={saving}
            className={`p-2 rounded-full backdrop-blur-md transition shadow-sm ml-auto ${
              isSaved
                ? 'bg-rose-500 text-white hover:bg-rose-600 scale-110'
                : 'bg-white/80 text-neutral-600 hover:bg-white hover:text-rose-500'
            }`}
            title={isSaved ? 'Bỏ lưu' : 'Lưu món yêu thích'}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
          </button>
        </div>

        {/* Rating overlay bottom left */}
        <div className="absolute bottom-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-black/40 backdrop-blur-md text-white text-xs font-medium">
          <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
          <span>{recipe.avg_rating ? recipe.avg_rating.toFixed(1) : '5.0'}</span>
          <span className="text-white/60">({recipe.rating_count || 12})</span>
        </div>
      </div>

      {/* Body Content */}
      <div className="flex-1 p-5 flex flex-col justify-between">
        <div>
          <h3 className="font-bold text-base text-neutral-900 group-hover:text-brand-600 transition-colors line-clamp-1 font-heading">
            {recipe.name}
          </h3>

          <p className="text-xs text-neutral-500 mt-1.5 line-clamp-2 leading-relaxed">
            {recipe.description || 'Món ăn đậm đà bản sắc Việt Nam với hương vị hấp dẫn và các bước chế biến đơn giản.'}
          </p>

          {/* Tags */}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {recipe.tags?.slice(0, 3).map((tag: any, idx: number) => {
              const tagName = typeof tag === 'string' ? tag : tag?.name;
              return (
                <span
                  key={typeof tag === 'string' ? `${tag}-${idx}` : (tag?.id || idx)}
                  className="px-2 py-0.5 text-[11px] font-medium rounded-md bg-neutral-100 text-neutral-600"
                >
                  #{tagName}
                </span>
              );
            })}
          </div>
        </div>

        {/* Footer Meta */}
        <div className="pt-4 mt-4 border-t border-neutral-100 flex items-center justify-between text-xs text-neutral-500 font-medium">
          <div className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-brand-500" />
            <span>{recipe.cook_time_min + recipe.prep_time_min} phút</span>
          </div>

          <span
            className={`px-2 py-0.5 rounded-md border text-[10px] font-bold uppercase tracking-wider ${
              difficultyNames[recipe.difficulty]?.color || 'bg-slate-50 text-slate-700'
            }`}
          >
            {difficultyNames[recipe.difficulty]?.label || recipe.difficulty}
          </span>
        </div>
      </div>
    </Link>
  );
};
