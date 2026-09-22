export type Difficulty = 'easy' | 'medium' | 'hard';
export type Region = 'mien_nam' | 'mien_bac' | 'mien_trung' | 'quoc_te';
export type MealType = 'breakfast' | 'lunch' | 'dinner';

export interface UserPreference {
  id: number;
  pref_type: 'diet' | 'taste' | 'allergy' | 'serving_size';
  pref_value: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
  preferences?: UserPreference[];
}

export interface Tag {
  id: number;
  name: string;
  color: string;
}

export interface Ingredient {
  id: number;
  name: string;
  category: 'rau_cu' | 'thit' | 'hai_san' | 'gia_vi' | 'khac';
  unit: string;
  emoji: string;
  calories_per_100g: number;
}

export interface RecipeIngredient {
  id?: number;
  ingredient_id: number;
  name: string;
  quantity: number;
  unit: string;
  is_optional: boolean;
  emoji?: string;
  calories_per_100g?: number;
}

export interface Step {
  id?: number;
  step_number: number;
  description: string;
  duration_min?: number | null;
}

export interface Recipe {
  id: number;
  name: string;
  description?: string;
  image_url?: string;
  difficulty: Difficulty;
  cook_time_min: number;
  prep_time_min: number;
  servings: number;
  avg_rating: number;
  rating_count: number;
  region?: Region;
  tags: Tag[];
  ingredients?: RecipeIngredient[];
  steps?: Step[];
  is_saved?: boolean;
}

export interface SearchByIngredientResult {
  recipe: Recipe;
  matched_count: number;
  total_required: number;
  match_percent: number;
  matched_ingredients: string[];
  missing_ingredients: string[];
}

export interface IngredientSubstitute {
  original_id: number;
  substitute_id: number;
  substitute_name: string;
  ratio: number;
  note?: string;
  emoji?: string;
}

export interface MealPlanItem {
  id: number;
  date: string; // YYYY-MM-DD
  meal_type: MealType;
  recipe_id: number;
  servings: number;
  recipe: Recipe;
}

export interface ShoppingListItem {
  ingredient_id: number;
  name: string;
  total_quantity: number;
  unit: string;
  emoji?: string;
  category: string;
  checked?: boolean;
}
