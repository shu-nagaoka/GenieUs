'use client'

import React, { useState, useEffect } from 'react'
import { Users, CheckCircle, AlertCircle, Clock, Sparkles, Brain } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

interface AgentStatus {
  id: string
  name: string
  icon: string
  status: 'waiting' | 'analyzing' | 'completed' | 'error'
  progress: number
}

interface MultiAgentProgressProps {
  message: string
  selectedAgents: string[]
  userId?: string
  sessionId?: string
  onComplete?: (response: string, agentData?: any) => void
  onError?: (error: string) => void
  className?: string
}

const AGENT_CONFIG = {
  sleep_specialist: {
    name: '睡眠のジーニー',
    icon: '😴',
    description: '睡眠・夜泣き専門'
  },
  nutrition_specialist: {
    name: '栄養のジーニー', 
    icon: '🍎',
    description: '食事・栄養専門'
  },
  development_specialist: {
    name: '発達のジーニー',
    icon: '✨',
    description: '発達・成長専門'
  },
  health_specialist: {
    name: '健康のジーニー',
    icon: '🏥',
    description: '健康・医療専門'
  },
  behavior_specialist: {
    name: 'しつけのジーニー',
    icon: '🎯',
    description: '行動・しつけ専門'
  },
  play_learning_specialist: {
    name: '遊び学習のジーニー',
    icon: '🎨',
    description: '遊び・学習専門'
  },
  safety_specialist: {
    name: '安全のジーニー',
    icon: '🛡️',
    description: '安全・事故防止専門'
  },
  work_life_specialist: {
    name: '両立のジーニー',
    icon: '💼',
    description: '仕事両立専門'
  },
  mental_care_specialist: {
    name: 'メンタルのジーニー',
    icon: '💙',
    description: '心理・メンタル専門'
  },
  search_specialist: {
    name: '検索のジーニー',
    icon: '🔍',
    description: '情報検索専門'
  }
}

