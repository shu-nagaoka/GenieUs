'use client'

import { useState, useMemo } from 'react'
import { useMealPlans, useCreateMealPlan, useDeleteMealPlan } from '@/hooks/useMealPlans'
import { AppLayout } from '@/components/layout/app-layout'
import { AuthCheck } from '@/components/features/auth/auth-check'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Calendar as CalendarIcon,
  Sparkles,
  Plus,
  Edit,
  Search,
  CheckCircle,
  Filter,
} from 'lucide-react'
import { FaUtensils } from 'react-icons/fa'
import { GiMagicLamp } from 'react-icons/gi'
import Link from 'next/link'

// 記録機能は削除 - プラン機能のみ

// 1週間食事プランのインターフェース
interface MealPlan {
  id: string
  week_start: string // YYYY-MM-DD format
  title: string
  description: string
  created_by: 'genie' | 'user'
  meals: {
    [day: string]: {
      // 'monday', 'tuesday', etc.
      breakfast?: PlannedMeal
      lunch?: PlannedMeal
      dinner?: PlannedMeal
      snack?: PlannedMeal
    }
  }
  nutrition_goals?: {
    daily_calories: number
    daily_protein: number
    daily_carbs: number
    daily_fat: number
  }
  notes?: string
  created_at: string
}

interface PlannedMeal {
  id: string
  title: string
  description: string
  ingredients: string[]
  estimated_nutrition?: {
    calories?: number
    protein?: number
    carbs?: number
    fat?: number
  }
  difficulty: 'easy' | 'medium' | 'hard'
  prep_time_minutes: number
  tags: string[]
  allergens?: string[]
  recipe_url?: string
}

// 1週間食事プランのサンプルデータ
const sampleMealPlans: MealPlan[] = [
  {
    id: 'plan-1',
    week_start: '2025-06-23', // Monday
    title: '栄養バランス重視プラン',
    description: '月齢10ヶ月向けの栄養バランスを考慮した1週間メニュー',
    created_by: 'genie',
    meals: {
      monday: {
        breakfast: {
          id: 'm1-b',
          title: 'フルーツオートミール',
          description: 'バナナとブルーベリーの栄養満点朝食',
          ingredients: ['オートミール', 'バナナ', 'ブルーベリー', '母乳/ミルク'],
          estimated_nutrition: { calories: 85, protein: 3.2, carbs: 18.5, fat: 1.2 },
          difficulty: 'easy',
          prep_time_minutes: 10,
          tags: ['離乳食', '後期', 'フルーツ'],
          allergens: [],
        },
        lunch: {
          id: 'm1-l',
          title: '鶏ひき肉とかぼちゃの煮物',
          description: 'タンパク質とビタミンAたっぷり',
          ingredients: ['鶏ひき肉', 'かぼちゃ', '人参', 'だし汁'],
          estimated_nutrition: { calories: 95, protein: 8.5, carbs: 12.2, fat: 2.1 },
          difficulty: 'medium',
          prep_time_minutes: 20,
          tags: ['離乳食', '後期', 'タンパク質'],
          allergens: [],
        },
        dinner: {
          id: 'm1-d',
          title: '豆腐ハンバーグ',
          description: '柔らかく食べやすいハンバーグ',
          ingredients: ['豆腐', '鶏ひき肉', '人参', '玉ねぎ'],
          estimated_nutrition: { calories: 78, protein: 7.2, carbs: 5.8, fat: 3.1 },
          difficulty: 'medium',
          prep_time_minutes: 25,
          tags: ['離乳食', '後期', '手づかみ'],
          allergens: ['大豆'],
        },
        snack: {
          id: 'm1-s',
          title: 'バナナヨーグルト',
          description: 'カルシウム補給のおやつ',
          ingredients: ['バナナ', 'プレーンヨーグルト'],
          estimated_nutrition: { calories: 68, protein: 3.2, carbs: 12.4, fat: 1.8 },
          difficulty: 'easy',
          prep_time_minutes: 5,
          tags: ['おやつ', 'カルシウム'],
          allergens: ['乳製品'],
        },
      },
      tuesday: {
        breakfast: {
          id: 't1-b',
          title: 'パンケーキ',
          description: '手づかみ食べしやすいミニパンケーキ',
          ingredients: ['小麦粉', '卵', '牛乳', 'バナナ'],
          estimated_nutrition: { calories: 110, protein: 4.5, carbs: 20.2, fat: 2.8 },
          difficulty: 'medium',
          prep_time_minutes: 15,
          tags: ['朝食', '手づかみ'],
          allergens: ['小麦', '卵', '乳製品'],
        },
        lunch: {
          id: 't1-l',
          title: '親子丼（取り分け）',
          description: '大人のメニューから取り分け',
          ingredients: ['軟飯', '鶏肉', '卵', '玉ねぎ', 'だし汁'],
          estimated_nutrition: { calories: 120, protein: 12.3, carbs: 15.8, fat: 3.2 },
          difficulty: 'easy',
          prep_time_minutes: 10,
          tags: ['取り分け', '家族食'],
          allergens: ['卵'],
        },
      },
      wednesday: {
        lunch: {
          id: 'w1-l',
          title: 'ミートボール',
          description: '柔らかく煮込んだミートボール',
          ingredients: ['牛ひき肉', '玉ねぎ', 'トマトソース', 'パスタ'],
          estimated_nutrition: { calories: 140, protein: 12.8, carbs: 18.2, fat: 3.5 },
          difficulty: 'medium',
          prep_time_minutes: 30,
          tags: ['夕食', 'タンパク質', 'イタリアン'],
          allergens: ['小麦'],
        },
      },
    },
    nutrition_goals: {
      daily_calories: 300,
      daily_protein: 15,
      daily_carbs: 45,
      daily_fat: 8,
    },
    notes: 'アレルギー反応を見ながら進めてください',
    created_at: '2025-06-20T10:00:00Z',
  },
]

