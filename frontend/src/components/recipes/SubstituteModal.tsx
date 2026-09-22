import React, { useEffect, useState } from 'react';
import { X, ArrowRightLeft, Sparkles, AlertCircle } from 'lucide-react';
import { ingredientsApi } from '@/api/ingredients';
import { IngredientSubstitute } from '@/types';

interface SubstituteModalProps {
  ingredientId: number | null;
  ingredientName: string;
  isOpen: boolean;
  onClose: () => void;
}

export const SubstituteModal: React.FC<SubstituteModalProps> = ({
  ingredientId,
  ingredientName,
  isOpen,
  onClose,
}) => {
  const [substitutes, setSubstitutes] = useState<IngredientSubstitute[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || !ingredientId) return;

    const fetchSubstitutes = async () => {
      setLoading(true);
      try {
        const res = await ingredientsApi.getSubstitutes(ingredientId);
        if (res.success && res.data) {
          const list = Array.isArray(res.data) ? res.data : (res.data.substitutes || []);
          setSubstitutes(list);
        } else {
          setSubstitutes([]);
        }
      } catch {
        setSubstitutes([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSubstitutes();
  }, [isOpen, ingredientId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in-up">
      <div className="relative w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl border border-neutral-100">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 rounded-full transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2.5 rounded-xl bg-amber-50 text-amber-600">
            <ArrowRightLeft className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-neutral-900 font-heading">Nguyên liệu thay thế</h3>
            <p className="text-xs text-neutral-500">
              Gợi ý khi nhà bạn thiếu: <span className="font-semibold text-brand-600">{ingredientName}</span>
            </p>
          </div>
        </div>

        {loading ? (
          <div className="py-8 text-center text-sm text-neutral-400">Đang tìm gợi ý thay thế...</div>
        ) : substitutes.length === 0 ? (
          <div className="py-8 text-center">
            <AlertCircle className="w-8 h-8 text-neutral-300 mx-auto mb-2" />
            <p className="text-sm text-neutral-600 font-medium">Chưa có nguyên liệu thay thế phù hợp</p>
            <p className="text-xs text-neutral-400 mt-1">
              Bạn có thể điều chỉnh hoặc gia giảm gia vị theo khẩu vị riêng.
            </p>
          </div>
        ) : (
          <div className="space-y-3 mt-4">
            {substitutes.map((sub, idx) => (
              <div
                key={idx}
                className="p-4 rounded-2xl bg-orange-50/50 border border-orange-100 flex flex-col gap-2 hover:bg-orange-50 transition"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{sub.emoji || '✨'}</span>
                    <span className="font-bold text-neutral-800 text-sm">
                      {sub.substitute_name || (sub as any).name || 'Nguyên liệu thay thế'}
                    </span>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-100 text-brand-700">
                    Tỷ lệ: {sub.ratio}:1
                  </span>
                </div>
                {sub.note && (
                  <p className="text-xs text-neutral-600 italic bg-white/70 p-2.5 rounded-xl">
                    💡 {sub.note}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-sm font-medium bg-neutral-100 hover:bg-neutral-200 text-neutral-700 transition"
          >
            Đã hiểu
          </button>
        </div>
      </div>
    </div>
  );
};