export function MultiAgentProgress({ 
  message,
  selectedAgents,
  userId = 'frontend_user',
  sessionId = 'default-session',
  onComplete,
  onError,
  className = "" 
}: MultiAgentProgressProps) {
  const [isProcessing, setIsProcessing] = useState(true)
  const [agents, setAgents] = useState<AgentStatus[]>([])
  const [currentPhase, setCurrentPhase] = useState<'initializing' | 'analyzing' | 'integrating' | 'completed'>('initializing')
  const [error, setError] = useState<string | undefined>(undefined)
  const [overallProgress, setOverallProgress] = useState(0)

  // エージェント状態初期化
  useEffect(() => {
    const initialAgents: AgentStatus[] = selectedAgents.map(agentId => ({
      id: agentId,
      name: AGENT_CONFIG[agentId]?.name || agentId,
      icon: AGENT_CONFIG[agentId]?.icon || '🤖',
      status: 'waiting',
      progress: 0
    }))
    setAgents(initialAgents)
  }, [selectedAgents])

  // マルチエージェント処理実行
  useEffect(() => {
    const executeMultiAgentAnalysis = async () => {
      setIsProcessing(true)
      setError(undefined)
      setCurrentPhase('initializing')
      
      try {
        // Phase 1: 初期化
        setCurrentPhase('initializing')
        updateAgentsStatus('waiting')
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Phase 2: 各エージェント分析開始
        setCurrentPhase('analyzing')
        updateAgentsStatus('analyzing')
        
        // 段階的に各エージェントの進捗を更新
        for (let i = 0; i < selectedAgents.length; i++) {
          await new Promise(resolve => setTimeout(resolve, 400))
          updateSingleAgentProgress(selectedAgents[i], 30 + (i * 15))
        }
        
        // 実際のAPI呼び出し（タイムアウト延長）
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 60000) // 60秒タイムアウト
        
        const response = await fetch(`http://localhost:8080/api/streaming/parallel-chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message,
            selected_agents: selectedAgents,
            user_id: userId,
            session_id: sessionId,
            context: {}
          }),
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        
        if (data.success) {
          console.log('🎯 マルチエージェント成功レスポンス:', data)
          
          // Phase 3: 統合処理
          setCurrentPhase('integrating')
          updateAgentsStatus('completed')
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          // Phase 4: 完了
          setCurrentPhase('completed')
          setOverallProgress(100)
          
          // 新しいレスポンス形式に対応: 各エージェントのレスポンスを統合
          const responses = data.data?.responses || []
          let finalResponse = ''
          
          if (responses.length > 0) {
            // 各専門家の回答を組み合わせ
            finalResponse = responses.map((resp: any, index: number) => 
              `**${resp.agent_name}**:\n${resp.response}`
            ).join('\n\n---\n\n')
          } else {
            finalResponse = data.message || '複数の専門家による分析が完了しました'
          }
          
          console.log('📝 最終統合レスポンス:', finalResponse)
          onComplete?.(finalResponse, data.data)
        } else {
          throw new Error(data.error || '分析中にエラーが発生しました')
        }
        
      } catch (err) {
        console.error('Multi-agent analysis error:', err)
        const errorMessage = err instanceof Error ? err.message : '分析中にエラーが発生しました'
        setError(errorMessage)
        updateAgentsStatus('error')
        onError?.(errorMessage)
      } finally {
        setIsProcessing(false)
      }
    }

    executeMultiAgentAnalysis()
  }, [message, selectedAgents, userId, sessionId, onComplete, onError])

  // 進捗更新ヘルパー関数
  const updateAgentsStatus = (status: AgentStatus['status']) => {
    setAgents(prev => prev.map(agent => ({
      ...agent,
      status,
      progress: status === 'completed' ? 100 : status === 'analyzing' ? 60 : status === 'waiting' ? 10 : 0
    })))
  }

  const updateSingleAgentProgress = (agentId: string, progress: number) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId 
        ? { ...agent, progress, status: 'analyzing' as const }
        : agent
    ))
  }

  // 全体進捗計算
  useEffect(() => {
    const totalProgress = agents.reduce((sum, agent) => sum + agent.progress, 0)
    const avgProgress = agents.length > 0 ? totalProgress / agents.length : 0
    setOverallProgress(avgProgress)
  }, [agents])

  const getPhaseMessage = () => {
    switch (currentPhase) {
      case 'initializing':
        return `${selectedAgents.length}人の専門家を準備中...`
      case 'analyzing':
        return '専門家が並列分析中...'
      case 'integrating':
        return '専門家の意見を統合中...'
      case 'completed':
        return '✅ 多角的分析が完了しました'
      default:
        return '処理中...'
    }
  }

  return (
    <Card className={`border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 ${className}`}>
      <CardContent className="p-6">
        {/* シンプルなヘッダー */}
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-amber-500 rounded-full text-white">
            <Users className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-amber-800">マルチエージェント分析</h3>
            <p className="text-sm text-amber-600">{getPhaseMessage()}</p>
          </div>
          <Badge variant="outline" className="border-amber-300 text-amber-700">
            {selectedAgents.length}人の専門家
          </Badge>
        </div>

        {/* シンプルな全体進捗のみ */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-amber-700">分析進捗</span>
            <span className="text-sm text-amber-600">{Math.round(overallProgress)}%</span>
          </div>
          <Progress value={overallProgress} className="h-3 bg-amber-100" />
        </div>

        {/* エラー表示 */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm font-medium">エラー</span>
            </div>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        )}

        {/* 統合中メッセージ */}
        {currentPhase === 'integrating' && (
          <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center gap-2 text-purple-700">
              <Brain className="w-4 h-4 animate-pulse" />
              <span className="text-sm font-medium">統合処理中</span>
            </div>
            <p className="text-sm text-purple-600 mt-1">
              各専門家の意見を統合し、総合的なアドバイスを作成しています...
            </p>
          </div>
        )}

        {/* 完了メッセージ */}
        {currentPhase === 'completed' && !error && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 text-green-700">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">分析完了</span>
            </div>
            <p className="text-sm text-green-600 mt-1">
              {selectedAgents.length}人の専門家による多角的分析が完了しました
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// シンプルなインライン分析インジケーター
export function MultiAgentInlineIndicator({ 
  isProcessing, 
  agentCount 
}: { 
  isProcessing: boolean
  agentCount: number 
}) {
  if (!isProcessing) return null

  return (
    <div className="flex items-center gap-2 text-amber-600 text-sm">
      <Users className="h-4 w-4 animate-pulse" />
      <span>{agentCount}人で分析中...</span>
      <div className="flex gap-1">
        <div className="h-1 w-1 bg-amber-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="h-1 w-1 bg-amber-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="h-1 w-1 bg-amber-400 rounded-full animate-bounce"></div>
      </div>
    </div>
  )
}