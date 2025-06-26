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

// グローバル重複防止機能
let globalStreamingRequests = new Set<string>()
const cleanupGlobalRequests = () => {
  // 30秒後に自動クリーンアップ
  setTimeout(() => {
    globalStreamingRequests.clear()
  }, 30000)
}

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
  onFollowupQuestions?: (questions: string[]) => void
  className?: string
}

export function GenieStyleProgress({
  message,
  userId = "frontend_user",
  sessionId = "default-session",
  onComplete,
  onError,
  onFollowupQuestions,
  className = ""
}: GenieStyleProgressProps) {
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([])
  const [isComplete, setIsComplete] = useState(false)
  const [finalResponse, setFinalResponse] = useState<string>("")
  const [cleanedFinalResponse, setCleanedFinalResponse] = useState<string>("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [genieSteps, setGenieSteps] = useState<GenieStep[]>([])
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const eventSourceRef = useRef<EventSource | null>(null)
  const timelineRef = useRef<HTMLDivElement>(null)

  // フォローアップクエスチョンを抽出し、本文から除去
  const extractFollowupQuestions = (response: string): { questions: string[], cleanResponse: string } => {
    try {
      const questions: string[] = []
      
      console.log('=== レスポンス内容確認 ===')
      console.log('レスポンス文字数:', response.length)
      console.log('レスポンス全文:')
      console.log(response)
      console.log('=== 💭検索開始 ===')
      
      // 💭マークの直接検索
      const thinkingCount = (response.match(/💭/g) || []).length
      const unicodeCount = (response.match(/\ud83d\udcad/g) || []).length
      console.log('💭マーク数:', thinkingCount)
      console.log('Unicode💭マーク数:', unicodeCount)
      
      // 💭マークを含む行を個別に処理
      const lines = response.split('\n')
      
      for (const line of lines) {
        const trimmedLine = line.trim()
        
        // 💭マークを含む行から質問を抽出
        if (trimmedLine.includes('💭') || trimmedLine.includes('\ud83d\udcad')) {
          console.log('💭マーク行発見:', trimmedLine)
          // 一行に複数の💭マークがある場合に対応
          const questionMatches = trimmedLine.match(/💭\s*([^💭\n?]+\?)/g) || []
          const unicodeMatches = trimmedLine.match(/\ud83d\udcad\s*([^\ud83d\udcad\n?]+\?)/g) || []
          
          // すべての💭マークを抽出（簡単なパターン）
          const allThinkingMarks = trimmedLine.match(/💭[^💭]*(?=💭|$)/g) || []
          console.log('この行で見つかった💭パターン:', allThinkingMarks)
          
          for (const match of allThinkingMarks) {
            let question = match.replace(/💭\s*/, '').trim()
            console.log('抽出中のテキスト:', question)
            
            // 質問マークで終わるように調整
            if (!question.endsWith('？') && !question.endsWith('?')) {
              question += '？'
            }
            
            if (question && question.length > 2 && !questions.includes(question)) {
              questions.push(question)
              console.log('質問を追加:', question)
            }
          }
        }
      }
      
      console.log('=== 最終結果 ===')
      console.log('抽出された質問数:', questions.length)
      console.log('抽出された質問:', questions)
      
      // より厳密な除去処理
      let cleanResponse = response
      
      // 💭マークを含む行全体を除去
      const cleanLines2 = response.split('\n')
      const cleanLines = []
      let inFollowupSection = false
      
      for (let i = 0; i < cleanLines2.length; i++) {
        const line = cleanLines2[i]
        const trimmedLine = line.trim()
        
        // フォローアップセクションの開始を検出
        if (trimmedLine.includes('続けて相談する') || 
            trimmedLine.includes('続けて相談したい方へ') || 
            trimmedLine.includes('【続けて相談したい方へ】') ||
            trimmedLine.includes('【続けて相談する】')) {
          inFollowupSection = true
          continue
        }
        
        // 💭マークを含む行をスキップ
        if (trimmedLine.includes('💭') || trimmedLine.includes('\ud83d\udcad')) {
          continue
        }
        
        // フォローアップセクション内の行をスキップ
        if (inFollowupSection) {
          continue
        }
        
        // 通常の行は保持
        cleanLines.push(line)
      }
      
      cleanResponse = cleanLines.join('\n').replace(/\n\s*\n\s*\n/g, '\n\n').trim()
      
      
      return { questions, cleanResponse }
    } catch (error) {
      console.warn('フォローアップクエスチョン抽出エラー:', error)
      return { questions: [], cleanResponse: response }
    }
  }

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

  // 専門家ルーティング情報を取得
  const getSpecialistRouting = (data: any) => {
    console.log('getSpecialistRouting called with data:', data)
    if (data?.specialist_name) {
      const result = {
        name: data.specialist_name,
        description: data.specialist_description || "",
        icon: getSpecialistIcon(data.specialist_name)
      }
      console.log('getSpecialistRouting returning:', result)
      return result
    }
    console.log('getSpecialistRouting returning null (no specialist_name)')
    return null
  }

  // 専門家アイコンを取得
  const getSpecialistIcon = (specialistName: string) => {
    if (specialistName?.includes('栄養') || specialistName?.includes('食事')) return '🍎'
    if (specialistName?.includes('睡眠')) return '😴'
    if (specialistName?.includes('発達')) return '🌱'
    if (specialistName?.includes('健康')) return '❤️'
    if (specialistName?.includes('行動') || specialistName?.includes('しつけ')) return '🎭'
    if (specialistName?.includes('遊び') || specialistName?.includes('学習')) return '🎲'
    if (specialistName?.includes('安全')) return '🛡️'
    if (specialistName?.includes('心理') || specialistName?.includes('メンタル')) return '💚'
    if (specialistName?.includes('仕事')) return '💼'
    if (specialistName?.includes('特別支援')) return '🤝'
    return '🧞‍♀️'
  }

  // Genieらしいメッセージに変換（ルーティング情報重視）
  const getGenieMessage = (type: string, originalMessage: string, data: any = {}) => {
    const specialist = getSpecialistRouting(data)
    
    switch (type) {
      case 'start':
        return '✨ Genieがお手伝いを始めます'
      case 'agent_starting':
        return '🪔 魔法のランプを準備中...'
      case 'agent_selecting':
        return specialist ? 
          `🎯 ${specialist.name}を呼び出し中...` :
          '🌟 最適なサポート方法を考えています'
      case 'agent_executing':
        return specialist ? 
          `${specialist.icon} ${specialist.name}が対応中...` :
          '💫 Genieが心を込めて分析中...'
      case 'specialist_routing':
        return specialist ?
          `🔄 ${specialist.icon} ${specialist.name}にバトンタッチ...` :
          originalMessage
      case 'analysis_complete':
        return '🎯 専門分析が完了しました'
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

  // ローディングアニメーションコンポーネント
  const LoadingSpinner = ({ size = "h-4 w-4" }: { size?: string }) => (
    <div className={`${size} animate-spin rounded-full border-2 border-amber-200 border-t-amber-600`}></div>
  )

  // ステップタイプからアイコンを取得（ローディング重視）
  const getStepIcon = (type: string, status: string = 'active') => {
    if (status === 'active') {
      switch (type) {
        case 'agent_selecting':
        case 'agent_executing':
        case 'specialist_routing':
          return <LoadingSpinner />
        case 'start':
          return <GiMagicLamp className="h-4 w-4" />
        case 'analysis_complete':
          return <IoCheckmarkCircle className="h-4 w-4" />
        case 'complete':
          return <IoCheckmarkCircle className="h-4 w-4" />
        case 'error':
          return <IoAlertCircle className="h-4 w-4" />
        default:
          return <LoadingSpinner />
      }
    } else {
      // 完了状態のアイコン
      switch (type) {
        case 'start':
          return <GiMagicLamp className="h-4 w-4" />
        case 'agent_selecting':
          return <IoSunny className="h-4 w-4" />
        case 'agent_executing':
          return <IoHeart className="h-4 w-4" />
        case 'specialist_routing':
          return <IoTrendingUp className="h-4 w-4" />
        case 'analysis_complete':
        case 'complete':
          return <IoCheckmarkCircle className="h-4 w-4" />
        case 'error':
          return <IoAlertCircle className="h-4 w-4" />
        default:
          return <IoSparkles className="h-4 w-4" />
      }
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
    // グローバル重複防止チェック
    const requestKey = `${userId}-${sessionId}-${message.substring(0, 50)}`
    
    console.log('🎯 startStreaming 呼び出し:', {
      requestKey,
      isStreaming,
      isComplete,
      globalRequestsSize: globalStreamingRequests.size,
      hasGlobalRequest: globalStreamingRequests.has(requestKey),
      message: message.substring(0, 100) + '...',
      timestamp: new Date().toISOString()
    })
    
    if (globalStreamingRequests.has(requestKey)) {
      console.log('⚠️ グローバル重複防止: 同じリクエストが実行中のため処理をスキップ')
      return
    }
    
    if (isStreaming) {
      console.log('⚠️ 既にストリーミング中のため処理をスキップ')
      return
    }

    if (isComplete) {
      console.log('⚠️ 既に完了済みのため処理をスキップ') 
      return
    }

    // グローバル実行フラグを設定
    globalStreamingRequests.add(requestKey)
    cleanupGlobalRequests()

    console.log('✅ ストリーミング開始処理実行')
    setIsStreaming(true)
    setProgressUpdates([])
    setIsComplete(false)
    setFinalResponse("")
    setCleanedFinalResponse("")
    setGenieSteps([])
    setCurrentStepIndex(0)

    try {
      // メッセージから会話履歴と家族情報を解析
      let actualMessage = message
      let conversationHistory = null
      let familyInfo = null
      let actualSessionId = sessionId
      let actualUserId = userId

      try {
        const parsed = JSON.parse(message)
        if (parsed.message) {
          actualMessage = parsed.message
          conversationHistory = parsed.conversation_history || null
          familyInfo = parsed.family_info || null
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

      // 家族情報があれば追加
      if (familyInfo) {
        requestBody.family_info = familyInfo
      }

      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const streamingUrl = `${apiBaseUrl}/api/streaming/streaming-chat`
      
      console.log('🌐 API呼び出し実行:', {
        url: streamingUrl,
        method: 'POST',
        requestBody: {
          ...requestBody,
          message: requestBody.message.substring(0, 50) + '...'
        },
        timestamp: new Date().toISOString()
      })

      const response = await fetch(streamingUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      console.log('📡 API レスポンス受信:', {
        ok: response.ok,
        status: response.status,
        timestamp: new Date().toISOString()
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

              // 専門家情報のデバッグログ
              if (data.type === 'specialist_calling' || data.type === 'specialist_ready' || data.type === 'final_response') {
                console.log(`=== ${data.type.toUpperCase()} デバッグ ===`)
                console.log('data.data:', data.data)
                console.log('specialist_name:', data.data?.specialist_name)
                console.log('specialist_description:', data.data?.specialist_description)
                console.log('agent_type:', data.data?.agent_type)
                console.log('============================')
              }

              setProgressUpdates(prev => [...prev, update])

              // 重要なイベントのみGenieタイムラインステップを追加
              const importantSteps = [
                'start',
                'agent_selecting', 
                'agent_executing',
                'specialist_routing',
                'analysis_complete'
              ]
              
              if (importantSteps.includes(data.type)) {
                const genieMessage = getGenieMessage(data.type, data.message, data.data)
                const newStep: GenieStep = {
                  id: Date.now().toString() + Math.random(),
                  message: genieMessage,
                  type: data.type,
                  timestamp: Date.now(),
                  status: 'active',
                  icon: getStepIcon(data.type, 'active'),
                  tools: data.data?.tools || undefined,
                  specialist: getSpecialistRouting(data.data)
                }

                setGenieSteps(prev => {
                  // 前のステップを完了状態に（ゆったりと）
                  const updated = prev.map(step => ({
                    ...step,
                    status: 'completed' as const
                  }))
                  return [...updated, newStep]
                })
              }

              setCurrentStepIndex(prev => prev + 1)
              
              // 自動スクロール
              setTimeout(() => {
                if (timelineRef.current) {
                  timelineRef.current.scrollTop = timelineRef.current.scrollHeight
                }
              }, 100)

              // 最終レスポンスの場合
              if (data.type === 'final_response') {
                console.log('📝 GenieStyleProgress: final_response イベント受信:', {
                  messageLength: data.message?.length || 0,
                  messagePreview: data.message?.substring(0, 100) + '...'
                })
                
                // フォローアップクエスチョンを抽出し、本文をクリーンアップ
                const { questions, cleanResponse } = extractFollowupQuestions(data.message)
                
                console.log('🧹 GenieStyleProgress: レスポンスクリーンアップ完了:', {
                  originalLength: data.message?.length || 0,
                  cleanedLength: cleanResponse.length,
                  extractedQuestions: questions.length,
                  cleanResponsePreview: cleanResponse.substring(0, 100) + '...'
                })
                
                // クリーンな回答を設定（💭マーク部分を除去）
                setFinalResponse(cleanResponse)
                setCleanedFinalResponse(cleanResponse)
                
                // 親コンポーネントにフォローアップクエスチョンを通知
                if (onFollowupQuestions && questions.length > 0) {
                  onFollowupQuestions(questions)
                }
              }

              // 完了の場合
              if (data.type === 'complete') {
                console.log('🎯 GenieStyleProgress: complete イベント受信:', {
                  cleanedFinalResponse,
                  finalResponse,
                  dataResponse: data.data?.response,
                  onCompleteExists: !!onComplete,
                  isAlreadyComplete: isComplete
                })
                
                // 既に完了済みの場合は重複処理を防ぐ
                if (isComplete) {
                  console.log('⚠️ GenieStyleProgress: 既に完了済み - 重複処理をスキップ')
                  return
                }
                
                // 2秒待機してUIを見やすくする
                await new Promise(resolve => setTimeout(resolve, 2000))
                
                setIsComplete(true)
                setIsStreaming(false)
                
                // 最後のステップも完了状態に
                setGenieSteps(prev => 
                  prev.map(step => ({
                    ...step,
                    status: 'completed' as const
                  }))
                )
                
                const responseToSend = cleanedFinalResponse || finalResponse || data.data?.response || ""
                
                console.log('📤 GenieStyleProgress: onComplete 実行:', {
                  responseToSend: responseToSend.substring(0, 100) + '...',
                  responseLength: responseToSend.length
                })
                
                if (onComplete) {
                  onComplete(responseToSend)
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
      
      // エラー時もグローバルフラグをクリア
      const requestKey = `${userId}-${sessionId}-${message.substring(0, 50)}`
      globalStreamingRequests.delete(requestKey)
      
      if (onError) {
        onError(error instanceof Error ? error.message : 'ストリーミングエラー')
      }
    }
  }

  // コンポーネントマウント時に自動開始（React Strict Mode対応）
  useEffect(() => {
    console.log('🚀 GenieStyleProgress: useEffect実行 - コンポーネントマウント', {
      instanceId: Math.random().toString(36).substr(2, 9),
      isStreaming,
      isComplete
    })
    
    // React Strict Modeで重複実行される場合の対策
    let shouldExecute = true
    
    const executeStreaming = async () => {
      if (shouldExecute && !isStreaming && !isComplete) {
        await startStreaming()
      }
    }
    
    executeStreaming()

    return () => {
      console.log('🧹 GenieStyleProgress: クリーンアップ実行')
      shouldExecute = false // 実行をキャンセル
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, []) // 依存配列を空にして、マウント時のみ実行

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
                        {step.status === 'active' ? getStepIcon(step.type, 'active') : getStepIcon(step.type, 'completed')}
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
                      <div className="mt-2 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-base">{getSpecialistIcon(step.specialist.name)}</span>
                          <span className="text-sm font-semibold text-blue-800">{step.specialist.name}</span>
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">登場</span>
                        </div>
                        {step.specialist.description && (
                          <p className="text-xs text-blue-600 leading-relaxed mt-1">
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

    </div>
  )
}