// 記録機能削除 - プランのみに特化

export default function FoodManagementPage() {
  return (
    <AuthCheck>
      <FoodManagementPageContent />
    </AuthCheck>
  )
}

function FoodManagementPageContent() {
  const [searchQuery, setSearchQuery] = useState('')
  
  const {
    data: apiMealPlans = [],
    isLoading,
    error: queryError,
    refetch: refetchMealPlans,
  } = useMealPlans('frontend_user')
  
  const createMealPlanMutation = useCreateMealPlan()
  const deleteMealPlanMutation = useDeleteMealPlan()

  // APIのMealPlanをUIのMealPlan形式に変換（メモ化）
  const mealPlans = useMemo(() => {
    if (apiMealPlans.length === 0) {
      // フォールバック: サンプルデータを使用
      return sampleMealPlans
    }

    return apiMealPlans.map((apiPlan: Record<string, unknown>) => ({
      id: apiPlan.id,
      week_start: apiPlan.week_start,
      title: apiPlan.title,
      description: apiPlan.description,
      created_by: apiPlan.created_by,
      meals: apiPlan.meals || {},
      nutrition_goals: apiPlan.nutrition_goals,
      notes: apiPlan.notes,
      created_at: apiPlan.created_at,
    }))
  }, [apiMealPlans])

  const error = queryError ? '食事プランの読み込みに失敗しました' : null
  const loading = isLoading || createMealPlanMutation.isPending || deleteMealPlanMutation.isPending

  // 記録関連の関数は削除

  // 新しい食事プラン作成
  const handleCreateMealPlan = async () => {
    try {
      // 今週の月曜日を取得
      const now = new Date()
      const dayOfWeek = now.getDay()
      const diff = now.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1) // 月曜日に調整
      const monday = new Date(now.setDate(diff))
      const weekStart = monday.toISOString().split('T')[0]

      const newPlanRequest = {
        week_start: weekStart,
        title: `新しい食事プラン (${new Date().toLocaleDateString('ja-JP')})`,
        description: 'Genieが提案する栄養バランスを考慮した食事プラン',
        created_by: 'user' as const,
        meals: {},
        nutrition_goals: {
          daily_calories: 300,
          daily_protein: 15,
          daily_carbs: 45,
          daily_fat: 8,
        },
        notes: '新しく作成した食事プランです。必要に応じて編集してください。',
      }

      const result = await createMealPlanMutation.mutateAsync(newPlanRequest)
      
      if (result.success) {
        console.log('Meal plan created successfully:', result.data)
        alert('新しい食事プランを作成しました！')
      } else {
        throw new Error(result.error || '食事プランの作成に失敗しました')
      }
    } catch (error) {
      console.error('Error creating meal plan:', error)
      const errorMessage = error instanceof Error ? error.message : '食事プランの作成に失敗しました'
      alert(`食事プランの作成に失敗しました: ${errorMessage}`)
    }
  }

  // 食事プラン削除
  const handleDeleteMealPlan = async (planId: string) => {
    try {
      if (!confirm('この食事プランを削除しますか？')) {
        return
      }

      const result = await deleteMealPlanMutation.mutateAsync(planId)

      if (result.success) {
        console.log('Meal plan deleted successfully')
        alert('食事プランを削除しました')
      } else {
        throw new Error(result.error || '食事プランの削除に失敗しました')
      }
    } catch (error) {
      console.error('Error deleting meal plan:', error)
      const errorMessage = error instanceof Error ? error.message : '食事プランの削除に失敗しました'
      alert(`食事プランの削除に失敗しました: ${errorMessage}`)
    }
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-green-50">
        {/* ページヘッダー */}
        <div className="border-b border-green-300 bg-white">
          <div className="mx-auto max-w-6xl px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-700">
                  <FaUtensils className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">食事管理</h1>
                  <p className="text-gray-600">食事プランで、お子さまの成長をサポート</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Button
                  className="bg-green-700 text-white hover:bg-green-800"
                  onClick={handleCreateMealPlan}
                  disabled={loading}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  {loading ? '作成中...' : '新しいプラン作成'}
                </Button>

                <Link href="/chat">
                  <Button
                    variant="outline"
                    className="border-green-400 text-green-800 hover:bg-green-100"
                  >
                    <Sparkles className="mr-2 h-4 w-4" />
                    Genieに相談
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-6xl space-y-8 p-6">
          {/* エラー表示 */}
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-red-700">
                  <span>⚠️</span>
                  <span>{error}</span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => refetchMealPlans()}
                    className="ml-auto border-red-300 text-red-700 hover:bg-red-100"
                  >
                    再試行
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ローディング表示 */}
          {loading && (
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-blue-700">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
                  <span>処理中...</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 食事プランセクション - シンプル化 */}
          <>
            {/* プランサマリーカード */}
            <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
              <Card className="border-0 bg-green-700 text-white shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-green-200">作成済みプラン</p>
                      <p className="mt-1 text-2xl font-bold">{mealPlans.length}件</p>
                      <p className="text-xs text-green-300">メニュープラン</p>
                    </div>
                    <CalendarIcon className="h-8 w-8 text-green-300" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 bg-emerald-700 text-white shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-emerald-200">Genie推奨</p>
                      <p className="mt-1 text-2xl font-bold">
                        {mealPlans.filter(p => p.created_by === 'genie').length}件
                      </p>
                      <p className="text-xs text-emerald-300">AIプラン</p>
                    </div>
                    <GiMagicLamp className="h-8 w-8 text-emerald-300" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 bg-teal-700 text-white shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-teal-200">今週のプラン</p>
                      <p className="mt-1 text-2xl font-bold">1件</p>
                      <p className="text-xs text-teal-300">実行中</p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-teal-300" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* 検索バー */}
            <Card className="border-0 bg-white shadow-lg">
              <CardHeader className="rounded-t-lg bg-green-700 text-white">
                <CardTitle className="flex items-center gap-3">
                  <Filter className="h-6 w-6" />
                  プラン検索
                </CardTitle>
                <CardDescription className="text-green-200">
                  お探しの食事プランを見つける
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <Input
                    placeholder="プラン名、説明で検索..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="border-green-300 pl-10 focus:border-green-500"
                  />
                </div>
              </CardContent>
            </Card>

            {/* プラン一覧 */}
            <div className="space-y-6">
              {mealPlans
                .filter(
                  plan =>
                    plan.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    plan.description.toLowerCase().includes(searchQuery.toLowerCase())
                )
                .map(plan => {
                  const getWeekDays = (weekStart: string) => {
                    const startDate = new Date(weekStart)
                    const days = []
                    for (let i = 0; i < 7; i++) {
                      const date = new Date(startDate)
                      date.setDate(startDate.getDate() + i)
                      days.push({
                        date: date.toISOString().split('T')[0],
                        dayName: date.toLocaleDateString('ja-JP', { weekday: 'short' }),
                        dayKey: [
                          'monday',
                          'tuesday',
                          'wednesday',
                          'thursday',
                          'friday',
                          'saturday',
                          'sunday',
                        ][i],
                      })
                    }
                    return days
                  }

                  const weekDays = getWeekDays(plan.week_start)
                  const nutritionSummary = {
                    totalCalories: 0,
                    totalProtein: 0,
                    totalCarbs: 0,
                    totalFat: 0,
                    mealsCount: 0,
                  }

                  // 栄養サマリー計算
                  Object.values(plan.meals).forEach((dayMeals: Record<string, unknown>) => {
                    Object.values(dayMeals).forEach((meal: Record<string, unknown>) => {
                      if (meal?.estimated_nutrition) {
                        const nutrition = meal.estimated_nutrition as Record<string, number>
                        nutritionSummary.totalCalories += nutrition.calories || 0
                        nutritionSummary.totalProtein += nutrition.protein || 0
                        nutritionSummary.totalCarbs += nutrition.carbs || 0
                        nutritionSummary.totalFat += nutrition.fat || 0
                        nutritionSummary.mealsCount++
                      }
                    })
                  })

                  return (
                    <Card key={plan.id} className="border-0 bg-white shadow-lg">
                      <CardHeader className="rounded-t-lg bg-green-700 text-white">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="flex items-center gap-3">
                              <CalendarIcon className="h-6 w-6" />
                              {plan.title}
                              {plan.created_by === 'genie' && (
                                <Badge className="bg-emerald-600 text-white">
                                  <GiMagicLamp className="mr-1 h-3 w-3" />
                                  Genie推奨
                                </Badge>
                              )}
                            </CardTitle>
                            <CardDescription className="mt-2 text-green-200">
                              {plan.description}
                            </CardDescription>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-green-200">
                              {new Date(plan.week_start).toLocaleDateString('ja-JP', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                              })}{' '}
                              〜
                            </p>
                            <p className="text-xs text-green-300">
                              {nutritionSummary.mealsCount}食分・約
                              {Math.round(nutritionSummary.totalCalories)}カロリー
                            </p>
                          </div>
                        </div>
                      </CardHeader>

                      <CardContent className="p-6">
                        {/* 栄養目標 */}
                        {plan.nutrition_goals && (
                          <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4">
                            <h4 className="mb-3 font-medium text-green-800">🎯 1日の栄養目標</h4>
                            <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                              <div className="rounded border border-green-100 bg-white p-2 text-center">
                                <div className="font-bold text-green-600">
                                  {plan.nutrition_goals.daily_calories}
                                </div>
                                <div className="text-xs text-green-500">カロリー</div>
                              </div>
                              <div className="rounded border border-green-100 bg-white p-2 text-center">
                                <div className="font-bold text-green-600">
                                  {plan.nutrition_goals.daily_protein}g
                                </div>
                                <div className="text-xs text-green-500">タンパク質</div>
                              </div>
                              <div className="rounded border border-green-100 bg-white p-2 text-center">
                                <div className="font-bold text-green-600">
                                  {plan.nutrition_goals.daily_carbs}g
                                </div>
                                <div className="text-xs text-green-500">炭水化物</div>
                              </div>
                              <div className="rounded border border-green-100 bg-white p-2 text-center">
                                <div className="font-bold text-green-600">
                                  {plan.nutrition_goals.daily_fat}g
                                </div>
                                <div className="text-xs text-green-500">脂質</div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 週間カレンダー */}
                        <div className="grid grid-cols-1 gap-4 lg:grid-cols-7">
                          {weekDays.map(day => {
                            const dayMeals = (plan.meals as Record<string, unknown>)[day.dayKey] || {}

                            return (
                              <div
                                key={day.date}
                                className="rounded-lg border border-gray-200 bg-white"
                              >
                                <div className="border-b border-gray-200 bg-green-50 p-3">
                                  <h5 className="text-center font-medium text-gray-800">
                                    {day.dayName}
                                  </h5>
                                  <p className="text-center text-xs text-gray-500">
                                    {new Date(day.date).getDate()}日
                                  </p>
                                </div>

                                <div className="space-y-2 p-3">
                                  {['breakfast', 'lunch', 'dinner', 'snack'].map(mealType => {
                                    const meal = dayMeals[mealType]
                                    const mealTypeLabels = {
                                      breakfast: '朝',
                                      lunch: '昼',
                                      dinner: '夕',
                                      snack: 'おやつ',
                                    }

                                    return (
                                      <div key={mealType} className="text-xs">
                                        <div className="mb-1 font-medium text-gray-600">
                                          {mealTypeLabels[mealType as keyof typeof mealTypeLabels]}
                                        </div>
                                        {meal ? (
                                          <div className="rounded border border-gray-100 bg-white p-2 transition-colors hover:border-green-200">
                                            <div className="font-medium leading-tight text-gray-800">
                                              {meal.title}
                                            </div>
                                            <div className="mt-1 text-gray-500">
                                              {meal.prep_time_minutes}分
                                            </div>
                                            {meal.estimated_nutrition && (
                                              <div className="mt-1 text-green-600">
                                                {meal.estimated_nutrition.calories}カロリー
                                              </div>
                                            )}
                                            {meal.allergens && meal.allergens.length > 0 && (
                                              <div className="mt-1 text-red-500">
                                                ⚠️ {meal.allergens.join(', ')}
                                              </div>
                                            )}
                                          </div>
                                        ) : (
                                          <div className="rounded border border-gray-100 bg-gray-50 p-2 text-center text-gray-400">
                                            未設定
                                          </div>
                                        )}
                                      </div>
                                    )
                                  })}
                                </div>
                              </div>
                            )
                          })}
                        </div>

                        {/* プランメモ */}
                        {plan.notes && (
                          <div className="mt-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4">
                            <div className="flex items-start gap-2">
                              <div className="text-yellow-600">📝</div>
                              <div>
                                <p className="mb-1 text-sm font-medium text-yellow-800">メモ</p>
                                <p className="text-sm text-yellow-700">{plan.notes}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* アクションボタン */}
                        <div className="mt-6 flex gap-3">
                          <Button className="flex-1 bg-green-700 text-white hover:bg-green-800">
                            <Edit className="mr-2 h-4 w-4" />
                            プラン編集
                          </Button>
                          <Button
                            variant="outline"
                            className="flex-1 border-red-300 text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteMealPlan(plan.id)}
                          >
                            削除
                          </Button>
                          <Link href="/chat" className="flex-1">
                            <Button
                              variant="outline"
                              className="w-full border-green-300 text-green-700 hover:bg-green-50"
                            >
                              <Sparkles className="mr-2 h-4 w-4" />
                              Genieに改善依頼
                            </Button>
                          </Link>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
            </div>

            {/* 空の状態 */}
            {mealPlans.filter(
              plan =>
                plan.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                plan.description.toLowerCase().includes(searchQuery.toLowerCase())
            ).length === 0 && (
              <div className="py-12 text-center">
                <CalendarIcon className="mx-auto mb-4 h-16 w-16 text-gray-300" />
                <h3 className="mb-2 text-lg font-medium text-gray-700">食事プランがありません</h3>
                <p className="mb-4 text-gray-500">初めての食事プランを作成しましょう</p>
                <div className="flex justify-center gap-3">
                  <Button
                    className="bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600"
                    onClick={handleCreateMealPlan}
                    disabled={loading}
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    {loading ? '作成中...' : '新しいプラン作成'}
                  </Button>
                  <Link href="/chat">
                    <Button
                      variant="outline"
                      className="border-blue-300 text-blue-700 hover:bg-blue-50"
                    >
                      <Sparkles className="mr-2 h-4 w-4" />
                      Genieに相談
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </>

          {/* AI栄養分析の説明 */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-green-200 bg-white/60 px-4 py-2 backdrop-blur-sm">
              <GiMagicLamp className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">
                Genieがお子さまの成長に合わせた最適な食事プランを提案します
              </span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
