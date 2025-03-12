// Recipe-related types
export interface RecipeParams {
  id: string;
}

// Define Recipe interface
export interface Recipe {
  id: string;
  title?: string;
  name?: string;
  sourceUrl?: string;
  source_url?: string;
  instructions?: string;
  sourceName?: string;
  image?: string;
  readyInMinutes?: number;
  ingredients?: string[];
  extendedIngredients?: any[];
  servings?: number;
  cuisines?: string[];
  cuisine?: string;
  diets?: string[];
  isFavorite?: boolean;
  summary?: string;
  nutrition?: {
    nutrients: Array<{
      name: string;
      amount: number;
      unit: string;
    }>;
  };
}

// User-related types
export interface UserParams {
  id: string;
}

// Other common types
export interface PaginationParams {
  page: number;
  limit: number;
}

export interface SortParams {
  sortBy: string;
  sortDirection: 'asc' | 'desc';
}

export interface FilterParams {
  query?: string;
  cuisine?: string;
  diet?: string;
  intolerances?: string;
  includeIngredients?: string;
  excludeIngredients?: string;
  type?: string;
  maxReadyTime?: number;
  minCalories?: number;
  maxCalories?: number;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T> {
  total: number;
  page: number;
  limit: number;
  totalPages: number;
} 