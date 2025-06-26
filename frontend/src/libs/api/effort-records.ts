/**
 * 努力記録API関連の関数
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
    // モックデータを返す（バックエンドAPI実装まで）
    const mockData: EffortRecord[] = [
      {
        id: '1',
        user_id: 'frontend_user',
        date: '2024-07-20',
        period: '過去1週間',
        effort_count: 27,
        highlights: ['初めて「パパ」と言いました！', '睡眠時間が30分改善', '離乳食を完食する日が増加'],
        score: 8.7,
        categories: {
          feeding: 85,
          sleep: 78,
          play: 92,
          care: 88
        },
        summary: 'この1週間、お子さんとの絆が深まった素晴らしい期間でした。特に言葉の発達と睡眠リズムの改善が目立ちました。',
        achievements: ['言語発達マイルストーン', '睡眠改善成功', '愛情表現向上'],
        created_at: '2024-07-20T21:00:00Z',
        updated_at: '2024-07-20T21:00:00Z'
      },
      {
        id: '2',
        user_id: 'frontend_user',
        date: '2024-07-13',
        period: '過去1週間',
        effort_count: 24,
        highlights: ['つかまり立ち成功！', '新しい遊びを覚えました', '夜泣きが減少しました'],
        score: 8.2,
        categories: {
          feeding: 80,
          sleep: 85,
          play: 88,
          care: 82
        },
        summary: '運動発達が著しく進歩した週でした。つかまり立ちの成功は大きなマイルストーンです。',
        achievements: ['運動発達マイルストーン', '夜泣き改善', '新しい遊び発見'],
        created_at: '2024-07-13T21:00:00Z',
        updated_at: '2024-07-13T21:00:00Z'
      },
      {
        id: '3',
        user_id: 'frontend_user',
        date: '2024-07-06',
        period: '過去1週間',
        effort_count: 22,
        highlights: ['笑顔が増えました', '離乳食に新しい食材追加', 'お昼寝時間が安定'],
        score: 7.9,
        categories: {
          feeding: 78,
          sleep: 80,
          play: 85,
          care: 79
        },
        summary: '感情表現が豊かになり、食事のバラエティも増えた充実した週でした。',
        achievements: ['感情表現向上', '食事バラエティ拡大', '生活リズム安定'],
        created_at: '2024-07-06T21:00:00Z',
        updated_at: '2024-07-06T21:00:00Z'
      }
    ]

    // 簡単な遅延を追加してローディング体験をシミュレート
    await new Promise(resolve => setTimeout(resolve, 500))

    return {
      success: true,
      data: mockData,
      message: '努力記録一覧を取得しました（モックデータ）'
    }
  } catch (error) {
    console.error('努力記録一覧取得エラー:', error)
    return {
      success: false,
      message: '努力記録一覧の取得に失敗しました'
    }
  }
}

/**
 * 努力記録詳細を取得
 */
export async function getEffortRecord(recordId: string, userId: string = 'frontend_user'): Promise<ApiResponse<EffortRecord>> {
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
      message: '努力記録詳細の取得に失敗しました'
    }
  }
}

/**
 * 新しい努力記録を作成
 */
export async function createEffortRecord(recordData: EffortRecordCreateRequest): Promise<ApiResponse<EffortRecord>> {
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
      updated_at: new Date().toISOString()
    }

    // 簡単な遅延を追加
    await new Promise(resolve => setTimeout(resolve, 800))

    return {
      success: true,
      data: newRecord,
      message: '努力記録を作成しました（モックデータ）'
    }
  } catch (error) {
    console.error('努力記録作成エラー:', error)
    return {
      success: false,
      message: '努力記録の作成に失敗しました'
    }
  }
}

/**
 * 努力記録を更新
 */
export async function updateEffortRecord(recordId: string, recordData: EffortRecordUpdateRequest): Promise<ApiResponse<EffortRecord>> {
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
      updated_at: new Date().toISOString()
    }

    // 簡単な遅延を追加
    await new Promise(resolve => setTimeout(resolve, 600))

    return {
      success: true,
      data: updatedRecord,
      message: '努力記録を更新しました（モックデータ）'
    }
  } catch (error) {
    console.error('努力記録更新エラー:', error)
    return {
      success: false,
      message: '努力記録の更新に失敗しました'
    }
  }
}

/**
 * 努力記録を削除
 */
export async function deleteEffortRecord(recordId: string, userId: string = 'frontend_user'): Promise<ApiResponse<EffortRecord>> {
  try {
    // モック: 記録を削除（実際のバックエンドAPI実装まで）
    
    // 簡単な遅延を追加
    await new Promise(resolve => setTimeout(resolve, 400))

    return {
      success: true,
      data: {} as EffortRecord,
      message: '努力記録を削除しました（モックデータ）'
    }
  } catch (error) {
    console.error('努力記録削除エラー:', error)
    return {
      success: false,
      message: '努力記録の削除に失敗しました'
    }
  }
}

/**
 * 努力記録統計を取得
 */
export async function getEffortRecordsStats(userId: string = 'frontend_user', period: number = 7): Promise<ApiResponse<{
  total_efforts: number
  streak_days: number
  average_score: number
  total_reports: number
}>> {
  try {
    // モック統計データを返す（バックエンドAPI実装まで）
    const mockStats = {
      total_efforts: 27,
      streak_days: 21,
      average_score: 8.3,
      total_reports: 3
    }

    // 簡単な遅延を追加
    await new Promise(resolve => setTimeout(resolve, 300))

    return {
      success: true,
      data: mockStats,
      message: '努力記録統計を取得しました（モックデータ）'
    }
  } catch (error) {
    console.error('努力記録統計取得エラー:', error)
    return {
      success: false,
      message: '努力記録統計の取得に失敗しました'
    }
  }
}