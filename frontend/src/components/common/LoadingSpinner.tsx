/**
 * 共通ローディングコンポーネント
 * キラキラエフェクト付きのおしゃれなローディング画面
 */

'use client'

import React from 'react'
import { Sparkles } from 'lucide-react'

interface LoadingSpinnerProps {
  message?: string
  fullScreen?: boolean
  className?: string
}

export default function LoadingSpinner({
  message = '読み込んでいます...',
  fullScreen = true,
  className = '',
}: LoadingSpinnerProps) {
  const containerClass = fullScreen
    ? 'min-h-screen bg-gradient-to-br from-gray-50 via-slate-50 to-stone-50 flex items-center justify-center'
    : `flex items-center justify-center p-8 ${className}`

  return (
    <div className={containerClass}>
      <div className="text-center">
        <div className="relative">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600"></div>
          <Sparkles className="absolute left-1/2 top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 transform text-blue-500" />
        </div>
        <p className="font-medium text-gray-600">{message}</p>
      </div>
    </div>
  )
}
