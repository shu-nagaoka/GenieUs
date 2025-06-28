import { useQuery } from '@tanstack/react-query'
import {
  getScheduleEvents,
} from '@/libs/api/schedules'

export const SCHEDULE_EVENTS_QUERY_KEY = ['schedule-events'] as const

export function useScheduleEvents(userId: string) {
  return useQuery({
    queryKey: [...SCHEDULE_EVENTS_QUERY_KEY, userId],
    queryFn: () => getScheduleEvents({ user_id: userId }),
    staleTime: 5 * 60 * 1000, // 5 minutes (スケジュールは変更される可能性があるため短め)
    gcTime: 30 * 60 * 1000, // 30 minutes
    select: (response) => {
      if (response.success && response.data) {
        return response.data || []
      }
      return []
    },
    placeholderData: (previousData) => previousData,
  })
}