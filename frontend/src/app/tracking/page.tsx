'use client'

import { useState, useEffect } from 'react'
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
  Award,
  Plus,
  Edit
} from 'lucide-react'
import { MdChildCare, MdPhotoCamera, MdTimeline } from 'react-icons/md'
import { FaChild, FaCamera, FaChartLine, FaHeart } from 'react-icons/fa'
import { GiMagicLamp, GiBabyFace, GiBodyHeight } from 'react-icons/gi'
import Link from 'next/link'
import { getGrowthRecords, GrowthRecord as ApiGrowthRecord, getChildrenForGrowthRecords, ChildInfo } from '@/lib/api/growth-records'
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
  type: 'body_growth' | 'language_growth' | 'skills' | 'social_skills' | 'hobbies' | 'life_skills' | 'physical' | 'emotional' | 'cognitive' | 'milestone' | 'photo'
  category: 'height' | 'weight' | 'speech' | 'smile' | 'movement' | 'expression' | 'achievement' | 'first_words' | 'vocabulary' | 'colors' | 'numbers' | 'puzzle' | 'drawing' | 'playing_together' | 'helping' | 'sharing' | 'kindness' | 'piano' | 'swimming' | 'dancing' | 'sports' | 'toilet' | 'brushing' | 'dressing' | 'cleaning'
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

