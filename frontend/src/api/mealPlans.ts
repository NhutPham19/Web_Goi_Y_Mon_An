import { apiClient } from './client';
import { MealPlanItem, ShoppingListItem } from '../types';

export const mealPlansApi = {
  getAll: async (startDate?: string, endDate?: string) => {
    const res = await apiClient.get('/meal-plans', {
      params: { week_start: startDate, start_date: startDate, end_date: endDate },
    });
    return res.data;
  },

  add: async (date: string, mealType: string, recipeId: number, servings = 4) => {
    const res = await apiClient.post('/meal-plans', {
      date,
      meal_type: mealType,
      recipe_id: recipeId,
      servings,
    });
    return res.data;
  },

  remove: async (id: number) => {
    const res = await apiClient.delete(`/meal-plans/${id}`);
    return res.data;
  },

  getShoppingList: async (startDate?: string, endDate?: string) => {
    const res = await apiClient.get('/meal-plans/shopping-list', {
      params: { week_start: startDate, start_date: startDate, end_date: endDate },
    });
    return res.data;
  },
};
