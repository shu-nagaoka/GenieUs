'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
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
  IoTrendingUp
} from 'react-icons/io5'
import { GiMagicLamp } from 'react-icons/gi'

interface ProgressUpdate {
  type: string
  message: string
  data: any
}

interface StreamingProgressDisplayProps {
  message: string
  userId?: string
  sessionId?: string
  onComplete?: (response: string) => void
  onError?: (error: string) => void
}

export function StreamingProgressDisplay({
  message,
  userId = "frontend_user",
  sessionId = "default-session",
  onComplete,
  onError
}: StreamingProgressDisplayProps) {
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([])
  const [isComplete, setIsComplete] = useState(false)
  const [finalResponse, setFinalResponse] = useState<string>("")
  const [isStreaming, setIsStreaming] = useState(false)
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

  // ストリーミング開始
  const startStreaming = async () => {
    if (isStreaming) return

    setIsStreaming(true)
    setProgressUpdates([])
    setIsComplete(false)
    setFinalResponse("")

    try {
      // SSEエンドポイントに接続
      const eventSource = new EventSource(
        `http://localhost:8000/api/v1/streaming/streaming-chat`,
        {
          // POSTデータを送信するためクエリパラメータで代替
          // 実際の実装では、POSTリクエストを送ってからSSE接続する方法を使う
        }
      )

      eventSourceRef.current = eventSource

      // 実際にはまずPOSTリクエストでストリーミングを開始
      const response = await fetch('http://localhost:8000/api/v1/streaming/streaming-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          user_id: userId,
          session_id: sessionId
        })
      })

      if (!response.ok) {
        throw new Error('ストリーミング開始に失敗しました')
      }

      // ReadableStreamからデータを読み取り
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

              // 最終レスポンスの場合
              if (data.type === 'final_response') {
                setFinalResponse(data.message)
              }

              // 完了の場合
              if (data.type === 'complete') {
                setIsComplete(true)
                setIsStreaming(false)
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
              // JSON パースエラーは無視（不完全なデータの可能性）
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

  // プログレス表示用のアイコン取得
  const getProgressIcon = (type: string) => {
    switch (type) {
      case 'thinking':
        return <IoSparkles className="h-4 w-4 text-blue-500 animate-pulse" />
      case 'tools_available':
        return <IoSettings className="h-4 w-4 text-purple-500" />
      case 'tool_detected':
        return <IoCheckmarkCircle className="h-4 w-4 text-green-500" />
      case 'tool_executing':
        return <IoTime className="h-4 w-4 text-orange-500 animate-spin" />
      case 'tool_progress':
        return <IoSettings className="h-4 w-4 text-blue-500" />
      case 'tool_response':
        return <IoCheckmarkCircle className="h-4 w-4 text-green-500" />
      case 'tool_complete':
        return <IoCheckmarkCircle className="h-4 w-4 text-green-600" />
      case 'response_generating':
        return <GiMagicLamp className="h-4 w-4 text-amber-500 animate-pulse" />
      case 'complete':
        return <IoCheckmarkCircle className="h-4 w-4 text-green-600" />
      case 'error':
        return <IoAlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <IoSparkles className="h-4 w-4 text-gray-500" />
    }
  }

  // プログレス項目の背景色
  const getProgressBgColor = (type: string) => {
    switch (type) {
      case 'thinking':
        return 'bg-blue-50 border-blue-200'
      case 'tools_available':
        return 'bg-purple-50 border-purple-200'
      case 'tool_detected':
      case 'tool_complete':
        return 'bg-green-50 border-green-200'
      case 'tool_executing':
      case 'tool_progress':
        return 'bg-orange-50 border-orange-200'
      case 'tool_response':
        return 'bg-emerald-50 border-emerald-200'
      case 'response_generating':
        return 'bg-amber-50 border-amber-200'
      case 'complete':
        return 'bg-green-50 border-green-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="space-y-3">
      {/* メインプログレスカード */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <GiMagicLamp className="h-4 w-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">🤖 AI相談員が対応中...</h3>
              <p className="text-sm text-gray-600">リアルタイムで進捗をお伝えします</p>
            </div>
          </div>

          {/* プログレス一覧 */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {progressUpdates.map((update, index) => (
              <div
                key={index}
                className={`flex items-center gap-2 p-2 rounded-lg border ${getProgressBgColor(update.type)} transition-all duration-300`}
              >
                {getProgressIcon(update.type)}
                <span className="text-sm text-gray-700 flex-1">{update.message}</span>
                
                {/* ツール情報の表示 */}
                {update.data?.tools && Array.isArray(update.data.tools) && (
                  <div className="flex gap-1">
                    {update.data.tools.slice(0, 3).map((tool: string, toolIndex: number) => (
                      <div
                        key={toolIndex}
                        className="flex items-center gap-1 px-2 py-1 bg-white/60 rounded text-xs text-gray-600"
                      >
                        {getToolIcon(tool)}
                        <span className="hidden sm:inline">{tool.replace('_', ' ')}</span>
                      </div>
                    ))}
                    {update.data.tools.length > 3 && (
                      <span className="text-xs text-gray-500">+{update.data.tools.length - 3}</span>
                    )}
                  </div>
                )}

                {/* ツール数の表示 */}
                {update.data?.tool_count && (
                  <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                    {update.data.tool_count}個
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* 進捗状態表示 */}
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              {isStreaming ? (
                <>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">処理中...</span>
                </>
              ) : isComplete ? (
                <>
                  <IoCheckmarkCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">完了</span>
                </>
              ) : (
                <>
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                  <span className="text-sm text-gray-500">待機中</span>
                </>
              )}
            </div>

            {/* 進捗数 */}
            <span className="text-xs text-gray-500">
              {progressUpdates.length}個のステップ
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 最終レスポンス表示 */}
      {finalResponse && (
        <Card className="bg-white border-amber-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <GiMagicLamp className="h-4 w-4 text-amber-500" />
              <span className="text-sm font-medium text-gray-800">AI相談員からの回答</span>
            </div>
            <div className="prose prose-sm max-w-none text-gray-700">
              {finalResponse}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}