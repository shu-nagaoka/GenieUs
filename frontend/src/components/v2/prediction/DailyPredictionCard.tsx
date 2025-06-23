'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Lightbulb, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  ArrowRight,
  Sparkles 
} from 'lucide-react'

interface DailyPrediction {
  today_prediction: string
  reasoning: string
  confidence: number
  suggested_actions: string[]
  risk_factors: string[]
}

interface PredictionApiResponse {
  status: string
  child_name: string
  child_age_months: number
  prediction: DailyPrediction
  data_points: number
}

interface DailyPredictionCardProps {
  childId?: string
  className?: string
}

export function DailyPredictionCard({ childId = "default_child", className = "" }: DailyPredictionCardProps) {
  const [prediction, setPrediction] = useState<PredictionApiResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchPrediction = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/v2/prediction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ child_id: childId })
      })

      if (!response.ok) {
        throw new Error(`予報取得に失敗しました: ${response.status}`)
      }

      const data: PredictionApiResponse = await response.json()
      setPrediction(data)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : '予報取得中にエラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPrediction()
  }, [childId])

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-orange-600'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return '高精度'
    if (confidence >= 0.6) return '中精度'
    return '参考程度'
  }

  if (loading) {
    return (
      <Card className={`${className} bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200`}>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-full bg-purple-200 animate-pulse" />
            <div className="h-4 w-32 bg-purple-200 rounded animate-pulse" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="h-4 w-full bg-purple-200 rounded animate-pulse" />
            <div className="h-4 w-3/4 bg-purple-200 rounded animate-pulse" />
            <div className="h-20 w-full bg-purple-200 rounded animate-pulse" />
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
            <AlertCircle className="h-5 w-5" />
            予報取得エラー
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600 mb-4">{error}</p>
          <Button 
            onClick={fetchPrediction}
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

  if (!prediction) return null

  return (
    <Card className={`${className} bg-gradient-to-br from-purple-50 via-indigo-50 to-purple-50 border-purple-200 shadow-lg hover:shadow-xl transition-all duration-300`}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3 text-purple-800">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-indigo-400 flex items-center justify-center">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            今日のお子さん予報
          </CardTitle>
          <Badge variant="secondary" className="bg-purple-100 text-purple-700 border-purple-200">
            {prediction.child_name}ちゃん
          </Badge>
        </div>
        
        {lastUpdated && (
          <div className="flex items-center gap-1 text-sm text-purple-600">
            <Clock className="h-3 w-3" />
            {lastUpdated.toLocaleTimeString('ja-JP', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })} 更新
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-6">
        {/* メイン予測 */}
        <div className="p-4 bg-white/60 backdrop-blur-sm rounded-lg border border-purple-100">
          <div className="flex items-start gap-3">
            <Lightbulb className="h-6 w-6 text-purple-600 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="font-medium text-purple-900 mb-2">今日の予報</h3>
              <p className="text-gray-700 leading-relaxed">
                {prediction.prediction.today_prediction}
              </p>
            </div>
          </div>
        </div>

        {/* 信頼度と根拠 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">予報の確かさ</span>
              <span className={`text-sm font-semibold ${getConfidenceColor(prediction.prediction.confidence)}`}>
                {getConfidenceLabel(prediction.prediction.confidence)}
              </span>
            </div>
            <Progress 
              value={prediction.prediction.confidence * 100} 
              className="h-2"
            />
            <p className="text-xs text-gray-500">
              {Math.round(prediction.prediction.confidence * 100)}% 
              （{prediction.data_points}件のデータ分析）
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">なぜそうなの？</h4>
            <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
              {prediction.prediction.reasoning}
            </p>
          </div>
        </div>

        {/* 推奨アクション */}
        {prediction.prediction.suggested_actions.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              やってみると良いこと
            </h4>
            <div className="space-y-2">
              {prediction.prediction.suggested_actions.map((action, index) => (
                <div 
                  key={index}
                  className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-100"
                >
                  <ArrowRight className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-green-800">{action}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 注意点 */}
        {prediction.prediction.risk_factors.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-amber-600" />
              気をつけたいこと
            </h4>
            <div className="space-y-2">
              {prediction.prediction.risk_factors.map((risk, index) => (
                <div 
                  key={index}
                  className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-100"
                >
                  <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-amber-800">{risk}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 更新ボタン */}
        <div className="flex justify-center pt-2">
          <Button 
            onClick={fetchPrediction}
            variant="outline"
            size="sm"
            className="border-purple-200 text-purple-700 hover:bg-purple-50"
            disabled={loading}
          >
            最新の予報を取得
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}