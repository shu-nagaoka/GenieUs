/**
 * パラレルチャットReact Queryフック
 * 
 * マルチエージェント並列処理機能のReact Query統合
 */

import { useMutation, useQuery } from '@tanstack/react-query'
import { 
  executeParallelChat, 
  getAvailableAgents,
  type ParallelChatRequest,
  type ParallelChatResponse,
  type AvailableAgentsResponse,
} from '@/libs/api/parallel-chat'

/**
 * パラレルチャット実行Mutation
 */
export function useParallelChat() {
  return useMutation<ParallelChatResponse, Error, ParallelChatRequest>({
    mutationFn: executeParallelChat,
    onSuccess: (data) => {
      if (data.success) {
        console.log('✅ パラレルチャット成功:', {
          processingTime: data.data?.processing_time,
          agentsCount: Object.keys(data.data?.agents_responses || {}).length,
        })
      } else {
        console.error('❌ パラレルチャット失敗:', data.error)
      }
    },
    onError: (error) => {
      console.error('❌ パラレルチャットMutationエラー:', error)
    },
  })
}

/**
 * 利用可能エージェント一覧取得Query
 */
export function useAvailableAgents() {
  return useQuery<AvailableAgentsResponse, Error>({
    queryKey: ['available-agents'],
    queryFn: getAvailableAgents,
    staleTime: 5 * 60 * 1000, // 5分間フレッシュ
    gcTime: 10 * 60 * 1000, // 10分間キャッシュ保持
    refetchOnWindowFocus: false,
    retry: 2,
  })
}