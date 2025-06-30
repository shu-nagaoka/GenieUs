import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  searchMealRecords,
  getMealRecord,
  createMealRecord,
  updateMealRecord,
  deleteMealRecord,
  getNutritionSummary,
  getMealRecordsByChild,
  getTodayMealRecords,
  getWeeklyNutritionSummary,
  type SearchMealRecordsRequest,
  type CreateMealRecordRequest,
  type UpdateMealRecordRequest,
  type MealRecord,
  type NutritionSummary,
} from '@/libs/api/meal-records'

export const MEAL_RECORDS_QUERY_KEY = ['meal-records'] as const
export const MEAL_RECORD_QUERY_KEY = ['meal-record'] as const
export const NUTRITION_SUMMARY_QUERY_KEY = ['nutrition-summary'] as const

// === Query Hooks ===

/**
 * 食事記録検索・一覧取得フック
 */
export function useMealRecords(searchRequest: SearchMealRecordsRequest) {
  return useQuery({
    queryKey: [...MEAL_RECORDS_QUERY_KEY, 'search', searchRequest],
    queryFn: () => searchMealRecords(searchRequest),
    staleTime: 5 * 60 * 1000, // 5 minutes (食事記録は比較的頻繁に更新される)
    gcTime: 30 * 60 * 1000, // 30 minutes
    select: (response) => {
      if (response.success && response.data) {
        return {
          meal_records: response.data.meal_records || [],
          total_count: response.data.total_count || 0,
        }
      }
      return {
        meal_records: [],
        total_count: 0,
      }
    },
    placeholderData: (previousData) => previousData,
  })
}

/**
 * 子供の食事記録一覧取得フック
 */
export function useMealRecordsByChild(childId: string, limit: number = 50) {
  return useQuery({
    queryKey: [...MEAL_RECORDS_QUERY_KEY, 'by-child', childId, limit],
    queryFn: () => getMealRecordsByChild(childId, limit),
    enabled: !!childId && childId.trim() !== '', // childIdが有効な場合のみAPIを呼び出す
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    select: (response) => {
      if (response.success && response.data) {
        return response.data.meal_records || []
      }
      return []
    },
    placeholderData: (previousData) => previousData,
  })
}

/**
 * 今日の食事記録取得フック
 */
export function useTodayMealRecords(childId: string) {
  return useQuery({
    queryKey: [...MEAL_RECORDS_QUERY_KEY, 'today', childId],
    queryFn: () => getTodayMealRecords(childId),
    enabled: !!childId && childId.trim() !== '', // childIdが有効な場合のみAPIを呼び出す
    staleTime: 2 * 60 * 1000, // 2 minutes (今日の記録は頻繁に確認する)
    gcTime: 10 * 60 * 1000, // 10 minutes
    select: (response) => {
      if (response.success && response.data) {
        return response.data.meal_records || []
      }
      return []
    },
    placeholderData: (previousData) => previousData,
  })
}

/**
 * 単一食事記録取得フック
 */
export function useMealRecord(mealRecordId: string) {
  return useQuery({
    queryKey: [...MEAL_RECORD_QUERY_KEY, mealRecordId],
    queryFn: () => getMealRecord(mealRecordId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    select: (response) => {
      if (response.success && response.data) {
        return response.data.meal_record
      }
      return null
    },
    placeholderData: (previousData) => previousData,
  })
}

/**
 * 栄養サマリー取得フック
 */
export function useNutritionSummary(
  childId: string,
  startDate?: string,
  endDate?: string
) {
  return useQuery({
    queryKey: [...NUTRITION_SUMMARY_QUERY_KEY, childId, startDate, endDate],
    queryFn: () => getNutritionSummary(childId, startDate, endDate),
    enabled: !!childId && childId.trim() !== '', // childIdが有効な場合のみAPIを呼び出す
    staleTime: 10 * 60 * 1000, // 10 minutes (栄養サマリーは時間をかけて変化する)
    gcTime: 60 * 60 * 1000, // 1 hour
    select: (response) => {
      if (response.success && response.data) {
        return response.data.summary
      }
      return null
    },
    placeholderData: (previousData) => previousData,
  })
}

/**
 * 今週の栄養サマリー取得フック
 */
export function useWeeklyNutritionSummary(childId: string) {
  return useQuery({
    queryKey: [...NUTRITION_SUMMARY_QUERY_KEY, 'weekly', childId],
    queryFn: () => getWeeklyNutritionSummary(childId),
    enabled: !!childId && childId.trim() !== '', // childIdが有効な場合のみAPIを呼び出す
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    select: (response) => {
      if (response.success && response.data) {
        return response.data.summary
      }
      return null
    },
    placeholderData: (previousData) => previousData,
  })
}

// === Mutation Hooks ===

/**
 * 食事記録作成ミューテーション
 */
export function useCreateMealRecord() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request: CreateMealRecordRequest) => createMealRecord(request),
    onSuccess: (data, variables) => {
      // 関連するクエリキーを無効化してリフェッチ
      queryClient.invalidateQueries({ queryKey: MEAL_RECORDS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: NUTRITION_SUMMARY_QUERY_KEY })
      
      // 今日の記録は特に頻繁に更新されるため個別に無効化
      queryClient.invalidateQueries({ 
        queryKey: [...MEAL_RECORDS_QUERY_KEY, 'today', variables.child_id] 
      })
      queryClient.invalidateQueries({ 
        queryKey: [...MEAL_RECORDS_QUERY_KEY, 'by-child', variables.child_id] 
      })
    },
    onError: (error) => {
      console.error('Create meal record mutation error:', error)
    },
  })
}

