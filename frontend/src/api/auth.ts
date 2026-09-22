import { apiClient } from './client';
import { User } from '../types';

export const authApi = {
  login: async (email: string, password: string) => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },

  register: async (email: string, password: string, full_name: string) => {
    const res = await apiClient.post('/auth/register', { email, password, full_name });
    return res.data;
  },

  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
};
