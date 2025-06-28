/**
 * 食事記録 API クライアント
 */

const API_BASE_URL = 'http://localhost:8080'

export interface CreateMealRecordRequest {
  child_id: string
  meal_name: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  detected_foods?: string[]
  nutrition_info?: Record<string, any>
  detection_source?: string
  confidence?: number
  image_path?: string
  notes?: string
  timestamp?: string
}

export interface MealRecordResponse {
  success: boolean
  meal_record?: {
    id: string
    child_id: string
    meal_name: string
    meal_type: string
    detected_foods: string[]
    nutrition_info: Record<string, any>
    created_at: string
  }
  error?: string
}

/**
 * 食事記録を作成
 */
export const createMealRecord = async (request: CreateMealRecordRequest): Promise<MealRecordResponse> => {
  try {
    console.log('🍽️ 食事記録API呼び出し:', request)
    
    const response = await fetch(`${API_BASE_URL}/api/v1/meal-records/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    console.log('📥 食事記録APIレスポンス:', {
      status: response.status,
      statusText: response.statusText,
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ 食事記録API エラーレスポンス:', errorText)
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('✅ 食事記録作成成功:', result)
    return result
  } catch (error) {
    console.error('❌ 食事記録作成エラー:', error)
    throw error
  }
}

/**
 * 画像解析結果から食事記録リクエストを作成
 */
export const createMealRecordFromAnalysis = (
  analysisData: any,
  childId: string = 'default_child'
): CreateMealRecordRequest => {
  const suggestedMealData = analysisData.suggested_meal_data || {}
  
  return {
    child_id: childId,
    meal_name: suggestedMealData.meal_name || 'AI検出食事',
    meal_type: suggestedMealData.estimated_meal_time || 'snack',
    detected_foods: suggestedMealData.detected_foods || [],
    nutrition_info: suggestedMealData.nutrition_balance || {},
    detection_source: 'image_ai',
    confidence: suggestedMealData.confidence || 0.8,
    image_path: analysisData.image_path,
    notes: '画像解析により自動検出された食事記録',
  }
}