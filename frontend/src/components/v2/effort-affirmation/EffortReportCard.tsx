'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Heart,
  Award,
  TrendingUp,
  Star,
  CheckCircle,
  Calendar,
  Share,
  RefreshCw,
  Sparkles,
} from 'lucide-react'

interface EffortMetric {
  metric_name: string
  value: number
  unit: string
  comparison: string
  impact: string
}

interface EffortReportApiResponse {
  status: string
  child_name: string
  period: string
  overall_score: number
  achievements: EffortMetric[]
  growth_evidence: string[]
  affirmation: string
  report_id: string
}

interface EffortReportCardProps {
  parentId?: string
  childId?: string
  periodDays?: number
  className?: string
}

export function EffortReportCard({
  parentId = 'default_parent',
  childId = 'default_child',
  periodDays = 7,
  className = '',
}: EffortReportCardProps) {
  const [report, setReport] = useState<EffortReportApiResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null)

  const fetchEffortReport = async () => {
    try {
      setLoading(true)
      setError(null)

      // サンプルデータを使用（API実装前）
      await new Promise(resolve => setTimeout(resolve, 1000)) // 読み込み感を演出

      const sampleData: EffortReportApiResponse = {
        status: 'success',
        child_name: '日佳梨',
        period: `過去${periodDays}日間`,
        overall_score: 8.7,
        achievements: [
          {
            metric_name: '記録継続日数',
            value: 21,
            unit: '日',
            comparison: '先週比+7日',
            impact: '素晴らしい継続力です',
          },
          {
            metric_name: '努力記録数',
            value: 27,
            unit: '回',
            comparison: '先週比+3回',
            impact: '着実に増加しています',
          },
          {
            metric_name: '成長記録',
            value: 12,
            unit: '件',
            comparison: '多様な成長を記録',
            impact: 'バランスの取れた記録',
          },
        ],
        growth_evidence: [
          '初めて「パパ」と言いました！',
          '睡眠時間が30分改善しました',
          '離乳食を完食する日が増えました',
          '笑顔の回数が大幅に増加',
        ],
        affirmation:
          'この期間、あなたの愛情深い子育てが実を結んでいます。お子さんの言葉の発達と睡眠の改善は、あなたの毎日の努力の成果です。特に語りかけや寝かしつけのルーティンが素晴らしい効果を生んでいます。',
        report_id: `report_${Date.now()}`,
      }

      setReport(sampleData)
      setLastGenerated(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'レポート生成中にエラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEffortReport()
  }, [parentId, childId, periodDays])

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-orange-600'
  }

  const getScoreGradient = (score: number) => {
    if (score >= 8) return 'from-green-400 to-emerald-500'
    if (score >= 6) return 'from-yellow-400 to-amber-500'
    return 'from-orange-400 to-red-500'
  }

  const shareReport = async () => {
    if (!report) return

    try {
      await navigator.share({
        title: `${report.child_name}ちゃんの努力レポート`,
        text: report.affirmation,
        url: window.location.href,
      })
    } catch (err) {
      // フォールバック: クリップボードにコピー
      navigator.clipboard.writeText(report.affirmation)
      alert('レポートをクリップボードにコピーしました！')
    }
  }

  if (loading) {
    return (
      <Card
        className={`${className} border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50`}
      >
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 animate-pulse rounded-full bg-amber-200" />
            <div className="h-4 w-40 animate-pulse rounded bg-amber-200" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-20 w-full animate-pulse rounded bg-amber-200" />
            <div className="grid grid-cols-2 gap-4">
              <div className="h-16 animate-pulse rounded bg-amber-200" />
              <div className="h-16 animate-pulse rounded bg-amber-200" />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={`${className} border-red-200 bg-gradient-to-br from-red-50 to-orange-50`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-red-700">
            <Heart className="h-5 w-5" />
            レポート生成エラー
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-red-600">{error}</p>
          <Button
            onClick={fetchEffortReport}
            variant="outline"
            size="sm"
            className="border-red-300 text-red-700 hover:bg-red-50"
          >
            再試行
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (!report) return null

  return (
    <Card
      className={`${className} border-amber-200 bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 shadow-lg transition-all duration-300 hover:shadow-xl`}
    >
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3 text-amber-800">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-400">
              <Heart className="h-4 w-4 text-white" />
            </div>
            あなたの努力レポート
          </CardTitle>
          <Badge variant="secondary" className="border-amber-200 bg-amber-100 text-amber-700">
            {report.period}
          </Badge>
        </div>

        {lastGenerated && (
          <div className="flex items-center gap-1 text-sm text-amber-600">
            <Calendar className="h-3 w-3" />
            {lastGenerated.toLocaleDateString('ja-JP')} 生成
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 総合スコア */}
        <div className="rounded-lg border border-amber-100 bg-white/60 p-6 text-center backdrop-blur-sm">
          <div className="mb-4 flex items-center justify-center gap-3">
            <Award className="h-8 w-8 text-amber-600" />
            <div>
              <h3 className="text-2xl font-bold text-amber-800">
                {report.overall_score.toFixed(1)}/10
              </h3>
              <p className="text-sm text-amber-600">努力総合スコア</p>
            </div>
          </div>

          <div className="relative">
            <Progress value={report.overall_score * 10} className="mb-2 h-3" />
            <div
              className={`absolute inset-0 bg-gradient-to-r ${getScoreGradient(report.overall_score)} rounded-full opacity-20`}
            />
          </div>

          <div className="flex justify-center gap-1">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`h-5 w-5 ${i < Math.floor(report.overall_score / 2) ? 'fill-current text-amber-400' : 'text-gray-300'}`}
              />
            ))}
          </div>
        </div>

        {/* 肯定メッセージ */}
        <div className="rounded-lg border border-amber-200 bg-gradient-to-r from-amber-100 to-orange-100 p-4">
          <div className="flex items-start gap-3">
            <Sparkles className="mt-1 h-6 w-6 flex-shrink-0 text-amber-600" />
            <div>
              <h4 className="mb-2 font-medium text-amber-900">Genieからのメッセージ</h4>
              <p className="leading-relaxed text-amber-800">{report.affirmation}</p>
            </div>
          </div>
        </div>

        {/* 達成指標 */}
        {report.achievements.length > 0 && (
          <div>
            <h4 className="mb-3 flex items-center gap-2 text-sm font-medium text-gray-700">
              <TrendingUp className="h-4 w-4 text-green-600" />
              あなたの達成指標
            </h4>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {report.achievements.map((achievement, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 bg-white/80 p-4 transition-shadow hover:shadow-md"
                >
                  <div className="mb-2 flex items-center justify-between">
                    <h5 className="text-sm font-medium text-gray-800">{achievement.metric_name}</h5>
                    <Badge variant="outline" className="text-xs">
                      {achievement.comparison}
                    </Badge>
                  </div>
                  <div className="mb-2 flex items-end gap-2">
                    <span className="text-2xl font-bold text-emerald-600">{achievement.value}</span>
                    <span className="text-sm text-gray-500">{achievement.unit}</span>
                  </div>
                  <p className="text-xs text-gray-600">{achievement.impact}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 成長の証拠 */}
        {report.growth_evidence.length > 0 && (
          <div>
            <h4 className="mb-3 flex items-center gap-2 text-sm font-medium text-gray-700">
              <CheckCircle className="h-4 w-4 text-green-600" />
              成長の証拠
            </h4>
            <div className="space-y-2">
              {report.growth_evidence.map((evidence, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 rounded-lg border border-green-100 bg-green-50 p-3"
                >
                  <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-600" />
                  <span className="text-sm text-green-800">{evidence}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* アクションボタン */}
        <div className="flex gap-3 pt-2">
          <Button
            onClick={shareReport}
            variant="outline"
            size="sm"
            className="flex-1 border-amber-200 text-amber-700 hover:bg-amber-50"
          >
            <Share className="mr-2 h-4 w-4" />
            シェア
          </Button>
          <Button
            onClick={fetchEffortReport}
            variant="outline"
            size="sm"
            className="border-amber-200 text-amber-700 hover:bg-amber-50"
            disabled={loading}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
