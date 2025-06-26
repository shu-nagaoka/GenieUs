/**
 * 統合認証フック - NextAuth + バックエンド認証の統合管理
 */

'use client'

import { useSession } from 'next-auth/react'
import { useState, useEffect, useCallback } from 'react'
import { loginToBackend, verifyBackendToken, getBackendUserProfile, BackendLoginResponse } from '@/libs/auth'
import { tokenManager } from '@/libs/api'

/**
 * 統合認証状態
 */
export interface AuthState {
  // NextAuth状態
  session: any
  sessionStatus: 'loading' | 'authenticated' | 'unauthenticated'
  
  // バックエンド認証状態
  backendToken: string | null
  backendUser: any
  backendAuthenticated: boolean
  
  // 統合状態
  fullyAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

/**
 * 認証アクション
 */
export interface AuthActions {
  // ログイン関連
  loginToBackend: () => Promise<void>
  logout: () => void
  
  // トークン管理
  refreshBackendToken: () => Promise<void>
  clearBackendAuth: () => void
  
  // ユーザー情報
  refreshUserProfile: () => Promise<void>
}

/**
 * 統合認証フック
 */
export function useAuth(): AuthState & AuthActions {
  const { data: session, status: sessionStatus } = useSession()
  
  // バックエンド認証状態
  const [backendToken, setBackendToken] = useState<string | null>(null)
  const [backendUser, setBackendUser] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 初期化: 保存されたトークンを復元
  useEffect(() => {
    const savedToken = tokenManager.getToken()
    if (savedToken) {
      setBackendToken(savedToken)
      // トークン検証
      verifyBackendToken(savedToken).then(({ valid, user }) => {
        if (valid) {
          setBackendUser(user)
        } else {
          tokenManager.clearToken()
          setBackendToken(null)
        }
        setIsLoading(false)
      }).catch(() => {
        tokenManager.clearToken()
        setBackendToken(null)
        setIsLoading(false)
      })
    } else {
      setIsLoading(false)
    }
  }, [])

  // NextAuth認証成功時の自動バックエンドログイン
  useEffect(() => {
    if (sessionStatus === 'authenticated' && session?.user && !backendToken) {
      handleBackendLogin()
    }
  }, [sessionStatus, session, backendToken])

  /**
   * バックエンドログイン実行
   */
  const handleBackendLogin = useCallback(async () => {
    if (!session?.user) {
      setError('フロントエンド認証が必要です')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result: BackendLoginResponse = await loginToBackend(session.user)
      
      // トークンとユーザー情報を保存
      setBackendToken(result.access_token)
      setBackendUser(result.user)
      tokenManager.setToken(result.access_token)
      
      console.log('バックエンド認証成功:', result.user.name)
    } catch (error) {
      console.error('Backend login failed:', error)
      setError(error instanceof Error ? error.message : 'バックエンド認証に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }, [session])

  /**
   * トークンリフレッシュ
   */
  const refreshBackendToken = useCallback(async () => {
    if (!session?.user) return

    try {
      const result = await loginToBackend(session.user)
      setBackendToken(result.access_token)
      setBackendUser(result.user)
      tokenManager.setToken(result.access_token)
    } catch (error) {
      console.error('Token refresh failed:', error)
      clearBackendAuth()
    }
  }, [session])

  /**
   * ユーザープロフィールリフレッシュ
   */
  const refreshUserProfile = useCallback(async () => {
    if (!backendToken) return

    try {
      const profile = await getBackendUserProfile(backendToken)
      setBackendUser(profile)
    } catch (error) {
      console.error('Profile refresh failed:', error)
    }
  }, [backendToken])

  /**
   * バックエンド認証クリア
   */
  const clearBackendAuth = useCallback(() => {
    setBackendToken(null)
    setBackendUser(null)
    tokenManager.clearToken()
    setError(null)
  }, [])

  /**
   * 完全ログアウト
   */
  const logout = useCallback(() => {
    clearBackendAuth()
    // NextAuthのログアウトは呼び出し元で実行
  }, [clearBackendAuth])

  // 計算プロパティ
  const backendAuthenticated = !!backendToken && !!backendUser
  const fullyAuthenticated = sessionStatus === 'authenticated' && backendAuthenticated
  const isAuthLoading = sessionStatus === 'loading' || isLoading

  return {
    // 状態
    session,
    sessionStatus,
    backendToken,
    backendUser,
    backendAuthenticated,
    fullyAuthenticated,
    isLoading: isAuthLoading,
    error,

    // アクション
    loginToBackend: handleBackendLogin,
    logout,
    refreshBackendToken,
    clearBackendAuth,
    refreshUserProfile,
  }
}

/**
 * 認証が必要なページで使用するフック
 */
export function useRequireAuth(): AuthState & AuthActions {
  const auth = useAuth()
  
  useEffect(() => {
    if (!auth.isLoading && !auth.fullyAuthenticated) {
      // 認証が必要だが未認証の場合の処理
      console.warn('認証が必要ですが、未認証です')
    }
  }, [auth.isLoading, auth.fullyAuthenticated])

  return auth
}

/**
 * 認証状態のみを返すライトウェイトフック
 */
export function useAuthStatus(): Pick<AuthState, 'fullyAuthenticated' | 'isLoading' | 'backendAuthenticated'> {
  const { fullyAuthenticated, isLoading, backendAuthenticated } = useAuth()
  
  return {
    fullyAuthenticated,
    isLoading,
    backendAuthenticated
  }
}