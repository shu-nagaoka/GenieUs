'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
  Award,
  Plus,
  Edit,
  Grid3X3,
  List,
  LayoutGrid,
  Clock,
} from 'lucide-react'
import { MdChildCare, MdPhotoCamera, MdTimeline } from 'react-icons/md'
import { FaChild, FaCamera, FaChartLine, FaHeart } from 'react-icons/fa'
import { GiMagicLamp, GiBabyFace, GiBodyHeight } from 'react-icons/gi'
import Link from 'next/link'
import {
  getGrowthRecords,
  GrowthRecord as ApiGrowthRecord,
  getChildrenForGrowthRecords,
  ChildInfo,
} from '@/libs/api/growth-records'
import { CreateGrowthRecordModal } from '@/components/features/growth/create-growth-record-modal'
import { EditGrowthRecordModal } from '@/components/features/growth/edit-growth-record-modal'

// バックエンドAPIから取得したデータを表示用に変換するインターフェース
interface GrowthRecord extends Omit<ApiGrowthRecord, 'user_id' | 'created_at' | 'updated_at'> {
  childName: string
  ageInMonths: number
  imageUrl?: string
  detectedBy: 'genie' | 'parent'
  developmentStage?: string
}

// EditGrowthRecordModalが期待する形式
interface EditableGrowthRecord {
  id: string
  child_id?: string
  child_name: string
  date: string
  age_in_months: number
  type:
    | 'body_growth'
    | 'language_growth'
    | 'skills'
    | 'social_skills'
    | 'hobbies'
    | 'life_skills'
    | 'physical'
    | 'emotional'
    | 'cognitive'
    | 'milestone'
    | 'photo'
  category:
    | 'height'
    | 'weight'
    | 'speech'
    | 'smile'
    | 'movement'
    | 'expression'
    | 'achievement'
    | 'first_words'
    | 'vocabulary'
    | 'colors'
    | 'numbers'
    | 'puzzle'
    | 'drawing'
    | 'playing_together'
    | 'helping'
    | 'sharing'
    | 'kindness'
    | 'piano'
    | 'swimming'
    | 'dancing'
    | 'sports'
    | 'toilet'
    | 'brushing'
    | 'dressing'
    | 'cleaning'
  title: string
  description: string
  value?: string | number
  unit?: string
  image_url?: string
  detected_by: 'genie' | 'parent'
  confidence?: number
  emotions?: string[]
  development_stage?: string
}

type ViewMode = 'detailed' | 'compact'

