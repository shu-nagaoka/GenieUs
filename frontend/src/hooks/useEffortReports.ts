import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getEffortRecords,
  getEffortRecordsStats,
  generateEffortReport,
  deleteEffortRecord,
} from '@/libs/api/effort-records'

export const EFFORT_RECORDS_QUERY_KEY = ['effort-records'] as const
export const EFFORT_STATS_QUERY_KEY = ['effort-stats'] as const

export function useEffortRecords(userId: string) {
  return useQuery({
    queryKey: [...EFFORT_RECORDS_QUERY_KEY, userId],
    queryFn: () => getEffortRecords({ user_id: userId }),
    staleTime: 10 * 60 * 1000, // 10 minutes (努力記録は時間をかけて蓄積されるため)
    gcTime: 60 * 60 * 1000, // 1 hour
    select: (response) => {
      if (response.success && response.data) {
        return response.data || []
      }
      return []
    },
    placeholderData: (previousData) => previousData,
  })
}

export function useEffortStats(userId: string, periodDays: number) {
  return useQuery({
    queryKey: [...EFFORT_STATS_QUERY_KEY, userId, periodDays],
    queryFn: () => getEffortRecordsStats(userId, periodDays),
    staleTime: 5 * 60 * 1000, // 5 minutes (統計は定期的に更新される)
    gcTime: 30 * 60 * 1000, // 30 minutes
    select: (response) => {
      if (response.success && response.data) {
        return response.data
      }
      return {
        total_efforts: 0,
        streak_days: 0,
        average_score: 0,
        total_reports: 0,
      }
    },
    placeholderData: (previousData) => previousData,
  })
}

export function useGenerateEffortReport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, periodDays }: { userId: string; periodDays: number }) =>
      generateEffortReport(userId, periodDays),
    onSuccess: (data, variables) => {
      // 成功時にクエリを無効化して再取得
      queryClient.invalidateQueries({
        queryKey: [...EFFORT_RECORDS_QUERY_KEY, variables.userId],
      })
      queryClient.invalidateQueries({
        queryKey: [...EFFORT_STATS_QUERY_KEY, variables.userId],
      })
    },
  })
}

export function useDeleteEffortRecord() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ recordId, userId }: { recordId: string; userId: string }) =>
      deleteEffortRecord(recordId, userId),
    onSuccess: (data, variables) => {
      // 成功時にクエリを無効化して再取得
      queryClient.invalidateQueries({
        queryKey: [...EFFORT_RECORDS_QUERY_KEY, variables.userId],
      })
      queryClient.invalidateQueries({
        queryKey: [...EFFORT_STATS_QUERY_KEY, variables.userId],
      })
    },
  })
}