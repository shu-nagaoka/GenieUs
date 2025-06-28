/**
 * 食事記録管理API
 * バックエンドAPI: /api/v1/meal-records
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

// === Interfaces ===

export interface NutritionInfo {
  calories?: number
  protein?: number
  carbs?: number
  fat?: number
  fiber?: number
  vitamins?: string[]
}

export interface MealRecord {
  id: string
  child_id: string
  meal_name: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  detected_foods: string[]
  nutrition_info: NutritionInfo
  timestamp: string
  detection_source: 'manual' | 'image_ai' | 'voice_ai'
  confidence: number
  image_path?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface CreateMealRecordRequest {
  child_id: string
  meal_name: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  detected_foods?: string[]
  nutrition_info?: NutritionInfo
  detection_source?: 'manual' | 'image_ai' | 'voice_ai'
  confidence?: number
  image_path?: string
  notes?: string
  timestamp?: string
}

export interface UpdateMealRecordRequest {
  meal_name?: string
  meal_type?: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  detected_foods?: string[]
  nutrition_info?: NutritionInfo
  notes?: string
}

export interface SearchMealRecordsRequest {
  child_id: string
  start_date?: string
  end_date?: string
  meal_type?: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  limit?: number
  offset?: number
}

export interface NutritionSummary {
  total_meals: number
  total_calories: number
  avg_nutrition: {
    protein: number
    carbs: number
    fat: number
    fiber: number
  }
  meal_type_distribution: {
    breakfast: number
    lunch: number
    dinner: number
    snack: number
  }
  most_common_foods: string[]
  nutrition_balance_score: number
  period_start?: string
  period_end?: string
}

// === API Response Types ===

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface MealRecordResponse {
  success: boolean
  meal_record?: MealRecord
  error?: string
}

export interface MealRecordListResponse {
  success: boolean
  meal_records?: MealRecord[]
  total_count: number
  error?: string
}

export interface NutritionSummaryResponse {
  success: boolean
  summary?: NutritionSummary
  error?: string
}

// === API Functions ===

/**
 * 食事記録作成
 */
export async function createMealRecord(
  request: CreateMealRecordRequest
): Promise<ApiResponse<MealRecordResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/meal-records/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事記録の作成に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Create meal record error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事記録の作成に失敗しました',
    }
  }
}

/**
 * 食事記録取得
 */
export async function getMealRecord(
  meal_record_id: string
): Promise<ApiResponse<MealRecordResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/meal-records/${meal_record_id}`)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事記録の取得に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Get meal record error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事記録の取得に失敗しました',
    }
  }
}

/**
 * 食事記録更新
 */
export async function updateMealRecord(
  meal_record_id: string,
  request: UpdateMealRecordRequest
): Promise<ApiResponse<MealRecordResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/meal-records/${meal_record_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('Update meal record API error:', {
        status: response.status,
        statusText: response.statusText,
        errorData
      })
      throw new Error(errorData.detail || errorData.message || `更新に失敗しました (${response.status})`)
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Update meal record error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事記録の更新に失敗しました',
    }
  }
}

/**
 * 食事記録削除
 */
export async function deleteMealRecord(
  meal_record_id: string
): Promise<ApiResponse<void>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/meal-records/${meal_record_id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('Delete meal record API error:', {
        status: response.status,
        statusText: response.statusText,
        errorData
      })
      throw new Error(errorData.detail || errorData.message || `削除に失敗しました (${response.status})`)
    }

    return { success: true, message: '食事記録を削除しました' }
  } catch (error) {
    console.error('Delete meal record error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事記録の削除に失敗しました',
    }
  }
}

/**
 * 食事記録検索・一覧取得
 */
export async function searchMealRecords(
  request: SearchMealRecordsRequest
): Promise<ApiResponse<MealRecordListResponse>> {
  try {
    const params = new URLSearchParams()
    params.append('child_id', request.child_id)
    
    if (request.start_date) params.append('start_date', request.start_date)
    if (request.end_date) params.append('end_date', request.end_date)
    if (request.meal_type) params.append('meal_type', request.meal_type)
    if (request.limit) params.append('limit', request.limit.toString())
    if (request.offset) params.append('offset', request.offset.toString())

    const response = await fetch(`${API_BASE_URL}/api/v1/meal-records/?${params.toString()}`)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事記録の検索に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Search meal records error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事記録の検索に失敗しました',
    }
  }
}

/**
 * 栄養サマリー取得
 */
export async function getNutritionSummary(
  child_id: string,
  start_date?: string,
  end_date?: string
): Promise<ApiResponse<NutritionSummaryResponse>> {
  try {
    const params = new URLSearchParams()
    if (start_date) params.append('start_date', start_date)
    if (end_date) params.append('end_date', end_date)

    const url = `${API_BASE_URL}/api/v1/meal-records/nutrition-summary/${child_id}`
    const fullUrl = params.toString() ? `${url}?${params.toString()}` : url

    const response = await fetch(fullUrl)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '栄養サマリーの取得に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Get nutrition summary error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '栄養サマリーの取得に失敗しました',
    }
  }
}

/**
 * 子供の食事記録一覧取得 (簡易版)
 */
export async function getMealRecordsByChild(
  child_id: string,
  limit: number = 50
): Promise<ApiResponse<MealRecordListResponse>> {
  return searchMealRecords({
    child_id,
    limit,
    offset: 0,
  })
}

/**
 * 今日の食事記録取得
 */
export async function getTodayMealRecords(
  child_id: string
): Promise<ApiResponse<MealRecordListResponse>> {
  const today = new Date()
  const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59)

  return searchMealRecords({
    child_id,
    start_date: startOfDay.toISOString(),
    end_date: endOfDay.toISOString(),
    limit: 50,
  })
}

/**
 * 今週の栄養サマリー取得
 */
export async function getWeeklyNutritionSummary(
  child_id: string
): Promise<ApiResponse<NutritionSummaryResponse>> {
  const today = new Date()
  const startOfWeek = new Date(today.getFullYear(), today.getMonth(), today.getDate() - today.getDay())
  const endOfWeek = new Date(today.getFullYear(), today.getMonth(), today.getDate() - today.getDay() + 6, 23, 59, 59)

  return getNutritionSummary(
    child_id,
    startOfWeek.toISOString(),
    endOfWeek.toISOString()
  )
}