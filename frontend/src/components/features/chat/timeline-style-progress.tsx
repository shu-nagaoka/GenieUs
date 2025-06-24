'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { 
  IoSettings,
  IoSparkles,
  IoCheckmarkCircle,
  IoAlertCircle,
  IoTime,
  IoCode,
  IoImage,
  IoVolumeHigh,
  IoDocumentText,
  IoTrendingUp,
  IoSearch,
  IoFlash,
  IoEllipsisHorizontal
} from 'react-icons/io5'
import { GiMagicLamp } from 'react-icons/gi'

interface ProgressUpdate {
  type: string
  message: string
  data: any
}

interface TimelineStep {
  id: string
  message: string
  type: string
  timestamp: number
  status: 'active' | 'completed' | 'pending'
  icon: React.ReactNode
  tools?: string[]
}

interface TimelineStyleProgressProps {
  message: string
  userId?: string
  sessionId?: string
  onComplete?: (response: string) => void
  onError?: (error: string) => void
  className?: string
}

export function TimelineStyleProgress({
  message,
  userId = "frontend_user",
  sessionId = "default-session",
  onComplete,
  onError,
  className = ""
}: TimelineStyleProgressProps) {
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([])
  const [isComplete, setIsComplete] = useState(false)
  const [finalResponse, setFinalResponse] = useState<string>("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [timelineSteps, setTimelineSteps] = useState<TimelineStep[]>([])
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const eventSourceRef = useRef<EventSource | null>(null)

  // ツールアイコンマップ
  const getToolIcon = (toolName: string) => {
    if (toolName.includes('image') || toolName.includes('analyze_child_image')) {
      return <IoImage className="h-4 w-4" />
    }
    if (toolName.includes('voice') || toolName.includes('analyze_child_voice')) {
      return <IoVolumeHigh className="h-4 w-4" />
    }
    if (toolName.includes('file') || toolName.includes('manage_child_files')) {
      return <IoDocumentText className="h-4 w-4" />
    }
    if (toolName.includes('record') || toolName.includes('manage_child_records')) {
      return <IoTrendingUp className="h-4 w-4" />
    }
    return <IoCode className="h-4 w-4" />
  }

  // ステップタイプからアイコンを取得
  const getStepIcon = (type: string) => {
    switch (type) {
      case 'thinking':
        return <IoSparkles className="h-4 w-4" />
      case 'tools_available':
        return <IoSettings className="h-4 w-4" />
      case 'agent_start':
        return <IoSearch className="h-4 w-4" />
      case 'tool_detected':
        return <IoFlash className="h-4 w-4" />
      case 'tool_executing':
        return <IoTime className="h-4 w-4" />
      case 'tool_progress':
        return <IoEllipsisHorizontal className="h-4 w-4" />
      case 'tool_response':
        return <IoCheckmarkCircle className="h-4 w-4" />
      case 'tool_complete':
        return <IoCheckmarkCircle className="h-4 w-4" />
      case 'response_generating':
        return <GiMagicLamp className="h-4 w-4" />
      case 'complete':
        return <IoCheckmarkCircle className="h-4 w-4" />
      case 'error':
        return <IoAlertCircle className="h-4 w-4" />
      default:
        return <IoEllipsisHorizontal className="h-4 w-4" />
    }
  }

  // ステップタイプから色を取得
  const getStepColor = (type: string, status: string) => {
    if (status === 'completed') return 'text-green-600 bg-green-100 border-green-200'
    if (status === 'active') {
      switch (type) {
        case 'thinking':
          return 'text-blue-600 bg-blue-100 border-blue-200'
        case 'tool_executing':
          return 'text-orange-600 bg-orange-100 border-orange-200'
        case 'response_generating':
          return 'text-amber-600 bg-amber-100 border-amber-200'
        default:
          return 'text-purple-600 bg-purple-100 border-purple-200'
      }
    }
    return 'text-gray-400 bg-gray-50 border-gray-200'
  }

  // ストリーミング開始
  const startStreaming = async () => {
    if (isStreaming) return

    setIsStreaming(true)
    setProgressUpdates([])
    setIsComplete(false)
    setFinalResponse("")
    setTimelineSteps([])
    setCurrentStepIndex(0)

    try {
      // メッセージから会話履歴を解析
      let actualMessage = message
      let conversationHistory = null
      let actualSessionId = sessionId
      let actualUserId = userId

      try {
        const parsed = JSON.parse(message)
        if (parsed.message) {
          actualMessage = parsed.message
          conversationHistory = parsed.conversation_history || null
          actualSessionId = parsed.session_id || sessionId
          actualUserId = parsed.user_id || userId
        }
      } catch (e) {
        // JSON parsing failed, use message as is
      }

      const requestBody: any = {
        message: actualMessage,
        user_id: actualUserId,
        session_id: actualSessionId
      }

      // 会話履歴があれば追加
      if (conversationHistory && conversationHistory.length > 0) {
        requestBody.conversation_history = conversationHistory
      }

      const response = await fetch('http://localhost:8000/api/v1/streaming/streaming-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error('ストリーミング開始に失敗しました')
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('ストリーミングデータの読み取りに失敗しました')
      }

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              const update: ProgressUpdate = {
                type: data.type,
                message: data.message,
                data: data.data || {}
              }

              setProgressUpdates(prev => [...prev, update])

              // タイムラインステップを追加
              const newStep: TimelineStep = {
                id: Date.now().toString() + Math.random(),
                message: data.message,
                type: data.type,
                timestamp: Date.now(),
                status: 'active',
                icon: getStepIcon(data.type),
                tools: data.data?.tools || undefined
              }

              setTimelineSteps(prev => {
                // 前のステップを完了状態に
                const updated = prev.map(step => ({
                  ...step,
                  status: 'completed' as const
                }))
                return [...updated, newStep]
              })

              setCurrentStepIndex(prev => prev + 1)

              // 最終レスポンスの場合
              if (data.type === 'final_response') {
                setFinalResponse(data.message)
              }

              // 完了の場合
              if (data.type === 'complete') {
                setIsComplete(true)
                setIsStreaming(false)
                
                // 最後のステップも完了状態に
                setTimelineSteps(prev => 
                  prev.map(step => ({
                    ...step,
                    status: 'completed' as const
                  }))
                )
                
                if (onComplete) {
                  onComplete(finalResponse || data.data?.response || "")
                }
              }

              // エラーの場合
              if (data.type === 'error') {
                setIsStreaming(false)
                if (onError) {
                  onError(data.message)
                }
              }
            } catch (e) {
              console.warn('JSON parse error:', e)
            }
          }
        }
      }

    } catch (error) {
      console.error('Streaming error:', error)
      setIsStreaming(false)
      if (onError) {
        onError(error instanceof Error ? error.message : 'ストリーミングエラー')
      }
    }
  }

  // コンポーネントマウント時に自動開始
  useEffect(() => {
    startStreaming()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [message])

  return (
    <div className={`space-y-4 ${className}`}>
      {/* タイムライン表示 */}
      <Card className="bg-white/95 backdrop-blur-sm border border-gray-200 shadow-lg overflow-hidden">
        <CardContent className="p-0">
          {/* ヘッダー */}
          <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <GiMagicLamp className="h-4 w-4 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">AI相談員の処理状況</h3>
                <p className="text-sm text-gray-600">リアルタイムで進捗をお伝えします</p>
              </div>
              {isStreaming && (
                <div className="ml-auto flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                  </div>
                  <span className="text-xs text-gray-500">処理中</span>
                </div>
              )}
            </div>
          </div>

          {/* タイムライン */}
          <div className="p-4 max-h-80 overflow-y-auto">
            <div className="space-y-4">
              {timelineSteps.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex gap-4 transition-all duration-500 ${
                    step.status === 'active' ? 'animate-in slide-in-from-right-2' : ''
                  }`}
                >
                  {/* タイムラインライン */}
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${
                      getStepColor(step.type, step.status)
                    }`}>
                      {step.status === 'active' && step.type === 'tool_executing' ? (
                        <div className="animate-spin">
                          {step.icon}
                        </div>
                      ) : (
                        step.icon
                      )}
                    </div>
                    {index < timelineSteps.length - 1 && (
                      <div className={`w-0.5 h-8 mt-2 transition-all duration-500 ${
                        step.status === 'completed' ? 'bg-green-300' : 'bg-gray-200'
                      }`} />
                    )}
                  </div>

                  {/* ステップ内容 */}
                  <div className="flex-1 pb-4">
                    <div className={`font-medium text-sm transition-all duration-300 ${
                      step.status === 'completed' ? 'text-gray-700' : 
                      step.status === 'active' ? 'text-gray-900' : 'text-gray-500'
                    }`}>
                      {step.message}
                    </div>
                    
                    {/* ツール表示 */}
                    {step.tools && step.tools.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {step.tools.map((tool, toolIndex) => (
                          <div
                            key={toolIndex}
                            className="flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs text-gray-600"
                          >
                            {getToolIcon(tool)}
                            <span>{tool.replace('_', ' ')}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <div className="text-xs text-gray-400 mt-1">
                      {new Date(step.timestamp).toLocaleTimeString('ja-JP', { 
                        hour: '2-digit', 
                        minute: '2-digit',
                        second: '2-digit'
                      })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 最終レスポンス表示 */}
      {finalResponse && isComplete && (
        <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="h-6 w-6 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <IoCheckmarkCircle className="h-3 w-3 text-white" />
              </div>
              <span className="text-sm font-medium text-green-700">回答完了</span>
            </div>
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-line">
              {finalResponse}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}