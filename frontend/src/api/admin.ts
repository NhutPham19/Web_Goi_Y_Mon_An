import { apiClient } from './client';
import { Recipe, Tag, Ingredient } from '../types';

export interface AdminStats {
  total_recipes: number;
  published_recipes: number;
  draft_recipes: number;
  total_users: number;
  total_ratings: number;
  total_views: number;
  top_rated_recipes: Recipe[];
  most_viewed_recipes: (Recipe & { view_count: number })[];
  recent_ratings: any[];
}

export interface CreateRecipePayload {
  name: string;
  description?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  cook_time_min: number;
  prep_time_min: number;
  servings: number;
  region?: string;
  is_published?: boolean;
  image_url?: string;
  backup_image_url?: string;
  tag_ids?: number[];
  ingredients?: {
    ingredient_id: number;
    quantity: number;
    unit: string;
    is_optional?: boolean;
  }[];
  steps?: {
    step_number: number;
    description: string;
    duration_min?: number | null;
  }[];
}

export const adminApi = {
  getStats: async () => {
    const res = await apiClient.get('/admin/stats');
    return res.data;
  },

  getRecipes: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    q?: string;
    region?: string;
    difficulty?: string;
    published?: 'all' | 'true' | 'false';
  }) => {
    const queryParams: any = { published: 'all', ...params };
    if (queryParams.search && !queryParams.q) {
      queryParams.q = queryParams.search;
    }
    const res = await apiClient.get('/recipes', { params: queryParams });
    return res.data;
  },

  createRecipe: async (payload: CreateRecipePayload) => {
    const res = await apiClient.post('/admin/recipes', payload);
    return res.data;
  },

  updateRecipe: async (id: number, payload: Partial<CreateRecipePayload>) => {
    const res = await apiClient.put(`/admin/recipes/${id}`, payload);
    return res.data;
  },

  deleteRecipe: async (id: number) => {
    const res = await apiClient.delete(`/admin/recipes/${id}`);
    return res.data;
  },

  togglePublish: async (id: number) => {
    const res = await apiClient.post(`/admin/recipes/${id}/publish`);
    return res.data;
  },

  uploadImageFile: async (id: number, file: File, slot: 1 | 2 = 1) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('image', file);
    formData.append('slot', slot.toString());
    const res = await apiClient.post(`/admin/recipes/${id}/image`, formData);
    return res.data;
  },

  setImageUrl: async (id: number, imageUrl: string, slot: 1 | 2 = 1) => {
    const res = await apiClient.post(`/admin/recipes/${id}/image`, {
      image_url: imageUrl,
      slot,
    });
    return res.data;
  },

  setPrimaryImage: async (id: number, slot: 1 | 2) => {
    const res = await apiClient.post(`/admin/recipes/${id}/set-primary`, { slot });
    return res.data;
  },
};
