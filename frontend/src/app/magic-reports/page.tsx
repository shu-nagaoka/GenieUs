'use client'
import { MagicReportGenerator } from '@/components/features/reports/magic-report-generator'
import { AppLayout } from '@/components/layout/app-layout'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowLeft, Sparkles } from 'lucide-react'

export default function MagicReportsPage() {
  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50">
        
        {/* ヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-purple-200 p-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  戻る
                </Button>
              </Link>
              <div className="text-3xl">📊</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">魔法のレポート</h1>
                <p className="text-sm text-gray-600">ジーニーがあなたの頑張りをレポートに</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-purple-600">
              <Sparkles className="h-4 w-4 animate-pulse" />
              <span className="text-sm font-medium">魔法モード</span>
            </div>
          </div>
        </div>

        <div className="max-w-4xl mx-auto p-6">
          <MagicReportGenerator />
        </div>
      </div>
    </AppLayout>
  )
}