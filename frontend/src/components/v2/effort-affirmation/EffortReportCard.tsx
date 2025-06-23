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
  Sparkles
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
  parentId = "default_parent", 
  childId = "default_child", 
  periodDays = 7,
  className = "" 
}: EffortReportCardProps) {
  const [report, setReport] = useState<EffortReportApiResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null)

  const fetchEffortReport = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/v2/effort-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          parent_id: parentId, 
          child_id: childId, 
          period_days: periodDays 
        })
      })

      if (!response.ok) {
        throw new Error(`レポート生成に失敗しました: ${response.status}`)
      }

      const data: EffortReportApiResponse = await response.json()
      setReport(data)
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
        url: window.location.href
      })
    } catch (err) {
      // フォールバック: クリップボードにコピー
      navigator.clipboard.writeText(report.affirmation)
      alert('レポートをクリップボードにコピーしました！')
    }
  }

  if (loading) {
    return (
      <Card className={`${className} bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200`}>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-full bg-amber-200 animate-pulse" />
            <div className="h-4 w-40 bg-amber-200 rounded animate-pulse" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-20 w-full bg-amber-200 rounded animate-pulse" />
            <div className="grid grid-cols-2 gap-4">
              <div className="h-16 bg-amber-200 rounded animate-pulse" />
              <div className="h-16 bg-amber-200 rounded animate-pulse" />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={`${className} bg-gradient-to-br from-red-50 to-orange-50 border-red-200`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-red-700">
            <Heart className="h-5 w-5" />
            レポート生成エラー
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600 mb-4">{error}</p>
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
    <Card className={`${className} bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 border-amber-200 shadow-lg hover:shadow-xl transition-all duration-300`}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3 text-amber-800">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center">
              <Heart className="h-4 w-4 text-white" />
            </div>
            あなたの努力レポート
          </CardTitle>
          <Badge variant="secondary" className="bg-amber-100 text-amber-700 border-amber-200">
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
        <div className="text-center p-6 bg-white/60 backdrop-blur-sm rounded-lg border border-amber-100">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Award className="h-8 w-8 text-amber-600" />
            <div>
              <h3 className="text-2xl font-bold text-amber-800">
                {report.overall_score.toFixed(1)}/10
              </h3>
              <p className="text-sm text-amber-600">努力総合スコア</p>
            </div>
          </div>
          
          <div className="relative">
            <Progress 
              value={report.overall_score * 10} 
              className="h-3 mb-2"
            />
            <div className={`absolute inset-0 bg-gradient-to-r ${getScoreGradient(report.overall_score)} rounded-full opacity-20`} />
          </div>
          
          <div className="flex justify-center gap-1">
            {[...Array(5)].map((_, i) => (
              <Star 
                key={i} 
                className={`h-5 w-5 ${i < Math.floor(report.overall_score / 2) ? 'text-amber-400 fill-current' : 'text-gray-300'}`} 
              />
            ))}
          </div>
        </div>

        {/* 肯定メッセージ */}
        <div className="p-4 bg-gradient-to-r from-amber-100 to-orange-100 rounded-lg border border-amber-200">
          <div className="flex items-start gap-3">
            <Sparkles className="h-6 w-6 text-amber-600 mt-1 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-amber-900 mb-2">Genieからのメッセージ</h4>
              <p className="text-amber-800 leading-relaxed">
                {report.affirmation}
              </p>
            </div>
          </div>
        </div>

        {/* 達成指標 */}
        {report.achievements.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              あなたの達成指標
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {report.achievements.map((achievement, index) => (
                <div 
                  key={index}
                  className="p-4 bg-white/80 rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="text-sm font-medium text-gray-800">
                      {achievement.metric_name}
                    </h5>
                    <Badge variant="outline" className="text-xs">
                      {achievement.comparison}
                    </Badge>
                  </div>
                  <div className="flex items-end gap-2 mb-2">
                    <span className="text-2xl font-bold text-emerald-600">
                      {achievement.value}
                    </span>
                    <span className="text-sm text-gray-500">
                      {achievement.unit}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">
                    {achievement.impact}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 成長の証拠 */}
        {report.growth_evidence.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              成長の証拠
            </h4>
            <div className="space-y-2">
              {report.growth_evidence.map((evidence, index) => (
                <div 
                  key={index}
                  className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-100"
                >
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
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
            <Share className="h-4 w-4 mr-2" />
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