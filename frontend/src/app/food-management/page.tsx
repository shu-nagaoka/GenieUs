'use client'

import { useState, useEffect } from 'react'
import { getMealPlans, createMealPlan, updateMealPlan, deleteMealPlan, MealPlan as ApiMealPlan } from '@/libs/api/meal-plans'
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
  Filter
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
    [day: string]: { // 'monday', 'tuesday', etc.
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
          allergens: []
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
          allergens: []
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
          allergens: ['大豆']
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
          allergens: ['乳製品']
        }
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
          allergens: ['小麦', '卵', '乳製品']
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
          allergens: ['卵']
        }
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
          allergens: ['小麦']
        }
      }
    },
    nutrition_goals: {
      daily_calories: 300,
      daily_protein: 15,
      daily_carbs: 45,
      daily_fat: 8
    },
    notes: 'アレルギー反応を見ながら進めてください',
    created_at: '2025-06-20T10:00:00Z'
  }
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
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState<string | null>(null)

  // 食事プラン一覧を取得
  const loadMealPlans = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await getMealPlans('frontend_user')
      
      if (result.success && result.data) {
        // APIのMealPlanをUIのMealPlan形式に変換
        const convertedPlans: MealPlan[] = result.data.meal_plans.map((apiPlan: any) => ({
          id: apiPlan.id,
          week_start: apiPlan.week_start,
          title: apiPlan.title,
          description: apiPlan.description,
          created_by: apiPlan.created_by,
          meals: apiPlan.meals || {},
          nutrition_goals: apiPlan.nutrition_goals,
          notes: apiPlan.notes,
          created_at: apiPlan.created_at
        }))
        setMealPlans(convertedPlans)
        console.log('Loaded meal plans:', convertedPlans.length)
      } else {
        console.warn('Failed to load meal plans:', result.error)
        // サンプルデータをフォールバックとして使用
        setMealPlans(sampleMealPlans)
      }
    } catch (error) {
      console.error('Error loading meal plans:', error)
      setError('食事プランの読み込みに失敗しました')
      // サンプルデータをフォールバックとして使用
      setMealPlans(sampleMealPlans)
    } finally {
      setLoading(false)
    }
  }

  // コンポーネントマウント時に食事プラン読み込み
  useEffect(() => {
    loadMealPlans()
  }, [])

  // 記録関連の関数は削除

  // 新しい食事プラン作成
  const handleCreateMealPlan = async () => {
    try {
      setLoading(true)
      setError(null)
      
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
          daily_fat: 8
        },
        notes: '新しく作成した食事プランです。必要に応じて編集してください。'
      }
      
      const result = await createMealPlan(newPlanRequest)
      
      if (result.success) {
        console.log('Meal plan created successfully:', result.data)
        alert('新しい食事プランを作成しました！')
        loadMealPlans() // プラン一覧を再読み込み
      } else {
        throw new Error(result.error || '食事プランの作成に失敗しました')
      }
    } catch (error) {
      console.error('Error creating meal plan:', error)
      setError(error instanceof Error ? error.message : '食事プランの作成に失敗しました')
      alert('食事プランの作成に失敗しました: ' + (error instanceof Error ? error.message : '不明なエラー'))
    } finally {
      setLoading(false)
    }
  }

  // 食事プラン削除
  const handleDeleteMealPlan = async (planId: string) => {
    try {
      if (!confirm('この食事プランを削除しますか？')) {
        return
      }
      
      setLoading(true)
      setError(null)
      
      const result = await deleteMealPlan(planId)
      
      if (result.success) {
        console.log('Meal plan deleted successfully')
        alert('食事プランを削除しました')
        loadMealPlans() // プラン一覧を再読み込み
      } else {
        throw new Error(result.error || '食事プランの削除に失敗しました')
      }
    } catch (error) {
      console.error('Error deleting meal plan:', error)
      setError(error instanceof Error ? error.message : '食事プランの削除に失敗しました')
      alert('食事プランの削除に失敗しました: ' + (error instanceof Error ? error.message : '不明なエラー'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-green-50">
        {/* ページヘッダー */}
        <div className="bg-white border-b border-green-300">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-green-700 flex items-center justify-center">
                  <FaUtensils className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">食事管理</h1>
                  <p className="text-gray-600">食事プランで、お子さまの成長をサポート</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Button 
                  className="bg-green-700 hover:bg-green-800 text-white"
                  onClick={handleCreateMealPlan}
                  disabled={loading}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {loading ? '作成中...' : '新しいプラン作成'}
                </Button>
                
                <Link href="/chat">
                  <Button variant="outline" className="border-green-400 text-green-800 hover:bg-green-100">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Genieに相談
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-6 space-y-8">
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
                    onClick={() => setError(null)}
                    className="ml-auto border-red-300 text-red-700 hover:bg-red-100"
                  >
                    ✕
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
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <span>処理中...</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 食事プランセクション - シンプル化 */}
          <>
              {/* プランサマリーカード */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <Card className="bg-green-700 text-white border-0 shadow-lg">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-green-200 text-sm font-medium">作成済みプラン</p>
                        <p className="text-2xl font-bold mt-1">{mealPlans.length}件</p>
                        <p className="text-green-300 text-xs">メニュープラン</p>
                      </div>
                      <CalendarIcon className="h-8 w-8 text-green-300" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-emerald-700 text-white border-0 shadow-lg">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-emerald-200 text-sm font-medium">Genie推奨</p>
                        <p className="text-2xl font-bold mt-1">{mealPlans.filter(p => p.created_by === 'genie').length}件</p>
                        <p className="text-emerald-300 text-xs">AIプラン</p>
                      </div>
                      <GiMagicLamp className="h-8 w-8 text-emerald-300" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-teal-700 text-white border-0 shadow-lg">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-teal-200 text-sm font-medium">今週のプラン</p>
                        <p className="text-2xl font-bold mt-1">1件</p>
                        <p className="text-teal-300 text-xs">実行中</p>
                      </div>
                      <CheckCircle className="h-8 w-8 text-teal-300" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 検索バー */}
              <Card className="shadow-lg border-0 bg-white">
                <CardHeader className="bg-green-700 text-white rounded-t-lg">
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
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="プラン名、説明で検索..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 border-green-300 focus:border-green-500"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* プラン一覧 */}
              <div className="space-y-6">
                {mealPlans
                  .filter(plan => 
                    plan.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    plan.description.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  .map((plan) => {
                    const getWeekDays = (weekStart: string) => {
                      const startDate = new Date(weekStart)
                      const days = []
                      for (let i = 0; i < 7; i++) {
                        const date = new Date(startDate)
                        date.setDate(startDate.getDate() + i)
                        days.push({
                          date: date.toISOString().split('T')[0],
                          dayName: date.toLocaleDateString('ja-JP', { weekday: 'short' }),
                          dayKey: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][i]
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
                      mealsCount: 0
                    }

                    // 栄養サマリー計算
                    Object.values(plan.meals).forEach((dayMeals: any) => {
                      Object.values(dayMeals).forEach((meal: any) => {
                        if (meal?.estimated_nutrition) {
                          nutritionSummary.totalCalories += meal.estimated_nutrition.calories || 0
                          nutritionSummary.totalProtein += meal.estimated_nutrition.protein || 0
                          nutritionSummary.totalCarbs += meal.estimated_nutrition.carbs || 0
                          nutritionSummary.totalFat += meal.estimated_nutrition.fat || 0
                          nutritionSummary.mealsCount++
                        }
                      })
                    })
                    
                    return (
                      <Card key={plan.id} className="shadow-lg border-0 bg-white">
                        <CardHeader className="bg-green-700 text-white rounded-t-lg">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="flex items-center gap-3">
                                <CalendarIcon className="h-6 w-6" />
                                {plan.title}
                                {plan.created_by === 'genie' && (
                                  <Badge className="bg-emerald-600 text-white">
                                    <GiMagicLamp className="h-3 w-3 mr-1" />
                                    Genie推奨
                                  </Badge>
                                )}
                              </CardTitle>
                              <CardDescription className="text-green-200 mt-2">
                                {plan.description}
                              </CardDescription>
                            </div>
                            <div className="text-right">
                              <p className="text-green-200 text-sm">
                                {new Date(plan.week_start).toLocaleDateString('ja-JP', { 
                                  year: 'numeric', month: 'short', day: 'numeric' 
                                })} 〜
                              </p>
                              <p className="text-green-300 text-xs">
                                {nutritionSummary.mealsCount}食分・約{Math.round(nutritionSummary.totalCalories)}カロリー
                              </p>
                            </div>
                          </div>
                        </CardHeader>
                        
                        <CardContent className="p-6">
                          {/* 栄養目標 */}
                          {plan.nutrition_goals && (
                            <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
                              <h4 className="font-medium text-green-800 mb-3">🎯 1日の栄養目標</h4>
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                <div className="text-center p-2 bg-white rounded border border-green-100">
                                  <div className="font-bold text-green-600">{plan.nutrition_goals.daily_calories}</div>
                                  <div className="text-green-500 text-xs">カロリー</div>
                                </div>
                                <div className="text-center p-2 bg-white rounded border border-green-100">
                                  <div className="font-bold text-green-600">{plan.nutrition_goals.daily_protein}g</div>
                                  <div className="text-green-500 text-xs">タンパク質</div>
                                </div>
                                <div className="text-center p-2 bg-white rounded border border-green-100">
                                  <div className="font-bold text-green-600">{plan.nutrition_goals.daily_carbs}g</div>
                                  <div className="text-green-500 text-xs">炭水化物</div>
                                </div>
                                <div className="text-center p-2 bg-white rounded border border-green-100">
                                  <div className="font-bold text-green-600">{plan.nutrition_goals.daily_fat}g</div>
                                  <div className="text-green-500 text-xs">脂質</div>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* 週間カレンダー */}
                          <div className="grid grid-cols-1 lg:grid-cols-7 gap-4">
                            {weekDays.map((day) => {
                              const dayMeals = (plan.meals as any)[day.dayKey] || {}
                              
                              return (
                                <div key={day.date} className="border border-gray-200 rounded-lg bg-white">
                                  <div className="p-3 border-b border-gray-200 bg-green-50">
                                    <h5 className="font-medium text-gray-800 text-center">
                                      {day.dayName}
                                    </h5>
                                    <p className="text-xs text-gray-500 text-center">
                                      {new Date(day.date).getDate()}日
                                    </p>
                                  </div>
                                  
                                  <div className="p-3 space-y-2">
                                    {['breakfast', 'lunch', 'dinner', 'snack'].map((mealType) => {
                                      const meal = dayMeals[mealType]
                                      const mealTypeLabels = {
                                        breakfast: '朝',
                                        lunch: '昼', 
                                        dinner: '夕',
                                        snack: 'おやつ'
                                      }
                                      
                                      return (
                                        <div key={mealType} className="text-xs">
                                          <div className="font-medium text-gray-600 mb-1">
                                            {mealTypeLabels[mealType as keyof typeof mealTypeLabels]}
                                          </div>
                                          {meal ? (
                                            <div className="p-2 bg-white rounded border border-gray-100 hover:border-green-200 transition-colors">
                                              <div className="font-medium text-gray-800 leading-tight">
                                                {meal.title}
                                              </div>
                                              <div className="text-gray-500 mt-1">
                                                {meal.prep_time_minutes}分
                                              </div>
                                              {meal.estimated_nutrition && (
                                                <div className="text-green-600 mt-1">
                                                  {meal.estimated_nutrition.calories}カロリー
                                                </div>
                                              )}
                                              {meal.allergens && meal.allergens.length > 0 && (
                                                <div className="text-red-500 mt-1">
                                                  ⚠️ {meal.allergens.join(', ')}
                                                </div>
                                              )}
                                            </div>
                                          ) : (
                                            <div className="p-2 bg-gray-50 rounded border border-gray-100 text-gray-400 text-center">
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
                            <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                              <div className="flex items-start gap-2">
                                <div className="text-yellow-600">📝</div>
                                <div>
                                  <p className="text-sm font-medium text-yellow-800 mb-1">メモ</p>
                                  <p className="text-sm text-yellow-700">{plan.notes}</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* アクションボタン */}
                          <div className="flex gap-3 mt-6">
                            <Button className="flex-1 bg-green-700 hover:bg-green-800 text-white">
                              <Edit className="h-4 w-4 mr-2" />
                              プラン編集
                            </Button>
                            <Link href="/chat" className="flex-1">
                              <Button variant="outline" className="w-full border-green-300 text-green-700 hover:bg-green-50">
                                <Sparkles className="h-4 w-4 mr-2" />
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
              {mealPlans.filter(plan => 
                plan.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                plan.description.toLowerCase().includes(searchQuery.toLowerCase())
              ).length === 0 && (
                <div className="text-center py-12">
                  <CalendarIcon className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-700 mb-2">食事プランがありません</h3>
                  <p className="text-gray-500 mb-4">初めての食事プランを作成しましょう</p>
                  <div className="flex gap-3 justify-center">
                    <Button 
                      className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white"
                      onClick={handleCreateMealPlan}
                      disabled={loading}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      {loading ? '作成中...' : '新しいプラン作成'}
                    </Button>
                    <Link href="/chat">
                      <Button variant="outline" className="border-blue-300 text-blue-700 hover:bg-blue-50">
                        <Sparkles className="h-4 w-4 mr-2" />
                        Genieに相談
                      </Button>
                    </Link>
                  </div>
                </div>
              )}
            </>

          {/* AI栄養分析の説明 */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-full border border-green-200">
              <GiMagicLamp className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-700 font-medium">
                Genieがお子さまの成長に合わせた最適な食事プランを提案します
              </span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}