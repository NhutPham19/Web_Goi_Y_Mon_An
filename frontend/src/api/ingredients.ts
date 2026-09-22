import { apiClient } from './client';
import { Ingredient, Tag, SearchByIngredientResult, IngredientSubstitute } from '../types';

export const ingredientsApi = {
  getAll: async () => {
    const res = await apiClient.get('/ingredients');
    return res.data;
  },

  getTags: async () => {
    const res = await apiClient.get('/ingredients/tags');
    return res.data;
  },

  searchByIngredients: async (ingredientIds: number[], matchThreshold = 0.3) => {
    const res = await apiClient.post('/search/by-ingredients', {
      ingredient_ids: ingredientIds,
      match_threshold: matchThreshold,
    });
    return res.data;
  },

  getSubstitutes: async (ingredientId: number) => {
    const res = await apiClient.get(`/ingredients/${ingredientId}/substitutes`);
    return res.data;
  },
};
