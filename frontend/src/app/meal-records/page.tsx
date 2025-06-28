'use client'

import { useState, useMemo } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { AuthCheck } from '@/components/features/auth/auth-check'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  UtensilsIcon,
  Calendar,
  TrendingUp,
  Plus,
  Sparkles,
  Clock,
  BarChart3,
  Star,
  CheckCircle,
  Target,
  Eye,
  Edit,
  Trash2,
  Archive,
  Activity,
  LayoutGrid,
  List,
  Camera,
  Brain,
  Award,
} from 'lucide-react'
import { FaUtensils, FaAppleAlt, FaCarrot, FaFish } from 'react-icons/fa'
import Link from 'next/link'
import { useMealRecordsManager, useCreateMealRecord } from '@/hooks/useMealRecords'
import { usePrimaryChildId, useChildrenOptions } from '@/hooks/use-family-info'
import type { MealRecord, NutritionSummary } from '@/libs/api/meal-records'

type ViewMode = 'card' | 'table'
type MealType = 'all' | 'breakfast' | 'lunch' | 'dinner' | 'snack'

const mealTypeLabels = {
  breakfast: '朝食',
  lunch: '昼食',
  dinner: '夕食',
  snack: 'おやつ',
}

const detectionSourceLabels = {
  manual: '手動入力',
  image_ai: '画像AI',
  voice_ai: '音声AI',
}

// 削除：静的なDEFAULT_CHILD_IDは使用しない

export default function MealRecordsPage() {
  return (
    <AuthCheck>
      <MealRecordsPageContent />
    </AuthCheck>
  )
}

