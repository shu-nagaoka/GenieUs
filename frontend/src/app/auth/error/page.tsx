'use client'

import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertTriangle } from 'lucide-react'
import Link from 'next/link'

export default function AuthErrorPage() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  const getErrorMessage = (error: string | null) => {
    switch (error) {
      case 'Configuration':
        return 'アプリケーションの設定に問題があります。管理者にお問い合わせください。'
      case 'AccessDenied':
        return 'アクセスが拒否されました。権限を確認してください。'
      case 'Verification':
        return 'メール認証に失敗しました。再度お試しください。'
      default:
        return '認証エラーが発生しました。再度お試しください。'
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 p-3 bg-red-100 rounded-full w-fit">
            <AlertTriangle className="h-6 w-6 text-red-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-red-600">
            認証エラー
          </CardTitle>
          <CardDescription>
            {getErrorMessage(error)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center space-y-2">
            <Button asChild className="w-full">
              <Link href="/auth/signin">
                サインインページに戻る
              </Link>
            </Button>
            <Button variant="outline" asChild className="w-full">
              <Link href="/">
                ホームページに戻る
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}