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
} from 'react-icons/io5'
import { GiMagicLamp } from 'react-icons/gi'

interface ProgressUpdate {
  type: string
  message: string
  data: any
}

interface InlineProgressDisplayProps {
  message: string
  userId?: string
  sessionId?: string
  onComplete?: (response: string) => void
  onError?: (error: string) => void
  className?: string
}

export function InlineProgressDisplay({
  message,
  userId = 'frontend_user',
  sessionId = 'default-session',
  onComplete,
  onError,
  className = '',
}: InlineProgressDisplayProps) {
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([])
  const [isComplete, setIsComplete] = useState(false)
  const [finalResponse, setFinalResponse] = useState<string>('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentStatus, setCurrentStatus] = useState<string>('thinking')
  const [toolsUsed, setToolsUsed] = useState<string[]>([])
  const eventSourceRef = useRef<EventSource | null>(null)

  // ツールアイコンマップ
  const getToolIcon = (toolName: string) => {
    if (toolName.includes('image') || toolName.includes('analyze_child_image')) {
      return <IoImage className="h-3 w-3" />
    }
    if (toolName.includes('voice') || toolName.includes('analyze_child_voice')) {
      return <IoVolumeHigh className="h-3 w-3" />
    }
    if (toolName.includes('file') || toolName.includes('manage_child_files')) {
      return <IoDocumentText className="h-3 w-3" />
    }
    if (toolName.includes('record') || toolName.includes('manage_child_records')) {
      return <IoTrendingUp className="h-3 w-3" />
    }
    return <IoCode className="h-3 w-3" />
  }

  // ストリーミング開始
  const startStreaming = async () => {
    if (isStreaming) return

    setIsStreaming(true)
    setProgressUpdates([])
    setIsComplete(false)
    setFinalResponse('')
    setCurrentStatus('thinking')
    setToolsUsed([])

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
              setCurrentStatus(data.type)

              // ツール情報を記録
              if (data.data?.tools && Array.isArray(data.data.tools)) {
                setToolsUsed(data.data.tools)
              }

              // 最終レスポンスの場合
              if (data.type === 'final_response') {
                setFinalResponse(data.message)
              }

              // 完了の場合
              if (data.type === 'complete') {
                setIsComplete(true)
                setIsStreaming(false)
                if (onComplete) {
                  onComplete(finalResponse || data.data?.response || '')
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

  // プログレス表示用のアイコン取得
  const getStatusIcon = () => {
    switch (currentStatus) {
      case 'thinking':
        return <IoSparkles className="h-4 w-4 animate-pulse text-blue-500" />
      case 'tools_available':
        return <IoSettings className="h-4 w-4 text-purple-500" />
      case 'tool_detected':
      case 'tool_executing':
        return <IoTime className="h-4 w-4 animate-spin text-orange-500" />
      case 'tool_complete':
        return <IoCheckmarkCircle className="h-4 w-4 text-green-500" />
      case 'response_generating':
        return <GiMagicLamp className="h-4 w-4 animate-pulse text-amber-500" />
      case 'complete':
        return <IoCheckmarkCircle className="h-4 w-4 text-green-600" />
      case 'error':
        return <IoAlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <IoSparkles className="h-4 w-4 text-gray-500" />
    }
  }

  // 現在のステータスメッセージ
  const getCurrentStatusMessage = () => {
    if (progressUpdates.length === 0) return '思考中...'
    return progressUpdates[progressUpdates.length - 1]?.message || '処理中...'
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {/* コンパクトなプログレス表示 */}
      <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardContent className="p-3">
          <div className="flex items-center gap-3">
            <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600">
              <GiMagicLamp className="h-3 w-3 text-white" />
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                {getStatusIcon()}
                <span className="truncate text-sm text-gray-700">{getCurrentStatusMessage()}</span>
              </div>

              {/* ツール使用表示 */}
              {toolsUsed.length > 0 && (
                <div className="mt-1 flex gap-1">
                  {toolsUsed.slice(0, 4).map((tool, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-1 rounded bg-white/60 px-2 py-0.5 text-xs text-gray-600"
                    >
                      {getToolIcon(tool)}
                      <span className="hidden sm:inline">{tool.replace('_', ' ')}</span>
                    </div>
                  ))}
                  {toolsUsed.length > 4 && (
                    <span className="self-center text-xs text-gray-500">
                      +{toolsUsed.length - 4}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* ステータスインジケーター */}
            <div className="flex items-center gap-1">
              {isStreaming ? (
                <div className="flex gap-1">
                  <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-blue-500"></div>
                  <div
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-blue-500"
                    style={{ animationDelay: '0.1s' }}
                  ></div>
                  <div
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-blue-500"
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                </div>
              ) : isComplete ? (
                <IoCheckmarkCircle className="h-4 w-4 text-green-500" />
              ) : (
                <div className="h-2 w-2 rounded-full bg-gray-400"></div>
              )}

              <span className="text-xs text-gray-500">{progressUpdates.length}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 最終レスポンス表示 */}
      {finalResponse && isComplete && (
        <Card className="border border-amber-200 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-3">
            <div className="prose prose-sm max-w-none whitespace-pre-line text-gray-700">
              {finalResponse}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
