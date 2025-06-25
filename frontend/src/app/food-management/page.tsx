'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
// import { Calendar } from '@/components/ui/calendar'
import { 
  Utensils,
  Calendar as CalendarIcon,
  Clock,
  Sparkles,
  Heart,
  Baby,
  Target,
  CheckCircle,
  Plus,
  Star,
  Grid3X3,
  LayoutList,
  ChevronLeft,
  ChevronRight,
  Edit,
  Search,
  Filter,
  Apple,
  Milk,
  Beef,
  Coffee
} from 'lucide-react'
import { FaUtensils, FaAppleAlt, FaCarrot, FaStar, FaHeart } from 'react-icons/fa'
import { GiMagicLamp, GiBroccoli, GiMilkCarton } from 'react-icons/gi'
import { MdFastfood, MdRestaurant, MdLocalDining } from 'react-icons/md'
import Link from 'next/link'

// 食事記録のインターフェース
interface FoodRecord {
  id: string
  title: string
  date: string
  time: string
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  category: 'baby_food' | 'family_meal' | 'snack' | 'drink'
  description: string
  ingredients: string[]
  nutrition?: {
    calories?: number
    protein?: number
    carbs?: number
    fat?: number
    fiber?: number
  }
  tags: string[]
  photos?: string[]
  reaction: 'excellent' | 'good' | 'okay' | 'poor'
  notes?: string
  createdBy: 'genie' | 'user'
  allergens?: string[]
}

