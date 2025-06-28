'use client'

import { useSession, signIn, signOut } from 'next-auth/react'
import { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { useAuth } from '@/hooks/useAuth'

interface AuthCheckProps {
  children: ReactNode
  requireAuth?: boolean
  requireBackendAuth?: boolean
}

export function AuthCheck({
  children,
  requireAuth = true,
  requireBackendAuth = false,
}: AuthCheckProps) {
  const { data: session, status } = useSession()
  const {
    fullyAuthenticated,
    backendAuthenticated,
    isLoading: authLoading,
    error,
    loginToBackend,
  } = useAuth()

  // ローディング状態
  if (status === 'loading' || authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  // フロントエンド認証が必要だが未認証
  if (requireAuth && !session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-amber-800">GenieUs</CardTitle>
            <p className="text-gray-600">AI子育て支援アプリケーション</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-gray-700">続行するにはログインが必要です</p>
            <Button onClick={() => signIn('google')} className="w-full" size="lg">
              Googleでログイン
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // バックエンド認証が必要だが未認証
  if (requireBackendAuth && session && !backendAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-amber-800">GenieUs</CardTitle>
            <p className="text-gray-600">個人データアクセス認証</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <p className="mb-2 text-gray-700">
                個人データにアクセスするためにバックエンド認証が必要です
              </p>
              {error && <p className="mb-4 text-sm text-red-600">{error}</p>}
            </div>
            <Button onClick={loginToBackend} className="w-full" size="lg">
              バックエンド認証を実行
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return <>{children}</>
}

export function UserProfile() {
  const { data: session, status } = useSession()
  const {
    backendUser,
    backendAuthenticated,
    isLoading: authLoading,
    logout: handleLogout,
  } = useAuth()

  if (status === 'loading' || authLoading) {
    return <LoadingSpinner />
  }

  if (!session) {
    return (
      <Button onClick={() => signIn('google')} variant="outline" size="sm">
        ログイン
      </Button>
    )
  }

  // バックエンド認証済みの場合はバックエンドユーザー情報を優先表示
  const displayUser = backendAuthenticated && backendUser ? backendUser : session.user
  const displayName = backendAuthenticated && backendUser ? backendUser.name : session.user?.name
  const displayImage =
    backendAuthenticated && backendUser ? backendUser.picture_url : session.user?.image

  return (
    <div className="flex items-center gap-3">
      <div className="relative">
        {displayImage ? (
          <img src={displayImage} alt={displayName || ''} className="h-8 w-8 rounded-full" />
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-300">
            <span className="text-sm text-gray-600">
              {displayName ? displayName.charAt(0).toUpperCase() : 'U'}
            </span>
          </div>
        )}
        {/* 認証状態インジケーター */}
        <div
          className={`absolute -bottom-1 -right-1 h-3 w-3 rounded-full border-2 border-white ${
            backendAuthenticated ? 'bg-green-500' : 'bg-yellow-500'
          }`}
          title={backendAuthenticated ? '完全認証済み' : 'フロントエンドのみ認証'}
        />
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-medium">{displayName}</span>
        {backendAuthenticated && (
          <span className="text-xs text-green-600">個人データアクセス可能</span>
        )}
      </div>
      <Button
        onClick={() => {
          handleLogout()
          signOut({ callbackUrl: '/' })
        }}
        variant="ghost"
        size="sm"
      >
        ログアウト
      </Button>
    </div>
  )
}
