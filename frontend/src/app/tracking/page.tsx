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
  Brain,
  Sparkles,
  TrendingUp,
  Baby,
  Heart,
  Eye,
  Calendar,
  BarChart3,
  Lightbulb,
  Camera,
  Mic,
  Play,
  Clock,
  Target,
  Star,
  Zap
} from 'lucide-react'

interface GrowthInsight {
  id: string
  type: 'pattern' | 'milestone' | 'prediction' | 'achievement'
  title: string
  description: string
  confidence: number
  timeframe: string
  category: 'feeding' | 'sleep' | 'development' | 'mood' | 'social'
  isNew?: boolean
  evidence?: string[]
}

interface VisualRecord {
  id: string
  type: 'photo' | 'video' | 'voice'
  timestamp: Date
  insights: string[]
  aiAnalysis?: string
}

export default function GrowthInsightsPage() {
  const [insights, setInsights] = useState<GrowthInsight[]>([
    {
      id: '1',
      type: 'pattern',
      title: '睡眠パターンの改善',
      description: '過去2週間で夜間の睡眠時間が30分延びています。18:30の入浴ルーティンが効果的です。',
      confidence: 0.87,
      timeframe: '過去2週間',
      category: 'sleep',
      isNew: true,
      evidence: ['連続睡眠時間の増加', '寝つきまでの時間短縮', '夜泣き頻度の減少']
    },
    {
      id: '2',
      type: 'milestone',
      title: 'バイバイ動作の習得',
      description: 'お子さんが意図的にバイバイの仕草をするようになりました。社会性発達の重要な節目です。',
      confidence: 0.92,
      timeframe: '昨日確認',
      category: 'social',
      isNew: true,
      evidence: ['反復的な手の動き', 'アイコンタクトと同時実行', '大人の反応への注目']
    },
    {
      id: '3',
      type: 'prediction',
      title: '離乳食の好み変化予測',
      description: '来週頃から甘味のある食材（さつまいも、にんじん）への興味が高まる可能性があります。',
      confidence: 0.73,
      timeframe: '来週予測',
      category: 'feeding',
      evidence: ['味覚発達の段階', '現在の食べ方パターン', '月齢に基づく予測']
    },
    {
      id: '4',
      type: 'achievement',
      title: '親子のコミュニケーション向上',
      description: 'あなたの語りかけ頻度が増え、お子さんの反応も豊かになっています。素晴らしい成果です。',
      confidence: 0.95,
      timeframe: '過去1ヶ月',
      category: 'social',
      evidence: ['語りかけ回数の増加', '子供の笑顔頻度向上', '相互反応の質向上']
    }
  ])

  const [visualRecords, setVisualRecords] = useState<VisualRecord[]>([
    {
      id: '1',
      type: 'photo',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      insights: ['表情：とても嬉しそう', '姿勢：安定したお座り', '注目：おもちゃに集中'],
      aiAnalysis: '発達良好。集中力と情緒の安定が見られます。'
    },
    {
      id: '2',
      type: 'voice',
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
      insights: ['音声：バブリング増加', '音程：多様な声色', '反応：親の声に敏感'],
      aiAnalysis: '言語発達の準備段階が順調に進んでいます。'
    }
  ])

  const getInsightIcon = (type: GrowthInsight['type']) => {
    switch (type) {
      case 'pattern': return <TrendingUp className="h-5 w-5 text-purple-600" />
      case 'milestone': return <Target className="h-5 w-5 text-emerald-600" />
      case 'prediction': return <Brain className="h-5 w-5 text-indigo-600" />
      case 'achievement': return <Star className="h-5 w-5 text-amber-600" />
    }
  }

  const getInsightColor = (type: GrowthInsight['type']) => {
    switch (type) {
      case 'pattern': return 'from-purple-50 to-violet-50 border-purple-200'
      case 'milestone': return 'from-emerald-50 to-green-50 border-emerald-200'
      case 'prediction': return 'from-indigo-50 to-blue-50 border-indigo-200'
      case 'achievement': return 'from-amber-50 to-yellow-50 border-amber-200'
    }
  }

  const getCategoryIcon = (category: GrowthInsight['category']) => {
    switch (category) {
      case 'feeding': return '🍼'
      case 'sleep': return '😴'
      case 'development': return '🧸'
      case 'mood': return '😊'
      case 'social': return '👶'
    }
  }

  return (
    <AppLayout>
      {/* v2.0 ページヘッダー */}
      <div className="bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50">
        <div className="px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-indigo-400 flex items-center justify-center">
                <Eye className="h-4 w-4 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-heading font-semibold text-gray-800">成長洞察</h1>
                <p className="text-sm text-purple-600">AI分析による見えない成長の可視化</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-purple-200">
              <Sparkles className="h-4 w-4 text-purple-600" />
              <span className="text-sm text-purple-700 font-medium">リアルタイム分析</span>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8">
        {/* AI洞察サマリー */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-200">
            <CardContent className="p-6 text-center">
              <Target className="h-8 w-8 mx-auto mb-3 text-emerald-600" />
              <h3 className="font-heading text-xl font-bold text-emerald-700">12</h3>
              <p className="text-sm text-emerald-600">今月の新しい洞察</p>
              <Badge className="mt-2 bg-emerald-100 text-emerald-700">+3 先週比</Badge>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
            <CardContent className="p-6 text-center">
              <Brain className="h-8 w-8 mx-auto mb-3 text-purple-600" />
              <h3 className="font-heading text-xl font-bold text-purple-700">87%</h3>
              <p className="text-sm text-purple-600">平均予測精度</p>
              <Badge className="mt-2 bg-purple-100 text-purple-700">高精度</Badge>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
            <CardContent className="p-6 text-center">
              <Star className="h-8 w-8 mx-auto mb-3 text-amber-600" />
              <h3 className="font-heading text-xl font-bold text-amber-700">8.9</h3>
              <p className="text-sm text-amber-600">成長スコア</p>
              <Badge className="mt-2 bg-amber-100 text-amber-700">優秀</Badge>
            </CardContent>
          </Card>
        </div>

        {/* 今日の予測洞察 */}
        <div className="mb-8">
          <DailyPredictionCard className="w-full" />
        </div>

        {/* AI洞察とビジュアル記録のタブ */}
        <Tabs defaultValue="insights" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-white/60 backdrop-blur-sm">
            <TabsTrigger value="insights" className="data-[state=active]:bg-purple-100">
              <Brain className="h-4 w-4 mr-2" />
              AI洞察
            </TabsTrigger>
            <TabsTrigger value="visual" className="data-[state=active]:bg-emerald-100">
              <Camera className="h-4 w-4 mr-2" />
              ビジュアル記録
            </TabsTrigger>
            <TabsTrigger value="patterns" className="data-[state=active]:bg-indigo-100">
              <BarChart3 className="h-4 w-4 mr-2" />
              成長パターン
            </TabsTrigger>
          </TabsList>

          {/* AI洞察タブ */}
          <TabsContent value="insights" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">最新のAI洞察</h3>
              <Button variant="outline" size="sm" className="border-purple-300 text-purple-600 hover:bg-purple-50">
                <Sparkles className="h-4 w-4 mr-2" />
                更新
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {insights.map((insight) => (
                <Card 
                  key={insight.id} 
                  className={`bg-gradient-to-br ${getInsightColor(insight.type)} hover:shadow-lg transition-all duration-300 ${
                    insight.isNew ? 'ring-2 ring-purple-400 ring-opacity-50' : ''
                  }`}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getInsightIcon(insight.type)}
                        <CardTitle className="text-base font-medium text-gray-800">
                          {insight.title}
                        </CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs">{getCategoryIcon(insight.category)}</span>
                        {insight.isNew && (
                          <Badge className="bg-red-100 text-red-700 text-xs">NEW</Badge>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-gray-500">{insight.timeframe}</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {insight.description}
                    </p>

                    {/* 信頼度 */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-gray-600">信頼度</span>
                        <span className="text-xs font-semibold text-gray-700">
                          {Math.round(insight.confidence * 100)}%
                        </span>
                      </div>
                      <Progress value={insight.confidence * 100} className="h-2" />
                    </div>

                    {/* エビデンス */}
                    {insight.evidence && (
                      <div className="space-y-2">
                        <p className="text-xs font-medium text-gray-600">根拠データ</p>
                        <div className="space-y-1">
                          {insight.evidence.slice(0, 2).map((evidence, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <div className="h-1.5 w-1.5 rounded-full bg-gray-400" />
                              <span className="text-xs text-gray-600">{evidence}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* ビジュアル記録タブ */}
          <TabsContent value="visual" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">ビジュアル記録とAI分析</h3>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="border-emerald-300 text-emerald-600 hover:bg-emerald-50">
                  <Camera className="h-4 w-4 mr-2" />
                  写真
                </Button>
                <Button variant="outline" size="sm" className="border-blue-300 text-blue-600 hover:bg-blue-50">
                  <Mic className="h-4 w-4 mr-2" />
                  音声
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {visualRecords.map((record) => (
                <Card key={record.id} className="bg-white/80 backdrop-blur-sm hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {record.type === 'photo' && <Camera className="h-4 w-4 text-emerald-600" />}
                        {record.type === 'video' && <Play className="h-4 w-4 text-blue-600" />}
                        {record.type === 'voice' && <Mic className="h-4 w-4 text-purple-600" />}
                        <span className="text-sm font-medium capitalize">{record.type}</span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {record.timestamp.toLocaleTimeString('ja-JP', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* AI分析結果 */}
                    {record.aiAnalysis && (
                      <div className="p-3 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                        <div className="flex items-center gap-2 mb-2">
                          <Brain className="h-4 w-4 text-purple-600" />
                          <span className="text-sm font-medium text-purple-800">AI分析</span>
                        </div>
                        <p className="text-sm text-purple-700">{record.aiAnalysis}</p>
                      </div>
                    )}

                    {/* 詳細洞察 */}
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-gray-600">検出された特徴</p>
                      <div className="space-y-1">
                        {record.insights.map((insight, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Zap className="h-3 w-3 text-yellow-500" />
                            <span className="text-xs text-gray-700">{insight}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 空状態 */}
            {visualRecords.length === 0 && (
              <Card className="bg-white/80 backdrop-blur-sm">
                <CardContent className="p-12 text-center">
                  <Camera className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-600 mb-2">ビジュアル記録がありません</h3>
                  <p className="text-sm text-gray-500 mb-4">
                    写真や音声を記録して、AIによる成長分析を受けてみましょう
                  </p>
                  <Button className="bg-emerald-500 hover:bg-emerald-600">
                    <Camera className="h-4 w-4 mr-2" />
                    最初の記録を作成
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* 成長パターンタブ */}
          <TabsContent value="patterns" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">長期的な成長パターン</h3>
              <Button variant="outline" size="sm" className="border-indigo-300 text-indigo-600 hover:bg-indigo-50">
                <Calendar className="h-4 w-4 mr-2" />
                期間変更
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-700">
                    <BarChart3 className="h-5 w-5" />
                    発達推移グラフ
                  </CardTitle>
                  <CardDescription>過去3ヶ月の総合的な成長推移</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-48 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg flex items-center justify-center border border-blue-200">
                    <div className="text-center">
                      <BarChart3 className="h-12 w-12 mx-auto mb-3 text-blue-500" />
                      <p className="text-blue-700 font-medium">インタラクティブグラフ</p>
                      <p className="text-xs text-blue-600">近日実装予定</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-emerald-700">
                    <Target className="h-5 w-5" />
                    マイルストーン達成
                  </CardTitle>
                  <CardDescription>月齢に応じた発達目標の達成状況</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-200">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full bg-green-500" />
                        <span className="text-sm font-medium">首すわり</span>
                      </div>
                      <Badge className="bg-green-100 text-green-700">達成</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-200">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full bg-green-500" />
                        <span className="text-sm font-medium">寝返り</span>
                      </div>
                      <Badge className="bg-green-100 text-green-700">達成</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-amber-50 border border-amber-200">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full bg-amber-500" />
                        <span className="text-sm font-medium">お座り</span>
                      </div>
                      <Badge className="bg-amber-100 text-amber-700">進行中</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 border border-gray-200">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full bg-gray-400" />
                        <span className="text-sm font-medium">つかまり立ち</span>
                      </div>
                      <Badge variant="outline">予定</Badge>
                    </div>
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