import { apiClient } from './client';
import { Recipe, UserPreference } from '../types';

export const recommendationsApi = {
  getForMe: async (limit = 10, forceRefresh = false) => {
    const res = await apiClient.get('/recommendations', {
      params: { limit, force_refresh: forceRefresh },
    });
    return res.data;
  },

  getPreferences: async () => {
    const res = await apiClient.get('/auth/users/me/preferences');
    return res.data;
  },

  updatePreferences: async (preferences: Array<{ pref_type: string; pref_value: string }>) => {
    const res = await apiClient.post('/auth/users/me/preferences', { preferences });
    return res.data;
  },
};
