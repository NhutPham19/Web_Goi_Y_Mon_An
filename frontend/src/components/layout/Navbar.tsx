import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { 
  UtensilsCrossed, 
  Sparkles, 
  Search, 
  CalendarDays, 
  Bookmark, 
  User, 
  LogOut, 
  Menu, 
  X,
  ChefHat
} from 'lucide-react';

interface NavbarProps {
  onOpenAuth: (mode?: 'login' | 'register') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenAuth }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Trang chủ', path: '/', icon: <UtensilsCrossed className="w-4 h-4" /> },
    { name: 'Gợi ý AI', path: '/recommend', icon: <Sparkles className="w-4 h-4 text-amber-500" /> },
    { name: 'Có gì nấu nấy', path: '/search-ingredients', icon: <Search className="w-4 h-4 text-brand-500" /> },
    { name: 'Thực đơn tuần', path: '/meal-planner', icon: <CalendarDays className="w-4 h-4 text-emerald-500" /> },
    { name: 'Đã lưu', path: '/saved', icon: <Bookmark className="w-4 h-4 text-rose-500" /> },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-orange-100 bg-white/80 backdrop-blur-md transition-all">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-amber-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition duration-200">
            <ChefHat className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xl font-bold bg-gradient-to-r from-brand-700 via-brand-600 to-amber-600 bg-clip-text text-transparent font-heading">
              Bếp Thông Minh
            </span>
            <span className="block text-[10px] text-muted-foreground font-medium -mt-1 tracking-wider uppercase">
              AI Recipe & Meal Planner
            </span>
          </div>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1.5">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-brand-50 text-brand-600 shadow-xs font-semibold'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100/60'
                }`}
              >
                {link.icon}
                {link.name}
              </Link>
            );
          })}
        </nav>

        {/* User / Auth Actions */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-3 pl-2 border-l border-neutral-200">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-sm">
                  {user.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="text-left leading-none">
                  <span className="block text-sm font-semibold text-neutral-800">{user.full_name}</span>
                  <span className="text-[11px] text-neutral-500">{user.email}</span>
                </div>
              </div>
              <button
                onClick={logout}
                title="Đăng xuất"
                className="p-2 text-neutral-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => onOpenAuth('login')}
                className="px-4 py-2 text-sm font-medium text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-xl transition"
              >
                Đăng nhập
              </button>
              <button
                onClick={() => onOpenAuth('register')}
                className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-brand-600 to-amber-500 hover:from-brand-700 hover:to-amber-600 rounded-xl shadow-md shadow-brand-500/20 hover:shadow-lg transition hover:-translate-y-0.5"
              >
                Đăng ký
              </button>
            </div>
          )}
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-lg text-neutral-600 hover:bg-neutral-100"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-neutral-200 bg-white px-4 pt-2 pb-6 space-y-2 shadow-xl animate-fade-in-up">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-base font-medium text-neutral-700 hover:bg-brand-50 hover:text-brand-600"
            >
              {link.icon}
              {link.name}
            </Link>
          ))}
          <div className="pt-4 border-t border-neutral-100">
            {isAuthenticated && user ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-sm">
                    {user.full_name?.charAt(0) || 'U'}
                  </div>
                  <div>
                    <div className="font-semibold text-sm">{user.full_name}</div>
                    <div className="text-xs text-neutral-500">{user.email}</div>
                  </div>
                </div>
                <button
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                  }}
                  className="px-3 py-1.5 text-xs text-rose-600 bg-rose-50 rounded-lg"
                >
                  Đăng xuất
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    onOpenAuth('login');
                    setMobileMenuOpen(false);
                  }}
                  className="w-full py-2.5 text-sm font-medium text-neutral-700 border border-neutral-200 rounded-xl"
                >
                  Đăng nhập
                </button>
                <button
                  onClick={() => {
                    onOpenAuth('register');
                    setMobileMenuOpen(false);
                  }}
                  className="w-full py-2.5 text-sm font-medium text-white bg-brand-600 rounded-xl"
                >
                  Đăng ký
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
