/**
 * スケジュール管理API クライアント
 */

// APIベースURL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// レスポンス型定義
interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
}

// スケジュールイベントの型定義
export interface ScheduleEvent {
  id: string
  user_id: string
  title: string
  date: string
  time: string
  type: 'medical' | 'outing' | 'school' | 'other'
  location?: string
  description?: string
  status: 'upcoming' | 'completed' | 'cancelled'
  created_by: 'genie' | 'user'
  created_at: string
  updated_at: string
}

// 作成リクエストの型定義
export interface ScheduleEventCreateRequest {
  title: string
  date: string
  time: string
  type: 'medical' | 'outing' | 'school' | 'other'
  location?: string
  description?: string
  status?: 'upcoming' | 'completed' | 'cancelled'
  created_by?: 'genie' | 'user'
  user_id?: string
}

// 更新リクエストの型定義
export interface ScheduleEventUpdateRequest {
  title?: string
  date?: string
  time?: string
  type?: 'medical' | 'outing' | 'school' | 'other'
  location?: string
  description?: string
  status?: 'upcoming' | 'completed' | 'cancelled'
  created_by?: 'genie' | 'user'
  user_id?: string
}

/**
 * スケジュールイベント一覧を取得
 */
export async function getScheduleEvents(params?: {
  user_id?: string
  status?: string
}): Promise<ApiResponse<ScheduleEvent[]>> {
  try {
    const searchParams = new URLSearchParams()
    if (params?.user_id) searchParams.append('user_id', params.user_id)
    if (params?.status) searchParams.append('status', params.status)

    const url = `${API_BASE_URL}/api/schedules/list${searchParams.toString() ? `?${searchParams.toString()}` : ''}`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('スケジュールイベント取得エラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : 'スケジュールイベントの取得に失敗しました',
    }
  }
}

/**
 * 特定のスケジュールイベントを取得
 */
export async function getScheduleEvent(
  eventId: string,
  userId: string = 'frontend_user'
): Promise<ApiResponse<ScheduleEvent>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/schedules/detail/${eventId}?user_id=${userId}`,
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

    const data = await response.json()
    return data
  } catch (error) {
    console.error('スケジュールイベント詳細取得エラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : 'スケジュールイベントの取得に失敗しました',
    }
  }
}

/**
 * 新しいスケジュールイベントを作成
 */
export async function createScheduleEvent(
  eventData: ScheduleEventCreateRequest
): Promise<ApiResponse<ScheduleEvent>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/schedules/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...eventData,
        user_id: eventData.user_id || 'frontend_user',
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('スケジュールイベント作成エラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : 'スケジュールイベントの作成に失敗しました',
    }
  }
}

/**
 * スケジュールイベントを更新
 */
export async function updateScheduleEvent(
  eventId: string,
  eventData: ScheduleEventUpdateRequest
): Promise<ApiResponse<ScheduleEvent>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/schedules/update/${eventId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...eventData,
        user_id: eventData.user_id || 'frontend_user',
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('スケジュールイベント更新エラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : 'スケジュールイベントの更新に失敗しました',
    }
  }
}

/**
 * スケジュールイベントを削除
 */
export async function deleteScheduleEvent(
  eventId: string,
  userId: string = 'frontend_user'
): Promise<ApiResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/schedules/delete/${eventId}?user_id=${userId}`,
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

    const data = await response.json()
    return data
  } catch (error) {
    console.error('スケジュールイベント削除エラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : 'スケジュールイベントの削除に失敗しました',
    }
  }
}

/**
 * スケジュールイベントのステータスを更新
 */
export async function updateScheduleEventStatus(
  eventId: string,
  status: 'upcoming' | 'completed' | 'cancelled',
  userId: string = 'frontend_user'
): Promise<ApiResponse<ScheduleEvent>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/schedules/status/${eventId}?user_id=${userId}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('スケジュールイベントステータス更新エラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : 'ステータスの更新に失敗しました',
    }
  }
}
