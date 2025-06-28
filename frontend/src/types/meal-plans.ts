/**
 * 食事プラン関連の型定義
 */

export interface NutritionInfo {
  calories?: number
  protein?: number
  carbs?: number
  fat?: number
  fiber?: number
  vitamins?: Record<string, number>
  minerals?: Record<string, number>
}

export interface PlannedMeal {
  id: string
  title: string
  description: string
  ingredients: string[]
  estimated_nutrition?: NutritionInfo
  preparation_time?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  allergens?: string[]
  notes?: string
}

export interface DayMealPlan {
  breakfast?: PlannedMeal
  lunch?: PlannedMeal
  dinner?: PlannedMeal
  snack?: PlannedMeal
}

export interface NutritionGoals {
  daily_calories: number
  daily_protein: number
  daily_carbs: number
  daily_fat: number
  daily_fiber?: number
}

export interface MealPlan {
  id: string
  user_id: string
  week_start: string // YYYY-MM-DD format
  title: string
  description?: string
  meals: Record<string, DayMealPlan> // 'monday', 'tuesday', etc.
  nutrition_goals?: NutritionGoals
  created_by: 'user' | 'genie'
  notes?: string
  created_at: string
  updated_at?: string
}

export interface MealPlanFormData {
  title: string
  description?: string
  week_start: string
  meals: Record<string, DayMealPlan>
  nutrition_goals?: NutritionGoals
  notes?: string
}

// API レスポンス型
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export type MealPlanApiResponse = ApiResponse<MealPlan>
export type MealPlansListApiResponse = ApiResponse<MealPlan[]>
