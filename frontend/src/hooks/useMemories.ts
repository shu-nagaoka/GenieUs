import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getMemories,
  toggleMemoryFavorite,
} from '@/libs/api/memories'

export const MEMORIES_QUERY_KEY = ['memories'] as const

export function useMemories(userId: string) {
  return useQuery({
    queryKey: [...MEMORIES_QUERY_KEY, userId],
    queryFn: () => getMemories({ user_id: userId }),
    staleTime: 2 * 60 * 1000, // 2 minutes (思い出は新しく追加される可能性があるため短め)
    gcTime: 15 * 60 * 1000, // 15 minutes
    select: (response) => {
      if (response.success && response.data) {
        return response.data || []
      }
      return []
    },
    placeholderData: (previousData) => previousData,
  })
}

export function useToggleMemoryFavorite() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ memoryId, userId }: { memoryId: string; userId: string }) =>
      toggleMemoryFavorite(memoryId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: MEMORIES_QUERY_KEY,
      })
    },
    onError: (error) => {
      console.error('思い出お気に入り切り替えエラー:', error)
    },
  })
}