/**
 * 食事記録更新ミューテーション
 */
export function useUpdateMealRecord() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ mealRecordId, request }: { 
      mealRecordId: string
      request: UpdateMealRecordRequest 
    }) => updateMealRecord(mealRecordId, request),
    onSuccess: (data, variables) => {
      // 更新された記録の詳細を無効化
      queryClient.invalidateQueries({ 
        queryKey: [...MEAL_RECORD_QUERY_KEY, variables.mealRecordId] 
      })
      
      // 関連するリストと統計を無効化
      queryClient.invalidateQueries({ queryKey: MEAL_RECORDS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: NUTRITION_SUMMARY_QUERY_KEY })
    },
    onError: (error) => {
      console.error('Update meal record mutation error:', error)
    },
  })
}

/**
 * 食事記録削除ミューテーション
 */
export function useDeleteMealRecord() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (mealRecordId: string) => deleteMealRecord(mealRecordId),
    onSuccess: (data, variables) => {
      // 削除された記録の詳細を削除
      queryClient.removeQueries({ 
        queryKey: [...MEAL_RECORD_QUERY_KEY, variables] 
      })
      
      // 関連するリストと統計を無効化
      queryClient.invalidateQueries({ queryKey: MEAL_RECORDS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: NUTRITION_SUMMARY_QUERY_KEY })
    },
    onError: (error) => {
      console.error('Delete meal record mutation error:', error)
    },
  })
}

// === 便利なカスタムフック ===

/**
 * 子供の食事記録の完全な管理フック
 * @param childId 子供ID
 * @param options オプション設定
 */
export function useMealRecordsManager(
  childId: string, 
  options?: {
    limit?: number
    enableTodayRecords?: boolean
    enableWeeklySummary?: boolean
  }
) {
  const { limit = 50, enableTodayRecords = true, enableWeeklySummary = true } = options || {}

  // 基本の食事記録リスト
  const mealRecordsQuery = useMealRecordsByChild(childId, limit)
  
  // 今日の記録 (オプション)
  const todayRecordsQuery = useTodayMealRecords(childId)
  const todayRecords = enableTodayRecords ? todayRecordsQuery.data : []

  // 今週の栄養サマリー (オプション)
  const weeklySummaryQuery = useWeeklyNutritionSummary(childId)
  const weeklySummary = enableWeeklySummary ? weeklySummaryQuery.data : null

  // ミューテーション
  const createMutation = useCreateMealRecord()
  const updateMutation = useUpdateMealRecord()
  const deleteMutation = useDeleteMealRecord()

  // ローディング状態の統合
  const isLoading = mealRecordsQuery.isLoading || 
    (enableTodayRecords && todayRecordsQuery.isLoading) ||
    (enableWeeklySummary && weeklySummaryQuery.isLoading)

  // エラー状態の統合
  const error = mealRecordsQuery.error || 
    (enableTodayRecords && todayRecordsQuery.error) ||
    (enableWeeklySummary && weeklySummaryQuery.error)

  return {
    // データ
    mealRecords: mealRecordsQuery.data || [],
    todayRecords,
    weeklySummary,
    
    // 状態
    isLoading,
    error,
    
    // アクション
    createMealRecord: createMutation.mutate,
    updateMealRecord: updateMutation.mutate,
    deleteMealRecord: deleteMutation.mutate,
    
    // ミューテーション状態
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    
    // リフレッシュ
    refetch: () => {
      mealRecordsQuery.refetch()
      if (enableTodayRecords) todayRecordsQuery.refetch()
      if (enableWeeklySummary) weeklySummaryQuery.refetch()
    },
  }
}