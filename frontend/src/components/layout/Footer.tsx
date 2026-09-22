import React from 'react';
import { ChefHat, Heart, Sparkles, Utensils } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-orange-100 bg-white/60 backdrop-blur-sm mt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="md:col-span-1 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white">
                <ChefHat className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg text-neutral-800 font-heading">Bếp Thông Minh</span>
            </div>
            <p className="text-sm text-neutral-500 leading-relaxed">
              Hệ thống gợi ý công thức và lập kế hoạch bữa ăn thông minh ứng dụng thuật toán máy học Hybrid Recommendation và tìm kiếm linh hoạt theo nguyên liệu có sẵn.
            </p>
          </div>

          {/* Quick links */}
          <div>
            <h4 className="font-semibold text-neutral-800 text-sm mb-3">Tính năng chính</h4>
            <ul className="space-y-2 text-sm text-neutral-500">
              <li><Link to="/recommend" className="hover:text-brand-600 transition">Gợi ý thông minh (AI)</Link></li>
              <li><Link to="/search-ingredients" className="hover:text-brand-600 transition">Có gì nấu nấy (Tủ lạnh)</Link></li>
              <li><Link to="/meal-planner" className="hover:text-brand-600 transition">Kế hoạch tuần & Đi chợ</Link></li>
              <li><Link to="/saved" className="hover:text-brand-600 transition">Công thức yêu thích</Link></li>
            </ul>
          </div>

          {/* Regions */}
          <div>
            <h4 className="font-semibold text-neutral-800 text-sm mb-3">Ẩm thực 3 Miền</h4>
            <ul className="space-y-2 text-sm text-neutral-500">
              <li><Link to="/?region=mien_bac" className="hover:text-brand-600 transition">Đặc sản Miền Bắc (Phở, Bún chả...)</Link></li>
              <li><Link to="/?region=mien_trung" className="hover:text-brand-600 transition">Đặc sản Miền Trung (Bún bò, Mì Quảng...)</Link></li>
              <li><Link to="/?region=mien_nam" className="hover:text-brand-600 transition">Đặc sản Miền Nam (Cơm tấm, Hủ tiếu...)</Link></li>
            </ul>
          </div>

          {/* Tech stack badge */}
          <div>
            <h4 className="font-semibold text-neutral-800 text-sm mb-3">Nền tảng công nghệ</h4>
            <div className="flex flex-wrap gap-1.5">
              <span className="px-2.5 py-1 text-xs rounded-lg bg-orange-50 text-brand-700 font-medium">Flask & Python</span>
              <span className="px-2.5 py-1 text-xs rounded-lg bg-emerald-50 text-emerald-700 font-medium">Supabase DB</span>
              <span className="px-2.5 py-1 text-xs rounded-lg bg-blue-50 text-blue-700 font-medium">React & Vite</span>
              <span className="px-2.5 py-1 text-xs rounded-lg bg-purple-50 text-purple-700 font-medium">21st.dev UI</span>
              <span className="px-2.5 py-1 text-xs rounded-lg bg-amber-50 text-amber-700 font-medium">Morph SVG</span>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-neutral-100 flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-400 gap-4">
          <p>© 2026 Bếp Thông Minh — Đồ án Chuyên ngành TVU 2026.</p>
          <div className="flex items-center gap-1">
            <span>Thiết kế và phát triển với</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
            <span>và đam mê ẩm thực Việt Nam</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
