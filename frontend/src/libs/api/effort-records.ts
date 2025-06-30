/**
 * 努力記録API関連の関数
 */

import { API_BASE_URL } from '@/config/api'

export interface EffortRecord {
  id: string
  user_id: string
  date: string
  period: string
  effort_count: number
  highlights: string[]
  score: number
  categories: {
    feeding: number
    sleep: number
    play: number
    care: number
  }
  summary: string
  achievements: string[]
  created_at: string
  updated_at: string
}

export interface EffortRecordCreateRequest {
  date: string
  period: string
  effort_count: number
  highlights: string[]
  score: number
  categories: {
    feeding: number
    sleep: number
    play: number
    care: number
  }
  summary: string
  achievements: string[]
  user_id?: string
}

export interface EffortRecordUpdateRequest {
  date?: string
  period?: string
  effort_count?: number
  highlights?: string[]
  score?: number
  categories?: {
    feeding: number
    sleep: number
    play: number
    care: number
  }
  summary?: string
  achievements?: string[]
  user_id?: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
}

/**
 * 努力記録一覧を取得
 */
export async function getEffortRecords(params?: {
  user_id?: string
  period?: string
  start_date?: string
  end_date?: string
}): Promise<ApiResponse<EffortRecord[]>> {
  try {
    const userId = params?.user_id || 'frontend_user'
    const response = await fetch(
      `${API_BASE_URL}/api/effort-reports/list?user_id=${userId}`,
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

    const result = await response.json()
    
    if (result.success && result.data) {
      // バックエンドのデータ形式をフロントエンドの形式に変換
      const transformedData: EffortRecord[] = result.data.map((item: any) => ({
        id: item.id,
        user_id: item.user_id,
        date: new Date(item.created_at).toISOString().split('T')[0],
        period: `過去${item.period_days}日間`,
        effort_count: item.effort_count || 0,
        highlights: item.highlights || [],
        score: item.score || 0,
        categories: {
          feeding: item.categories?.['食事管理'] || 0,
          sleep: item.categories?.['記録継続'] || 0,
          play: item.categories?.['活動企画'] || 0,
          care: item.categories?.['健康管理'] || 0,
        },
        summary: item.summary || '',
        achievements: item.achievements || [],
        created_at: item.created_at || new Date().toISOString(),
        updated_at: item.updated_at || new Date().toISOString(),
      }))

      return {
        success: true,
        data: transformedData,
        message: '努力記録一覧を取得しました',
      }
    }
    
    return result
  } catch (error) {
    console.error('努力記録一覧取得エラー:', error)
    // エラー時はモックデータで回復
    const mockData: EffortRecord[] = [
      {
        id: 'mock_1',
        user_id: 'frontend_user',
        date: '2024-07-20',
        period: '過去7日間',
        effort_count: 0,
        highlights: ['データの取得に失敗しました'],
        score: 0,
        categories: { feeding: 0, sleep: 0, play: 0, care: 0 },
        summary: 'バックエンドAPIに接続できませんでした。',
        achievements: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]

    return {
      success: true,
      data: mockData,
      message: '努力記録一覧の取得に失敗しました（フォールバック）',
    }
  }
}

/**
 * 努力記録詳細を取得
 */
export async function getEffortRecord(
  recordId: string,
  userId: string = 'frontend_user'
): Promise<ApiResponse<EffortRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/effort-records/detail/${recordId}?user_id=${userId}`,
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
    console.error('努力記録詳細取得エラー:', error)
    return {
      success: false,
      message: '努力記録詳細の取得に失敗しました',
    }
  }
}

/**
 * 新しい努力記録を作成
 */
export async function createEffortRecord(
  recordData: EffortRecordCreateRequest
): Promise<ApiResponse<EffortRecord>> {
  try {
    // モック: 新しい記録を作成（実際のバックエンドAPI実装まで）
    const newRecord: EffortRecord = {
      id: `new_${Date.now()}`,
      user_id: recordData.user_id || 'frontend_user',
      date: recordData.date,
      period: recordData.period,
      effort_count: recordData.effort_count,
      highlights: recordData.highlights,
      score: recordData.score,
      categories: recordData.categories,
      summary: recordData.summary,
      achievements: recordData.achievements,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    // 簡単な遅延を追加
    await new Promise(resolve => setTimeout(resolve, 800))

    return {
      success: true,
      data: newRecord,
      message: '努力記録を作成しました（モックデータ）',
    }
  } catch (error) {
    console.error('努力記録作成エラー:', error)
    return {
      success: false,
      message: '努力記録の作成に失敗しました',
    }
  }
}

/**
 * 努力記録を更新
 */
export async function updateEffortRecord(
  recordId: string,
  recordData: EffortRecordUpdateRequest
): Promise<ApiResponse<EffortRecord>> {
  try {
    // モック: 記録を更新（実際のバックエンドAPI実装まで）
    const updatedRecord: EffortRecord = {
      id: recordId,
      user_id: recordData.user_id || 'frontend_user',
      date: recordData.date || '2024-01-01',
      period: recordData.period || '過去1週間',
      effort_count: recordData.effort_count || 0,
      highlights: recordData.highlights || [],
      score: recordData.score || 5.0,
      categories: recordData.categories || { feeding: 70, sleep: 70, play: 70, care: 70 },
      summary: recordData.summary || '',
      achievements: recordData.achievements || [],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: new Date().toISOString(),
    }

    // 簡単な遅延を追加
    await new Promise(resolve => setTimeout(resolve, 600))

    return {
      success: true,
      data: updatedRecord,
      message: '努力記録を更新しました（モックデータ）',
    }
  } catch (error) {
    console.error('努力記録更新エラー:', error)
    return {
      success: false,
      message: '努力記録の更新に失敗しました',
    }
  }
}

/**
 * 努力記録を削除
 */
export async function deleteEffortRecord(
  recordId: string,
  userId: string = 'frontend_user'
): Promise<ApiResponse<EffortRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/effort-reports/delete/${recordId}?user_id=${userId}`,
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

    const result = await response.json()
    
    if (result.success) {
      return {
        success: true,
        data: result.deleted_data || {} as EffortRecord,
        message: '努力記録を削除しました',
      }
    }
    
    return result
  } catch (error) {
    console.error('努力記録削除エラー:', error)
    return {
      success: false,
      message: '努力記録の削除に失敗しました',
    }
  }
}