export default function GrowthTrackingPage() {
  const [selectedChild, setSelectedChild] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
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
        getGrowthRecords({ user_id: 'frontend_user' })
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
          developmentStage: apiRecord.development_stage
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
    let filtered = growthRecords.filter(record => 
      selectedChild === 'all' || record.childName === children.find(c => c.child_id === selectedChild)?.name
    )
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(record => record.type === selectedCategory || record.category === selectedCategory)
    }
    
    return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  // 親しみやすいカテゴリ名マッピング
  const categoryLabels = {
    'body_growth': 'からだの成長',
    'language_growth': 'ことばの成長', 
    'skills': 'できること',
    'social_skills': 'お友達との関わり',
    'hobbies': '習い事・特技',
    'life_skills': '生活スキル'
  }

  const detailCategoryLabels = {
    'height': '身長・体重',
    'weight': '身長・体重',
    'speech': 'おしゃべり',
    'smile': '表情・感情',
    'movement': '運動・歩行',
    'expression': '感情表現',
    'achievement': '達成・成功体験',
    'social': 'お友達と遊ぶ',
    'helping': 'お手伝い',
    'rule_following': 'ルールを守る',
    'piano': 'ピアノ',
    'swimming': '水泳',
    'drawing': 'お絵描き',
    'dancing': 'ダンス',
    'toilet': 'トイレ',
    'brushing': '歯磨き',
    'dressing': 'お着替え',
    'cleaning': 'お片付け'
  }

  const getRecordIcon = (category: string) => {
    switch (category) {
      case 'height':
      case 'weight': return <Ruler className="h-5 w-5" />
      case 'speech': return <MessageCircle className="h-5 w-5" />
      case 'smile':
      case 'expression': return <Smile className="h-5 w-5" />
      case 'movement': return <TrendingUp className="h-5 w-5" />
      case 'achievement': return <Award className="h-5 w-5" />
      case 'social':
      case 'helping':
      case 'rule_following': return <Heart className="h-5 w-5" />
      case 'piano':
      case 'swimming':
      case 'drawing':
      case 'dancing': return <Star className="h-5 w-5" />
      case 'toilet':
      case 'brushing':
      case 'dressing':
      case 'cleaning': return <Target className="h-5 w-5" />
      default: return <Star className="h-5 w-5" />
    }
  }

  const getRecordColor = (type: string) => {
    switch (type) {
      case 'body_growth': return 'from-blue-500 to-blue-600'
      case 'language_growth': return 'from-green-500 to-green-600'
      case 'skills': return 'from-purple-500 to-purple-600'
      case 'social_skills': return 'from-pink-500 to-pink-600'
      case 'hobbies': return 'from-amber-500 to-amber-600'
      case 'life_skills': return 'from-teal-500 to-teal-600'
      // 従来のタイプも保持（後方互換性）
      case 'physical': return 'from-blue-500 to-blue-600'
      case 'emotional': return 'from-teal-500 to-teal-600'
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
      development_stage: record.developmentStage
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
    
    return {
      totalRecords: records.length,
      photosCount: records.filter(r => r.imageUrl).length,
      milestonesCount: records.filter(r => r.type === 'milestone' || r.type === 'skills').length,
      avgConfidence: records.length > 0 ? Math.round(records.reduce((acc, r) => acc + (r.confidence || 95), 0) / records.length) : 0
    }
  }

  const selectedChildStats = getStatsForChild(selectedChild)

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-slate-50 to-teal-50">
        {/* ページヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-blue-100">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-teal-600 flex items-center justify-center shadow-lg">
                  <MdTimeline className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">お子さんの成長記録</h1>
                  <p className="text-gray-600">からだ・ことば・できることを記録して成長を見守ります</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className="bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white shadow-lg"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  記録を追加
                </Button>
                <Link href="/chat">
                  <Button variant="outline" className="border-blue-300 text-blue-700 hover:bg-blue-50">
                    <Camera className="h-4 w-4 mr-2" />
                    Genieで記録
                  </Button>
                </Link>
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-blue-200">
                  <GiMagicLamp className="h-4 w-4 text-blue-600" />
                  <span className="text-sm text-blue-700 font-medium">AI自動検出</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-6 space-y-8">
          {/* 成長サマリーカード */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-blue-600 to-blue-700 text-white border-0 shadow-xl">
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

            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">写真記録</p>
                    <p className="text-2xl font-bold mt-1">{selectedChildStats.photosCount}枚</p>
                    <p className="text-blue-200 text-xs">AI解析済み</p>
                  </div>
                  <Camera className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-500 to-slate-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-100 text-sm font-medium">できること</p>
                    <p className="text-2xl font-bold mt-1">{selectedChildStats.milestonesCount}個</p>
                    <p className="text-slate-200 text-xs">新しくできた</p>
                  </div>
                  <Award className="h-8 w-8 text-slate-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-sky-500 to-sky-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sky-100 text-sm font-medium">AI精度</p>
                    <p className="text-2xl font-bold mt-1">{selectedChildStats.avgConfidence}%</p>
                    <p className="text-sky-200 text-xs">検出信頼度</p>
                  </div>
                  <Target className="h-8 w-8 text-sky-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 子ども選択とフィルター */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-blue-500 to-teal-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Baby className="h-6 w-6" />
                成長記録フィルター
              </CardTitle>
              <CardDescription className="text-blue-100">
                お子さんと記録タイプを選択して成長を確認
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">お子さんを選択</label>
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
                            <span>{child.name} ({child.age}歳)</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">記録カテゴリ</label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="border-blue-200 focus:border-blue-400">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">すべて</SelectItem>
                      {Object.entries(categoryLabels).map(([key, label]) => (
                        <SelectItem key={key} value={key}>{label}</SelectItem>
                      ))}
                      {/* 詳細カテゴリも表示 */}
                      {Object.entries(detailCategoryLabels).map(([key, label]) => (
                        <SelectItem key={`detail_${key}`} value={key}>{label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 成長タイムライン */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-slate-500 to-slate-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <MdTimeline className="h-6 w-6" />
                成長タイムライン
              </CardTitle>
              <CardDescription className="text-slate-100">
                時系列で見るお子さんの成長記録
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="relative">
                {/* タイムライン線 */}
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-300 to-teal-300"></div>
                
                {/* ローディング表示 */}
                {loading && (
                  <div className="text-center py-12">
                    <div className="inline-flex items-center gap-2">
                      <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-gray-600">成長記録を読み込み中...</span>
                    </div>
                  </div>
                )}

                {/* 記録が見つからない場合 */}
                {!loading && getFilteredRecords().length === 0 && (
                  <div className="text-center py-12">
                    <div className="mb-4">
                      <TrendingUp className="h-16 w-16 mx-auto text-gray-300" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">
                      {growthRecords.length === 0 ? '成長記録がありません' : '成長記録が見つかりません'}
                    </h3>
                    <p className="text-gray-500 mb-4">
                      {growthRecords.length === 0 
                        ? '最初の成長記録を作成しましょう' 
                        : 'フィルター条件を変更するか、新しい記録を作成してください'
                      }
                    </p>
                    <div className="flex gap-3 justify-center">
                      <Button 
                        onClick={() => setShowCreateModal(true)}
                        className="bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white"
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        記録を作成
                      </Button>
                      <Link href="/chat">
                        <Button variant="outline" className="border-blue-300 text-blue-700 hover:bg-blue-50">
                          <Camera className="h-4 w-4 mr-2" />
                          Genieで記録
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}

                {/* 成長記録タイムライン */}
                {!loading && getFilteredRecords().length > 0 && (
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
                                    {categoryLabels[record.type] || 
                                     detailCategoryLabels[record.category] ||
                                     (record.type === 'physical' ? 'からだの成長' :
                                      record.type === 'emotional' ? 'お友達との関わり' :
                                      record.type === 'cognitive' ? 'できること' :
                                      record.type === 'milestone' ? 'できること' : '写真')}
                                  </Badge>
                                  {record.confidence && (
                                    <Badge variant="outline" className="text-xs">
                                      信頼度 {Math.round(record.confidence * 100)}%
                                    </Badge>
                                  )}
                                </div>
                                
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
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
                                
                                {/* 編集ボタン */}
                                <div className="mt-4 flex gap-2">
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleEditRecord(record)}
                                    className="border-blue-300 text-blue-700 hover:bg-blue-50"
                                  >
                                    <Edit className="h-4 w-4 mr-1" />
                                    編集
                                  </Button>
                                </div>
                              </div>
                              
                              {record.imageUrl && (
                                <div className="ml-4 flex-shrink-0">
                                  <div className="w-32 h-24 rounded-lg border border-blue-200 overflow-hidden">
                                    <img 
                                      src={record.imageUrl.startsWith('/api/') ? `http://localhost:8000${record.imageUrl}` : record.imageUrl}
                                      alt={record.title}
                                      className="w-full h-full object-cover"
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