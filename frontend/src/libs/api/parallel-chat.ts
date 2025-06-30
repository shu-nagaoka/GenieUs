/**
 * パラレルチャットAPI
 * 
 * マルチエージェント並列処理機能のAPIクライアント
 */

import { API_BASE_URL } from '@/config/api'

export interface ParallelChatRequest {
  message: string
  selectedAgents: string[]
  userId: string
  sessionId: string
  context?: Record<string, string>
}

export interface AgentResponse {
  agent_id: string
  agent_name: string
  response: string
  confidence_score: number
  processing_time: number
  success: boolean
  error_message?: string
}

export interface ParallelChatResponse {
  success: boolean
  data?: {
    agents_responses: Record<string, string>
    agent_details: AgentResponse[]
    integrated_summary: string
    confidence_scores: Record<string, number>
    processing_time: number
  }
  message?: string
  error?: string
}

export interface AvailableAgent {
  id: string
  name: string
  description: string
  has_tools: boolean
  confidence_rating: string
}

export interface AvailableAgentsResponse {
  success: boolean
  data?: {
    agents: AvailableAgent[]
    max_agents: number
  }
  message?: string
  error?: string
}

/**
 * パラレルチャット実行
 */
export async function executeParallelChat(
  request: ParallelChatRequest
): Promise<ParallelChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/streaming/parallel-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: request.message,
        selected_agents: request.selectedAgents,
        user_id: request.userId,
        session_id: request.sessionId,
        context: request.context || {},
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data: ParallelChatResponse = await response.json()
    return data
  } catch (error) {
    console.error('❌ パラレルチャットAPIエラー:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      message: 'パラレルチャット処理中にエラーが発生しました',
    }
  }
}

/**
 * 利用可能なエージェント一覧取得
 */
export async function getAvailableAgents(): Promise<AvailableAgentsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/streaming/available-agents`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data: AvailableAgentsResponse = await response.json()
    return data
  } catch (error) {
    console.error('❌ 利用可能エージェント取得APIエラー:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      message: 'エージェント情報の取得中にエラーが発生しました',
    }
  }
}