// サンプルデータを関数外に移動
const sampleFoodRecords: FoodRecord[] = [
    {
      id: '1',
      title: 'かぼちゃとにんじんのペースト',
      date: '2025-06-25',
      time: '12:00',
      type: 'lunch',
      category: 'baby_food',
      description: '離乳食中期向けの栄養満点ペースト',
      ingredients: ['かぼちゃ', 'にんじん', 'だし汁'],
      nutrition: { calories: 45, protein: 1.2, carbs: 10.5, fat: 0.3, fiber: 2.1 },
      tags: ['離乳食', '中期', '野菜', 'ビタミンA'],
      reaction: 'excellent',
      notes: 'とても喜んで食べてくれました！おかわりも欲しがりました。',
      createdBy: 'user',
      allergens: []
    },
    {
      id: '2',
      title: 'バナナヨーグルト',
      date: '2025-06-25',
      time: '15:00',
      type: 'snack',
      category: 'snack',
      description: 'おやつタイムの定番',
      ingredients: ['バナナ', 'プレーンヨーグルト', 'きなこ'],
      nutrition: { calories: 68, protein: 3.2, carbs: 12.4, fat: 1.8, fiber: 1.5 },
      tags: ['おやつ', 'カルシウム', '手づかみ食べ'],
      reaction: 'good',
      notes: 'バナナを手でつかんで上手に食べました',
      createdBy: 'genie',
      allergens: ['乳製品']
    },
    {
      id: '3',
      title: '鶏ひき肉とほうれん草のおじや',
      date: '2025-06-24',
      time: '18:00',
      type: 'dinner',
      category: 'baby_food',
      description: 'タンパク質と鉄分たっぷりの夕食',
      ingredients: ['軟飯', '鶏ひき肉', 'ほうれん草', '人参', 'だし汁'],
      nutrition: { calories: 95, protein: 8.5, carbs: 12.2, fat: 2.1, fiber: 1.8 },
      tags: ['離乳食', '後期', 'タンパク質', '鉄分'],
      reaction: 'okay',
      notes: 'ほうれん草を少し残しました。次回は細かく刻んでみます',
      createdBy: 'genie',
      allergens: []
    },
    {
      id: '4',
      title: '親子丼（取り分け）',
      date: '2025-06-23',
      time: '12:30',
      type: 'lunch',
      category: 'family_meal',
      description: '大人のメニューから取り分け',
      ingredients: ['軟飯', '鶏肉', '卵', '玉ねぎ', 'だし汁'],
      nutrition: { calories: 120, protein: 12.3, carbs: 15.8, fat: 3.2, fiber: 0.8 },
      tags: ['取り分け', '家族食', 'タンパク質'],
      reaction: 'excellent',
      notes: '家族と同じメニューで嬉しそうでした',
      createdBy: 'user',
      allergens: ['卵']
    },
    {
      id: '5',
      title: 'フルーツボウル朝食',
      date: '2025-06-25',
      time: '07:30',
      type: 'breakfast',
      category: 'baby_food',
      description: '朝の元気チャージ！',
      ingredients: ['いちご', 'ブルーベリー', 'バナナ', 'ヨーグルト'],
      nutrition: { calories: 85, protein: 2.8, carbs: 18.5, fat: 1.2, fiber: 3.1 },
      tags: ['朝食', 'フルーツ', 'ビタミンC'],
      reaction: 'excellent',
      notes: '色とりどりのフルーツに大興奮でした',
      createdBy: 'user',
      allergens: ['乳製品']
    },
    {
      id: '6',
      title: 'パンケーキ朝食',
      date: '2025-06-24',
      time: '08:00',
      type: 'breakfast',
      category: 'baby_food',
      description: '手づかみ食べしやすいミニパンケーキ',
      ingredients: ['小麦粉', '卵', '牛乳', 'バナナ'],
      nutrition: { calories: 110, protein: 4.5, carbs: 20.2, fat: 2.8, fiber: 1.5 },
      tags: ['朝食', '手づかみ', 'パンケーキ'],
      reaction: 'good',
      notes: '手でつまんで上手に食べました',
      createdBy: 'genie',
      allergens: ['小麦', '卵', '乳製品']
    },
    {
      id: '7',
      title: 'ミートボール夕食',
      date: '2025-06-23',
      time: '18:30',
      type: 'dinner',
      category: 'baby_food',
      description: '柔らかく煮込んだミートボール',
      ingredients: ['牛ひき肉', '玉ねぎ', 'トマトソース', 'パスタ'],
      nutrition: { calories: 140, protein: 12.8, carbs: 18.2, fat: 3.5, fiber: 2.1 },
      tags: ['夕食', 'タンパク質', 'イタリアン'],
      reaction: 'excellent',
      notes: 'パスタと一緒にモリモリ食べました',
      createdBy: 'user',
      allergens: ['小麦']
    },
    {
      id: '8',
      title: 'おせんべい',
      date: '2025-06-24',
      time: '15:30',
      type: 'snack',
      category: 'snack',
      description: '赤ちゃん用のお米せんべい',
      ingredients: ['米', '塩'],
      nutrition: { calories: 35, protein: 0.8, carbs: 8.2, fat: 0.1, fiber: 0.3 },
      tags: ['おやつ', 'お米', '手づかみ'],
      reaction: 'good',
      notes: 'サクサク音を楽しみながら食べました',
      createdBy: 'genie',
      allergens: []
    }
  ]

