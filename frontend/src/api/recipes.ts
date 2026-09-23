import { apiClient } from './client';
import { Recipe } from '../types';

export interface GetRecipesParams {
  page?: number;
  limit?: number;
  search?: string;
  q?: string;
  tag?: string;
  region?: string;
  difficulty?: string;
  max_cook_time?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
  published?: 'true' | 'false' | 'all';
}

export const recipesApi = {
  getAll: async (params?: GetRecipesParams) => {
    const queryParams: any = { ...params };
    if (queryParams.search && !queryParams.q) {
      queryParams.q = queryParams.search;
    }
    const res = await apiClient.get('/recipes', { params: queryParams });
    return res.data;
  },

  getById: async (id: number | string) => {
    const res = await apiClient.get(`/recipes/${id}`);
    return res.data;
  },

  rate: async (recipeId: number, score: number, review_text?: string) => {
    const res = await apiClient.post(`/recipes/${recipeId}/ratings`, { score, review_text });
    return res.data;
  },

  recordView: async (recipeId: number) => {
    try {
      await apiClient.post(`/recipes/${recipeId}/views`);
    } catch {
      // fire-and-forget
    }
  },

  getSaved: async () => {
    const res = await apiClient.get('/users/me/saved');
    return res.data;
  },

  saveRecipe: async (recipeId: number) => {
    const res = await apiClient.post(`/users/me/saved/${recipeId}`);
    return res.data;
  },

  unsaveRecipe: async (recipeId: number) => {
    const res = await apiClient.delete(`/users/me/saved/${recipeId}`);
    return res.data;
  },
};