function MealRecordsPageContent() {
  const [viewMode, setViewMode] = useState<ViewMode>('card')
  const [selectedMealType, setSelectedMealType] = useState<MealType>('all')
  const [selectedRecord, setSelectedRecord] = useState<MealRecord | null>(null)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedChildId, setSelectedChildId] = useState<string>('')

  // 家族情報から子供情報を取得
  const { childId: primaryChildId, isLoading: familyLoading, error: familyError } = usePrimaryChildId()
  const { options: childrenOptions } = useChildrenOptions()
  
  // 選択された子供ID（デフォルトは最初の子供）
  const currentChildId = selectedChildId || primaryChildId || ''

  // 新しい記録作成用のフォーム状態
  const [newMealForm, setNewMealForm] = useState({
    child_id: '',
    meal_name: '',
    meal_type: 'breakfast' as const,
    detected_foods: '',
    notes: '',
  })

  // 編集用のフォーム状態
  const [editMealForm, setEditMealForm] = useState({
    child_id: '',
    meal_name: '',
    meal_type: 'breakfast' as const,
    detected_foods: '',
    notes: '',
  })

  // API hooks
  const {
    mealRecords,
    weeklySummary,
    isLoading,
    error,
    createMealRecord,
    updateMealRecord,
    deleteMealRecord,
    isCreating,
    isUpdating,
    isDeleting,
  } = useMealRecordsManager(currentChildId)

  // フィルタリング済みの食事記録
  const filteredMealRecords = useMemo(() => {
    if (selectedMealType === 'all') {
      return mealRecords
    }
    return mealRecords.filter(record => record.meal_type === selectedMealType)
  }, [mealRecords, selectedMealType])

  // デフォルトの栄養サマリー（APIデータがない場合）
  const nutritionSummary = weeklySummary || {
    total_meals: 0,
    total_calories: 0,
    avg_nutrition: { protein: 0, carbs: 0, fat: 0, fiber: 0 },
    meal_type_distribution: { breakfast: 0, lunch: 0, dinner: 0, snack: 0 },
    most_common_foods: [],
    nutrition_balance_score: 0,
  }

  // 安全なアクセス用のヘルパー
  const safeAvgNutrition = nutritionSummary?.avg_nutrition || { protein: 0, carbs: 0, fat: 0, fiber: 0 }

  const openDetailModal = (record: MealRecord) => {
    setSelectedRecord(record)
    setShowDetailModal(true)
  }

  const closeDetailModal = () => {
    setSelectedRecord(null)
    setShowDetailModal(false)
  }

  const handleCreateMealRecord = async () => {
    try {
      const foodArray = newMealForm.detected_foods
        .split(',')
        .map(food => food.trim())
        .filter(food => food.length > 0)

      await createMealRecord({
        child_id: newMealForm.child_id || currentChildId,
        meal_name: newMealForm.meal_name,
        meal_type: newMealForm.meal_type,
        detected_foods: foodArray.length > 0 ? foodArray : undefined,
        nutrition_info: {}, // デフォルト空オブジェクト
        detection_source: 'manual',
        notes: newMealForm.notes || undefined,
      })

      // フォームリセット
      setNewMealForm({
        child_id: '',
        meal_name: '',
        meal_type: 'breakfast',
        detected_foods: '',
        notes: '',
      })
      
      // モーダル閉じる
      setShowCreateModal(false)
    } catch (error) {
      console.error('食事記録の作成に失敗しました:', error)
      // エラー処理は既存のuseMealRecordsManagerで処理される
    }
  }

  const handleEditMealRecord = (record: MealRecord) => {
    setSelectedRecord(record)
    setEditMealForm({
      child_id: record.child_id,
      meal_name: record.meal_name,
      meal_type: record.meal_type,
      detected_foods: record.detected_foods.join(', '),
      notes: record.notes || '',
    })
    setShowDetailModal(false)
    setShowEditModal(true)
  }

  const handleUpdateMealRecord = async () => {
    if (!selectedRecord) return

    try {
      const foodArray = editMealForm.detected_foods
        .split(',')
        .map(food => food.trim())
        .filter(food => food.length > 0)

      await updateMealRecord({
        mealRecordId: selectedRecord.id,
        request: {
          meal_name: editMealForm.meal_name,
          meal_type: editMealForm.meal_type,
          detected_foods: foodArray.length > 0 ? foodArray : undefined,
          notes: editMealForm.notes || undefined,
        }
      })

      setShowEditModal(false)
      setSelectedRecord(null)
    } catch (error) {
      console.error('食事記録の更新に失敗しました:', error)
    }
  }

  const handleDeleteMealRecord = async (recordId: string) => {
    if (!confirm('この食事記録を削除しますか？')) return

    try {
      await deleteMealRecord(recordId)
      setShowDetailModal(false)
      setSelectedRecord(null)
    } catch (error) {
      console.error('食事記録の削除に失敗しました:', error)
    }
  }

  if (isLoading || familyLoading) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
          <div className="inline-flex items-center gap-2">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-orange-500 border-t-transparent"></div>
            <span className="text-gray-600">
              {familyLoading ? '家族情報を読み込み中...' : '食事記録を読み込み中...'}
            </span>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (error || familyError) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
          <Card className="border-red-200 bg-red-50 shadow-xl">
            <CardContent className="p-6 text-center">
              <div className="mb-4 flex justify-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                  <UtensilsIcon className="h-6 w-6 text-red-600" />
                </div>
              </div>
              <h2 className="mb-2 text-lg font-semibold text-red-800">
                {familyError ? '家族情報の読み込みに失敗しました' : '食事記録の読み込みに失敗しました'}
              </h2>
              <p className="mb-4 text-sm text-red-600">
                {(error || familyError)?.message || 'ネットワークエラーまたはサーバーエラーが発生しました'}
              </p>
              <Button 
                onClick={() => window.location.reload()} 
                className="bg-red-600 text-white hover:bg-red-700"
              >
                再読み込み
              </Button>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    )
  }

  // 家族情報が取得できているかチェック
  if (!currentChildId) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
          <Card className="border-amber-200 bg-amber-50 shadow-xl">
            <CardContent className="p-6 text-center">
              <div className="mb-4 flex justify-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-100">
                  <UtensilsIcon className="h-6 w-6 text-amber-600" />
                </div>
              </div>
              <h2 className="mb-2 text-lg font-semibold text-amber-800">お子様の情報が登録されていません</h2>
              <p className="mb-4 text-sm text-amber-600">
                食事記録を使用するには、まず家族情報でお子様を登録してください
              </p>
              <Link href="/family">
                <Button className="bg-amber-600 text-white hover:bg-amber-700">
                  家族情報を登録する
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
        {/* ページヘッダー */}
        <div className="border-b border-orange-100 bg-white/80 backdrop-blur-sm">
          <div className="mx-auto max-w-6xl px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-orange-500 to-amber-600 shadow-lg">
                  <FaUtensils className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">食事記録</h1>
                  <p className="text-gray-600">
                    {currentChildId}の食事を記録・栄養バランスを管理します
                    {childrenOptions.length > 1 && (
                      <span className="ml-2 text-sm text-amber-600">
                        ({childrenOptions.length}人のお子様が登録済み)
                      </span>
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {/* 子供選択ドロップダウン（複数いる場合のみ表示） */}
                {childrenOptions.length > 1 && (
                  <Select value={currentChildId} onValueChange={setSelectedChildId}>
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="お子様を選択" />
                    </SelectTrigger>
                    <SelectContent>
                      {childrenOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}

                <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
                  <DialogTrigger asChild>
                    <Button className="bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-lg hover:from-orange-600 hover:to-amber-600">
                      <Plus className="mr-2 h-4 w-4" />
                      新しい記録
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                      <DialogTitle>新しい食事記録</DialogTitle>
                      <DialogDescription>
                        お子様の食事情報を記録してください
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      {/* 子供選択 */}
                      <div>
                        <Label htmlFor="child-select">お子様を選択</Label>
                        <Select 
                          value={newMealForm.child_id || currentChildId}
                          onValueChange={(value) => setNewMealForm(prev => ({ ...prev, child_id: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="お子様を選択してください" />
                          </SelectTrigger>
                          <SelectContent>
                            {childrenOptions.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="meal-name">食事名</Label>
                          <Input 
                            id="meal-name" 
                            placeholder="例: 朝食バランス定食"
                            value={newMealForm.meal_name}
                            onChange={(e) => setNewMealForm(prev => ({ ...prev, meal_name: e.target.value }))}
                          />
                        </div>
                        <div>
                          <Label htmlFor="meal-type">食事タイプ</Label>
                          <Select 
                            value={newMealForm.meal_type}
                            onValueChange={(value) => setNewMealForm(prev => ({ ...prev, meal_type: value as 'breakfast' | 'lunch' | 'dinner' | 'snack' }))}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="選択してください" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="breakfast">朝食</SelectItem>
                              <SelectItem value="lunch">昼食</SelectItem>
                              <SelectItem value="dinner">夕食</SelectItem>
                              <SelectItem value="snack">おやつ</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="foods">食材・料理</Label>
                        <Input 
                          id="foods" 
                          placeholder="例: ごはん, 味噌汁, 焼き魚, 野菜サラダ"
                          value={newMealForm.detected_foods}
                          onChange={(e) => setNewMealForm(prev => ({ ...prev, detected_foods: e.target.value }))}
                        />
                      </div>
                      <div>
                        <Label htmlFor="notes">メモ</Label>
                        <Textarea 
                          id="notes" 
                          placeholder="食事の様子や特記事項があれば..."
                          value={newMealForm.notes}
                          onChange={(e) => setNewMealForm(prev => ({ ...prev, notes: e.target.value }))}
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" className="flex-1">
                          <Camera className="mr-2 h-4 w-4" />
                          写真で記録
                        </Button>
                        <Button variant="outline" className="flex-1">
                          <Brain className="mr-2 h-4 w-4" />
                          AI分析で記録
                        </Button>
                      </div>
                      <Button 
                        className="w-full bg-gradient-to-r from-orange-500 to-amber-500"
                        onClick={handleCreateMealRecord}
                        disabled={isCreating || !newMealForm.meal_name}
                      >
                        {isCreating ? (
                          <div className="flex items-center gap-2">
                            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                            保存中...
                          </div>
                        ) : (
                          '記録を保存'
                        )}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>

                <Link href="/chat">
                  <Button className="bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg hover:from-amber-600 hover:to-orange-600">
                    <Sparkles className="mr-2 h-4 w-4" />
                    Genieに相談
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-6xl space-y-8 p-6">
          {/* 栄養サマリーカード */}
          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
            <Card className="border-0 bg-gradient-to-br from-orange-500 to-amber-600 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-100">総食事回数</p>
                    <p className="mt-1 text-2xl font-bold">{nutritionSummary.total_meals}回</p>
                    <p className="text-xs text-orange-200">今週</p>
                  </div>
                  <UtensilsIcon className="h-8 w-8 text-orange-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-gradient-to-br from-amber-500 to-yellow-600 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-amber-100">総カロリー</p>
                    <p className="mt-1 text-2xl font-bold">{nutritionSummary.total_calories}</p>
                    <p className="text-xs text-amber-200">kcal</p>
                  </div>
                  <Activity className="h-8 w-8 text-amber-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-100">栄養バランス</p>
                    <p className="mt-1 text-2xl font-bold">{nutritionSummary.nutrition_balance_score}</p>
                    <p className="text-xs text-green-200">/10点</p>
                  </div>
                  <Star className="h-8 w-8 text-green-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-100">平均タンパク質</p>
                    <p className="mt-1 text-2xl font-bold">{safeAvgNutrition.protein}g</p>
                    <p className="text-xs text-blue-200">1食あたり</p>
                  </div>
                  <FaFish className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* フィルターとビュー切り替え */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-2xl font-bold text-gray-800">食事記録一覧</h2>
              <Select value={selectedMealType} onValueChange={(value: MealType) => setSelectedMealType(value)}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">すべて</SelectItem>
                  <SelectItem value="breakfast">朝食</SelectItem>
                  <SelectItem value="lunch">昼食</SelectItem>
                  <SelectItem value="dinner">夕食</SelectItem>
                  <SelectItem value="snack">おやつ</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2 rounded-lg border border-orange-200 bg-white/60 p-1">
              <Button
                size="sm"
                variant={viewMode === 'card' ? 'default' : 'ghost'}
                onClick={() => setViewMode('card')}
                className={`h-8 px-3 ${viewMode === 'card' ? 'bg-orange-500 text-white' : 'text-orange-600 hover:bg-orange-50'}`}
              >
                <LayoutGrid className="mr-1 h-4 w-4" />
                カード
              </Button>
              <Button
                size="sm"
                variant={viewMode === 'table' ? 'default' : 'ghost'}
                onClick={() => setViewMode('table')}
                className={`h-8 px-3 ${viewMode === 'table' ? 'bg-orange-500 text-white' : 'text-orange-600 hover:bg-orange-50'}`}
              >
                <List className="mr-1 h-4 w-4" />
                テーブル
              </Button>
            </div>
          </div>

          {/* 食事記録一覧 */}
          <Card className="border-0 bg-white/80 shadow-xl backdrop-blur-sm">
            <CardContent className="p-6">
              {viewMode === 'card' ? (
                // カード表示
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {filteredMealRecords.map(record => (
                    <Card
                      key={record.id}
                      className="cursor-pointer border-0 bg-gradient-to-br from-white to-orange-50 shadow-md transition-all duration-200 hover:from-orange-50 hover:to-amber-50 hover:shadow-lg"
                      onClick={() => openDetailModal(record)}
                    >
                      <CardContent className="p-5">
                        <div className="mb-3 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-orange-500 to-amber-600">
                              <UtensilsIcon className="h-4 w-4 text-white" />
                            </div>
                            <div>
                              <p className="text-sm font-semibold text-gray-800">{record.meal_name}</p>
                              <p className="text-xs text-gray-500">
                                {mealTypeLabels[record.meal_type]} • {new Date(record.timestamp).toLocaleDateString('ja-JP')}
                              </p>
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <Badge className="bg-gradient-to-r from-orange-500 to-amber-600 text-white">
                              {record.nutrition_info.calories || 0} kcal
                            </Badge>
                            {record.detection_source !== 'manual' && (
                              <Badge variant="outline" className="border-blue-300 text-blue-700 text-xs">
                                {detectionSourceLabels[record.detection_source]}
                              </Badge>
                            )}
                          </div>
                        </div>

                        <div className="space-y-3">
                          <div>
                            <p className="mb-1 text-sm font-medium text-gray-700">食材・料理</p>
                            <div className="flex flex-wrap gap-1">
                              {record.detected_foods.slice(0, 3).map((food, index) => (
                                <Badge key={index} variant="secondary" className="text-xs">
                                  {food}
                                </Badge>
                              ))}
                              {record.detected_foods.length > 3 && (
                                <Badge variant="secondary" className="text-xs text-gray-500">
                                  +{record.detected_foods.length - 3}
                                </Badge>
                              )}
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-2 text-center">
                            <div className="rounded bg-orange-50 p-2">
                              <p className="text-xs text-orange-600 font-medium">タンパク質</p>
                              <p className="text-sm font-bold text-orange-800">{record.nutrition_info.protein || 0}g</p>
                            </div>
                            <div className="rounded bg-amber-50 p-2">
                              <p className="text-xs text-amber-600 font-medium">炭水化物</p>
                              <p className="text-sm font-bold text-amber-800">{record.nutrition_info.carbs || 0}g</p>
                            </div>
                            <div className="rounded bg-green-50 p-2">
                              <p className="text-xs text-green-600 font-medium">食物繊維</p>
                              <p className="text-sm font-bold text-green-800">{record.nutrition_info.fiber || 0}g</p>
                            </div>
                          </div>

                          <Button
                            variant="outline"
                            size="sm"
                            className="w-full border-orange-300 text-orange-700 hover:bg-orange-50"
                            onClick={e => {
                              e.stopPropagation()
                              openDetailModal(record)
                            }}
                          >
                            <Eye className="mr-2 h-3 w-3" />
                            詳細を見る
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                // テーブル表示
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-orange-200">
                        <th className="px-4 py-3 text-left font-medium text-orange-700">食事名</th>
                        <th className="px-4 py-3 text-left font-medium text-orange-700">タイプ</th>
                        <th className="px-4 py-3 text-left font-medium text-orange-700">日時</th>
                        <th className="px-4 py-3 text-center font-medium text-orange-700">カロリー</th>
                        <th className="px-4 py-3 text-left font-medium text-orange-700">主な食材</th>
                        <th className="px-4 py-3 text-center font-medium text-orange-700">記録方法</th>
                        <th className="px-4 py-3 text-center font-medium text-orange-700">詳細</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredMealRecords.map(record => (
                        <tr
                          key={record.id}
                          className="cursor-pointer border-b border-gray-100 transition-colors hover:bg-orange-50/50"
                          onClick={() => openDetailModal(record)}
                        >
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <UtensilsIcon className="h-4 w-4 text-orange-500" />
                              <span className="text-sm font-medium text-gray-800">{record.meal_name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <Badge variant="outline" className="border-orange-300 text-orange-700">
                              {mealTypeLabels[record.meal_type]}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {new Date(record.timestamp).toLocaleString('ja-JP')}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <Badge className="bg-gradient-to-r from-orange-500 to-amber-600 text-white">
                              {record.nutrition_info.calories || 0} kcal
                            </Badge>
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex flex-wrap gap-1">
                              {record.detected_foods.slice(0, 2).map((food, index) => (
                                <Badge key={index} variant="secondary" className="text-xs">
                                  {food}
                                </Badge>
                              ))}
                              {record.detected_foods.length > 2 && (
                                <span className="text-xs text-gray-500">+{record.detected_foods.length - 2}</span>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <Badge variant="outline" className="border-blue-300 text-blue-700 text-xs">
                              {detectionSourceLabels[record.detection_source]}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <Button
                              variant="outline"
                              size="sm"
                              className="border-orange-300 text-orange-700 hover:bg-orange-50"
                              onClick={e => {
                                e.stopPropagation()
                                openDetailModal(record)
                              }}
                            >
                              <Eye className="mr-1 h-3 w-3" />
                              詳細
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AIチャット連携カード */}
          <Card className="border-0 bg-gradient-to-br from-orange-50 to-amber-50 shadow-xl">
            <CardHeader className="rounded-t-lg bg-gradient-to-r from-orange-500 to-amber-600 text-white">
              <CardTitle className="flex items-center gap-3">
                <Sparkles className="h-6 w-6" />
                Genieとの栄養相談
              </CardTitle>
              <CardDescription className="text-orange-100">
                食事記録をもとに、Genieが栄養バランスのアドバイスを提供します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="rounded-lg border border-orange-200 bg-white/60 p-4">
                <div className="mb-4 flex items-start gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-orange-500 to-amber-600 shadow-lg">
                    <FaUtensils className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="mb-2 text-sm font-medium text-orange-800">
                      💡 Genieは、食事記録を分析して：
                    </p>
                    <ul className="space-y-1 text-sm text-orange-700">
                      <li>• 栄養バランスの改善点をアドバイス</li>
                      <li>• 成長に必要な栄養素の提案</li>
                      <li>• 食べやすいレシピの紹介</li>
                      <li>• 偏食対策のサポート</li>
                    </ul>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Link href="/chat" className="flex-1">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-lg hover:from-orange-600 hover:to-amber-600">
                      <Sparkles className="mr-2 h-4 w-4" />
                      栄養相談をする
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    className="border-orange-300 text-orange-700 hover:bg-orange-50"
                  >
                    <BarChart3 className="mr-2 h-4 w-4" />
                    詳細分析
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 食事記録詳細モーダル */}
        {showDetailModal && selectedRecord && (
          <Dialog open={showDetailModal} onOpenChange={setShowDetailModal}>
            <DialogContent className="sm:max-w-[800px]">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <UtensilsIcon className="h-5 w-5 text-orange-500" />
                  {selectedRecord.meal_name}
                </DialogTitle>
                <DialogDescription>
                  {mealTypeLabels[selectedRecord.meal_type]} • {new Date(selectedRecord.timestamp).toLocaleString('ja-JP')}
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-6 py-4">
                {/* 基本情報 */}
                <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  <Card className="border-0 bg-gradient-to-br from-orange-500 to-amber-600 text-white">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-orange-100">総カロリー</p>
                      <p className="text-2xl font-bold">{selectedRecord.nutrition_info.calories || 0}</p>
                      <p className="text-xs text-orange-200">kcal</p>
                    </CardContent>
                  </Card>

                  <Card className="border-0 bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-blue-100">タンパク質</p>
                      <p className="text-2xl font-bold">{selectedRecord.nutrition_info.protein || 0}</p>
                      <p className="text-xs text-blue-200">g</p>
                    </CardContent>
                  </Card>

                  <Card className="border-0 bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-green-100">記録方法</p>
                      <p className="text-lg font-bold">{detectionSourceLabels[selectedRecord.detection_source]}</p>
                      {selectedRecord.detection_source !== 'manual' && (
                        <p className="text-xs text-green-200">信頼度: {Math.round(selectedRecord.confidence * 100)}%</p>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* 栄養情報詳細 */}
                <Card className="border-0 shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-orange-600" />
                      栄養成分詳細
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                      <div className="text-center p-3 bg-orange-50 rounded-lg">
                        <p className="text-sm font-medium text-orange-600">炭水化物</p>
                        <p className="text-lg font-bold text-orange-800">{selectedRecord.nutrition_info.carbs || 0}g</p>
                      </div>
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm font-medium text-blue-600">脂質</p>
                        <p className="text-lg font-bold text-blue-800">{selectedRecord.nutrition_info.fat || 0}g</p>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <p className="text-sm font-medium text-green-600">食物繊維</p>
                        <p className="text-lg font-bold text-green-800">{selectedRecord.nutrition_info.fiber || 0}g</p>
                      </div>
                      <div className="text-center p-3 bg-purple-50 rounded-lg">
                        <p className="text-sm font-medium text-purple-600">ビタミン</p>
                        <p className="text-sm font-bold text-purple-800">
                          {selectedRecord.nutrition_info.vitamins?.length || 0}種類
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 食材一覧 */}
                <Card className="border-0 shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FaAppleAlt className="h-5 w-5 text-orange-600" />
                      含まれる食材・料理
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {selectedRecord.detected_foods.map((food, index) => (
                        <Badge key={index} className="bg-gradient-to-r from-orange-500 to-amber-600 text-white px-3 py-1">
                          {food}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* ビタミン情報 */}
                {selectedRecord.nutrition_info.vitamins && selectedRecord.nutrition_info.vitamins.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Star className="h-5 w-5 text-orange-600" />
                        含まれるビタミン・栄養素
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {selectedRecord.nutrition_info.vitamins.map((vitamin, index) => (
                          <Badge key={index} variant="outline" className="border-green-300 text-green-700">
                            <Star className="mr-1 h-3 w-3" />
                            {vitamin}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* メモ */}
                {selectedRecord.notes && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Edit className="h-5 w-5 text-orange-600" />
                        メモ
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700">{selectedRecord.notes}</p>
                    </CardContent>
                  </Card>
                )}

                {/* アクションボタン */}
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    className="border-orange-300 text-orange-700 hover:bg-orange-50"
                    onClick={() => handleEditMealRecord(selectedRecord)}
                    disabled={isUpdating}
                  >
                    <Edit className="mr-2 h-4 w-4" />
                    編集
                  </Button>
                  <Button
                    variant="outline"
                    className="border-red-300 text-red-700 hover:bg-red-50"
                    onClick={() => handleDeleteMealRecord(selectedRecord.id)}
                    disabled={isDeleting}
                  >
                    {isDeleting ? (
                      <>
                        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-red-600 border-t-transparent"></div>
                        削除中...
                      </>
                    ) : (
                      <>
                        <Trash2 className="mr-2 h-4 w-4" />
                        削除
                      </>
                    )}
                  </Button>
                  <Link href="/chat" className="flex-1">
                    <Button className="w-full bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                      <Sparkles className="mr-2 h-4 w-4" />
                      この食事についてGenieに相談
                    </Button>
                  </Link>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        )}

        {/* 食事記録編集モーダル */}
        {showEditModal && selectedRecord && (
          <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Edit className="h-5 w-5 text-orange-500" />
                  食事記録を編集
                </DialogTitle>
                <DialogDescription>
                  記録内容を修正してください
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="edit-meal-name">食事名</Label>
                    <Input 
                      id="edit-meal-name" 
                      placeholder="例: 朝食バランス定食"
                      value={editMealForm.meal_name}
                      onChange={(e) => setEditMealForm(prev => ({ ...prev, meal_name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-meal-type">食事タイプ</Label>
                    <Select 
                      value={editMealForm.meal_type}
                      onValueChange={(value) => setEditMealForm(prev => ({ ...prev, meal_type: value as 'breakfast' | 'lunch' | 'dinner' | 'snack' }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="選択してください" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="breakfast">朝食</SelectItem>
                        <SelectItem value="lunch">昼食</SelectItem>
                        <SelectItem value="dinner">夕食</SelectItem>
                        <SelectItem value="snack">おやつ</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="edit-foods">食材・料理</Label>
                  <Input 
                    id="edit-foods" 
                    placeholder="例: ごはん, 味噌汁, 焼き魚, 野菜サラダ"
                    value={editMealForm.detected_foods}
                    onChange={(e) => setEditMealForm(prev => ({ ...prev, detected_foods: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="edit-notes">メモ</Label>
                  <Textarea 
                    id="edit-notes" 
                    placeholder="食事の様子や特記事項があれば..."
                    value={editMealForm.notes}
                    onChange={(e) => setEditMealForm(prev => ({ ...prev, notes: e.target.value }))}
                  />
                </div>
                <div className="flex gap-3">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowEditModal(false)}
                    className="flex-1"
                  >
                    キャンセル
                  </Button>
                  <Button 
                    className="flex-1 bg-gradient-to-r from-orange-500 to-amber-500"
                    onClick={handleUpdateMealRecord}
                    disabled={isUpdating || !editMealForm.meal_name}
                  >
                    {isUpdating ? (
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                        更新中...
                      </div>
                    ) : (
                      '変更を保存'
                    )}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </AppLayout>
  )
}