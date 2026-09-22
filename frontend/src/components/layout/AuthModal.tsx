import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { X, Lock, Mail, User, Sparkles } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialMode = 'login',
}) => {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    let success = false;
    if (mode === 'login') {
      success = await login(email, password);
    } else {
      success = await register(email, password, fullName);
    }
    setLoading(false);
    if (success) {
      onClose();
    }
  };

  const fillDemo = (role: 'user' | 'admin') => {
    if (role === 'admin') {
      setEmail('admin@gmail.com');
      setPassword('Password123@');
    } else {
      setEmail('nhut@gmail.com');
      setPassword('Password123@');
    }
    setMode('login');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in-up">
      <div className="relative w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl border border-neutral-100">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 rounded-full transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="text-center mb-6">
          <div className="inline-flex p-3 rounded-2xl bg-brand-50 text-brand-600 mb-3">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-2xl font-bold text-neutral-900 font-heading">
            {mode === 'login' ? 'Đăng Nhập Tài Khoản' : 'Tạo Tài Khoản Mới'}
          </h3>
          <p className="text-sm text-neutral-500 mt-1">
            {mode === 'login'
              ? 'Đăng nhập để nhận gợi ý khẩu vị chuẩn xác và lưu công thức yêu thích'
              : 'Tham gia cùng cộng đồng Bếp Thông Minh'}
          </p>
        </div>

        {/* Demo Fast Fill */}
        <div className="mb-6 p-3 rounded-2xl bg-amber-50/80 border border-amber-200/60 flex items-center justify-between text-xs text-amber-900">
          <span className="font-medium">💡 Tài khoản thử nghiệm:</span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => fillDemo('user')}
              className="px-2.5 py-1 bg-white rounded-lg shadow-xs hover:bg-amber-100 font-semibold transition"
            >
              Nhựt (User)
            </button>
            <button
              type="button"
              onClick={() => fillDemo('admin')}
              className="px-2.5 py-1 bg-white rounded-lg shadow-xs hover:bg-amber-100 font-semibold transition"
            >
              Admin
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1.5">Họ và tên</label>
              <div className="relative">
                <User className="w-4 h-4 text-neutral-400 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  required
                  placeholder="Nguyễn Văn A"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-neutral-700 mb-1.5">Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-neutral-400 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-neutral-700 mb-1.5">Mật khẩu</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-neutral-400 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-brand-600 to-amber-500 text-white font-medium text-sm shadow-md hover:shadow-lg transition hover:-translate-y-0.5 disabled:opacity-50"
          >
            {loading ? 'Đang xử lý...' : mode === 'login' ? 'Đăng nhập ngay' : 'Đăng ký tài khoản'}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-6 text-center text-xs text-neutral-500">
          {mode === 'login' ? (
            <p>
              Chưa có tài khoản?{' '}
              <button
                type="button"
                onClick={() => setMode('register')}
                className="font-semibold text-brand-600 hover:underline"
              >
                Đăng ký ngay
              </button>
            </p>
          ) : (
            <p>
              Đã có tài khoản?{' '}
              <button
                type="button"
                onClick={() => setMode('login')}
                className="font-semibold text-brand-600 hover:underline"
              >
                Đăng nhập
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
