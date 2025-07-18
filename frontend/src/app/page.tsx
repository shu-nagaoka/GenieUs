'use client'

import React from 'react'
import { useSession, signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { GiMagicLamp } from 'react-icons/gi'
import { FiStar, FiHeart, FiUsers, FiMessageCircle, FiArrowRight } from 'react-icons/fi'
import LoadingSpinner from '@/components/common/LoadingSpinner'

export default function LandingPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  const handleGetStarted = () => {
    if (session) {
      // ログイン済みの場合はダッシュボードへ
      router.push('/dashboard')
    } else {
      // 未ログインの場合はGoogleログインを実行
      signIn('google')
    }
  }

  if (status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      {/* ヘッダー */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          {/* ロゴとタイトル */}
          <div className="mb-12">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 shadow-xl">
              <GiMagicLamp className="h-10 w-10 text-white" />
            </div>
            <h1 className="mb-4 text-5xl font-bold text-amber-800">GenieUs</h1>
            <p className="mx-auto max-w-2xl text-xl leading-relaxed text-gray-600">
              見えない成長に、光をあてる。
              <br />
              不安な毎日を、自信に変える。
            </p>
          </div>

          {/* メインCTA */}
          <Card className="mx-auto mb-12 max-w-md shadow-lg">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl text-gray-800">
                {session ? `おかえりなさい、${session.user?.name}さん` : 'AI子育て支援を始める'}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {session ? (
                <>
                  <p className="text-gray-600">
                    GenieUsダッシュボードに戻って、
                    <br />
                    子育てサポートを続けましょう
                  </p>
                  <Button
                    onClick={handleGetStarted}
                    className="w-full bg-gradient-to-r from-amber-500 to-orange-500 py-3 text-lg font-semibold text-white shadow-md hover:from-amber-600 hover:to-orange-600"
                    size="lg"
                  >
                    <FiArrowRight className="mr-3 h-5 w-5" />
                    ダッシュボードに戻る
                  </Button>
                </>
              ) : (
                <>
                  <p className="text-gray-600">
                    Google アカウントでログインして、
                    <br />
                    あなただけの子育てサポートを開始しましょう
                  </p>
                  <Button
                    onClick={handleGetStarted}
                    className="w-full bg-gradient-to-r from-amber-500 to-orange-500 py-3 text-lg font-semibold text-white shadow-md hover:from-amber-600 hover:to-orange-600"
                    size="lg"
                  >
                    <svg className="mr-3 h-5 w-5" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Google アカウントで始める
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          {/* 特徴紹介 */}
          <div className="mx-auto grid max-w-4xl gap-8 md:grid-cols-3">
            <Card className="text-center transition-shadow hover:shadow-lg">
              <CardContent className="p-6">
                <FiMessageCircle className="mx-auto mb-4 h-12 w-12 text-amber-500" />
                <h3 className="mb-2 text-lg font-semibold">AI Genie と相談</h3>
                <p className="text-sm text-gray-600">
                  24時間いつでも、専門的で温かい子育てアドバイス
                </p>
              </CardContent>
            </Card>

            <Card className="text-center transition-shadow hover:shadow-lg">
              <CardContent className="p-6">
                <FiHeart className="mx-auto mb-4 h-12 w-12 text-red-500" />
                <h3 className="mb-2 text-lg font-semibold">成長を記録</h3>
                <p className="text-sm text-gray-600">大切な瞬間を残し、子どもの成長を可視化</p>
              </CardContent>
            </Card>

            <Card className="text-center transition-shadow hover:shadow-lg">
              <CardContent className="p-6">
                <FiUsers className="mx-auto mb-4 h-12 w-12 text-blue-500" />
                <h3 className="mb-2 text-lg font-semibold">家族で共有</h3>
                <p className="text-sm text-gray-600">家族みんなで子育ての喜びと成長を共有</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
