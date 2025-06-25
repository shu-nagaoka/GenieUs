/**
 * 成長記録API関連の関数
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 新しいカテゴリ型定義
export type GrowthType = 
  | 'body_growth'      // からだの成長
  | 'language_growth'  // ことばの成長
  | 'skills'          // できること
  | 'social_skills'   // お友達との関わり
  | 'hobbies'         // 習い事・特技
  | 'life_skills'     // 生活スキル
  // 後方互換性のため従来タイプも保持
  | 'physical' | 'emotional' | 'cognitive' | 'milestone' | 'photo'

export type GrowthCategory = 
  // からだの成長
  | 'height' | 'weight' | 'movement'
  // ことばの成長
  | 'speech' | 'first_words' | 'vocabulary'
  // できること
  | 'colors' | 'numbers' | 'puzzle' | 'drawing'
  // お友達との関わり
  | 'playing_together' | 'helping' | 'sharing' | 'kindness'
  // 習い事・特技
  | 'piano' | 'swimming' | 'dancing' | 'sports'
  // 生活スキル
  | 'toilet' | 'brushing' | 'dressing' | 'cleaning'
  // 従来カテゴリ（後方互換性）
  | 'smile' | 'expression' | 'achievement'

export type DetectedBy = 'genie' | 'parent'

export interface GrowthRecord {
  id: string
  user_id: string
  child_id?: string  // 家族情報からの子どもID
  child_name: string
  date: string
  age_in_months: number
  type: GrowthType
  category: GrowthCategory
  title: string
  description: string
  value?: string | number
  unit?: string
  image_url?: string
  detected_by: DetectedBy
  confidence?: number
  emotions?: string[]
  development_stage?: string
  created_at: string
  updated_at: string
}

export interface GrowthRecordCreateRequest {
  child_id?: string  // 家族情報からの子どもID
  child_name: string
  date: string
  age_in_months: number
  type: GrowthType
  category: GrowthCategory
  title: string
  description: string
  value?: string | number
  unit?: string
  image_url?: string
  detected_by?: DetectedBy
  confidence?: number
  emotions?: string[]
  development_stage?: string
  user_id?: string
}

export interface GrowthRecordUpdateRequest {
  child_id?: string  // 家族情報からの子どもID
  child_name?: string
  date?: string
  age_in_months?: number
  type?: GrowthType
  category?: GrowthCategory
  title?: string
  description?: string
  value?: string | number
  unit?: string
  image_url?: string
  detected_by?: DetectedBy
  confidence?: number
  emotions?: string[]
  development_stage?: string
  user_id?: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
}

export interface GrowthCategoryInfo {
  label: string
  description: string
  color: string
  icon: string
  categories: Array<{
    value: string
    label: string
    unit: string
  }>
}

export interface GrowthCategoriesResponse {
  types: Record<string, GrowthCategoryInfo>
}

export interface ChildInfo {
  child_id: string
  name: string
  age: string
  age_in_months: number
  gender: string
  birth_date: string
}

/**
 * 成長記録一覧を取得
 */
export async function getGrowthRecords(params?: {
  user_id?: string
  child_name?: string
  type?: string
  category?: string
}): Promise<ApiResponse<GrowthRecord[]>> {
  try {
    const searchParams = new URLSearchParams()
    
    if (params?.user_id) searchParams.append('user_id', params.user_id)
    if (params?.child_name) searchParams.append('child_name', params.child_name)
    if (params?.type) searchParams.append('type', params.type)
    if (params?.category) searchParams.append('category', params.category)

    const url = `${API_BASE_URL}/api/v1/growth-records/list${searchParams.toString() ? '?' + searchParams.toString() : ''}`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('成長記録一覧取得エラー:', error)
    return {
      success: false,
      message: '成長記録一覧の取得に失敗しました'
    }
  }
}

/**
 * 成長記録詳細を取得
 */
export async function getGrowthRecord(recordId: string, userId: string = 'frontend_user'): Promise<ApiResponse<GrowthRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/growth-records/detail/${recordId}?user_id=${userId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('成長記録詳細取得エラー:', error)
    return {
      success: false,
      message: '成長記録詳細の取得に失敗しました'
    }
  }
}

/**
 * 新しい成長記録を作成
 */
export async function createGrowthRecord(recordData: GrowthRecordCreateRequest): Promise<ApiResponse<GrowthRecord>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/growth-records/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...recordData,
        user_id: recordData.user_id || 'frontend_user'
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('成長記録作成エラー:', error)
    return {
      success: false,
      message: '成長記録の作成に失敗しました'
    }
  }
}

/**
 * 成長記録を更新
 */
export async function updateGrowthRecord(recordId: string, recordData: GrowthRecordUpdateRequest): Promise<ApiResponse<GrowthRecord>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/growth-records/update/${recordId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...recordData,
        user_id: recordData.user_id || 'frontend_user'
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('成長記録更新エラー:', error)
    return {
      success: false,
      message: '成長記録の更新に失敗しました'
    }
  }
}

/**
 * 成長記録を削除
 */
export async function deleteGrowthRecord(recordId: string, userId: string = 'frontend_user'): Promise<ApiResponse<GrowthRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/growth-records/delete/${recordId}?user_id=${userId}`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('成長記録削除エラー:', error)
    return {
      success: false,
      message: '成長記録の削除に失敗しました'
    }
  }
}

/**
 * 子ども別の成長記録を取得
 */
export async function getGrowthRecordsByChild(childName: string, userId: string = 'frontend_user'): Promise<ApiResponse<GrowthRecord[]>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/growth-records/child/${encodeURIComponent(childName)}?user_id=${userId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('子ども別成長記録取得エラー:', error)
    return {
      success: false,
      message: '子ども別成長記録の取得に失敗しました'
    }
  }
}

/**
 * 成長記録カテゴリ情報を取得
 */
export async function getGrowthCategories(): Promise<ApiResponse<GrowthCategoriesResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/growth-records/categories`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('成長記録カテゴリ取得エラー:', error)
    return {
      success: false,
      message: '成長記録カテゴリの取得に失敗しました'
    }
  }
}

/**
 * 家族情報から子ども一覧を取得
 */
export async function getChildrenForGrowthRecords(userId: string = 'frontend_user'): Promise<ApiResponse<ChildInfo[]>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/growth-records/children?user_id=${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('子ども情報取得エラー:', error)
    return {
      success: false,
      message: '子ども情報の取得に失敗しました'
    }
  }
}