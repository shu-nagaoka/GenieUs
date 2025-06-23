'use client'
import { GenieDashboard } from '@/components/features/dashboard/genie-dashboard'
import { FloatingMagicOrb } from '@/components/features/one-action/floating-magic-orb'
import { useState } from 'react'

export default function GenieHomePage() {
  const [lastAction, setLastAction] = useState<string | null>(null)

  const handleMagicAction = (type: 'voice' | 'photo' | 'text', content: string) => {
    setLastAction(`${type}: ${content}`)
    // ここで実際のバックエンドAPIを呼び出し
    console.log('Magic action:', { type, content })
  }

  return (
    <div className="relative">
      <GenieDashboard />
      <FloatingMagicOrb onAction={handleMagicAction} />
      
      {/* デバッグ用 - 最後のアクション表示 */}
      {lastAction && (
        <div className="fixed bottom-20 left-4 p-2 bg-black/80 text-white text-xs rounded">
          {lastAction}
        </div>
      )}
    </div>
  )
}