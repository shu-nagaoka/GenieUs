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
} from 'react-icons/io5'
import { GiMagicLamp } from 'react-icons/gi'

interface ProgressUpdate {
  type: string
  message: string
  data: any
}

interface SearchResult {
  title: string
  url: string
  snippet?: string
  domain?: string
}

interface SearchData {
  search_query?: string
  search_results?: SearchResult[]
  results_count?: number
  timestamp?: string
  function_call_id?: string
}

interface PerplexityStyleProgressProps {
  message: string
  userId?: string
  sessionId?: string
  onComplete?: (response: string, searchData?: SearchData) => void
  onError?: (error: string) => void
  className?: string
}

export function PerplexityStyleProgress({
  message,
  userId = 'frontend_user',
  sessionId = 'default-session',
  onComplete,
  onError,
  className = '',
}: PerplexityStyleProgressProps) {
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([])
  const [isComplete, setIsComplete] = useState(false)
  const [finalResponse, setFinalResponse] = useState<string>('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentPhase, setCurrentPhase] = useState<string>('thinking')
  const [toolsUsed, setToolsUsed] = useState<string[]>([])
  const [progress, setProgress] = useState<number>(0)
  const [animatedSteps, setAnimatedSteps] = useState<
    Array<{ id: string; text: string; type: string; timestamp: number }>
  >([])
  const [searchData, setSearchData] = useState<SearchData | null>(null)
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

  // フェーズごとのアイコンとカラー
  const getPhaseConfig = (phase: string) => {
    switch (phase) {
      case 'thinking':
        return {
          icon: <IoSparkles className="h-5 w-5" />,
          color: 'from-blue-500 to-purple-600',
          bgColor: 'from-blue-50 to-purple-50',
        }
      case 'tools_available':
        return {
          icon: <IoSettings className="h-5 w-5" />,
          color: 'from-purple-500 to-indigo-600',
          bgColor: 'from-purple-50 to-indigo-50',
        }
      case 'tool_executing':
        return {
          icon: <IoFlash className="h-5 w-5" />,
          color: 'from-orange-500 to-red-600',
          bgColor: 'from-orange-50 to-red-50',
        }
      case 'response_generating':
        return {
          icon: <GiMagicLamp className="h-5 w-5" />,
          color: 'from-amber-500 to-orange-600',
          bgColor: 'from-amber-50 to-orange-50',
        }
      case 'complete':
        return {
          icon: <IoCheckmarkCircle className="h-5 w-5" />,
          color: 'from-green-500 to-emerald-600',
          bgColor: 'from-green-50 to-emerald-50',
        }
      default:
        return {
          icon: <IoSearch className="h-5 w-5" />,
          color: 'from-gray-500 to-gray-600',
          bgColor: 'from-gray-50 to-gray-50',
        }
    }
  }

  // プログレス計算
  const calculateProgress = (type: string) => {
    const progressMap: Record<string, number> = {
      thinking: 10,
      tools_available: 20,
      agent_start: 30,
      tool_detected: 40,
      tool_executing: 60,
      tool_complete: 80,
      response_generating: 90,
      complete: 100,
    }
    return progressMap[type] || 0
  }

  // ストリーミング開始
  const startStreaming = async () => {
    if (isStreaming) return

    setIsStreaming(true)
    setProgressUpdates([])
    setIsComplete(false)
    setFinalResponse('')
    setCurrentPhase('thinking')
    setToolsUsed([])
    setProgress(0)
    setAnimatedSteps([])
    setSearchData(null)

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiBaseUrl}/api/streaming/streaming-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          user_id: userId,
          session_id: sessionId,
        }),
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
                data: data.data || {},
              }

              setProgressUpdates(prev => [...prev, update])
              setCurrentPhase(data.type)
              setProgress(calculateProgress(data.type))

              // アニメーション用ステップを追加
              setAnimatedSteps(prev => [
                ...prev,
                {
                  id: Date.now().toString() + Math.random(),
                  text: data.message,
                  type: data.type,
                  timestamp: Date.now(),
                },
              ])

              // ツール情報を記録
              if (data.data?.tools && Array.isArray(data.data.tools)) {
                setToolsUsed(data.data.tools)
              }

              // 検索結果の場合
              if (data.type === 'search_results') {
                const searchInfo: SearchData = {
                  search_query: data.data?.search_query,
                  search_results: data.data?.search_results || [],
                  results_count: data.data?.results_count || 0,
                  timestamp: data.data?.timestamp,
                  function_call_id: data.data?.function_call_id,
                }
                setSearchData(searchInfo)
              }

              // 最終レスポンスの場合
              if (data.type === 'final_response') {
                setFinalResponse(data.message)
              }

              // 完了の場合
              if (data.type === 'complete') {
                setIsComplete(true)
                setIsStreaming(false)
                setProgress(100)
                if (onComplete) {
                  onComplete(finalResponse || data.data?.response || '', searchData)
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

  const phaseConfig = getPhaseConfig(currentPhase)

  return (
    <div className={`space-y-4 ${className}`}>
      {/* メイン進捗カード - Perplexity風 */}
      <Card
        className={`bg-gradient-to-br ${phaseConfig.bgColor} overflow-hidden border-0 shadow-lg`}
      >
        <CardContent className="p-0">
          {/* ヘッダー部分 */}
          <div className="border-b border-white/20 p-4">
            <div className="flex items-center gap-3">
              <div
                className={`h-10 w-10 rounded-full bg-gradient-to-br ${phaseConfig.color} flex items-center justify-center text-white shadow-lg`}
              >
                {phaseConfig.icon}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-800">AI相談員が分析中...</h3>
                <p className="text-sm text-gray-600">リアルタイム処理状況</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-700">{progress}%</div>
                <div className="text-xs text-gray-500">{animatedSteps.length} steps</div>
              </div>
            </div>
          </div>

          {/* プログレスバー */}
          <div className="px-4 py-2">
            <div className="h-2 w-full overflow-hidden rounded-full bg-white/30">
              <div
                className={`h-full bg-gradient-to-r ${phaseConfig.color} transition-all duration-700 ease-out`}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* アニメーションステップ */}
          <div className="scrollbar-thin scrollbar-thumb-gray-300 max-h-32 space-y-2 overflow-y-auto p-4">
            {animatedSteps.slice(-4).map((step, index) => (
              <div
                key={step.id}
                className={`flex transform items-center gap-2 text-sm transition-all duration-500 ${
                  index === animatedSteps.slice(-4).length - 1
                    ? 'translate-x-0 scale-100 opacity-100'
                    : 'scale-95 opacity-70'
                }`}
                style={{
                  animationDelay: `${index * 100}ms`,
                  animation:
                    index === animatedSteps.slice(-4).length - 1
                      ? 'slideInRight 0.5s ease-out'
                      : 'none',
                }}
              >
                <div
                  className={`h-2 w-2 rounded-full bg-gradient-to-r ${phaseConfig.color} flex-shrink-0`}
                />
                <span className="flex-1 text-gray-700">{step.text}</span>
                {step.type.includes('tool') && <IoFlash className="h-3 w-3 text-orange-500" />}
              </div>
            ))}
          </div>

          {/* ツール表示 */}
          {toolsUsed.length > 0 && (
            <div className="px-4 pb-4">
              <div className="mb-2 flex items-center gap-2">
                <IoSettings className="h-4 w-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">使用中のツール</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {toolsUsed.map((tool, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-1 rounded-full bg-white/60 px-3 py-1 text-xs text-gray-700 shadow-sm backdrop-blur-sm"
                  >
                    {getToolIcon(tool)}
                    <span>{tool.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* アクティブインジケーター */}
          {isStreaming && (
            <div className="px-4 pb-4">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div
                    className={`h-2 w-2 rounded-full bg-gradient-to-r ${phaseConfig.color} animate-pulse`}
                  ></div>
                  <div
                    className={`h-2 w-2 rounded-full bg-gradient-to-r ${phaseConfig.color} animate-pulse`}
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                  <div
                    className={`h-2 w-2 rounded-full bg-gradient-to-r ${phaseConfig.color} animate-pulse`}
                    style={{ animationDelay: '0.4s' }}
                  ></div>
                </div>
                <span className="text-xs text-gray-600">処理中...</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 最終レスポンス表示 */}
      {finalResponse && isComplete && (
        <Card className="border border-green-200 bg-white/95 shadow-lg backdrop-blur-md">
          <CardContent className="p-4">
            <div className="mb-3 flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-emerald-600">
                <IoCheckmarkCircle className="h-3 w-3 text-white" />
              </div>
              <span className="text-sm font-medium text-green-700">回答完了</span>
            </div>
            <div className="prose prose-sm max-w-none whitespace-pre-line text-gray-700">
              {finalResponse}
            </div>
          </CardContent>
        </Card>
      )}

      {/* CSS アニメーション */}
      <style jsx>{`
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .scrollbar-thin {
          scrollbar-width: thin;
        }

        .scrollbar-thumb-gray-300::-webkit-scrollbar {
          width: 4px;
        }

        .scrollbar-thumb-gray-300::-webkit-scrollbar-thumb {
          background-color: #d1d5db;
          border-radius: 2px;
        }
      `}</style>
    </div>
  )
}
