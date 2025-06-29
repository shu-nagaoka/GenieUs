import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/app/api/auth/[...nextauth]/route'
import { API_BASE_URL } from '@/config/api'

export function getServerAuthSession() {
  return getServerSession(authOptions)
}

// Client-side auth utilities
export const signIn = (provider?: string) => {
  return import('next-auth/react').then(({ signIn }) => signIn(provider))
}

export const signOut = () => {
  return import('next-auth/react').then(({ signOut }) => signOut())
}

// ========== バックエンド認証統合 ==========

/**
 * バックエンドログインレスポンス型
 */
export interface BackendLoginResponse {
  success: boolean
  access_token: string
  token_type: string
  user: {
    google_id: string
    email: string
    name: string
    picture_url?: string
    created_at: string
    last_login: string
  }
}

/**
 * Google OAuth情報でバックエンドにログイン
 */
export async function loginToBackend(sessionUser: any): Promise<BackendLoginResponse> {
  try {
    const apiUrl = `${API_BASE_URL}/api/auth/login/google`
    console.log('Auth API URL:', apiUrl) // デバッグ用
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        google_user_info: {
          sub: sessionUser.id || sessionUser.sub,
          email: sessionUser.email,
          name: sessionUser.name,
          picture: sessionUser.image,
          email_verified: true,
        },
      }),
    })

    if (!response.ok) {
      throw new Error(`Backend login failed: ${response.status}`)
    }

    const result = await response.json()

    if (!result.success) {
      throw new Error('Backend login unsuccessful')
    }

    return result
  } catch (error) {
    console.error('Backend login error:', error)
    throw new Error('バックエンド認証に失敗しました')
  }
}

/**
 * JWTトークンを検証
 */
export async function verifyBackendToken(token: string): Promise<{ valid: boolean; user?: any }> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/verify`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    if (response.ok) {
      const userData = await response.json()
      return { valid: true, user: userData }
    } else {
      return { valid: false }
    }
  } catch (error) {
    console.error('Token verification error:', error)
    return { valid: false }
  }
}

/**
 * バックエンドからユーザープロフィールを取得
 */
export async function getBackendUserProfile(token: string): Promise<any> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/profile`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error(`Profile fetch failed: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Profile fetch error:', error)
    throw new Error('プロフィール取得に失敗しました')
  }
}

// ========== レガシー関数（互換性維持） ==========

// Token validation utility for API calls
export async function validateGoogleToken(token: string): Promise<any> {
  try {
    const response = await fetch(
      `https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=${token}`
    )

    if (!response.ok) {
      throw new Error('Token validation failed')
    }

    return await response.json()
  } catch (error) {
    console.error('Token validation error:', error)
    throw new Error('Invalid token')
  }
}

// API call with authentication
export async function authenticatedFetch(url: string, options: RequestInit = {}, token?: string) {
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
