'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Search, Globe, CheckCircle, AlertCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { API_BASE_URL } from '@/config/api'

interface SearchData {
  search_query?: string
  search_results?: any[]
  results_count?: number
  timestamp?: string
  function_call_id?: string
}

interface WebSearchProgressProps {
  message: string
  userId?: string
  sessionId?: string
  onComplete?: (response: string, searchData?: SearchData) => void
  onError?: (error: string) => void
  className?: string
}

export function WebSearchProgress({ 
  message,
  userId = 'frontend_user',
  sessionId = 'default-session',
  onComplete,
  onError,
  className = "" 
}: WebSearchProgressProps) {
  const [isSearching, setIsSearching] = useState(true)
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [error, setError] = useState<string | undefined>(undefined)
  const [finalResponse, setFinalResponse] = useState<string>('')
  const [searchData, setSearchData] = useState<SearchData | undefined>(undefined)
  const [hasCompleted, setHasCompleted] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    // GenieStyleProgressと同じアプローチを使用
    const startWebSearchStreaming = async () => {
      setIsSearching(true)
      setError(undefined)
      
      try {
        // メッセージから必要な情報を解析
        let actualMessage = message
        let parsedData: any = {}
        
        try {
          const parsed = JSON.parse(message)
          if (parsed.message) {
            actualMessage = parsed.message
            parsedData = parsed
          }
        } catch (e) {
          // JSON parsing failed, use message as is
        }

        const requestBody = {
          message: actualMessage,
          user_id: userId,
          session_id: sessionId,
          conversation_history: parsedData.conversation_history || [],
          family_info: parsedData.family_info || {},
          web_search_enabled: true, // Web検索を強制有効化
          message_type: parsedData.message_type || "text",
          has_image: parsedData.has_image || false,
          image_path: parsedData.image_path || "",
          multimodal_context: parsedData.multimodal_context || {}
        }

        console.log('🔍 Web検索API呼び出し:', {
          url: `${API_BASE_URL}/api/streaming/streaming-chat`,
          requestBody: {
            ...requestBody,
            message: requestBody.message.substring(0, 100) + '...'
          }
        })

        const response = await fetch(`${API_BASE_URL}/api/streaming/streaming-chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        })

        console.log('📡 Web検索API レスポンス:', {
          ok: response.ok,
          status: response.status,
          statusText: response.statusText
        })

        if (!response.ok) {
          const errorText = await response.text()
          console.error('❌ API エラーレスポンス:', errorText)
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        // ストリーミングレスポンスを処理
        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
          throw new Error('ストリーミングデータの読み取りに失敗しました')
        }

        let finalResponseText = ''
        let extractedSearchData: SearchData | undefined

        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                console.log('🔍 Web検索ストリーミングイベント:', data)

                if (data.type === 'search_results') {
                  console.log('🔍 検索結果受信:', data.data)
                  setSearchResults(data.data?.search_results || [])
                  extractedSearchData = {
                    search_query: data.data?.search_query,
                    search_results: data.data?.search_results,
                    results_count: data.data?.results_count,
                    timestamp: new Date().toISOString()
                  }
                  setSearchData(extractedSearchData)
                } else if (data.type === 'final_response' && !hasCompleted) {
                  // data.messageまたはdata.responseのどちらかを使用
                  const responseText = data.response || data.message
                  console.log('✅ Web検索最終レスポンス受信:', responseText)
                  finalResponseText = responseText
                  setFinalResponse(responseText)
                  setIsSearching(false)
                  setHasCompleted(true)
                } else if (data.type === 'error') {
                  throw new Error(data.message || 'Web検索中にエラーが発生しました')
                }
              } catch (parseError) {
                console.warn('ストリーミングデータのパースエラー:', parseError)
              }
            }
          }
        }

        // 最終的なコールバック実行（重複防止）
        if (finalResponseText && onComplete && !hasCompleted) {
          setHasCompleted(true)
          onComplete(finalResponseText, extractedSearchData)
        }

      } catch (error) {
        console.error('❌ Web検索エラー:', error)
        const errorMessage = error instanceof Error ? error.message : '不明なエラーが発生しました'
        setError(errorMessage)
        setIsSearching(false)
        
        if (onError) {
          onError(errorMessage)
        }
      }
    }

    startWebSearchStreaming()
  }, [message, userId, sessionId, onComplete, onError])

  return (
    <Card className={`border-blue-200 bg-blue-50 ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          {/* ステータスアイコン */}
          <div className="flex-shrink-0">
            {error ? (
              <AlertCircle className="h-5 w-5 text-red-500" />
            ) : isSearching ? (
              <div className="relative">
                <Search className="h-5 w-5 text-blue-600 animate-pulse" />
                <div className="absolute -top-1 -right-1">
                  <div className="h-2 w-2 bg-blue-400 rounded-full animate-ping"></div>
                </div>
              </div>
            ) : searchResults && searchResults.length > 0 ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
              <Globe className="h-5 w-5 text-blue-600" />
            )}
          </div>

          {/* ステータステキスト */}
          <div className="flex-1">
            {error ? (
              <div className="text-red-700">
                <div className="font-medium">検索エラー</div>
                <div className="text-sm text-red-600">{error}</div>
              </div>
            ) : isSearching ? (
              <div className="text-blue-700">
                <div className="font-medium flex items-center gap-2">
                  <span>Web検索中</span>
                  <div className="flex gap-1">
                    <div className="h-1.5 w-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="h-1.5 w-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="h-1.5 w-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                  </div>
                </div>
                <div className="text-sm text-blue-600">最新情報を検索しています...</div>
              </div>
            ) : searchResults && searchResults.length > 0 ? (
              <div className="text-green-700">
                <div className="font-medium">検索完了</div>
                <div className="text-sm text-green-600">
                  {searchResults.length}件の関連情報を見つけました
                </div>
              </div>
            ) : (
              <div className="text-blue-700">
                <div className="font-medium">Web検索モード</div>
                <div className="text-sm text-blue-600">最新情報を検索して回答します</div>
              </div>
            )}
          </div>

          {/* 検索結果カウント */}
          {searchResults && searchResults.length > 0 && !isSearching && (
            <div className="flex-shrink-0">
              <div className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                {searchResults.length}件
              </div>
            </div>
          )}
        </div>

        {/* 検索ステップ詳細（検索中のみ） */}
        {isSearching && (
          <div className="mt-3 space-y-2">
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <div className="h-1.5 w-1.5 bg-blue-400 rounded-full animate-pulse"></div>
              <span>関連するキーワードで検索中...</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-1.5">
              <div className="bg-blue-500 h-1.5 rounded-full animate-pulse" style={{ width: '70%' }}></div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// シンプルなインライン検索インジケーター
export function WebSearchInlineIndicator({ isSearching }: { isSearching: boolean }) {
  if (!isSearching) return null

  return (
    <div className="flex items-center gap-2 text-blue-600 text-sm">
      <Search className="h-4 w-4 animate-pulse" />
      <span>検索中...</span>
      <div className="flex gap-1">
        <div className="h-1 w-1 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="h-1 w-1 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="h-1 w-1 bg-blue-400 rounded-full animate-bounce"></div>
      </div>
    </div>
  )
}