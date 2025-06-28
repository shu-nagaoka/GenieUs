import { useQuery } from '@tanstack/react-query'
import { getAgents, type Agent, type ApiResponse } from '@/libs/api/agents'

export const AGENTS_QUERY_KEY = ['agents'] as const

export function useAgents() {
  return useQuery({
    queryKey: AGENTS_QUERY_KEY,
    queryFn: async () => {
      console.log('🔄 Fetching agents...')
      const result = await getAgents()
      console.log('📊 Agents API result:', result)
      return result
    },
    // エージェントデータは静的なので長時間キャッシュ
    staleTime: 60 * 60 * 1000, // 1 hour
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
    // エラー時のフォールバック用
    placeholderData: (previousData) => previousData,
    select: (response: ApiResponse<Agent[]>) => {
      console.log('🔍 Selecting data from response:', response)
      // APIレスポンスから実際のデータを取得
      if (response.success && response.data) {
        // アクティブなエージェントのみフィルタリング
        const activeAgents = response.data.filter(agent => agent.status === 'active')
        console.log('✅ Active agents found:', activeAgents.length)
        return activeAgents
      }
      console.log('❌ No data found in response')
      return []
    },
    // エラー処理を強化
    throwOnError: false,
    retry: (failureCount, error) => {
      console.error('🚨 Query failed:', error)
      return failureCount < 3
    },
  })
}