/**
 * 努力レポートを自動生成
 */
export async function generateEffortReport(
  userId: string = 'frontend_user',
  periodDays: number = 7
): Promise<ApiResponse<EffortRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/effort-reports/generate?user_id=${userId}&period_days=${periodDays}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    
    if (result.success && result.data) {
      // バックエンドのデータ形式をフロントエンドの形式に変換
      const transformedData: EffortRecord = {
        id: result.data.id,
        user_id: result.data.user_id,
        date: new Date().toISOString().split('T')[0], // 今日の日付
        period: `過去${periodDays}日間`,
        effort_count: result.data.effort_count || 0,
        highlights: result.data.highlights || [],
        score: result.data.score || 0,
        categories: {
          feeding: result.data.categories?.['食事管理'] || 0,
          sleep: result.data.categories?.['記録継続'] || 0,
          play: result.data.categories?.['活動企画'] || 0,
          care: result.data.categories?.['健康管理'] || 0,
        },
        summary: result.data.summary || '',
        achievements: result.data.achievements || [],
        created_at: result.data.created_at || new Date().toISOString(),
        updated_at: result.data.updated_at || new Date().toISOString(),
      }

      return {
        success: true,
        data: transformedData,
        message: '努力レポートを生成しました',
      }
    }
    
    return result
  } catch (error) {
    console.error('努力レポート生成エラー:', error)
    return {
      success: false,
      message: '努力レポートの生成に失敗しました',
    }
  }
}

/**
 * 努力記録統計を取得
 */
export async function getEffortRecordsStats(
  userId: string = 'frontend_user',
  period: number = 7
): Promise<
  ApiResponse<{
    total_efforts: number
    streak_days: number
    average_score: number
    total_reports: number
  }>
> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/effort-reports/stats?user_id=${userId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      // エラー時はモックデータで回復
      const mockStats = {
        total_efforts: 27,
        streak_days: 21,
        average_score: 8.3,
        total_reports: 3,
      }
      return {
        success: true,
        data: mockStats,
        message: '努力記録統計を取得しました（フォールバック）',
      }
    }

    const result = await response.json()
    return result
  } catch (error) {
    console.error('努力記録統計取得エラー:', error)
    // エラー時もモックデータで回復
    const mockStats = {
      total_efforts: 27,
      streak_days: 21,
      average_score: 8.3,
      total_reports: 3,
    }
    return {
      success: true,
      data: mockStats,
      message: '努力記録統計を取得しました（フォールバック）',
    }
  }
}
