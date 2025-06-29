/**
 * 統一API呼び出し機能 - バックエンド認証統合対応
 */

import { BackendLoginResponse } from './auth'
import { API_BASE_URL } from '@/config/api'

/**
 * API呼び出しオプション
 */
export interface ApiCallOptions extends RequestInit {
  requireAuth?: boolean
  baseUrl?: string
}

/**
 * API エラーレスポンス
 */
export interface ApiError {
  error: string
  message: string
  status: number
}

/**
 * API呼び出し結果
 */
export interface ApiResponse<T = any> {
  data?: T
  error?: ApiError
  success: boolean
}

/**
 * 認証トークン管理
 */
class TokenManager {
  private static instance: TokenManager
  private token: string | null = null

  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager()
    }
    return TokenManager.instance
  }

  setToken(token: string): void {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('backend_token', token)
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('backend_token')
    }
    return this.token
  }

  clearToken(): void {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('backend_token')
    }
  }
}

/**
 * 統一API呼び出し関数
 */
export async function apiCall<T = any>(
  endpoint: string,
  options: ApiCallOptions = {}
): Promise<ApiResponse<T>> {
  const {
    requireAuth = false,
    baseUrl = API_BASE_URL,
    ...fetchOptions
  } = options

  try {
    const tokenManager = TokenManager.getInstance()
    const token = tokenManager.getToken()

    // 認証が必要だが、トークンがない場合
    if (requireAuth && !token) {
      return {
        success: false,
        error: {
          error: 'authentication_required',
          message: '認証が必要です',
          status: 401,
        },
      }
    }

    // ヘッダー構築
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    }

    // 認証ヘッダー追加
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    // API呼び出し実行
    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...fetchOptions,
      headers,
    })

    // レスポンス処理
    const responseData = await response.json()

    if (!response.ok) {
      return {
        success: false,
        error: {
          error: responseData.error || 'api_error',
          message: responseData.message || 'API呼び出しに失敗しました',
          status: response.status,
        },
      }
    }

    return {
      success: true,
      data: responseData,
    }
  } catch (error) {
    console.error('API call error:', error)
    return {
      success: false,
      error: {
        error: 'network_error',
        message: 'ネットワークエラーが発生しました',
        status: 0,
      },
    }
  }
}

/**
 * 認証付きAPI呼び出し（必須認証）
 */
export async function authenticatedApiCall<T = any>(
  endpoint: string,
  options: ApiCallOptions = {}
): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, { ...options, requireAuth: true })
}

/**
 * GET API呼び出し
 */
export async function apiGet<T = any>(
  endpoint: string,
  options: Omit<ApiCallOptions, 'method'> = {}
): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, { ...options, method: 'GET' })
}

/**
 * POST API呼び出し
 */
export async function apiPost<T = any>(
  endpoint: string,
  data?: any,
  options: Omit<ApiCallOptions, 'method' | 'body'> = {}
): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, {
    ...options,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * PUT API呼び出し
 */
export async function apiPut<T = any>(
  endpoint: string,
  data?: any,
  options: Omit<ApiCallOptions, 'method' | 'body'> = {}
): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, {
    ...options,
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * DELETE API呼び出し
 */
export async function apiDelete<T = any>(
  endpoint: string,
  options: Omit<ApiCallOptions, 'method'> = {}
): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, { ...options, method: 'DELETE' })
}

/**
 * トークン管理関数群
 */
export const tokenManager = {
  /**
   * トークンを設定
   */
  setToken: (token: string) => {
    TokenManager.getInstance().setToken(token)
  },

  /**
   * トークンを取得
   */
  getToken: (): string | null => {
    return TokenManager.getInstance().getToken()
  },

  /**
   * トークンをクリア
   */
  clearToken: () => {
    TokenManager.getInstance().clearToken()
  },

  /**
   * 認証状態を確認
   */
  isAuthenticated: (): boolean => {
    return !!TokenManager.getInstance().getToken()
  },
}

/**
 * エラーハンドリングヘルパー
 */
export function handleApiError(error: ApiError): string {
  switch (error.error) {
    case 'authentication_required':
      return '認証が必要です。ログインしてください。'
    case 'network_error':
      return 'ネットワークエラーが発生しました。接続を確認してください。'
    case 'validation_error':
      return '入力内容に問題があります。確認してください。'
    case 'server_error':
      return 'サーバーエラーが発生しました。しばらく時間をおいて再度お試しください。'
    default:
      return error.message || '予期しないエラーが発生しました。'
  }
}

/**
 * レガシーサポート: 既存のAPI呼び出し形式との互換性
 */
export async function legacyFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const tokenManager = TokenManager.getInstance()
  const token = tokenManager.getToken()

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  }

  return fetch(url, {
    ...options,
    headers,
  })
}
