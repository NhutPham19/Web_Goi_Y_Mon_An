import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { authApi } from '../api/auth';
import { toast } from 'sonner';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, fullName: string) => Promise<boolean>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      const res = await authApi.getMe();
      if (res.success && res.data) {
        setUser(res.data);
        localStorage.setItem('user', JSON.stringify(res.data));
      }
    } catch {
      // Token might be invalid
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, [token]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const res = await authApi.login(email, password);
      if (res.success && res.data) {
        const receivedToken = res.data.token || res.data.access_token;
        const receivedUser = res.data.user;
        setToken(receivedToken);
        setUser(receivedUser);
        localStorage.setItem('token', receivedToken);
        localStorage.setItem('user', JSON.stringify(receivedUser));
        toast.success(`Chào mừng trở lại, ${receivedUser.full_name}!`);
        return true;
      }
      return false;
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Đăng nhập thất bại. Vui lòng kiểm tra lại.';
      toast.error(msg);
      return false;
    }
  };

  const register = async (email: string, password: string, fullName: string): Promise<boolean> => {
    try {
      const res = await authApi.register(email, password, fullName);
      if (res.success && res.data) {
        const receivedToken = res.data.token || res.data.access_token;
        const receivedUser = res.data.user;
        setToken(receivedToken);
        setUser(receivedUser);
        localStorage.setItem('token', receivedToken);
        localStorage.setItem('user', JSON.stringify(receivedUser));
        toast.success('Đăng ký tài khoản thành công!');
        return true;
      }
      return false;
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Đăng ký thất bại.';
      toast.error(msg);
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    toast.info('Đã đăng xuất');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
