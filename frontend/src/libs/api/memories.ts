/**
 * メモリー記録API関連の関数
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface MemoryRecord {
  id: string
  user_id: string
  title: string
  description: string
  date: string
  type: 'photo' | 'video' | 'album'
  category: 'milestone' | 'daily' | 'family' | 'special'
  media_url?: string
  thumbnail_url?: string
  location?: string
  tags: string[]
  favorited: boolean
  created_at: string
  updated_at: string
}

export interface MemoryRecordCreateRequest {
  title: string
  description: string
  date: string
  type: 'photo' | 'video' | 'album'
  category: 'milestone' | 'daily' | 'family' | 'special'
  media_url?: string
  thumbnail_url?: string
  location?: string
  tags?: string[]
  favorited?: boolean
  user_id?: string
}

export interface MemoryRecordUpdateRequest {
  title?: string
  description?: string
  date?: string
  type?: 'photo' | 'video' | 'album'
  category?: 'milestone' | 'daily' | 'family' | 'special'
  media_url?: string
  thumbnail_url?: string
  location?: string
  tags?: string[]
  favorited?: boolean
  user_id?: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
}

/**
 * メモリー一覧を取得
 */
export async function getMemories(params?: {
  user_id?: string
  type?: string
  category?: string
  favorited?: boolean
  tags?: string
}): Promise<ApiResponse<MemoryRecord[]>> {
  try {
    const searchParams = new URLSearchParams()
    
    if (params?.user_id) searchParams.append('user_id', params.user_id)
    if (params?.type) searchParams.append('type', params.type)
    if (params?.category) searchParams.append('category', params.category)
    if (params?.favorited !== undefined) searchParams.append('favorited', String(params.favorited))
    if (params?.tags) searchParams.append('tags', params.tags)

    const url = `${API_BASE_URL}/api/v1/memories/list${searchParams.toString() ? '?' + searchParams.toString() : ''}`
    
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
    console.error('メモリー一覧取得エラー:', error)
    return {
      success: false,
      message: 'メモリー一覧の取得に失敗しました'
    }
  }
}

/**
 * メモリー詳細を取得
 */
export async function getMemory(memoryId: string, userId: string = 'frontend_user'): Promise<ApiResponse<MemoryRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/memories/detail/${memoryId}?user_id=${userId}`,
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
    console.error('メモリー詳細取得エラー:', error)
    return {
      success: false,
      message: 'メモリー詳細の取得に失敗しました'
    }
  }
}

/**
 * 新しいメモリーを作成
 */
export async function createMemory(memoryData: MemoryRecordCreateRequest): Promise<ApiResponse<MemoryRecord>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/memories/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...memoryData,
        user_id: memoryData.user_id || 'frontend_user'
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('メモリー作成エラー:', error)
    return {
      success: false,
      message: 'メモリーの作成に失敗しました'
    }
  }
}

/**
 * メモリーを更新
 */
export async function updateMemory(memoryId: string, memoryData: MemoryRecordUpdateRequest): Promise<ApiResponse<MemoryRecord>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/memories/update/${memoryId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...memoryData,
        user_id: memoryData.user_id || 'frontend_user'
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('メモリー更新エラー:', error)
    return {
      success: false,
      message: 'メモリーの更新に失敗しました'
    }
  }
}

/**
 * メモリーを削除
 */
export async function deleteMemory(memoryId: string, userId: string = 'frontend_user'): Promise<ApiResponse<MemoryRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/memories/delete/${memoryId}?user_id=${userId}`,
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
    console.error('メモリー削除エラー:', error)
    return {
      success: false,
      message: 'メモリーの削除に失敗しました'
    }
  }
}

/**
 * メモリーのお気に入り状態を切り替え
 */
export async function toggleMemoryFavorite(memoryId: string, favorited: boolean, userId: string = 'frontend_user'): Promise<ApiResponse<MemoryRecord>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/memories/favorite/${memoryId}?favorited=${favorited}&user_id=${userId}`,
      {
        method: 'PATCH',
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
    console.error('お気に入り切り替えエラー:', error)
    return {
      success: false,
      message: 'お気に入りの切り替えに失敗しました'
    }
  }
}

/**
 * お気に入りメモリー一覧を取得
 */
export async function getFavoriteMemories(userId: string = 'frontend_user'): Promise<ApiResponse<MemoryRecord[]>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/memories/favorites?user_id=${userId}`,
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
    console.error('お気に入りメモリー取得エラー:', error)
    return {
      success: false,
      message: 'お気に入りメモリーの取得に失敗しました'
    }
  }
}

/**
 * アルバム一覧を取得
 */
export async function getAlbums(userId: string = 'frontend_user'): Promise<ApiResponse<MemoryRecord[]>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/memories/albums?user_id=${userId}`,
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
    console.error('アルバム取得エラー:', error)
    return {
      success: false,
      message: 'アルバムの取得に失敗しました'
    }
  }
}

/**
 * タグ一覧を取得
 */
export async function getMemoryTags(userId: string = 'frontend_user'): Promise<ApiResponse<string[]>> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/memories/tags?user_id=${userId}`,
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
    console.error('タグ取得エラー:', error)
    return {
      success: false,
      message: 'タグの取得に失敗しました'
    }
  }
}