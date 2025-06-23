'use client'
import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { DailyPredictionCard } from '@/components/v2/prediction/DailyPredictionCard'
import { FloatingVoiceButton } from '@/components/v2/voice-recording/FloatingVoiceButton'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardTitle, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle,
  Plus,
  Bell,
  MapPin,
  FileText,
  Brain,
  Sparkles,
  TrendingUp,
  Baby,
  Target,
  Star,
  Lightbulb,
  Zap,
  Eye,
  BarChart3,
  Activity
} from 'lucide-react'

interface PredictiveScheduleItem {
  id: string
  title: string
  type: 'prediction' | 'milestone' | 'vaccination' | 'checkup' | 'development'
  predictedDate: Date
  confidence: number
  category: 'health' | 'development' | 'behavior' | 'feeding' | 'sleep'
  aiReasoning: string
  suggestedActions: string[]
  status: 'predicted' | 'scheduled' | 'completed' | 'modified'
  priority: 'high' | 'medium' | 'low'
  parentInfluence?: string
  basedOnData: string[]
}

interface SmartReminder {
  id: string
  title: string
  message: string
  timing: 'morning' | 'before_event' | 'evening'
  frequency: 'daily' | 'weekly' | 'custom'
  isAiGenerated: boolean
  nextTrigger: Date
  adaptiveReason?: string
}

