import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getMealPlans,
  createMealPlan,
  updateMealPlan,
  deleteMealPlan,
  type MealPlanUpdateRequest,
} from '@/libs/api/meal-plans'

export const MEAL_PLANS_QUERY_KEY = ['meal-plans'] as const

export function useMealPlans(userId: string) {
  return useQuery({
    queryKey: [...MEAL_PLANS_QUERY_KEY, userId],
    queryFn: () => getMealPlans(userId),
    // 食事プランは頻繁に変更される可能性があるため、短めのキャッシュ時間
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    // データ選択: APIレスポンスから実際のデータを抽出
    select: (response) => {
      if (response.success && response.data) {
        return response.data.meal_plans || []
      }
      return []
    },
    // エラー時のフォールバック
    placeholderData: (previousData) => previousData,
  })
}

export function useCreateMealPlan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createMealPlan,
    onSuccess: () => {
      // 成功時にキャッシュを無効化して最新データを取得
      queryClient.invalidateQueries({
        queryKey: MEAL_PLANS_QUERY_KEY,
      })
    },
    onError: (error) => {
      console.error('食事プラン作成エラー:', error)
    },
  })
}

export function useUpdateMealPlan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ planId, updateData }: { planId: string; updateData: MealPlanUpdateRequest }) =>
      updateMealPlan(planId, updateData),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: MEAL_PLANS_QUERY_KEY,
      })
    },
    onError: (error) => {
      console.error('食事プラン更新エラー:', error)
    },
  })
}

export function useDeleteMealPlan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteMealPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: MEAL_PLANS_QUERY_KEY,
      })
    },
    onError: (error) => {
      console.error('食事プラン削除エラー:', error)
    },
  })
}