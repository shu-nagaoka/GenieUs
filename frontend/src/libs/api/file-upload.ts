/**
 * ファイルアップロード関連のAPI関数
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface UploadResponse {
  success: boolean
  file_url?: string
  file_id?: string
  message?: string
}

/**
 * 画像ファイルをアップロード
 */
export async function uploadImage(file: File, userId: string = 'frontend_user'): Promise<UploadResponse> {
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', userId)

    const response = await fetch(`${API_BASE_URL}/api/files/upload/image`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('画像アップロードエラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : '画像のアップロードに失敗しました'
    }
  }
}

/**
 * 画像のURLを取得（表示用）
 */
export function getImageUrl(filename: string): string {
  return `${API_BASE_URL}/api/files/images/${filename}`
}

/**
 * 画像を削除
 */
export async function deleteImage(filename: string, userId: string = 'frontend_user'): Promise<{ success: boolean; message?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/files/images/${filename}?user_id=${userId}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('画像削除エラー:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : '画像の削除に失敗しました'
    }
  }
}