'use client'

import { useState } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { EffortReportCard } from '@/components/v2/effort-affirmation/EffortReportCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Heart, 
  Calendar,
  TrendingUp,
  Award,
  Sparkles,
  Clock,
  BarChart3
} from 'lucide-react'

export default function EffortReportPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<number>(7)
  const [reportKey, setReportKey] = useState<number>(0)

  const handlePeriodChange = (value: string) => {
    setSelectedPeriod(parseInt(value))
    setReportKey(prev => prev + 1) // Force re-render of EffortReportCard
  }

  const regenerateReport = () => {
    setReportKey(prev => prev + 1)
  }

  return (
    <AppLayout>
      {/* ページヘッダー */}
      <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
        <div className="px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center">
                <Heart className="h-4 w-4 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-heading font-semibold text-gray-800">がんばったことレポート</h1>
                <p className="text-sm text-amber-600">あなたの努力とお子さんの成長を実感</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-amber-200">
              <Sparkles className="h-4 w-4 text-amber-600" />
              <span className="text-sm text-amber-700 font-medium">毎日自動作成</span>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8">
        {/* コントロールパネル */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-white/80 backdrop-blur-sm border-amber-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Calendar className="h-4 w-4 text-amber-600" />
                いつの期間でみる？
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Select value={selectedPeriod.toString()} onValueChange={handlePeriodChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3">過去3日間</SelectItem>
                  <SelectItem value="7">過去1週間</SelectItem>
                  <SelectItem value="14">過去2週間</SelectItem>
                  <SelectItem value="30">過去1ヶ月</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-emerald-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-emerald-600" />
                レポートの作成
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-2xl font-bold text-emerald-600">毎日</p>
                <p className="text-xs text-gray-600">21:00 自動生成</p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-purple-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Award className="h-4 w-4 text-purple-600" />
                これまでのレポート
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">12</p>
                <p className="text-xs text-gray-600">件生成済み</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* メインレポート */}
        <div className="mb-8">
          <EffortReportCard 
            key={reportKey}
            periodDays={selectedPeriod}
            className="w-full"
          />
        </div>

        {/* 追加機能セクション */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 努力の推移 */}
          <Card className="bg-white/80 backdrop-blur-sm border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-700">
                <BarChart3 className="h-5 w-5" />
                努力の推移
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-blue-800">今週の記録数</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-16 bg-blue-200 rounded-full">
                      <div className="h-2 w-12 bg-blue-500 rounded-full"></div>
                    </div>
                    <span className="text-sm font-medium text-blue-700">15件</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-sm text-green-800">記録の継続日数</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-16 bg-green-200 rounded-full">
                      <div className="h-2 w-14 bg-green-500 rounded-full"></div>
                    </div>
                    <span className="text-sm font-medium text-green-700">21日</span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm text-purple-800">多様性スコア</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-16 bg-purple-200 rounded-full">
                      <div className="h-2 w-10 bg-purple-500 rounded-full"></div>
                    </div>
                    <span className="text-sm font-medium text-purple-700">8.2/10</span>
                  </div>
                </div>
              </div>
              
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full mt-4 border-blue-300 text-blue-600 hover:bg-blue-50"
              >
                詳細な推移を見る
              </Button>
            </CardContent>
          </Card>

          {/* 今日のハイライト */}
          <Card className="bg-white/80 backdrop-blur-sm border-green-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-700">
                <Clock className="h-5 w-5" />
                今日のハイライト
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-100">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">特別な瞬間</span>
                  </div>
                  <p className="text-sm text-green-700">
                    お子さんが初めて「パパ」と言いました！あなたの毎日の語りかけが実を結んでいます。
                  </p>
                </div>

                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">成長記録</span>
                  </div>
                  <p className="text-sm text-blue-700">
                    睡眠時間が先週比で30分改善しました。あなたの寝かしつけルーティンが効果的です。
                  </p>
                </div>

                <div className="p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg border border-amber-100">
                  <div className="flex items-center gap-2 mb-2">
                    <Heart className="h-4 w-4 text-amber-600" />
                    <span className="text-sm font-medium text-amber-800">愛情指標</span>
                  </div>
                  <p className="text-sm text-amber-700">
                    今日だけで5回の笑顔を記録しました。お子さんはあなたの愛情を確実に感じています。
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 手動更新ボタン */}
        <div className="mt-8 text-center">
          <Button 
            onClick={regenerateReport}
            className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white px-8 py-3"
          >
            <Sparkles className="h-5 w-5 mr-2" />
            新しいレポートを作る
          </Button>
          <p className="text-sm text-gray-600 mt-2">
            毎晚9時に自動で作成されます
          </p>
        </div>
      </div>
    </AppLayout>
  )
}