export default function GrowthTrackingPage() {
  const [selectedChild, setSelectedChild] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [viewMode, setViewMode] = useState<ViewMode>('detailed')
  const [growthRecords, setGrowthRecords] = useState<GrowthRecord[]>([])
  const [children, setChildren] = useState<ChildInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<EditableGrowthRecord | null>(null)

  // APIから成長記録データと子ども情報を取得
  const loadData = async () => {
    try {
      setLoading(true)

      // 並行して子ども情報と成長記録を取得
      const [childrenResult, recordsResult] = await Promise.all([
        getChildrenForGrowthRecords(),
        getGrowthRecords({ user_id: 'frontend_user' }),
      ])

      // 子ども情報を設定
      if (childrenResult.success && childrenResult.data) {
        setChildren(childrenResult.data)
      }

      // 成長記録を設定
      if (recordsResult.success && recordsResult.data) {
        // APIデータを表示用に変換
        const convertedRecords: GrowthRecord[] = recordsResult.data.map(apiRecord => ({
          id: apiRecord.id,
          childName: apiRecord.child_name,
          date: apiRecord.date,
          ageInMonths: apiRecord.age_in_months,
          type: apiRecord.type,
          category: apiRecord.category,
          title: apiRecord.title,
          description: apiRecord.description,
          value: apiRecord.value,
          unit: apiRecord.unit,
          imageUrl: apiRecord.image_url,
          detectedBy: apiRecord.detected_by,
          confidence: apiRecord.confidence,
          emotions: apiRecord.emotions,
          developmentStage: apiRecord.development_stage,
        }))
        setGrowthRecords(convertedRecords)
      } else {
        console.error('成長記録の取得に失敗しました:', recordsResult.message)
      }
    } catch (error) {
      console.error('データ読み込みエラー:', error)
    } finally {
      setLoading(false)
    }
  }

  // 初回ロード
  useEffect(() => {
    loadData()
  }, [])

  const getFilteredRecords = () => {
    let filtered = growthRecords.filter(
      record =>
        selectedChild === 'all' ||
        record.childName === children.find(c => c.child_id === selectedChild)?.name
    )

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(
        record => record.type === selectedCategory || record.category === selectedCategory
      )
    }

    return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  // 親しみやすいカテゴリ名マッピング
  const categoryLabels = {
    body_growth: 'からだの成長',
    language_growth: 'ことばの成長',
    skills: 'できること',
    social_skills: 'お友達との関わり',
    hobbies: '習い事・特技',
    life_skills: '生活スキル',
  }

  const detailCategoryLabels = {
    height: '身長・体重',
    weight: '身長・体重',
    speech: 'おしゃべり',
    smile: '表情・感情',
    movement: '運動・歩行',
    expression: '感情表現',
    achievement: '達成・成功体験',
    social: 'お友達と遊ぶ',
    helping: 'お手伝い',
    rule_following: 'ルールを守る',
    piano: 'ピアノ',
    swimming: '水泳',
    drawing: 'お絵描き',
    dancing: 'ダンス',
    toilet: 'トイレ',
    brushing: '歯磨き',
    dressing: 'お着替え',
    cleaning: 'お片付け',
  }

  const getRecordIcon = (category: string) => {
    switch (category) {
      case 'height':
      case 'weight':
        return <Ruler className="h-5 w-5" />
      case 'speech':
        return <MessageCircle className="h-5 w-5" />
      case 'smile':
      case 'expression':
        return <Smile className="h-5 w-5" />
      case 'movement':
        return <TrendingUp className="h-5 w-5" />
      case 'achievement':
        return <Award className="h-5 w-5" />
      case 'social':
      case 'helping':
      case 'rule_following':
        return <Heart className="h-5 w-5" />
      case 'piano':
      case 'swimming':
      case 'drawing':
      case 'dancing':
        return <Star className="h-5 w-5" />
      case 'toilet':
      case 'brushing':
      case 'dressing':
      case 'cleaning':
        return <Target className="h-5 w-5" />
      default:
        return <Star className="h-5 w-5" />
    }
  }

  const getRecordColor = (type: string) => {
    switch (type) {
      case 'body_growth':
        return 'from-blue-500 to-blue-600'
      case 'language_growth':
        return 'from-green-500 to-green-600'
      case 'skills':
        return 'from-purple-500 to-purple-600'
      case 'social_skills':
        return 'from-pink-500 to-pink-600'
      case 'hobbies':
        return 'from-amber-500 to-amber-600'
      case 'life_skills':
        return 'from-teal-500 to-teal-600'
      // 従来のタイプも保持（後方互換性）
      case 'physical':
        return 'from-blue-500 to-blue-600'
      case 'emotional':
        return 'from-teal-500 to-teal-600'
      case 'cognitive':
        return 'from-purple-500 to-purple-600'
      case 'milestone':
        return 'from-green-500 to-green-600'
      case 'photo':
        return 'from-amber-500 to-amber-600'
      default:
        return 'from-gray-500 to-gray-600'
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const handleEditRecord = (record: GrowthRecord) => {
    // 対応する child_id を取得
    const matchedChild = children.find(child => child.name === record.childName)

    // GrowthRecord を EditableGrowthRecord に変換
    const editableRecord: EditableGrowthRecord = {
      id: record.id,
      child_id: matchedChild?.child_id,
      child_name: record.childName,
      date: record.date,
      age_in_months: record.ageInMonths,
      type: record.type,
      category: record.category,
      title: record.title,
      description: record.description,
      value: record.value,
      unit: record.unit,
      image_url: record.imageUrl,
      detected_by: record.detectedBy,
      confidence: record.confidence,
      emotions: record.emotions,
      development_stage: record.developmentStage,
    }
    setSelectedRecord(editableRecord)
    setShowEditModal(true)
  }

  const handleRecordUpdated = () => {
    loadData()
  }

  const handleRecordDeleted = () => {
    loadData()
  }

  const handleRecordCreated = () => {
    loadData()
  }

  const getStatsForChild = (childId: string) => {
    let records = growthRecords
    if (childId !== 'all') {
      const childName = children.find(c => c.child_id === childId)?.name || ''
      records = growthRecords.filter(r => r.childName === childName)
    }

    // 日付計算用
    const now = new Date()
    const thisMonth = records.filter(r => {
      const recordDate = new Date(r.date)
      return (
        recordDate.getMonth() === now.getMonth() && recordDate.getFullYear() === now.getFullYear()
      )
    }).length

    // 連続記録日数計算
    const sortedRecords = records.sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    )
    let consecutiveDays = 0
    const today = new Date()

    for (let i = 0; i < sortedRecords.length; i++) {
      const recordDate = new Date(sortedRecords[i].date)
      const diffDays = Math.floor((today.getTime() - recordDate.getTime()) / (1000 * 60 * 60 * 24))

      if (diffDays === consecutiveDays) {
        consecutiveDays++
      } else {
        break
      }
    }

    // 最新記録からの日数
    const daysSinceLastRecord =
      records.length > 0
        ? Math.floor(
            (now.getTime() - new Date(sortedRecords[0].date).getTime()) / (1000 * 60 * 60 * 24)
          )
        : 0

    // AI検出率
    const aiDetectedCount = records.filter(r => r.detectedBy === 'genie').length
    const aiDetectionRate =
      records.length > 0 ? Math.round((aiDetectedCount / records.length) * 100) : 0

    return {
      totalRecords: records.length,
      photosCount: records.filter(r => r.imageUrl).length,
      milestonesCount: records.filter(r => r.type === 'milestone' || r.type === 'skills').length,
      thisMonthCount: thisMonth,
      consecutiveDays: consecutiveDays,
      daysSinceLastRecord: daysSinceLastRecord,
      aiDetectionRate: aiDetectionRate,
    }
  }

  const selectedChildStats = getStatsForChild(selectedChild)

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-slate-50 to-teal-50">
        {/* ページヘッダー */}
        <div className="border-b border-blue-100 bg-white/80 backdrop-blur-sm">
          <div className="mx-auto max-w-6xl px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-teal-600 shadow-lg">
                  <MdTimeline className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">お子さんの成長記録</h1>
                  <p className="text-gray-600">
                    からだ・ことば・できることを記録して成長を見守ります
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-gradient-to-r from-blue-500 to-teal-500 text-white shadow-lg hover:from-blue-600 hover:to-teal-600"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  記録を追加
                </Button>
                <Link href="/chat">
                  <Button
                    variant="outline"
                    className="border-blue-300 text-blue-700 hover:bg-blue-50"
                  >
                    <Camera className="mr-2 h-4 w-4" />
                    Genieで記録
                  </Button>
                </Link>
                <div className="hidden items-center gap-2 rounded-lg border border-blue-200 bg-white/60 px-3 py-1.5 backdrop-blur-sm md:flex">
                  <GiMagicLamp className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-700">AI自動検出</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-6xl space-y-8 p-6">
          {/* 成長サマリーカード */}
          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
            <Card className="border-0 bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-100">記録総数</p>
                    <p className="mt-1 text-2xl font-bold">{selectedChildStats.totalRecords}件</p>
                    <p className="text-xs text-blue-200">継続観察中</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-100">写真記録</p>
                    <p className="mt-1 text-2xl font-bold">{selectedChildStats.photosCount}枚</p>
                    <p className="text-xs text-blue-200">AI解析済み</p>
                  </div>
                  <Camera className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-gradient-to-br from-slate-500 to-slate-600 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-100">できること</p>
                    <p className="mt-1 text-2xl font-bold">
                      {selectedChildStats.milestonesCount}個
                    </p>
                    <p className="text-xs text-slate-200">新しくできた</p>
                  </div>
                  <Award className="h-8 w-8 text-slate-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-gradient-to-br from-slate-400 to-slate-500 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-100">今月の記録</p>
                    <p className="mt-1 text-2xl font-bold">{selectedChildStats.thisMonthCount}件</p>
                    <p className="text-xs text-slate-200">継続記録中</p>
                  </div>
                  <Calendar className="h-8 w-8 text-slate-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 子ども選択とフィルター */}
          <Card className="min-h-[140px] border-0 bg-white/80 shadow-xl backdrop-blur-sm">
            <CardHeader className="rounded-t-lg bg-gradient-to-r from-blue-500 to-teal-600 pb-4 text-white">
              <CardTitle className="flex items-center gap-3 text-lg">
                <Baby className="h-5 w-5" />
                フィルター
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    お子さんを選択
                  </label>
                  <Select value={selectedChild} onValueChange={setSelectedChild}>
                    <SelectTrigger className="border-blue-200 focus:border-blue-400">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">
                        <div className="flex items-center gap-2">
                          <Baby className="h-4 w-4" />
                          <span>すべてのお子さん</span>
                        </div>
                      </SelectItem>
                      {children.map(child => (
                        <SelectItem key={child.child_id} value={child.child_id}>
                          <div className="flex items-center gap-2">
                            <Baby className="h-4 w-4" />
                            <span>
                              {child.name} ({child.age}歳)
                            </span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    記録カテゴリ
                  </label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="border-blue-200 focus:border-blue-400">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">
                        <div className="flex items-center gap-2">
                          <Star className="h-4 w-4" />
                          <span>すべて</span>
                        </div>
                      </SelectItem>
                      {Object.entries(categoryLabels).map(([key, label]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex items-center gap-2">
                            {key === 'body_growth' && <Ruler className="h-4 w-4" />}
                            {key === 'language_growth' && <MessageCircle className="h-4 w-4" />}
                            {key === 'skills' && <Star className="h-4 w-4" />}
                            {key === 'social_skills' && <Heart className="h-4 w-4" />}
                            {key === 'hobbies' && <Award className="h-4 w-4" />}
                            {key === 'life_skills' && <Target className="h-4 w-4" />}
                            <span>{label}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 成長タイムライン */}
          <Card className="min-h-[400px] border-0 bg-white/80 shadow-xl backdrop-blur-sm">
            <CardHeader className="rounded-t-lg bg-gradient-to-r from-slate-500 to-slate-600 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-3">
                    <MdTimeline className="h-6 w-6" />
                    成長タイムライン
                  </CardTitle>
                  <CardDescription className="text-slate-100">
                    時系列で見るお子さんの成長記録
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2 rounded-lg bg-white/20 p-1">
                  <Button
                    size="sm"
                    variant={viewMode === 'detailed' ? 'default' : 'ghost'}
                    onClick={() => setViewMode('detailed')}
                    className={`h-8 px-3 ${viewMode === 'detailed' ? 'bg-white text-slate-600' : 'text-white hover:bg-white/20'}`}
                  >
                    <LayoutGrid className="mr-1 h-4 w-4" />
                    詳細
                  </Button>
                  <Button
                    size="sm"
                    variant={viewMode === 'compact' ? 'default' : 'ghost'}
                    onClick={() => setViewMode('compact')}
                    className={`h-8 px-3 ${viewMode === 'compact' ? 'bg-white text-slate-600' : 'text-white hover:bg-white/20'}`}
                  >
                    <List className="mr-1 h-4 w-4" />
                    一覧
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="relative">
                {/* タイムライン線（詳細表示時のみ） */}
                {viewMode === 'detailed' && (
                  <div className="absolute bottom-0 left-8 top-0 w-0.5 bg-gradient-to-b from-blue-300 to-teal-300"></div>
                )}

                {/* ローディング表示 */}
                {loading && (
                  <div className="py-12 text-center">
                    <div className="inline-flex items-center gap-2">
                      <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"></div>
                      <span className="text-gray-600">成長記録を読み込み中...</span>
                    </div>
                    {/* スケルトンローダー */}
                    <div className="mt-8 space-y-6">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="flex items-start gap-6">
                          <div className="h-16 w-16 animate-pulse rounded-full bg-gray-200"></div>
                          <div className="flex-1">
                            <div className="mb-2 h-4 animate-pulse rounded bg-gray-200"></div>
                            <div className="mb-2 h-3 w-3/4 animate-pulse rounded bg-gray-100"></div>
                            <div className="h-3 w-1/2 animate-pulse rounded bg-gray-100"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 記録が見つからない場合 */}
                {!loading && getFilteredRecords().length === 0 && (
                  <div className="py-12 text-center">
                    <div className="mb-4">
                      <TrendingUp className="mx-auto h-16 w-16 text-gray-300" />
                    </div>
                    <h3 className="mb-2 text-lg font-medium text-gray-700">
                      {growthRecords.length === 0
                        ? '成長記録がありません'
                        : '成長記録が見つかりません'}
                    </h3>
                    <p className="mb-4 text-gray-500">
                      {growthRecords.length === 0
                        ? '最初の成長記録を作成しましょう'
                        : 'フィルター条件を変更するか、新しい記録を作成してください'}
                    </p>
                    <div className="flex justify-center gap-3">
                      <Button
                        onClick={() => setShowCreateModal(true)}
                        className="bg-gradient-to-r from-blue-500 to-teal-500 text-white hover:from-blue-600 hover:to-teal-600"
                      >
                        <Plus className="mr-2 h-4 w-4" />
                        記録を作成
                      </Button>
                      <Link href="/chat">
                        <Button
                          variant="outline"
                          className="border-blue-300 text-blue-700 hover:bg-blue-50"
                        >
                          <Camera className="mr-2 h-4 w-4" />
                          Genieで記録
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}

                {/* 成長記録タイムライン */}
                {!loading && getFilteredRecords().length > 0 && (
                  <>
                    {viewMode === 'detailed' ? (
                      // 詳細表示
                      <div className="space-y-8">
                        {getFilteredRecords().map((record, index) => (
                          <div key={record.id} className="relative flex items-start gap-6">
                            {/* タイムライン点 */}
                            <div
                              className={`relative z-10 h-16 w-16 flex-shrink-0 rounded-full bg-gradient-to-br ${getRecordColor(record.type)} flex items-center justify-center text-white shadow-lg`}
                            >
                              {getRecordIcon(record.category)}
                              <div className="absolute -right-1 -top-1">
                                {record.detectedBy === 'genie' && (
                                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-purple-500">
                                    <GiMagicLamp className="h-3 w-3 text-white" />
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* 記録カード */}
                            <Card className="flex-1 border-0 bg-gradient-to-br from-white to-gray-50 shadow-lg transition-all duration-300 hover:shadow-xl">
                              <CardContent className="p-6">
                                <div className="mb-4 flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="mb-2 flex items-center gap-3">
                                      <h4 className="text-lg font-bold text-gray-800">
                                        {record.title}
                                      </h4>
                                      <Badge
                                        className={`bg-gradient-to-r ${getRecordColor(record.type)} text-white`}
                                      >
                                        {categoryLabels[record.type] ||
                                          detailCategoryLabels[record.category] ||
                                          (record.type === 'physical'
                                            ? 'からだの成長'
                                            : record.type === 'emotional'
                                              ? 'お友達との関わり'
                                              : record.type === 'cognitive'
                                                ? 'できること'
                                                : record.type === 'milestone'
                                                  ? 'できること'
                                                  : '写真')}
                                      </Badge>
                                      {record.confidence && (
                                        <Badge variant="outline" className="text-xs">
                                          信頼度 {Math.round(record.confidence * 100)}%
                                        </Badge>
                                      )}
                                    </div>

                                    <div className="mb-3 grid grid-cols-1 gap-4 text-sm text-gray-600 md:grid-cols-3">
                                      <div className="flex items-center gap-2">
                                        <Calendar className="h-4 w-4 text-blue-600" />
                                        <span>{formatDate(record.date)}</span>
                                      </div>
                                      <div className="flex items-center gap-2">
                                        <Baby className="h-4 w-4 text-blue-600" />
                                        <span>{record.ageInMonths}ヶ月</span>
                                      </div>
                                      {record.value && (
                                        <div className="flex items-center gap-2">
                                          <BarChart3 className="h-4 w-4 text-blue-600" />
                                          <span>
                                            {record.value}
                                            {record.unit}
                                          </span>
                                        </div>
                                      )}
                                    </div>

                                    <p className="mb-3 text-gray-700">{record.description}</p>

                                    {record.developmentStage && (
                                      <div className="mb-3">
                                        <Badge className="bg-green-100 text-green-700">
                                          {record.developmentStage}
                                        </Badge>
                                      </div>
                                    )}

                                    {record.emotions && record.emotions.length > 0 && (
                                      <div className="mb-3 flex flex-wrap gap-2">
                                        {record.emotions.map((emotion, idx) => (
                                          <Badge key={idx} variant="outline" className="text-xs">
                                            {emotion}
                                          </Badge>
                                        ))}
                                      </div>
                                    )}

                                    {/* 編集ボタン */}
                                    <div className="mt-4 flex gap-2">
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleEditRecord(record)}
                                        className="border-blue-300 text-blue-700 hover:bg-blue-50"
                                      >
                                        <Edit className="mr-1 h-4 w-4" />
                                        編集
                                      </Button>
                                    </div>
                                  </div>

                                  {record.imageUrl && (
                                    <div className="ml-4 flex-shrink-0">
                                      <div className="h-24 w-32 overflow-hidden rounded-lg border border-blue-200">
                                        <img
                                          src={
                                            record.imageUrl.startsWith('/api/')
                                              ? `http://localhost:8000${record.imageUrl}`
                                              : record.imageUrl
                                          }
                                          alt={record.title}
                                          className="h-full w-full object-cover"
                                        />
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          </div>
                        ))}
                      </div>
                    ) : (
                      // コンパクト表示
                      <div className="space-y-3">
                        {getFilteredRecords().map((record, index) => (
                          <div
                            key={record.id}
                            className="rounded-lg border border-gray-200 bg-white transition-colors hover:border-blue-300"
                          >
                            <div className="flex items-center gap-4 p-4">
                              {/* アイコン */}
                              <div
                                className={`h-10 w-10 flex-shrink-0 rounded-full bg-gradient-to-br ${getRecordColor(record.type)} flex items-center justify-center text-white`}
                              >
                                {getRecordIcon(record.category)}
                              </div>

                              {/* コンテンツ */}
                              <div className="min-w-0 flex-1">
                                <div className="mb-1 flex items-center gap-2">
                                  <h4 className="truncate font-semibold text-gray-800">
                                    {record.title}
                                  </h4>
                                  <Badge
                                    className={`bg-gradient-to-r text-xs ${getRecordColor(record.type)} text-white`}
                                  >
                                    {categoryLabels[record.type] ||
                                      detailCategoryLabels[record.category] ||
                                      (record.type === 'physical'
                                        ? 'からだの成長'
                                        : record.type === 'emotional'
                                          ? 'お友達との関わり'
                                          : record.type === 'cognitive'
                                            ? 'できること'
                                            : record.type === 'milestone'
                                              ? 'できること'
                                              : '写真')}
                                  </Badge>
                                </div>
                                <div className="flex items-center gap-4 text-sm text-gray-600">
                                  <span className="flex items-center gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {formatDate(record.date)}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Baby className="h-3 w-3" />
                                    {record.childName}
                                  </span>
                                  <span>{record.ageInMonths}ヶ月</span>
                                  {record.detectedBy === 'genie' && (
                                    <Badge variant="outline" className="text-xs">
                                      <GiMagicLamp className="mr-1 h-3 w-3" />
                                      AI検出
                                    </Badge>
                                  )}
                                </div>
                              </div>

                              {/* アクションボタン */}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleEditRecord(record)}
                                className="flex-shrink-0 border-blue-300 text-blue-700 hover:bg-blue-50"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 成長記録作成モーダル */}
      <CreateGrowthRecordModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
        onRecordCreated={handleRecordCreated}
      />

      {/* 成長記録編集モーダル */}
      <EditGrowthRecordModal
        open={showEditModal}
        onOpenChange={setShowEditModal}
        record={selectedRecord}
        onRecordUpdated={handleRecordUpdated}
        onRecordDeleted={handleRecordDeleted}
      />
    </AppLayout>
  )
}
