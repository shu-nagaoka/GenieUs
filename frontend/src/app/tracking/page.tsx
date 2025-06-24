'use client'

import { useState } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  TrendingUp,
  Camera,
  Sparkles,
  Heart,
  Baby,
  Ruler,
  Scale,
  MessageCircle,
  Smile,
  Star,
  Calendar,
  Eye,
  Image,
  BarChart3,
  Target,
  Award
} from 'lucide-react'
import { MdChildCare, MdPhotoCamera, MdTimeline } from 'react-icons/md'
import { FaChild, FaCamera, FaChartLine, FaHeart } from 'react-icons/fa'
import { GiMagicLamp, GiBabyFace, GiBodyHeight } from 'react-icons/gi'
import Link from 'next/link'

interface GrowthRecord {
  id: string
  childName: string
  date: string
  ageInMonths: number
  type: 'physical' | 'emotional' | 'cognitive' | 'milestone' | 'photo'
  category: 'height' | 'weight' | 'speech' | 'smile' | 'movement' | 'expression' | 'achievement'
  title: string
  description: string
  value?: string | number
  unit?: string
  imageUrl?: string
  detectedBy: 'genie' | 'parent'
  confidence?: number
  emotions?: string[]
  developmentStage?: string
}

export default function GrowthTrackingPage() {
  const [selectedChild, setSelectedChild] = useState<string>('hanako')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  // サンプル成長記録データ
  const growthRecords: GrowthRecord[] = [
    {
      id: '1',
      childName: '花子ちゃん',
      date: '2024-07-20',
      ageInMonths: 8,
      type: 'physical',
      category: 'height',
      title: '身長測定',
      description: 'Genieが写真から身長を自動測定しました',
      value: 67.5,
      unit: 'cm',
      detectedBy: 'genie',
      confidence: 0.92,
      developmentStage: '標準範囲'
    },
    {
      id: '2',
      childName: '花子ちゃん',
      date: '2024-07-20',
      ageInMonths: 8,
      type: 'emotional',
      category: 'smile',
      title: '初めての人見知り笑顔',
      description: '知らない人に対しても笑顔を見せるようになりました',
      imageUrl: '/api/placeholder/300/200',
      detectedBy: 'genie',
      confidence: 0.87,
      emotions: ['喜び', '安心', '興味'],
      developmentStage: '社会性発達'
    },
    {
      id: '3',
      childName: '花子ちゃん',
      date: '2024-07-18',
      ageInMonths: 8,
      type: 'cognitive',
      category: 'speech',
      title: '「まんま」発音',
      description: '明確に「まんま」と発音しました！',
      detectedBy: 'genie',
      confidence: 0.94,
      developmentStage: '言語発達順調'
    },
    {
      id: '4',
      childName: '花子ちゃん',
      date: '2024-07-15',
      ageInMonths: 8,
      type: 'milestone',
      category: 'movement',
      title: 'つかまり立ち成功',
      description: 'ソファにつかまって立ち上がることができました',
      imageUrl: '/api/placeholder/300/200',
      detectedBy: 'genie',
      confidence: 0.96,
      developmentStage: '運動発達良好'
    },
    {
      id: '5',
      childName: '花子ちゃん',
      date: '2024-07-10',
      ageInMonths: 7,
      type: 'physical',
      category: 'weight',
      title: '体重測定',
      description: '健康的な体重増加を確認',
      value: 7.8,
      unit: 'kg',
      detectedBy: 'genie',
      confidence: 0.89,
      developmentStage: '標準範囲'
    },
    {
      id: '6',
      childName: '花子ちゃん',
      date: '2024-07-05',
      ageInMonths: 7,
      type: 'photo',
      category: 'expression',
      title: '表情豊かな瞬間',
      description: 'Genieが感情表現の成長を検出しました',
      imageUrl: '/api/placeholder/300/200',
      detectedBy: 'genie',
      confidence: 0.91,
      emotions: ['驚き', '好奇心', '集中'],
      developmentStage: '感情表現発達'
    }
  ]

  const children = [
    { id: 'hanako', name: '花子ちゃん', age: '8ヶ月', avatar: '👶' },
    { id: 'taro', name: '太郎くん', age: '2歳', avatar: '🧒' }
  ]

  const getFilteredRecords = () => {
    let filtered = growthRecords.filter(record => 
      selectedChild === 'all' || record.childName === children.find(c => c.id === selectedChild)?.name
    )
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(record => record.category === selectedCategory)
    }
    
    return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  const getRecordIcon = (category: string) => {
    switch (category) {
      case 'height': return <Ruler className="h-5 w-5" />
      case 'weight': return <Scale className="h-5 w-5" />
      case 'speech': return <MessageCircle className="h-5 w-5" />
      case 'smile': return <Smile className="h-5 w-5" />
      case 'movement': return <TrendingUp className="h-5 w-5" />
      case 'expression': return <Heart className="h-5 w-5" />
      default: return <Star className="h-5 w-5" />
    }
  }

  const getRecordColor = (type: string) => {
    switch (type) {
      case 'physical': return 'from-blue-500 to-blue-600'
      case 'emotional': return 'from-pink-500 to-pink-600'
      case 'cognitive': return 'from-purple-500 to-purple-600'
      case 'milestone': return 'from-green-500 to-green-600'
      case 'photo': return 'from-amber-500 to-amber-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ja-JP', { 
      year: 'numeric',
      month: 'short', 
      day: 'numeric'
    })
  }

  const getStatsForChild = (childId: string) => {
    const childName = children.find(c => c.id === childId)?.name || ''
    const records = growthRecords.filter(r => r.childName === childName)
    
    return {
      totalRecords: records.length,
      photosCount: records.filter(r => r.imageUrl).length,
      milestonesCount: records.filter(r => r.type === 'milestone').length,
      avgConfidence: Math.round(records.reduce((acc, r) => acc + (r.confidence || 0), 0) / records.length * 100)
    }
  }

  const selectedChildStats = getStatsForChild(selectedChild)

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50">
        {/* ページヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-pink-100">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center shadow-lg">
                  <MdTimeline className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">見守った成長</h1>
                  <p className="text-gray-600">Genieが記録したお子さんの大切な成長の軌跡</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Link href="/chat">
                  <Button className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white shadow-lg">
                    <Camera className="h-4 w-4 mr-2" />
                    成長を記録
                  </Button>
                </Link>
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-pink-200">
                  <GiMagicLamp className="h-4 w-4 text-pink-600" />
                  <span className="text-sm text-pink-700 font-medium">AI自動検出</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-6 space-y-8">
          {/* 成長サマリーカード */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">記録総数</p>
                    <p className="text-2xl font-bold mt-1">{selectedChildStats.totalRecords}件</p>
                    <p className="text-blue-200 text-xs">継続観察中</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm font-medium">写真記録</p>
                    <p className="text-2xl font-bold mt-1">{selectedChildStats.photosCount}枚</p>
                    <p className="text-green-200 text-xs">AI解析済み</p>
                  </div>
                  <Camera className="h-8 w-8 text-green-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm font-medium">マイルストーン</p>
                    <p className="text-2xl font-bold mt-1">{selectedChildStats.milestonesCount}個</p>
                    <p className="text-purple-200 text-xs">達成済み</p>
                  </div>
                  <Award className="h-8 w-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-amber-100 text-sm font-medium">AI精度</p>
                    <p className="text-2xl font-bold mt-1">{selectedChildStats.avgConfidence}%</p>
                    <p className="text-amber-200 text-xs">検出信頼度</p>
                  </div>
                  <Target className="h-8 w-8 text-amber-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 子ども選択とフィルター */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Baby className="h-6 w-6" />
                成長記録フィルター
              </CardTitle>
              <CardDescription className="text-pink-100">
                お子さんと記録タイプを選択して成長を確認
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">お子さんを選択</label>
                  <Select value={selectedChild} onValueChange={setSelectedChild}>
                    <SelectTrigger className="border-pink-200 focus:border-pink-400">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {children.map(child => (
                        <SelectItem key={child.id} value={child.id}>
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{child.avatar}</span>
                            <span>{child.name} ({child.age})</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">記録カテゴリ</label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="border-pink-200 focus:border-pink-400">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">すべて</SelectItem>
                      <SelectItem value="height">身長</SelectItem>
                      <SelectItem value="weight">体重</SelectItem>
                      <SelectItem value="speech">言葉</SelectItem>
                      <SelectItem value="smile">笑顔</SelectItem>
                      <SelectItem value="movement">運動</SelectItem>
                      <SelectItem value="expression">表情</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 成長タイムライン */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <MdTimeline className="h-6 w-6" />
                成長タイムライン
              </CardTitle>
              <CardDescription className="text-purple-100">
                時系列で見るお子さんの成長記録
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="relative">
                {/* タイムライン線 */}
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-pink-300 to-purple-300"></div>
                
                <div className="space-y-8">
                  {getFilteredRecords().map((record, index) => (
                    <div key={record.id} className="relative flex items-start gap-6">
                      {/* タイムライン点 */}
                      <div className={`relative z-10 flex-shrink-0 w-16 h-16 rounded-full bg-gradient-to-br ${getRecordColor(record.type)} flex items-center justify-center shadow-lg text-white`}>
                        {getRecordIcon(record.category)}
                        <div className="absolute -top-1 -right-1">
                          {record.detectedBy === 'genie' && (
                            <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
                              <GiMagicLamp className="h-3 w-3 text-white" />
                            </div>
                          )}
                        </div>
                      </div>

                      {/* 記録カード */}
                      <Card className="flex-1 border-0 shadow-lg bg-gradient-to-br from-white to-gray-50 hover:shadow-xl transition-all duration-300">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-bold text-lg text-gray-800">{record.title}</h4>
                                <Badge className={`bg-gradient-to-r ${getRecordColor(record.type)} text-white`}>
                                  {record.type === 'physical' ? '身体' :
                                   record.type === 'emotional' ? '感情' :
                                   record.type === 'cognitive' ? '認知' :
                                   record.type === 'milestone' ? 'マイルストーン' : '写真'}
                                </Badge>
                                {record.confidence && (
                                  <Badge variant="outline" className="text-xs">
                                    信頼度 {Math.round(record.confidence * 100)}%
                                  </Badge>
                                )}
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                                <div className="flex items-center gap-2">
                                  <Calendar className="h-4 w-4 text-pink-600" />
                                  <span>{formatDate(record.date)}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Baby className="h-4 w-4 text-pink-600" />
                                  <span>{record.ageInMonths}ヶ月</span>
                                </div>
                                {record.value && (
                                  <div className="flex items-center gap-2">
                                    <BarChart3 className="h-4 w-4 text-pink-600" />
                                    <span>{record.value}{record.unit}</span>
                                  </div>
                                )}
                              </div>
                              
                              <p className="text-gray-700 mb-3">{record.description}</p>
                              
                              {record.developmentStage && (
                                <div className="mb-3">
                                  <Badge className="bg-green-100 text-green-700">
                                    {record.developmentStage}
                                  </Badge>
                                </div>
                              )}
                              
                              {record.emotions && record.emotions.length > 0 && (
                                <div className="flex flex-wrap gap-2 mb-3">
                                  {record.emotions.map((emotion, idx) => (
                                    <Badge key={idx} variant="outline" className="text-xs">
                                      {emotion}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                            
                            {record.imageUrl && (
                              <div className="ml-4 flex-shrink-0">
                                <div className="w-32 h-24 bg-gradient-to-br from-pink-100 to-purple-100 rounded-lg border border-pink-200 flex items-center justify-center">
                                  <div className="text-center">
                                    <Image className="h-8 w-8 text-pink-400 mx-auto mb-1" />
                                    <p className="text-xs text-pink-600">成長写真</p>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AIチャット連携カード */}
          <Card className="shadow-xl border-0 bg-gradient-to-br from-pink-50 to-purple-50">
            <CardHeader className="bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Sparkles className="h-6 w-6" />
                Genieとの成長記録連携
              </CardTitle>
              <CardDescription className="text-pink-100">
                写真や動画を送るだけで、Genieが自動で成長を記録・分析します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="bg-white/60 p-4 rounded-lg border border-pink-200">
                <div className="flex items-start gap-3 mb-4">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center shadow-lg">
                    <GiMagicLamp className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-pink-800 font-medium mb-2">
                      📸 Genieができること：
                    </p>
                    <ul className="text-sm text-pink-700 space-y-1">
                      <li>• 写真から身長・体重を自動測定</li>
                      <li>• 表情や笑顔の変化を感情分析</li>
                      <li>• 発話や言葉の発達を音声解析</li>
                      <li>• 運動能力やマイルストーンを自動検出</li>
                      <li>• 成長の軌跡を美しいタイムラインで表示</li>
                    </ul>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Link href="/chat" className="flex-1">
                    <Button className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white shadow-lg">
                      <Camera className="h-4 w-4 mr-2" />
                      写真で成長を記録
                    </Button>
                  </Link>
                  <Button 
                    variant="outline"
                    className="border-pink-300 text-pink-700 hover:bg-pink-50"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    詳細分析
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 自動記録の説明 */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-full border border-pink-200">
              <GiMagicLamp className="h-4 w-4 text-pink-600" />
              <span className="text-sm text-pink-700 font-medium">Genieが24時間、大切な成長の瞬間を見守ります</span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}