export default function PredictiveSchedulePage() {
  const [predictiveItems, setPredictiveItems] = useState<PredictiveScheduleItem[]>([
    {
      id: '1',
      title: '成長スパート期間の開始',
      type: 'prediction',
      predictedDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
      confidence: 0.84,
      category: 'development',
      aiReasoning: '過去の成長パターンと現在の食事量増加から、3日後頃から成長スパート期に入る可能性が高いです。',
      suggestedActions: [
        '栄養価の高い食事を準備',
        '睡眠時間を十分確保',
        '成長による不機嫌への心構え'
      ],
      status: 'predicted',
      priority: 'high',
      parentInfluence: 'あなたのバランスの良い食事計画が成長を促進しています',
      basedOnData: ['食事量パターン', '睡眠の質向上', '体重増加トレンド']
    },
    {
      id: '2',
      title: '離乳食の新食材導入適期',
      type: 'prediction',
      predictedDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      confidence: 0.78,
      category: 'feeding',
      aiReasoning: 'お子さんの消化機能の発達と現在の食べ方から、来週が新しい食材にチャレンジする最適なタイミングです。',
      suggestedActions: [
        'にんじんやさつまいもを準備',
        '小さじ1から開始',
        'アレルギー反応に注意深く観察'
      ],
      status: 'predicted',
      priority: 'medium',
      basedOnData: ['消化機能発達段階', '現在の食べ方パターン', '月齢発達指標']
    },
    {
      id: '3',
      title: 'お座り完全習得の目安',
      type: 'milestone',
      predictedDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
      confidence: 0.91,
      category: 'development',
      aiReasoning: '現在の首や体幹の発達状況から、2週間後頃にお座りが完全に安定する見込みです。',
      suggestedActions: [
        'お座り練習の時間を増やす',
        '周囲の安全確保',
        '達成時の写真撮影準備'
      ],
      status: 'predicted',
      priority: 'high',
      parentInfluence: '毎日の お座り練習サポートが効果的です',
      basedOnData: ['体幹筋力測定', 'バランス感覚テスト', '発達マイルストーン']
    },
    {
      id: '4',
      title: '夜泣き減少期の到来',
      type: 'prediction',
      predictedDate: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000),
      confidence: 0.73,
      category: 'sleep',
      aiReasoning: '睡眠パターンの改善傾向と生活リズムの安定化から、夜泣きが大幅に減少する時期が近づいています。',
      suggestedActions: [
        '現在の寝かしつけルーティンを継続',
        '睡眠環境の更なる最適化',
        '親の休息時間確保の準備'
      ],
      status: 'predicted',
      priority: 'medium',
      parentInfluence: 'あなたの一貫した寝かしつけが良い結果を生んでいます',
      basedOnData: ['睡眠時間推移', '夜泣き頻度データ', '入眠パターン']
    },
    {
      id: '5',
      title: 'BCG予防接種 (スケジュール済み)',
      type: 'vaccination',
      predictedDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
      confidence: 1.0,
      category: 'health',
      aiReasoning: '定期接種スケジュールに基づく確定予定',
      suggestedActions: [
        '母子手帳を持参',
        '体調確認',
        '接種後の経過観察'
      ],
      status: 'scheduled',
      priority: 'high',
      basedOnData: ['定期接種スケジュール']
    }
  ])

  const [smartReminders, setSmartReminders] = useState<SmartReminder[]>([
    {
      id: '1',
      title: '成長スパート準備',
      message: '明日から成長スパート期が予測されています。栄養価の高い食事と十分な睡眠を準備しましょう。',
      timing: 'morning',
      frequency: 'custom',
      isAiGenerated: true,
      nextTrigger: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
      adaptiveReason: 'AI予測に基づく先回りサポート'
    },
    {
      id: '2',
      title: '毎日の成長記録',
      message: '今日の様子はいかがでしたか？音声で記録すると、より正確な予測が可能になります。',
      timing: 'evening',
      frequency: 'daily',
      isAiGenerated: true,
      nextTrigger: new Date(Date.now() + 6 * 60 * 60 * 1000),
      adaptiveReason: 'データ精度向上のための記録促進'
    }
  ])

  const getTypeIcon = (type: PredictiveScheduleItem['type']) => {
    switch (type) {
      case 'prediction': return <Brain className="h-5 w-5 text-purple-600" />
      case 'milestone': return <Target className="h-5 w-5 text-emerald-600" />
      case 'vaccination': return <AlertCircle className="h-5 w-5 text-red-600" />
      case 'checkup': return <Activity className="h-5 w-5 text-blue-600" />
      case 'development': return <TrendingUp className="h-5 w-5 text-indigo-600" />
    }
  }

  const getTypeColor = (type: PredictiveScheduleItem['type']) => {
    switch (type) {
      case 'prediction': return 'from-purple-50 to-indigo-50 border-purple-200'
      case 'milestone': return 'from-emerald-50 to-green-50 border-emerald-200'
      case 'vaccination': return 'from-red-50 to-rose-50 border-red-200'
      case 'checkup': return 'from-blue-50 to-cyan-50 border-blue-200'
      case 'development': return 'from-indigo-50 to-blue-50 border-indigo-200'
    }
  }

  const getCategoryEmoji = (category: PredictiveScheduleItem['category']) => {
    switch (category) {
      case 'health': return '🏥'
      case 'development': return '🧸'
      case 'behavior': return '😊'
      case 'feeding': return '🍼'
      case 'sleep': return '😴'
    }
  }

  const getStatusBadge = (status: PredictiveScheduleItem['status']) => {
    switch (status) {
      case 'predicted': return <Badge className="bg-purple-100 text-purple-700">AI予測</Badge>
      case 'scheduled': return <Badge className="bg-blue-100 text-blue-700">確定済み</Badge>
      case 'completed': return <Badge className="bg-green-100 text-green-700">完了</Badge>
      case 'modified': return <Badge className="bg-amber-100 text-amber-700">調整済み</Badge>
    }
  }

  const formatPredictedDate = (date: Date) => {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const dayAfter = new Date(today)
    dayAfter.setDate(dayAfter.getDate() + 2)

    if (date.toDateString() === today.toDateString()) {
      return '今日'
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return '明日'
    } else if (date.toDateString() === dayAfter.toDateString()) {
      return '明後日'
    } else {
      const days = Math.ceil((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      return `${days}日後`
    }
  }

  const upcomingPredictions = predictiveItems
    .filter(item => item.predictedDate > new Date())
    .sort((a, b) => a.predictedDate.getTime() - b.predictedDate.getTime())

  const highConfidencePredictions = upcomingPredictions.filter(item => item.confidence >= 0.8)
  const mediumConfidencePredictions = upcomingPredictions.filter(item => item.confidence >= 0.6 && item.confidence < 0.8)

  return (
    <AppLayout>
      {/* v2.0 ページヘッダー */}
      <div className="bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50">
        <div className="px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-indigo-400 flex items-center justify-center">
                <Brain className="h-4 w-4 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-heading font-semibold text-gray-800">予測管理</h1>
                <p className="text-sm text-purple-600">AI予測で先回りして子育てをサポート</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-purple-200">
              <Sparkles className="h-4 w-4 text-purple-600" />
              <span className="text-sm text-purple-700 font-medium">スマート予測</span>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8">
        {/* 予測サマリー */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
            <CardContent className="p-6 text-center">
              <Brain className="h-8 w-8 mx-auto mb-3 text-purple-600" />
              <h3 className="font-heading text-xl font-bold text-purple-700">{upcomingPredictions.length}</h3>
              <p className="text-sm text-purple-600">AI予測項目</p>
              <Badge className="mt-2 bg-purple-100 text-purple-700">アクティブ</Badge>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-200">
            <CardContent className="p-6 text-center">
              <Target className="h-8 w-8 mx-auto mb-3 text-emerald-600" />
              <h3 className="font-heading text-xl font-bold text-emerald-700">{highConfidencePredictions.length}</h3>
              <p className="text-sm text-emerald-600">高精度予測</p>
              <Badge className="mt-2 bg-emerald-100 text-emerald-700">80%以上</Badge>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
            <CardContent className="p-6 text-center">
              <Lightbulb className="h-8 w-8 mx-auto mb-3 text-amber-600" />
              <h3 className="font-heading text-xl font-bold text-amber-700">{smartReminders.length}</h3>
              <p className="text-sm text-amber-600">スマートリマインダー</p>
              <Badge className="mt-2 bg-amber-100 text-amber-700">自動生成</Badge>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
            <CardContent className="p-6 text-center">
              <Calendar className="h-8 w-8 mx-auto mb-3 text-blue-600" />
              <h3 className="font-heading text-xl font-bold text-blue-700">7</h3>
              <p className="text-sm text-blue-600">日間先読み</p>
              <Badge className="mt-2 bg-blue-100 text-blue-700">動的調整</Badge>
            </CardContent>
          </Card>
        </div>

        {/* 今日の予測 */}
        <div className="mb-8">
          <DailyPredictionCard className="w-full" />
        </div>

        {/* 予測管理タブ */}
        <Tabs defaultValue="predictions" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/60 backdrop-blur-sm">
            <TabsTrigger value="predictions" className="data-[state=active]:bg-purple-100">
              <Brain className="h-4 w-4 mr-2" />
              AI予測
            </TabsTrigger>
            <TabsTrigger value="timeline" className="data-[state=active]:bg-indigo-100">
              <Calendar className="h-4 w-4 mr-2" />
              予測タイムライン
            </TabsTrigger>
            <TabsTrigger value="reminders" className="data-[state=active]:bg-amber-100">
              <Bell className="h-4 w-4 mr-2" />
              スマートリマインダー
            </TabsTrigger>
            <TabsTrigger value="insights" className="data-[state=active]:bg-emerald-100">
              <BarChart3 className="h-4 w-4 mr-2" />
              予測精度
            </TabsTrigger>
          </TabsList>

          {/* AI予測タブ */}
          <TabsContent value="predictions" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">アクティブな予測</h3>
              <Button variant="outline" size="sm" className="border-purple-300 text-purple-600 hover:bg-purple-50">
                <Sparkles className="h-4 w-4 mr-2" />
                予測更新
              </Button>
            </div>

            <div className="space-y-4">
              {upcomingPredictions.map((item) => (
                <Card 
                  key={item.id} 
                  className={`bg-gradient-to-br ${getTypeColor(item.type)} hover:shadow-lg transition-all duration-300`}
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getTypeIcon(item.type)}
                        <div>
                          <CardTitle className="text-base font-medium text-gray-800">
                            {item.title}
                          </CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs">{getCategoryEmoji(item.category)}</span>
                            <span className="text-xs text-gray-500">
                              {formatPredictedDate(item.predictedDate)}頃
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(item.status)}
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {/* AI分析理由 */}
                    <div className="p-3 bg-white/60 backdrop-blur-sm rounded-lg border border-gray-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Eye className="h-4 w-4 text-purple-600" />
                        <span className="text-sm font-medium text-purple-800">AI分析</span>
                      </div>
                      <p className="text-sm text-gray-700">{item.aiReasoning}</p>
                    </div>

                    {/* 予測精度 */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-600">予測精度</span>
                        <span className="text-sm font-semibold text-gray-700">
                          {Math.round(item.confidence * 100)}%
                        </span>
                      </div>
                      <Progress value={item.confidence * 100} className="h-2" />
                    </div>

                    {/* 提案アクション */}
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-600">推奨アクション</p>
                      <div className="space-y-1">
                        {item.suggestedActions.slice(0, 2).map((action, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Zap className="h-3 w-3 text-yellow-500" />
                            <span className="text-sm text-gray-700">{action}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* 親の影響 */}
                    {item.parentInfluence && (
                      <div className="p-3 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200">
                        <div className="flex items-center gap-2 mb-1">
                          <Star className="h-4 w-4 text-amber-600" />
                          <span className="text-sm font-medium text-amber-800">あなたの影響</span>
                        </div>
                        <p className="text-sm text-amber-700">{item.parentInfluence}</p>
                      </div>
                    )}

                    {/* 根拠データ */}
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-gray-600">根拠データ</p>
                      <div className="flex flex-wrap gap-1">
                        {item.basedOnData.map((data, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {data}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* 予測タイムラインタブ */}
          <TabsContent value="timeline" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">7日間予測タイムライン</h3>
              <Button variant="outline" size="sm" className="border-indigo-300 text-indigo-600 hover:bg-indigo-50">
                <Calendar className="h-4 w-4 mr-2" />
                期間変更
              </Button>
            </div>

            <Card className="bg-white/80 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="space-y-6">
                  {[0, 1, 2, 3, 4, 5, 6].map((dayOffset) => {
                    const date = new Date()
                    date.setDate(date.getDate() + dayOffset)
                    
                    const dayPredictions = upcomingPredictions.filter(item => 
                      item.predictedDate.toDateString() === date.toDateString()
                    )

                    return (
                      <div key={dayOffset} className="flex gap-4">
                        <div className="w-20 flex-shrink-0 text-center">
                          <div className={`text-sm font-medium ${dayOffset === 0 ? 'text-purple-700' : 'text-gray-600'}`}>
                            {dayOffset === 0 ? '今日' : dayOffset === 1 ? '明日' : `${dayOffset}日後`}
                          </div>
                          <div className="text-xs text-gray-500">
                            {date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' })}
                          </div>
                        </div>
                        
                        <div className="flex-1 space-y-2">
                          {dayPredictions.length > 0 ? (
                            dayPredictions.map((prediction) => (
                              <div 
                                key={prediction.id}
                                className="flex items-center gap-3 p-3 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200"
                              >
                                {getTypeIcon(prediction.type)}
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-gray-800">{prediction.title}</p>
                                  <p className="text-xs text-gray-600">信頼度 {Math.round(prediction.confidence * 100)}%</p>
                                </div>
                              </div>
                            ))
                          ) : (
                            <div className="p-3 text-center text-gray-400 text-sm">
                              予測なし
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* スマートリマインダータブ */}
          <TabsContent value="reminders" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">アクティブなリマインダー</h3>
              <Button variant="outline" size="sm" className="border-amber-300 text-amber-600 hover:bg-amber-50">
                <Plus className="h-4 w-4 mr-2" />
                追加
              </Button>
            </div>

            <div className="space-y-3">
              {smartReminders.map((reminder) => (
                <Card key={reminder.id} className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <Bell className="h-5 w-5 text-amber-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-gray-800">{reminder.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{reminder.message}</p>
                          {reminder.adaptiveReason && (
                            <p className="text-xs text-amber-700 mt-2">
                              📍 {reminder.adaptiveReason}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {reminder.isAiGenerated && (
                          <Badge className="bg-purple-100 text-purple-700 text-xs">AI生成</Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>
                        {reminder.timing === 'morning' && '朝'}
                        {reminder.timing === 'before_event' && 'イベント前'}
                        {reminder.timing === 'evening' && '夜'}
                        • {reminder.frequency === 'daily' ? '毎日' : reminder.frequency === 'weekly' ? '週1回' : '状況に応じて'}
                      </span>
                      <span>
                        次回: {reminder.nextTrigger.toLocaleString('ja-JP', { 
                          month: 'short', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* 予測精度タブ */}
          <TabsContent value="insights" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">予測精度と改善</h3>
              <Button variant="outline" size="sm" className="border-emerald-300 text-emerald-600 hover:bg-emerald-50">
                <BarChart3 className="h-4 w-4 mr-2" />
                詳細分析
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-emerald-700">
                    <Target className="h-5 w-5" />
                    予測精度統計
                  </CardTitle>
                  <CardDescription>過去30日間の予測精度分析</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-200">
                      <span className="text-sm font-medium">発達予測</span>
                      <Badge className="bg-green-100 text-green-700">92%</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-200">
                      <span className="text-sm font-medium">睡眠パターン</span>
                      <Badge className="bg-green-100 text-green-700">87%</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                      <span className="text-sm font-medium">食事の好み</span>
                      <Badge className="bg-yellow-100 text-yellow-700">74%</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 rounded-lg bg-blue-50 border border-blue-200">
                      <span className="text-sm font-medium">体調変化</span>
                      <Badge className="bg-blue-100 text-blue-700">81%</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-purple-700">
                    <Lightbulb className="h-5 w-5" />
                    AI学習状況
                  </CardTitle>
                  <CardDescription>あなたのデータからの学習進捗</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="h-4 w-4 text-purple-600" />
                      <span className="text-sm font-medium text-purple-800">学習データ量</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>記録データ</span>
                        <span className="font-medium">347件</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>音声データ</span>
                        <span className="font-medium">89件</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>画像データ</span>
                        <span className="font-medium">156件</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-200">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="h-4 w-4 text-emerald-600" />
                      <span className="text-sm font-medium text-emerald-800">予測改善</span>
                    </div>
                    <p className="text-sm text-emerald-700">
                      継続的な記録により、予測精度が月平均5%向上しています
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* フローティング音声ボタン */}
        <FloatingVoiceButton position="bottom-right" />
      </div>
    </AppLayout>
  )
}