export default function FoodManagementPage() {
  const [selectedTab, setSelectedTab] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'cards' | 'calendar'>('cards')
  const [foodRecords, setFoodRecords] = useState<FoodRecord[]>(sampleFoodRecords) // 初期値に直接設定
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date())
  const [currentDate, setCurrentDate] = useState(new Date())

  // デバッグ用：データの状態を監視
  useEffect(() => {
    console.log('foodRecords state:', foodRecords.length, 'records')
    console.log('Sample data:', sampleFoodRecords.length, 'records')
  }, [foodRecords])

  // タブ変更の監視
  useEffect(() => {
    console.log('Selected tab changed to:', selectedTab)
  }, [selectedTab])

  const getRecordsByType = (type: string) => {
    let filtered = foodRecords
    
    console.log('Filtering by type:', type, 'Total records:', foodRecords.length)
    
    if (type !== 'all') {
      filtered = filtered.filter(record => record.type === type)
      console.log('After type filter:', filtered.length)
    }
    
    if (searchQuery) {
      filtered = filtered.filter(record => 
        record.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        record.ingredients.some(ing => ing.toLowerCase().includes(searchQuery.toLowerCase())) ||
        record.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
      console.log('After search filter:', filtered.length)
    }
    
    const sorted = filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    console.log('Final filtered records:', sorted.map(r => ({ title: r.title, type: r.type })))
    
    return sorted
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'breakfast': return <Coffee className="h-5 w-5" />
      case 'lunch': return <Utensils className="h-5 w-5" />
      case 'dinner': return <MdRestaurant className="h-5 w-5" />
      case 'snack': return <Apple className="h-5 w-5" />
      default: return <Utensils className="h-5 w-5" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'breakfast': return 'bg-yellow-500'
      case 'lunch': return 'bg-orange-500'
      case 'dinner': return 'bg-blue-500'
      case 'snack': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  const getReactionIcon = (reaction: string) => {
    switch (reaction) {
      case 'excellent': return <Star className="h-4 w-4 fill-current text-yellow-400" />
      case 'good': return <Heart className="h-4 w-4 fill-current text-pink-400" />
      case 'okay': return <CheckCircle className="h-4 w-4 text-blue-400" />
      case 'poor': return <div className="h-4 w-4 rounded-full bg-gray-400" />
      default: return <CheckCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ja-JP', { 
      month: 'short', 
      day: 'numeric',
      weekday: 'short'
    })
  }

  const getTotalNutrition = () => {
    const total = { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 }
    foodRecords.forEach(record => {
      if (record.nutrition) {
        total.calories += record.nutrition.calories || 0
        total.protein += record.nutrition.protein || 0
        total.carbs += record.nutrition.carbs || 0
        total.fat += record.nutrition.fat || 0
        total.fiber += record.nutrition.fiber || 0
      }
    })
    return total
  }

  const getStatsData = () => {
    const today = new Date().toISOString().split('T')[0]
    const todayRecords = foodRecords.filter(r => r.date === today)
    
    return {
      totalRecords: foodRecords.length,
      todayMeals: todayRecords.length,
      excellentReactions: foodRecords.filter(r => r.reaction === 'excellent').length,
      genieRecommendations: foodRecords.filter(r => r.createdBy === 'genie').length,
      todayNutrition: getTotalNutrition()
    }
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate)
    newDate.setMonth(currentDate.getMonth() + (direction === 'next' ? 1 : -1))
    setCurrentDate(newDate)
  }

  const statsData = getStatsData()

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
        {/* ページヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-orange-100">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg">
                  <FaUtensils className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">食事管理</h1>
                  <p className="text-gray-600">Genieと一緒に記録する栄養バランスと成長記録</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Button className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white shadow-lg">
                  <Plus className="h-4 w-4 mr-2" />
                  食事記録を追加
                </Button>
                <Link href="/chat">
                  <Button variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Genieに相談
                  </Button>
                </Link>
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-orange-200">
                  <GiMagicLamp className="h-4 w-4 text-orange-600" />
                  <span className="text-sm text-orange-700 font-medium">栄養分析AI</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-6 space-y-8">
          {/* 栄養サマリーカード */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-orange-600 to-orange-700 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 text-sm font-medium">総記録数</p>
                    <p className="text-2xl font-bold mt-1">{statsData.totalRecords}回</p>
                    <p className="text-orange-200 text-xs">食事記録</p>
                  </div>
                  <Utensils className="h-8 w-8 text-orange-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-amber-100 text-sm font-medium">今日の食事</p>
                    <p className="text-2xl font-bold mt-1">{statsData.todayMeals}回</p>
                    <p className="text-amber-200 text-xs">本日実績</p>
                  </div>
                  <CalendarIcon className="h-8 w-8 text-amber-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-yellow-100 text-sm font-medium">大満足</p>
                    <p className="text-2xl font-bold mt-1">{statsData.excellentReactions}回</p>
                    <p className="text-yellow-200 text-xs">喜んで完食</p>
                  </div>
                  <Star className="h-8 w-8 text-yellow-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm font-medium">Genie提案</p>
                    <p className="text-2xl font-bold mt-1">{statsData.genieRecommendations}回</p>
                    <p className="text-green-200 text-xs">AI推奨メニュー</p>
                  </div>
                  <GiMagicLamp className="h-8 w-8 text-green-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm font-medium">今日のカロリー</p>
                    <p className="text-2xl font-bold mt-1">{Math.round(statsData.todayNutrition.calories)}</p>
                    <p className="text-purple-200 text-xs">kcal</p>
                  </div>
                  <Target className="h-8 w-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 検索・フィルター */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Filter className="h-6 w-6" />
                食事記録フィルター
              </CardTitle>
              <CardDescription className="text-orange-100">
                お探しの食事記録を見つけやすくする検索・フィルター機能
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                {/* 検索バー */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="メニュー名、食材、タグで検索..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 border-orange-200 focus:border-orange-400"
                  />
                </div>
                
                {/* ビューモード切り替えとタブ */}
                <div className="flex items-center justify-between">
                  <Tabs value={selectedTab} onValueChange={setSelectedTab} className="flex-1">
                    <TabsList className="grid w-full grid-cols-5">
                      <TabsTrigger value="all" className="flex items-center gap-2">
                        <Utensils className="h-4 w-4" />
                        すべて
                      </TabsTrigger>
                      <TabsTrigger value="breakfast" className="flex items-center gap-2">
                        <Coffee className="h-4 w-4" />
                        朝食
                      </TabsTrigger>
                      <TabsTrigger value="lunch" className="flex items-center gap-2">
                        <MdRestaurant className="h-4 w-4" />
                        昼食
                      </TabsTrigger>
                      <TabsTrigger value="dinner" className="flex items-center gap-2">
                        <MdLocalDining className="h-4 w-4" />
                        夕食
                      </TabsTrigger>
                      <TabsTrigger value="snack" className="flex items-center gap-2">
                        <Apple className="h-4 w-4" />
                        おやつ
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant={viewMode === 'cards' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        console.log('Switching to cards view')
                        setViewMode('cards')
                      }}
                      className="flex items-center gap-2"
                    >
                      <LayoutList className="h-4 w-4" />
                      カード
                    </Button>
                    <Button
                      variant={viewMode === 'calendar' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        console.log('Switching to calendar view')
                        setViewMode('calendar')
                      }}
                      className="flex items-center gap-2"
                    >
                      <Grid3X3 className="h-4 w-4" />
                      カレンダー
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 食事記録表示 */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <FaUtensils className="h-6 w-6" />
                食事記録ギャラリー
              </CardTitle>
              <CardDescription className="text-amber-100">
                {getRecordsByType(selectedTab).length}件の食事記録が見つかりました（現在のタブ: {selectedTab}）
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              {/* カードビュー */}
              {viewMode === 'cards' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {getRecordsByType(selectedTab).map((record) => (
                    <Card key={record.id} className="border-0 shadow-lg bg-gradient-to-br from-white to-gray-50 hover:shadow-xl transition-all duration-300">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className={`h-10 w-10 rounded-full ${getTypeColor(record.type)} flex items-center justify-center text-white shadow-lg`}>
                              {getTypeIcon(record.type)}
                            </div>
                            <div>
                              <h4 className="font-bold text-lg text-gray-800">{record.title}</h4>
                              <div className="flex items-center gap-2 text-sm text-gray-500">
                                <CalendarIcon className="h-4 w-4" />
                                <span>{formatDate(record.date)} {record.time}</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {getReactionIcon(record.reaction)}
                            {record.createdBy === 'genie' && (
                              <Badge className="bg-gradient-to-r from-purple-500 to-violet-600 text-white text-xs">
                                <GiMagicLamp className="h-3 w-3 mr-1" />
                                Genie
                              </Badge>
                            )}
                          </div>
                        </div>

                        <p className="text-sm text-gray-600 mb-3">{record.description}</p>

                        {/* 食材タグ */}
                        <div className="mb-3">
                          <div className="flex flex-wrap gap-1">
                            {record.ingredients.slice(0, 3).map((ingredient, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {ingredient}
                              </Badge>
                            ))}
                            {record.ingredients.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{record.ingredients.length - 3}
                              </Badge>
                            )}
                          </div>
                        </div>

                        {/* 栄養情報 */}
                        {record.nutrition && (
                          <div className="mb-3 p-3 bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg border border-orange-200">
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <div>カロリー: {record.nutrition.calories}kcal</div>
                              <div>タンパク質: {record.nutrition.protein}g</div>
                              <div>炭水化物: {record.nutrition.carbs}g</div>
                              <div>脂質: {record.nutrition.fat}g</div>
                            </div>
                          </div>
                        )}

                        {/* アレルゲン警告 */}
                        {record.allergens && record.allergens.length > 0 && (
                          <div className="mb-3 p-2 bg-red-50 rounded-lg border border-red-200">
                            <div className="flex items-center gap-1 text-xs text-red-700">
                              <span>⚠️ アレルゲン:</span>
                              <span>{record.allergens.join(', ')}</span>
                            </div>
                          </div>
                        )}

                        {/* 反応メモ */}
                        {record.notes && (
                          <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <p className="text-xs text-blue-700">{record.notes}</p>
                          </div>
                        )}

                        {/* アクションボタン */}
                        <div className="flex gap-2 mt-4">
                          <Button size="sm" variant="outline" className="flex-1 border-orange-300 text-orange-700 hover:bg-orange-50">
                            <Edit className="h-3 w-3 mr-1" />
                            編集
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* カレンダービュー（スケジュールページと同様） */}
              {viewMode === 'calendar' && (
                <div className="space-y-4">
                  {/* カレンダーヘッダー */}
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg border border-orange-200">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigateMonth('prev')}
                      className="text-orange-700 hover:bg-orange-100"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    
                    <h3 className="text-lg font-semibold text-orange-800">
                      {currentDate.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long' })}
                    </h3>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigateMonth('next')}
                      className="text-orange-700 hover:bg-orange-100"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* カレンダーコンポーネント */}
                  <div className="bg-white rounded-lg border border-orange-200 p-4">
                    <div className="text-center py-8">
                      <CalendarIcon className="h-16 w-16 mx-auto text-orange-300 mb-4" />
                      <h3 className="text-lg font-medium text-gray-700 mb-2">カレンダービュー</h3>
                      <p className="text-gray-500 mb-4">選択した日付の食事記録を表示</p>
                      <p className="text-sm text-orange-600">
                        {selectedDate ? `選択日: ${selectedDate.toLocaleDateString('ja-JP')}` : '日付を選択してください'}
                      </p>
                      
                      {/* 簡易的な日付選択 */}
                      <div className="mt-4 grid grid-cols-7 gap-2 max-w-md mx-auto">
                        {Array.from({length: 7}, (_, i) => {
                          const date = new Date()
                          date.setDate(date.getDate() - 3 + i)
                          const isToday = date.toDateString() === new Date().toDateString()
                          const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString()
                          
                          return (
                            <button
                              key={i}
                              onClick={() => setSelectedDate(date)}
                              className={`p-2 text-xs rounded-lg border transition-colors ${
                                isSelected 
                                  ? 'bg-orange-500 text-white border-orange-500' 
                                  : isToday 
                                  ? 'bg-orange-100 text-orange-700 border-orange-200'
                                  : 'bg-white text-gray-600 border-gray-200 hover:bg-orange-50'
                              }`}
                            >
                              <div className="font-medium">{date.getDate()}</div>
                              <div className="text-xs opacity-75">
                                {date.toLocaleDateString('ja-JP', { weekday: 'short' })}
                              </div>
                            </button>
                          )
                        })}
                      </div>
                      
                      {/* 選択した日の食事記録 */}
                      {selectedDate && (
                        <div className="mt-6">
                          <h4 className="font-medium text-gray-800 mb-3">
                            {selectedDate.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' })}の食事記録
                          </h4>
                          <div className="space-y-2">
                            {getRecordsByType(selectedTab)
                              .filter(record => record.date === selectedDate.toISOString().split('T')[0])
                              .map(record => (
                                <div key={record.id} className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg border border-orange-200">
                                  <div className={`h-8 w-8 rounded-full ${getTypeColor(record.type)} flex items-center justify-center text-white`}>
                                    {getTypeIcon(record.type)}
                                  </div>
                                  <div className="flex-1 text-left">
                                    <div className="font-medium text-gray-800">{record.title}</div>
                                    <div className="text-sm text-gray-500">{record.time}</div>
                                  </div>
                                  {getReactionIcon(record.reaction)}
                                </div>
                              ))}
                            {getRecordsByType(selectedTab)
                              .filter(record => record.date === selectedDate.toISOString().split('T')[0])
                              .length === 0 && (
                              <p className="text-gray-500 text-sm">この日の食事記録はありません</p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* 空の状態 */}
              {getRecordsByType(selectedTab).length === 0 && (
                <div className="text-center py-12">
                  <div className="mb-4">
                    <FaUtensils className="h-16 w-16 mx-auto text-gray-300" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-700 mb-2">食事記録がありません</h3>
                  <p className="text-gray-500 mb-4">最初の食事記録を作成しましょう</p>
                  <div className="flex gap-3 justify-center">
                    <Button className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white">
                      <Plus className="h-4 w-4 mr-2" />
                      食事記録を作成
                    </Button>
                    <Link href="/chat">
                      <Button variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50">
                        <Sparkles className="h-4 w-4 mr-2" />
                        Genieに相談
                      </Button>
                    </Link>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AIチャット連携カード */}
          <Card className="shadow-xl border-0 bg-gradient-to-br from-orange-50 to-amber-50">
            <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Sparkles className="h-6 w-6" />
                Genieとの食事管理連携
              </CardTitle>
              <CardDescription className="text-orange-100">
                写真を送るだけで、Genieが栄養分析と成長に最適なメニューを提案します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="bg-white/60 p-4 rounded-lg border border-orange-200">
                <div className="flex items-start gap-3 mb-4">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg">
                    <GiMagicLamp className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-orange-800 font-medium mb-2">
                      🍽️ Genieができること：
                    </p>
                    <ul className="text-sm text-orange-700 space-y-1">
                      <li>• 食事写真から自動で栄養成分を分析・記録</li>
                      <li>• 月齢・年齢に応じた最適な食材とレシピを提案</li>
                      <li>• アレルギー情報を考慮した安全なメニュー作成</li>
                      <li>• 不足しがちな栄養素を補うサプリメント提案</li>
                      <li>• 食べる反応から好き嫌いパターンを学習・改善</li>
                    </ul>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Link href="/chat" className="flex-1">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white shadow-lg">
                      <FaUtensils className="h-4 w-4 mr-2" />
                      Genieに食事相談
                    </Button>
                  </Link>
                  <Link href="/schedule" className="flex-1">
                    <Button 
                      variant="outline"
                      className="w-full border-orange-300 text-orange-700 hover:bg-orange-50"
                    >
                      <CalendarIcon className="h-4 w-4 mr-2" />
                      予定と連携
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI栄養分析の説明 */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-full border border-orange-200">
              <GiMagicLamp className="h-4 w-4 text-orange-600" />
              <span className="text-sm text-orange-700 font-medium">Genieが24時間、栄養バランスと成長をサポートします</span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}