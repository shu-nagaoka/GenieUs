'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { 
  IoSparkles,
  IoCheckmarkCircle,
  IoAlertCircle,
  IoTime,
  IoImage,
  IoVolumeHigh,
  IoDocumentText,
  IoTrendingUp,
  IoHeart,
  IoSunny
} from 'react-icons/io5'
import { GiMagicLamp } from 'react-icons/gi'

interface ProgressUpdate {
  type: string
  message: string
  data: any
}

interface GenieStep {
  id: string
  message: string
  type: string
  timestamp: number
  status: 'active' | 'completed' | 'pending'
  icon: React.ReactNode
  tools?: string[]
  specialist?: {
    name: string
    description: string
  } | null
}

interface GenieStyleProgressProps {
  message: string
  userId?: string
  sessionId?: string
  onComplete?: (response: string) => void
  onError?: (error: string) => void
  className?: string
}

export function GenieStyleProgress({
  message,
  userId = "frontend_user",
  sessionId = "default-session",
  onComplete,
  onError,
  className = ""
}: GenieStyleProgressProps) {
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([])
  const [isComplete, setIsComplete] = useState(false)
  const [finalResponse, setFinalResponse] = useState<string>("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [genieSteps, setGenieSteps] = useState<GenieStep[]>([])
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const eventSourceRef = useRef<EventSource | null>(null)
  const timelineRef = useRef<HTMLDivElement>(null)

  // ツールアイコンマップ（温かみのある表現）
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
    return <IoSparkles className="h-4 w-4" />
  }

  // 専門家情報の表示
  const getSpecialistDisplay = (data: any) => {
    if (data?.specialist_name) {
      return {
        name: data.specialist_name,
        description: data.specialist_description || ""
      }
    }
    return null
  }

  // ツールの日本語名変換
  const getToolDisplayName = (toolName: string) => {
    const toolMap: Record<string, string> = {
      'analyze_child_image': '画像解析',
      'analyze_child_voice': '音声解析', 
      'manage_child_records': '記録管理',
      'manage_child_files': 'ファイル管理',
      'childcare_consultation': '子育て相談',
      'image_processing': '画像処理',
      'voice_processing': '音声処理',
      'data_analysis': 'データ分析',
      'file_organization': 'ファイル整理',
      'general_advice': '総合アドバイス',
      'sequential_analysis': '連携分析',
      'multi_step_processing': '段階的処理',
      'parallel_analysis': '並列分析',
      'comprehensive_evaluation': '総合評価',
      'general_support': '一般サポート'
    }
    return toolMap[toolName] || toolName.replace('_', ' ')
  }

  // Genieらしいメッセージに変換（よりモダンに）
  const getGenieMessage = (type: string, originalMessage: string, data: any = {}) => {
    const specialist = getSpecialistDisplay(data)
    
    switch (type) {
      case 'start':
        return '✨ Genieがお手伝いを始めます'
      case 'agent_starting':
        return '🪔 魔法のランプを準備中...'
      case 'agent_selecting':
        return specialist ? 
          `🎯 ${specialist.name}を選択中...` :
          '🌟 最適なサポート方法を考えています'
      case 'agent_executing':
        return specialist ? 
          `💫 ${specialist.name}が分析中...` :
          '💫 Genieが心を込めて分析中...'
      case 'analysis_complete':
        return '🎯 分析が完了しました'
      case 'final_response':
        return originalMessage
      case 'complete':
        return '✅ お手伝い完了です！'
      case 'error':
        return '😔 申し訳ございません...'
      default:
        return originalMessage
    }
  }

  // ステップタイプからアイコンを取得（Genieテーマ）
  const getStepIcon = (type: string) => {
    switch (type) {
      case 'start':
        return <GiMagicLamp className="h-4 w-4" />
      case 'agent_starting':
        return <IoSparkles className="h-4 w-4" />
      case 'agent_selecting':
        return <IoSunny className="h-4 w-4" />
      case 'agent_executing':
        return <IoHeart className="h-4 w-4" />
      case 'analysis_complete':
        return <IoCheckmarkCircle className="h-4 w-4" />
      case 'final_response':
        return <GiMagicLamp className="h-4 w-4" />
      case 'complete':
        return <IoCheckmarkCircle className="h-4 w-4" />
      case 'error':
        return <IoAlertCircle className="h-4 w-4" />
      default:
        return <IoSparkles className="h-4 w-4" />
    }
  }

  // フラットで温かみのある色設定
  const getStepColor = (type: string, status: string) => {
    if (status === 'completed') return 'text-green-600 bg-green-100 border-green-300'
    if (status === 'active') {
      switch (type) {
        case 'start':
        case 'agent_starting':
          return 'text-amber-600 bg-amber-100 border-amber-300'
        case 'agent_selecting':
          return 'text-orange-600 bg-orange-100 border-orange-300'
        case 'agent_executing':
          return 'text-rose-600 bg-rose-100 border-rose-300'
        case 'analysis_complete':
          return 'text-emerald-600 bg-emerald-100 border-emerald-300'
        default:
          return 'text-amber-600 bg-amber-100 border-amber-300'
      }
    }
    return 'text-gray-400 bg-gray-100 border-gray-300'
  }

  // ストリーミング開始
  const startStreaming = async () => {
    if (isStreaming) return

    setIsStreaming(true)
    setProgressUpdates([])
    setIsComplete(false)
    setFinalResponse("")
    setGenieSteps([])
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

              // Genieタイムラインステップを追加
              const genieMessage = getGenieMessage(data.type, data.message, data.data)
              const newStep: GenieStep = {
                id: Date.now().toString() + Math.random(),
                message: genieMessage,
                type: data.type,
                timestamp: Date.now(),
                status: 'active',
                icon: getStepIcon(data.type),
                tools: data.data?.tools || undefined,
                specialist: getSpecialistDisplay(data.data)
              }

              setGenieSteps(prev => {
                // 前のステップを完了状態に（ゆったりと）
                const updated = prev.map(step => ({
                  ...step,
                  status: 'completed' as const
                }))
                return [...updated, newStep]
              })

              setCurrentStepIndex(prev => prev + 1)
              
              // 自動スクロール
              setTimeout(() => {
                if (timelineRef.current) {
                  timelineRef.current.scrollTop = timelineRef.current.scrollHeight
                }
              }, 100)

              // 最終レスポンスの場合
              if (data.type === 'final_response') {
                setFinalResponse(data.message)
              }

              // 完了の場合
              if (data.type === 'complete') {
                setIsComplete(true)
                setIsStreaming(false)
                
                // 最後のステップも完了状態に
                setGenieSteps(prev => 
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
      {/* Genieタイムライン表示 */}
      <Card className="bg-amber-50 border border-amber-200 shadow-sm overflow-hidden w-full">
        <CardContent className="p-0">
          {/* フラットヘッダー */}
          <div className="p-3 border-b border-amber-200 bg-amber-100">
            <div className="flex items-center gap-3">
              <div className="h-7 w-7 rounded-lg bg-amber-500 flex items-center justify-center">
                <GiMagicLamp className="h-3 w-3 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-sm text-amber-800">Genieがお手伝い中</h3>
                <p className="text-xs text-amber-700">心を込めてサポートします</p>
              </div>
              {isStreaming && (
                <div className="ml-auto flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-amber-500 rounded-full opacity-80"></div>
                    <div className="w-2 h-2 bg-orange-500 rounded-full opacity-60"></div>
                    <div className="w-2 h-2 bg-yellow-500 rounded-full opacity-40"></div>
                  </div>
                  <span className="text-xs text-amber-600">魔法をかけています...</span>
                </div>
              )}
            </div>
          </div>

          {/* コンパクト自動スクロールのタイムライン */}
          <div className="p-4 max-h-80 overflow-y-auto scrollbar-hide" ref={timelineRef}>
            <div className="space-y-3">
              {genieSteps.map((step, index) => (
                <div
                  key={step.id}
                  className="flex gap-4 transition-all duration-300 ease-out"
                >
                  {/* フラットタイムラインライン */}
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-lg border flex items-center justify-center transition-all duration-300 ${
                      getStepColor(step.type, step.status)
                    }`}>
                      <div className="transition-all duration-300">
                        {step.icon}
                      </div>
                    </div>
                    {index < genieSteps.length - 1 && (
                      <div className={`w-0.5 h-6 mt-1 transition-all duration-300 ${
                        step.status === 'completed' 
                          ? 'bg-green-400' 
                          : 'bg-amber-300'
                      }`} />
                    )}
                  </div>

                  {/* コンパクトステップ内容 */}
                  <div className="flex-1 pb-3">
                    <div className={`font-medium text-sm transition-all duration-300 ${
                      step.status === 'completed' ? 'text-amber-700' : 
                      step.status === 'active' ? 'text-amber-900' : 'text-amber-500'
                    }`}>
                      {step.message}
                    </div>
                    
                    {/* フラット専門家情報表示 */}
                    {step.specialist && (
                      <div className="mt-1 p-2 bg-amber-100 rounded border border-amber-200">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1.5 h-1.5 bg-amber-500 rounded-full"></div>
                          <span className="text-xs font-semibold text-amber-800">{step.specialist.name}</span>
                        </div>
                        {step.specialist.description && (
                          <p className="text-xs text-amber-600 leading-relaxed">
                            {step.specialist.description}
                          </p>
                        )}
                      </div>
                    )}
                    
                    {/* フラットツール表示 */}
                    {step.tools && step.tools.length > 0 && (
                      <div className="mt-1">
                        <div className="text-xs font-medium text-amber-600 mb-1 flex items-center gap-1">
                          <IoSparkles className="w-2.5 h-2.5" />
                          利用可能ツール
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {step.tools.slice(0, 5).map((tool, toolIndex) => (
                            <div
                              key={toolIndex}
                              className={`flex items-center gap-1 px-2 py-1 rounded border text-xs font-medium transition-all duration-300 ${
                                step.status === 'active' 
                                  ? 'bg-white text-amber-700 border-amber-300' 
                                  : 'bg-amber-50 text-amber-600 border-amber-200'
                              }`}
                            >
                              <div className="scale-75">{getToolIcon(tool)}</div>
                              <span className="text-xs">{getToolDisplayName(tool)}</span>
                              {step.status === 'active' && (
                                <div className="w-1 h-1 bg-amber-500 rounded-full"></div>
                              )}
                            </div>
                          ))}
                          {step.tools.length > 5 && (
                            <div className="text-xs text-amber-500 px-1 py-1 font-medium">
                              +{step.tools.length - 5}個
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <div className="text-xs text-amber-500 mt-1 font-medium flex items-center gap-1">
                      <IoTime className="w-2.5 h-2.5" />
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

      {/* 最終レスポンス表示（温かみのあるデザイン） */}
      {finalResponse && isComplete && (
        <Card className="bg-gradient-to-r from-green-50 via-emerald-50 to-teal-50 border border-green-200 shadow-lg">
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center shadow-sm">
                <GiMagicLamp className="h-4 w-4 text-white" />
              </div>
              <div>
                <span className="text-base font-semibold text-green-800">Genieからのメッセージ</span>
                <p className="text-sm text-green-600">心を込めてお答えしました</p>
              </div>
            </div>
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-line leading-relaxed">
              {finalResponse}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}