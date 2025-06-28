'use client'
import { useState, useEffect, useRef, lazy } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { AppLayout } from '@/components/layout/app-layout'
import { useChatHistory } from '@/hooks/use-chat-history'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { AuthCheck } from '@/components/features/auth/auth-check'

// 重いコンポーネントをレイジーローディング
const ReactMarkdown = lazy(() => import('react-markdown'))
const GenieStyleProgress = lazy(() =>
  import('@/components/features/chat/genie-style-progress').then(m => ({
    default: m.GenieStyleProgress,
  }))
)
const FollowupQuestions = lazy(() =>
  import('@/components/features/chat/followup-questions').then(m => ({
    default: m.FollowupQuestions,
  }))
)
const SearchResultsDisplay = lazy(() =>
  import('@/components/features/chat/search-results-display').then(m => ({
    default: m.SearchResultsDisplay,
  }))
)
const InteractiveConfirmation = lazy(() =>
  import('@/components/features/chat/interactive-confirmation').then(m => ({
    default: m.InteractiveConfirmation,
  }))
)
import { getFamilyInfo, formatFamilyInfoForChat } from '@/libs/api/family'
import { uploadImage } from '@/libs/api/file-upload'
import { parseInteractiveConfirmation, sendConfirmationResponse, type InteractiveConfirmationData } from '@/libs/api/interactive-confirmation'
import remarkGfm from 'remark-gfm'
// アイコンをバランス良く設定 - 必要なアイコンは保持
import {
  Send,
  Mic,
  Camera,
  History,
  Save,
  User,
  Sparkles,
  Star,
  MessageCircle,
  Search,
} from 'lucide-react'
import { GiMagicLamp } from 'react-icons/gi'
import { IoStop } from 'react-icons/io5'

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

interface Message {
  id: string
  content: string
  sender: 'user' | 'genie'
  timestamp: Date
  type?: 'text' | 'audio' | 'image' | 'streaming'
  followUpQuestions?: string[]
  searchData?: SearchData
  confirmationData?: InteractiveConfirmationData
  debugInfo?: {
    workflow_used?: string
    agents_involved?: string[]
    processing_time?: number
  }
}

export default function ChatPage() {
  return (
    <AuthCheck>
      <ChatPageContent />
    </AuthCheck>
  )
}

function ChatPageContent() {
  const {
    sessions,
    currentSession,
    loading: historyLoading,
    createSession,
    updateSession,
    loadSession,
    setCurrentSession,
  } = useChatHistory()

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content:
        'こんにちは！**GenieUs**です\n\n話すだけで **家族管理・成長記録・努力見える化** すべてがつながる子育てアシスタント！\n\n**15人の専門GenieUs Agents**が連携してサポートします\n\n**こんなことができます：**\n• **「家族情報を登録」** → パパ・ママ・お子さんの情報をまとめて管理\n• **「今日どうだった？」** → 複数の専門エージェントがあなたの話を理解・記録\n• **「初めて歩いた！」** → 写真付きで大切な瞬間をメモリーズに保存\n• **「頑張ったことを教えて」** → あなたの愛情と努力をGenieが理解・認める\n• **「夜泣きがひどくて困っています」** → 専門エージェントが具体的にアドバイス\n• **「近くの病院を検索して」** → 最新情報を検索してお届け\n• **「子供向けイベントを探して」** → お出かけ先やイベントをご提案\n\n**専門分野：** 睡眠・栄養・夜泣き・離乳食・発達・遊び・しつけ・健康・行動・安全・心理・仕事両立・特別支援・検索・窓口申請・おでかけイベントなど\n\n何でもお気軽にお話しください！あなたに最適な専門エージェントが自動的にサポートします',
      sender: 'genie',
      timestamp: new Date('2025-01-01T00:00:00.000Z'),
      type: 'text',
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [unsavedChanges, setUnsavedChanges] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [useStreamingProgress] = useState(true)
  const [currentStreamingId, setCurrentStreamingId] = useState<string | null>(null)
  const [familyInfo, setFamilyInfo] = useState<Record<string, unknown> | null>(null)
  const [currentFollowupQuestions, setCurrentFollowupQuestions] = useState<string[]>([])
  const [webSearchEnabled, setWebSearchEnabled] = useState<boolean>(false)
  const [hasActiveConfirmation, setHasActiveConfirmation] = useState<boolean>(false)
  const [processingConfirmation, setProcessingConfirmation] = useState<boolean>(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // ローカルファイルパスを取得するヘルパー関数
  const getLocalFilePath = async (file: File): Promise<string | null> => {
    try {
      console.log('📁 画像ファイルアップロード開始:', file.name)
      const uploadResult = await uploadImage(file, 'frontend_user')
      if (uploadResult.success && uploadResult.file_url) {
        // URLからファイル名を抽出
        const filename = uploadResult.file_url.split('/').pop()
        // バックエンドの絶対パスを生成
        const localFilePath = `/Users/tnoce/dev/GenieUs/backend/src/data/uploads/images/${filename}`
        console.log('✅ 画像アップロード成功, ローカルパス:', localFilePath)
        return localFilePath
      } else {
        console.error('❌ 画像アップロード失敗:', uploadResult)
        // フォールバック: Base64データを返す
        return imagePreview
      }
    } catch (error) {
      console.error('❌ 画像アップロードエラー:', error)
      // フォールバック: Base64データを返す
      return imagePreview
    }
  }

  // 画像状態変更をトラッキング（デバッグ用）
  useEffect(() => {
    console.log('🖼️ selectedImage状態が変更されました:', {
      timestamp: new Date().toISOString(),
      hasSelectedImage: !!selectedImage,
      fileName: selectedImage?.name || 'なし',
      fileSize: selectedImage ? `${Math.round(selectedImage.size / 1024)}KB` : 'なし',
      fileType: selectedImage?.type || 'なし'
    })
  }, [selectedImage])

  // プレビュー状態変更をトラッキング（デバッグ用）
  useEffect(() => {
    console.log('🖼️ imagePreview状態が変更されました:', {
      timestamp: new Date().toISOString(),
      hasPreview: !!imagePreview,
      previewDataSize: imagePreview ? `${Math.round(imagePreview.length / 1024)}KB` : 'なし'
    })
  }, [imagePreview])

  // コンポーネント初期化トラッキング（デバッグ用）
  useEffect(() => {
    console.log('🎯 ChatPageContent初期化完了:', {
      timestamp: new Date().toISOString(),
      fileInputRefExists: !!fileInputRef.current,
      webSearchEnabled,
      hasSelectedImage: !!selectedImage,
      hasImagePreview: !!imagePreview
    })
  }, [])

  const scrollToBottom = (smooth = true) => {
    messagesEndRef.current?.scrollIntoView({
      behavior: smooth ? 'smooth' : 'auto',
      block: 'end',
      inline: 'nearest',
    })
  }


  const sendMessage = async () => {
    if (!inputValue.trim() && !selectedImage) return

    console.log('📤 メッセージ送信開始:', { inputValue })

    // メッセージタイプを決定
    let messageType: 'text' | 'audio' | 'image' = 'text'
    let messageContent = inputValue

    if (selectedImage) {
      messageType = 'image'
      messageContent = inputValue
        ? `${inputValue}`
        : '画像を分析してください'
      console.log('🖼️ 画像添付検出:', {
        messageType,
        hasImage: true,
        imageDataSize: imagePreview ? `${Math.round(imagePreview.length / 1024)}KB` : 'なし',
        originalMessage: inputValue
      })
    } else if (isRecording) {
      messageType = 'audio'
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent,
      sender: 'user',
      timestamp: new Date(),
      type: messageType,
    }

    setMessages(prev => [...prev, userMessage])
    const query = inputValue
    setInputValue('')

    // 画像の状態を一時的に保存（送信処理で使用するため）
    const currentSelectedImage = selectedImage
    const currentImagePreview = imagePreview
    
    // 音声状態をリセット（画像は送信後にリセット）
    setIsRecording(false)

    // 会話履歴を準備（ストリーミング・従来共通）
    const conversationHistory = messages
      .filter(msg => {
        // 初期の挨拶メッセージを除外（内容で判定）
        const isInitialMessage =
          msg.content.includes('こんにちは！**GenieUs**です') ||
          msg.content.includes('こんにちは！私はGenieです') ||
          msg.content.includes('こんにちは！私はジーニーです') ||
          msg.content.includes('話すだけで **家族管理・成長記録・努力見える化**')
        return !isInitialMessage
      })
      .map(msg => ({
        id: msg.id,
        content: msg.content,
        sender: msg.sender,
        timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString(),
        type: msg.type,
      }))

    // セッションIDを決定
    const sessionId = currentSession ? currentSession.id : 'default-session'

    // ストリーミング進捗を使用する場合（現在はGenieスタイル固定）
    if (useStreamingProgress) {
      // ストリーミング用のプレースホルダーメッセージを追加
      const streamingMessageId = (Date.now() + 1).toString()

      console.log('🚀 ストリーミング開始:', {
        streamingMessageId,
        query,
        sessionId,
        conversationHistoryLength: conversationHistory.length,
      })

      setCurrentStreamingId(streamingMessageId)

      // Web検索ON または 画像添付時の強力な指示を埋め込み
      let finalStreamingMessage = query
      
      if (webSearchEnabled) {
        finalStreamingMessage = `🔍 FORCE_SEARCH_AGENT_ROUTING 🔍
SYSTEM_INSTRUCTION: この質問は必ず検索エージェント(search_specialist)で処理してください。
他のエージェントへのルーティングは禁止します。
専門性コンテキストより検索要求を優先してください。
検索要求: ${query}
END_SYSTEM_INSTRUCTION`
      } else if (currentSelectedImage) {
        finalStreamingMessage = `🖼️ FORCE_IMAGE_ANALYSIS_ROUTING 🖼️
SYSTEM_INSTRUCTION: この画像は必ず画像分析エージェント(image_specialist)で処理してください。
他のエージェントへのルーティングは禁止します。
画像添付時は画像分析を最優先してください。
コーディネーターをスキップして直接image_specialistにルーティングしてください。
画像分析要求: ${query || '画像を分析してください'}
END_SYSTEM_INSTRUCTION`
      }

      // 画像がある場合のローカルファイルパス取得
      const imagePath = currentSelectedImage ? await getLocalFilePath(currentSelectedImage) : null

      const streamingMessage: Message = {
        id: streamingMessageId,
        content: JSON.stringify({
          message: finalStreamingMessage, // 検索指示埋め込み後のメッセージ
          conversation_history: conversationHistory,
          session_id: sessionId,
          user_id: 'frontend_user',
          family_info: familyInfo,
          message_type: messageType,
          has_image: !!currentSelectedImage,
          image_path: imagePath,
          multimodal_context: {
            type: messageType,
            image_description: currentSelectedImage ? 'ユーザーが画像をアップロードしました' : null,
          },
          web_search_enabled: webSearchEnabled,
        }), // 会話履歴と家族情報も含めて送信
        sender: 'genie',
        timestamp: new Date(),
        type: 'streaming',
      }

      console.log('📋 プレースホルダーメッセージ追加:', {
        messageId: streamingMessage.id,
        messageType: streamingMessage.type,
      })

      setMessages(prev => {
        const newMessages = [...prev, streamingMessage]
        console.log('📊 メッセージ配列状態:', {
          beforeCount: prev.length,
          afterCount: newMessages.length,
          lastMessage: newMessages[newMessages.length - 1],
        })
        return newMessages
      })

      setTimeout(scrollToBottom, 100)
      
      // ストリーミング送信完了後に画像状態をクリア
      if (currentSelectedImage) {
        removeImage()
      }
      
      return // 従来のAPI呼び出しはスキップ
    }

    // 従来のマルチエージェント演出を開始 - 削除
    // setIsOrchestrating(true)

    // ユーザーメッセージ追加後にスクロール
    setTimeout(scrollToBottom, 100)

    try {
      // 会話履歴を準備（初期メッセージと新しく追加するユーザーメッセージを除く）
      const conversationHistory = messages
        .filter(msg => {
          // 初期の挨拶メッセージを除外（内容で判定）
          const isInitialMessage =
            msg.content.includes('こんにちは！**GenieUs**です') ||
            msg.content.includes('こんにちは！私はGenieです') ||
            msg.content.includes('こんにちは！私はジーニーです') ||
            msg.content.includes('話すだけで **家族管理・成長記録・努力見える化**')
          return !isInitialMessage
        })
        .map(msg => ({
          id: msg.id,
          content: msg.content,
          sender: msg.sender,
          timestamp:
            typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString(),
          type: msg.type,
        }))

      // セッションIDを決定（履歴から続ける場合は既存のセッションID、新規の場合はデフォルト）
      const sessionId = currentSession ? currentSession.id : 'default-session'

      // デバッグログ
      console.log('🚀 APIリクエスト送信準備:', {
        sessionId,
        hasCurrentSession: !!currentSession,
        historyLength: conversationHistory.length,
        messageType,
        hasImage: !!currentSelectedImage,
        imageDataSize: currentSelectedImage && currentImagePreview ? `${Math.round(currentImagePreview.length / 1024)}KB` : 'なし',
        webSearchEnabled,
        messageContent,
        historyPreview: conversationHistory.slice(-2).map(msg => ({
          sender: msg.sender,
          contentPreview: msg.content.substring(0, 50) + '...',
        })),
      })

      // 実際のAPIを呼び出し（バックエンドAPIエンドポイントに合わせて修正）
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

      // Web検索ON または 画像添付時の強力な指示を埋め込み
      let finalMessage = query
      
      if (webSearchEnabled) {
        finalMessage = `🔍 FORCE_SEARCH_AGENT_ROUTING 🔍
SYSTEM_INSTRUCTION: この質問は必ず検索エージェント(search_specialist)で処理してください。
他のエージェントへのルーティングは禁止します。
専門性コンテキストより検索要求を優先してください。
検索要求: ${query}
END_SYSTEM_INSTRUCTION`
      } else if (currentSelectedImage) {
        finalMessage = `🖼️ FORCE_IMAGE_ANALYSIS_ROUTING 🖼️
SYSTEM_INSTRUCTION: この画像は必ず画像分析エージェント(image_specialist)で処理してください。
他のエージェントへのルーティングは禁止します。
画像添付時は画像分析を最優先してください。
コーディネーターをスキップして直接image_specialistにルーティングしてください。
画像分析要求: ${query}
END_SYSTEM_INSTRUCTION`
      }

      // 送信するリクエストボディをログ出力
      const requestBody = {
        message: finalMessage,
        user_id: 'frontend_user',
        session_id: sessionId,
        conversation_history: conversationHistory.length > 0 ? conversationHistory : null,
        family_info: familyInfo,
        message_type: messageType,
        has_image: !!currentSelectedImage,
        image_path: currentSelectedImage ? await getLocalFilePath(currentSelectedImage) : null,
        multimodal_context: {
          type: messageType,
          voice_input: isRecording,
          image_description: currentSelectedImage ? 'ユーザーが画像をアップロードしました' : null,
        },
        web_search_enabled: webSearchEnabled,
      }

      console.log('📤 送信するリクエストボディ:', {
        ...requestBody,
        image_path: requestBody.image_path ? `Base64データ(${Math.round(requestBody.image_path.length / 1024)}KB)` : null,
        message: requestBody.message.substring(0, 300) + (requestBody.message.length > 300 ? '...' : ''),
      })

      const response = await fetch(`${API_BASE_URL}/api/streaming/streaming-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      console.log('📥 APIレスポンス受信:', {
        status: response.status,
        statusText: response.statusText,
        contentType: response.headers.get('content-type')
      })

      if (!response.ok) {
        throw new Error('APIリクエストが失敗しました')
      }

      const data = await response.json()

      // レスポンスデータをログ出力
      console.log('📋 レスポンスデータ詳細:', {
        hasData: !!data,
        dataKeys: Object.keys(data || {}),
        routingInfo: data.routing_info || 'なし',
        agentType: data.agent_type || 'なし'
      })

      // デバッグ情報をコンソールに出力
      if (data.debug_info) {
        console.log('🔧 Backend debug info:', data.debug_info)
      }

      // フォローアップ質問をログに出力
      if (data.follow_up_questions) {
        console.log('💭 Follow-up questions:', data.follow_up_questions)
      }

      // エージェント情報を保存
      if (data.agent_info) {
        setCurrentAgentInfo(data.agent_info)
      }

      // インタラクティブ確認データを解析
      const confirmationData = parseInteractiveConfirmation(data.response)
      if (confirmationData) {
        console.log('🤝 インタラクティブ確認データ検出:', confirmationData)
        setHasActiveConfirmation(true)
      }

      const genieMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        sender: 'genie',
        timestamp: new Date(),
        type: 'text',
        followUpQuestions: data.follow_up_questions || [],
        confirmationData: confirmationData || undefined,
        debugInfo: {
          workflow_used: data.debug_info?.session_info?.workflow_used,
          agents_involved: data.debug_info?.session_info?.agents_involved || [],
          processing_time: data.debug_info?.session_info?.processing_time,
        },
      }

      setMessages(prev => [...prev, genieMessage])

      // API応答を受信後、オーケストレーションを終了
      setIsOrchestrating(false)

      // Genieの回答追加後にスクロール
      setTimeout(scrollToBottom, 100)
    } catch (error) {
      console.error('API Error:', error)

      // エラー時のフォールバック応答
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content:
          '申し訳ございません。現在サーバーに接続できません。しばらく時間をおいて再度お試しください。\n\n開発中のため、バックエンドサーバーが起動していない可能性があります。',
        sender: 'genie',
        timestamp: new Date(),
        type: 'text',
      }
      setMessages(prev => [...prev, errorMessage])
      setIsOrchestrating(false)

      // エラーメッセージ追加後にもスクロール
      setTimeout(scrollToBottom, 100)
    } finally {
      // 送信完了後に画像状態をクリア
      if (currentSelectedImage) {
        removeImage()
      }
      // setIsTyping(false)
    }
  }

  // マルチエージェント演出完了後の処理 - 現在未使用
  // const handleOrchestrationComplete = () => {
  //   setIsOrchestrating(false)
  //   setIsTyping(true)
  // }

  // インタラクティブ確認ハンドラ
  const handleConfirmationResponse = async (answer: string, confirmationId: string) => {
    try {
      console.log('🤝 確認応答送信:', { answer, confirmationId })
      setProcessingConfirmation(true)

      // 該当の確認メッセージからcontextDataを取得
      const confirmationMessage = messages.find(msg => 
        msg.confirmationData?.confirmation_id === confirmationId
      )
      const contextData = confirmationMessage?.confirmationData?.context_data || {}

      console.log('🔍 送信するコンテキストデータ:', contextData)

      // 確認応答をサーバーに送信
      const response = await sendConfirmationResponse({
        confirmation_id: confirmationId,
        user_response: answer,
        user_id: 'frontend_user',
        session_id: currentSession ? currentSession.id : 'default-session',
        response_metadata: {
          context_data: contextData
        }
      })

      console.log('✅ 確認応答処理完了:', response)

      // フォローアップアクションに応じた処理
      if (response.followup_action?.action_type === 'proceed') {
        // 肯定的な応答の場合、追加のメッセージを表示
        const followupMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: response.message + '\n\n処理を実行しています...',
          sender: 'genie',
          timestamp: new Date(),
          type: 'text',
        }
        setMessages(prev => [...prev, followupMessage])
      } else if (response.followup_action?.action_type === 'cancel') {
        // 否定的な応答の場合
        const cancelMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: response.message,
          sender: 'genie',
          timestamp: new Date(),
          type: 'text',
        }
        setMessages(prev => [...prev, cancelMessage])
      }

      setTimeout(scrollToBottom, 100)

      // 確認処理完了後、1秒後に状態をリセット（UI遷移を自然にするため）
      setTimeout(() => {
        setHasActiveConfirmation(false)
        setProcessingConfirmation(false)
      }, 1000)

    } catch (error) {
      console.error('❌ 確認応答処理エラー:', error)
      
      // エラー時も状態をリセット
      setHasActiveConfirmation(false)
      setProcessingConfirmation(false)
      
      // エラーメッセージを表示
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: '申し訳ございません。確認応答の処理中にエラーが発生しました。もう一度お試しください。',
        sender: 'genie',
        timestamp: new Date(),
        type: 'text',
      }
      setMessages(prev => [...prev, errorMessage])
      setTimeout(scrollToBottom, 100)
    }
  }

  // フォローアップクエスチョンを除去するヘルパー関数
  const cleanResponseContent = (response: string): string => {
    try {
      // 💭マークを含む行を除去
      const lines = response.split('\n')
      const cleanLines = []
      let inFollowupSection = false

      for (const line of lines) {
        const trimmedLine = line.trim()

        // フォローアップセクションの開始を検出
        if (
          trimmedLine.includes('続けて相談する') ||
          trimmedLine.includes('続けて相談したい方へ') ||
          trimmedLine.includes('【続けて相談したい方へ】') ||
          trimmedLine.includes('【続けて相談する】')
        ) {
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

      return cleanLines
        .join('\n')
        .replace(/\n\s*\n\s*\n/g, '\n\n')
        .trim()
    } catch (error) {
      console.warn('レスポンスクリーンアップエラー:', error)
      return response
    }
  }

  // ストリーミング完了時の処理
  const handleStreamingComplete = (response: string, searchData?: SearchData) => {
    console.log('🔄 handleStreamingComplete 開始:', {
      currentStreamingId,
      responseLength: response.length,
      responsePreview: response.substring(0, 100) + '...',
    })

    // 既にストリーミングが完了している場合は重複処理を防ぐ
    if (!currentStreamingId) {
      console.log('⚠️ handleStreamingComplete: 既に完了済み - 重複処理をスキップ')
      return
    }

    const cleanedResponse = cleanResponseContent(response)

    // インタラクティブ確認データを解析
    const confirmationData = parseInteractiveConfirmation(response)
    if (confirmationData) {
      console.log('🤝 ストリーミング応答でインタラクティブ確認データ検出:', confirmationData)
      setHasActiveConfirmation(true)
    }

    console.log('✨ メッセージ置換実行:', {
      targetId: currentStreamingId,
      cleanedResponseLength: cleanedResponse.length,
      cleanedResponsePreview: cleanedResponse.substring(0, 100) + '...',
      hasConfirmationData: !!confirmationData,
    })

    setMessages(prev => {
      const updatedMessages = prev.map(msg =>
        msg.id === currentStreamingId
          ? { ...msg, content: cleanedResponse, type: 'text' as const, searchData, confirmationData: confirmationData || undefined }
          : msg
      )

      console.log('📝 メッセージ配列更新:', {
        beforeCount: prev.length,
        afterCount: updatedMessages.length,
        replacedMessage: updatedMessages.find(m => m.id === currentStreamingId),
        hasSearchData: !!searchData,
      })

      return updatedMessages
    })

    console.log('🎯 ストリーミング状態リセット:', {
      oldStreamingId: currentStreamingId,
      newStreamingId: null,
    })

    setCurrentStreamingId(null)
    // setIsTyping(false)

    console.log('✅ handleStreamingComplete 完了')
  }

  // ストリーミングエラー時の処理
  const handleStreamingError = (error: string) => {
    console.log('❌ handleStreamingError 開始:', {
      currentStreamingId,
      error,
    })

    setMessages(prev =>
      prev.map(msg =>
        msg.id === currentStreamingId
          ? {
              ...msg,
              content: `申し訳ございません。エラーが発生しました: ${error}`,
              type: 'text' as const,
            }
          : msg
      )
    )
    setCurrentStreamingId(null)
    // setIsTyping(false)

    console.log('❌ handleStreamingError 完了')
  }

  // チャットを保存
  const saveChat = async () => {
    if (messages.length <= 1) return // 初期メッセージのみの場合は保存しない

    try {
      const firstUserMessage = messages.find(msg => msg.sender === 'user')
      const title = firstUserMessage
        ? firstUserMessage.content.length > 50
          ? firstUserMessage.content.substring(0, 50) + '...'
          : firstUserMessage.content
        : '新しいチャット'

      const sessionMessages = messages.map(msg => ({
        ...msg,
        timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString(),
      }))

      if (currentSession) {
        // 既存セッションを更新
        await updateSession(currentSession.id, sessionMessages)
      } else {
        // 新しいセッションを作成
        const newSession = await createSession(title, sessionMessages)
        if (newSession) {
          setCurrentSession(newSession)
        }
      }
      setUnsavedChanges(false)
    } catch (error) {
      console.error('Failed to save chat:', error)
    }
  }

  // 新しいチャットを開始
  const startNewChat = () => {
    setMessages([
      {
        id: '1',
        content:
          'こんにちは！**GenieUs**です\n\n話すだけで **家族管理・成長記録・努力見える化** すべてがつながる子育てアシスタント！\n\n**15人の専門GenieUs Agents**が連携してサポートします\n\n**こんなことができます：**\n• **「家族情報を登録」** → パパ・ママ・お子さんの情報をまとめて管理\n• **「今日どうだった？」** → 複数の専門エージェントがあなたの話を理解・記録\n• **「初めて歩いた！」** → 写真付きで大切な瞬間をメモリーズに保存\n• **「頑張ったことを教えて」** → あなたの愛情と努力をGenieが理解・認める\n• **「夜泣きがひどくて困っています」** → 専門エージェントが具体的にアドバイス\n• **「近くの病院を検索して」** → 最新情報を検索してお届け\n• **「子供向けイベントを探して」** → お出かけ先やイベントをご提案\n\n**専門分野：** 睡眠・栄養・夜泣き・離乳食・発達・遊び・しつけ・健康・行動・安全・心理・仕事両立・特別支援・検索・窓口申請・おでかけイベントなど\n\n何でもお気軽にお話しください！あなたに最適な専門エージェントが自動的にサポートします',
        sender: 'genie',
        timestamp: new Date('2025-01-01T00:00:00.000Z'),
        type: 'text',
      },
    ])
    setCurrentSession(null)
    setUnsavedChanges(false)

    // 新しいチャット開始時に最上部にスクロール
    setTimeout(() => scrollToBottom(false), 100)
  }

  // 履歴からチャットを読み込み
  const loadChatFromHistory = async (sessionId: string) => {
    const session = await loadSession(sessionId)
    if (session) {
      // メッセージを復元
      setMessages(
        session.messages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }))
      )

      // 現在のセッションとして設定（これで続きから会話できる）
      setCurrentSession(session)
      setUnsavedChanges(false)
      setShowHistory(false)

      // 履歴読み込み後に最下部にスクロール
      setTimeout(() => scrollToBottom(false), 300)

      // デバッグ情報をログに出力
      console.log('Loaded chat session:', {
        sessionId: session.id,
        title: session.title,
        messageCount: session.messages.length,
      })
    }
  }

  // Web検索モード切り替え
  const toggleWebSearch = () => {
    const newState = !webSearchEnabled
    setWebSearchEnabled(newState)

    // 🎯 Web検索ON時は画像を削除
    if (newState && selectedImage) {
      removeImage()
      console.log('🔍 Web検索有効化により画像を削除')
    }

    console.log('🔍 Web検索状態を切り替え:', {
      from: webSearchEnabled,
      to: newState,
      timestamp: new Date().toISOString(),
    })
  }

  // 音声録音開始/停止
  const toggleRecording = async () => {
    if (isRecording) {
      // 録音停止（実装は簡略化）
      setIsRecording(false)
      setInputValue(inputValue + ' [音声入力完了]')
    } else {
      // 録音開始
      setIsRecording(true)
      // 実際の音声録音機能は FloatingVoiceButton を参考に実装
    }
  }

  // 画像リサイズ処理
  const resizeImage = (
    file: File,
    maxWidth: number = 800,
    maxHeight: number = 600,
    quality: number = 0.8
  ): Promise<string> => {
    return new Promise(resolve => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')!
      const img = new Image()

      img.onload = () => {
        // 元の縦横比を保持してリサイズ
        let { width, height } = img

        if (width > height) {
          if (width > maxWidth) {
            height = (height * maxWidth) / width
            width = maxWidth
          }
        } else {
          if (height > maxHeight) {
            width = (width * maxHeight) / height
            height = maxHeight
          }
        }

        canvas.width = width
        canvas.height = height
        ctx.drawImage(img, 0, 0, width, height)

        // JPEGに変換してサイズ削減
        const resizedDataUrl = canvas.toDataURL('image/jpeg', quality)
        resolve(resizedDataUrl)
      }

      const reader = new FileReader()
      reader.onload = e => {
        img.src = e.target?.result as string
      }
      reader.readAsDataURL(file)
    })
  }

  // 画像選択処理
  const handleImageSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('🎯 handleImageSelect関数が呼び出されました:', {
      timestamp: new Date().toISOString(),
      eventType: event.type,
      filesCount: event.target.files?.length || 0,
      firstFileName: event.target.files?.[0]?.name || 'なし',
      firstFileType: event.target.files?.[0]?.type || 'なし',
      firstFileSize: event.target.files?.[0]?.size || 0
    })

    const file = event.target.files?.[0]
    if (file) {
      console.log('📁 ファイルが選択されました:', {
        name: file.name,
        size: `${Math.round(file.size / 1024)}KB`,
        type: file.type,
        lastModified: new Date(file.lastModified).toISOString()
      })

      // 画像形式チェック
      if (!file.type.startsWith('image/')) {
        console.log('❌ 画像形式チェック失敗:', { fileType: file.type })
        alert('画像ファイルを選択してください。')
        return
      }

      console.log('✅ 画像形式チェック通過、リサイズ開始')
      try {
        // 画像をリサイズしてプレビュー設定
        const resizedImage = await resizeImage(file, 800, 600, 0.8)
        console.log('✅ 画像リサイズ完了:', {
          originalSize: `${Math.round(file.size / 1024)}KB`,
          resizedDataSize: `${Math.round(resizedImage.length / 1024)}KB`
        })

        setImagePreview(resizedImage)
        setSelectedImage(file) // 元ファイルも保持

        console.log('🖼️ 画像状態更新完了:', {
          hasPreview: !!resizedImage,
          hasSelectedImage: !!file,
          webSearchWasEnabled: webSearchEnabled
        })

        // 🎯 Web検索を自動無効化
        if (webSearchEnabled) {
          setWebSearchEnabled(false)
          console.log('🖼️ 画像選択によりWeb検索を無効化')
        }
      } catch (error) {
        console.error('❌ 画像処理エラー:', error)
        console.log('🔍 エラー詳細:', {
          errorMessage: error.message,
          errorStack: error.stack,
          fileName: file.name,
          fileSize: file.size
        })
        alert('画像の処理中にエラーが発生しました。')
      }
    } else {
      console.log('❌ ファイルが選択されていません')
    }
  }

  // 画像削除
  const removeImage = () => {
    console.log('🗑️ 画像削除処理実行:', {
      timestamp: new Date().toISOString(),
      hadSelectedImage: !!selectedImage,
      hadPreview: !!imagePreview,
      fileInputValue: fileInputRef.current?.value || '空'
    })
    
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    
    console.log('✅ 画像削除処理完了')
  }

  // フォローアップ質問をクリックしたときの処理
  const handleFollowUpClick = (question: string) => {
    console.log('🔍 フォローアップクエスチョンクリック:', { question })
    setInputValue(question)
    // 状態更新を待ってから送信（重複を防ぐため）
    setTimeout(() => {
      sendMessage()
    }, 50) // 少し長めに待機
    // フォローアップクエスチョンをクリア
    setCurrentFollowupQuestions([])
  }

  // フォローアップクエスチョンを受け取る処理
  const handleFollowupQuestions = (questions: string[]) => {
    setCurrentFollowupQuestions(questions)
  }

  // テキスト指定でメッセージ送信
  const _sendMessageWithText = async (text: string) => {
    if (!text.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: text,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')

    // ストリーミング用のプレースホルダーメッセージを追加
    const streamingMessageId = (Date.now() + 1).toString()
    setCurrentStreamingId(streamingMessageId)

    // Web検索ONの場合、メッセージに検索指示を埋め込み
    const finalText = webSearchEnabled ? `【最新情報を検索してください】${text}` : text

    const streamingMessage: Message = {
      id: streamingMessageId,
      content: JSON.stringify({
        message: finalText, // 検索指示埋め込み後のメッセージ
        conversation_history: messages
          .filter(msg => {
            const isInitialMessage =
              msg.content.includes('こんにちは！**GenieUs**です') ||
              msg.content.includes('こんにちは！私はGenieです') ||
              msg.content.includes('こんにちは！私はジーニーです') ||
              msg.content.includes('話すだけで **家族管理・成長記録・努力見える化**')
            return !isInitialMessage
          })
          .map(msg => ({
            id: msg.id,
            content: msg.content,
            sender: msg.sender,
            timestamp:
              typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString(),
            type: msg.type,
          })),
        session_id: currentSession ? currentSession.id : 'default-session',
        user_id: 'frontend_user',
        family_info: familyInfo,
      }),
      sender: 'genie',
      timestamp: new Date(),
      type: 'streaming',
    }

    setMessages(prev => [...prev, streamingMessage])
    setTimeout(scrollToBottom, 100)
  }

  // 家族情報を読み込み
  useEffect(() => {
    const loadFamilyInfo = async () => {
      try {
        const response = await getFamilyInfo('frontend_user')
        if (response.success && response.data) {
          setFamilyInfo(formatFamilyInfoForChat(response.data))
        }
      } catch (error) {
        console.error('家族情報の読み込みに失敗しました:', error)
      }
    }

    loadFamilyInfo()
  }, [])

  // メッセージが変更されたら未保存フラグを立てる
  useEffect(() => {
    if (messages.length > 1) {
      setUnsavedChanges(true)
    }
  }, [messages])

  // メッセージが変更されたら自動スクロール
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // オーケストレーション開始/終了時もスクロール - 削除
  // useEffect(() => {
  //   if (isOrchestrating) {
  //     setTimeout(scrollToBottom, 200)
  //   }
  // }, [isOrchestrating])

  const quickQuestions = [
    '夜泣きがひどくて困っています',
    '離乳食を食べてくれません',
    '発達が気になります',
    '授乳のタイミングがわかりません',
    'イヤイヤ期の対応方法を教えて',
    '保育園選びで悩んでいます',
    'ママ友との付き合い方について',
    '仕事復帰の準備をしたい',
  ]

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
        {/* ページヘッダー */}
        <div className="border-b border-amber-100 bg-white/80 backdrop-blur-sm">
          <div className="mx-auto max-w-6xl px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-amber-500 to-orange-600 shadow-lg">
                  <GiMagicLamp className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">Genieと話す</h1>
                  <p className="text-gray-600">あなただけの魔法のランプが子育てをサポート</p>
                  {currentSession && (
                    <p className="mt-1 max-w-[300px] truncate text-sm text-amber-600">
                      {currentSession.title}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Button
                  onClick={startNewChat}
                  className="bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg hover:from-amber-600 hover:to-orange-600"
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  Genieに相談
                </Button>
                <Button
                  onClick={() => setShowHistory(!showHistory)}
                  variant="outline"
                  className="border-amber-300 text-amber-700 hover:bg-amber-50"
                >
                  <History className="mr-2 h-4 w-4" />
                  履歴
                </Button>
                {unsavedChanges && (
                  <Button
                    onClick={saveChat}
                    className="bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-lg hover:from-emerald-600 hover:to-green-600"
                  >
                    <Save className="mr-2 h-4 w-4" />
                    保存
                  </Button>
                )}
                <div className="hidden items-center gap-2 rounded-lg border border-amber-200 bg-white/60 px-3 py-1.5 backdrop-blur-sm md:flex">
                  <GiMagicLamp className="h-4 w-4 text-amber-600" />
                  <span className="text-sm font-medium text-amber-700">24時間対応</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="overflow-y-auto">
          <div className="mx-auto max-w-6xl space-y-6 p-6 pb-4">
            {messages.map(message => (
              <div
                key={message.id}
                className={`flex gap-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.sender === 'genie' && (
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-amber-500 to-orange-600 shadow-lg">
                    <GiMagicLamp className="h-5 w-5 text-white" />
                  </div>
                )}

                <div
                  className={`${
                    message.type === 'streaming' ? 'w-full max-w-[90%]' : 'max-w-[85%]'
                  } ${message.sender === 'user' ? 'order-first' : ''}`}
                >
                  {message.type === 'streaming' ? (
                    // ストリーミング進捗表示（Genieスタイル固定）
                    <GenieStyleProgress
                      message={message.content}
                      userId="frontend_user"
                      sessionId={currentSession ? currentSession.id : 'default-session'}
                      onComplete={handleStreamingComplete}
                      onError={handleStreamingError}
                      onFollowupQuestions={handleFollowupQuestions}
                    />
                  ) : (
                    // 通常のメッセージ表示
                    <Card
                      className={`border-0 shadow-lg ${
                        message.sender === 'user'
                          ? 'bg-gradient-to-br from-amber-500 to-orange-500 text-white'
                          : 'border border-amber-100 bg-white/90 backdrop-blur-sm'
                      }`}
                    >
                      <CardContent className="p-4">
                        {message.sender === 'genie' ? (
                          <div className="space-y-4">
                            <div className="prose prose-sm max-w-none text-gray-800 prose-headings:font-bold prose-headings:text-gray-800 prose-p:text-gray-700 prose-blockquote:border-amber-300 prose-blockquote:text-gray-600 prose-strong:text-gray-800 prose-ol:text-gray-700 prose-ul:text-gray-700 prose-li:text-gray-700">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {message.content}
                              </ReactMarkdown>
                            </div>

                            {/* 検索結果表示 */}
                            {message.searchData && (
                              <SearchResultsDisplay
                                searchQuery={{
                                  query: message.searchData.search_query || '',
                                  timestamp: message.searchData.timestamp
                                    ? new Date(message.searchData.timestamp).getTime()
                                    : Date.now(),
                                  results_count: message.searchData.results_count,
                                }}
                                searchResults={message.searchData.search_results?.map(result => ({
                                  title: result.title,
                                  url: result.url,
                                  snippet: result.snippet,
                                  displayLink: result.domain,
                                }))}
                              />
                            )}

                            {/* インタラクティブ確認表示 */}
                            {message.confirmationData && (
                              <InteractiveConfirmation
                                confirmationId={message.confirmationData.confirmation_id}
                                question={message.confirmationData.question}
                                options={message.confirmationData.options}
                                contextData={message.confirmationData.context_data}
                                onConfirm={handleConfirmationResponse}
                                timeout={message.confirmationData.timeout_seconds}
                              />
                            )}
                          </div>
                        ) : (
                          <p className="whitespace-pre-line text-white">{message.content}</p>
                        )}

                        {/* デバッグ情報表示（開発時のみ） */}
                        {message.sender === 'genie' && message.debugInfo?.workflow_used && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            <span className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-600">
                              {message.debugInfo.workflow_used}エージェント使用
                            </span>
                            {message.debugInfo.processing_time && (
                              <span className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-600">
                                {message.debugInfo.processing_time}ms
                              </span>
                            )}
                          </div>
                        )}

                        <p
                          className={`mt-3 text-xs ${
                            message.sender === 'user' ? 'text-amber-100' : 'text-gray-500'
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString('ja-JP', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </div>

                {message.sender === 'user' && (
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg">
                    <User className="h-5 w-5 text-white" />
                  </div>
                )}
              </div>
            ))}

            {/* マルチエージェント協調演出 - 削除 */}

            {/* タイピングアニメーション - 削除 */}

            {/* フォローアップクエスチョン */}
            {currentFollowupQuestions.length > 0 && (
              <div className="px-6 pb-4">
                <FollowupQuestions
                  questions={currentFollowupQuestions}
                  onQuestionClick={handleFollowUpClick}
                />
              </div>
            )}

            {/* スクロール用の参照点 */}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* インプットエリア */}
        <div className="sticky bottom-0 bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 pt-4">
          {/* よくある相談 */}
          {messages.length === 1 && (
            <div className="mx-auto max-w-5xl px-6 py-2">
              <div className="rounded-lg border border-amber-200 bg-white/60 p-3 backdrop-blur-sm">
                <div className="mb-2 flex items-center gap-2">
                  <Star className="h-4 w-4 text-amber-600" />
                  <h3 className="text-sm font-medium text-gray-700">よくある相談</h3>
                </div>
                <div className="grid grid-cols-2 gap-1.5 md:grid-cols-4">
                  {quickQuestions.map((question, index) => (
                    <button
                      key={index}
                      className="rounded-md border border-amber-100 bg-white p-2 text-left text-xs text-gray-700 transition-all duration-200 hover:border-amber-300 hover:bg-amber-50 hover:text-amber-800"
                      onClick={() => setInputValue(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* インプットエリア */}
          <div className="mx-auto max-w-4xl p-4">
            <div className="rounded-lg border border-amber-200 bg-white/90 p-4 shadow-lg backdrop-blur-sm">
              {/* 画像プレビュー */}
              {imagePreview && (
                <div className="relative mb-3 inline-block">
                  <img
                    src={imagePreview}
                    alt="選択された画像"
                    className="max-h-32 rounded-lg border border-amber-200"
                  />
                  <button
                    onClick={removeImage}
                    className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-xs text-white transition-colors hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              )}

              {/* Web検索モード表示 */}
              {webSearchEnabled && (
                <div className="mb-3 flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 p-2">
                  <Search className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-700">Web検索モード有効</span>
                  <span className="text-xs text-green-600">最新情報を検索して回答します</span>
                </div>
              )}

              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <textarea
                    value={inputValue}
                    onChange={e => setInputValue(e.target.value)}
                    placeholder={
                      hasActiveConfirmation || processingConfirmation
                        ? '確認処理中です... 🤝'
                        : webSearchEnabled
                        ? 'Web検索で最新情報を調べます... 🔍'
                        : '何でも相談してください... ✨'
                    }
                    disabled={hasActiveConfirmation || processingConfirmation}
                    className={`h-12 max-h-[100px] w-full resize-none rounded-lg border px-4 py-3 text-sm transition-all duration-200 ${
                      hasActiveConfirmation || processingConfirmation
                        ? 'cursor-not-allowed border-gray-200 bg-gray-100 text-gray-400 opacity-75'
                        : 'border-amber-200 bg-white focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-500'
                    }`}
                    rows={1}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                        e.preventDefault()
                        sendMessage()
                      }
                    }}
                  />
                </div>

                {/* Web検索ボタン */}
                <Button
                  onClick={toggleWebSearch}
                  disabled={!!selectedImage}
                  className={`h-12 rounded-lg border px-3 transition-all duration-200 ${
                    selectedImage
                      ? 'cursor-not-allowed border-gray-200 bg-gray-100 text-gray-400 opacity-50'
                      : webSearchEnabled
                        ? 'border-green-500 bg-green-500 text-white shadow-lg hover:bg-green-600'
                        : 'border-purple-200 bg-purple-50 text-purple-700 hover:border-purple-300 hover:bg-purple-100'
                  }`}
                  type="button"
                  title={
                    selectedImage
                      ? '画像選択中は使用できません'
                      : webSearchEnabled
                        ? 'Web検索を無効にする'
                        : 'Web検索を有効にする'
                  }
                >
                  <Search className="h-4 w-4" />
                </Button>

                {/* 画像アップロードボタン */}
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleImageSelect}
                  accept="image/*"
                  className="hidden"
                />
                <Button
                  onClick={() => {
                    console.log('📷 カメラボタンがクリックされました:', {
                      timestamp: new Date().toISOString(),
                      webSearchEnabled,
                      fileInputExists: !!fileInputRef.current,
                      fileInputValue: fileInputRef.current?.value || '空',
                      disabled: webSearchEnabled
                    })
                    
                    if (webSearchEnabled) {
                      console.log('⚠️ Web検索が有効なためカメラ機能は無効です')
                      return
                    }
                    
                    console.log('✅ ファイル選択ダイアログを開きます')
                    fileInputRef.current?.click()
                  }}
                  disabled={webSearchEnabled}
                  className={`h-12 rounded-lg border px-3 transition-all duration-200 ${
                    webSearchEnabled
                      ? 'cursor-not-allowed border-gray-200 bg-gray-100 text-gray-400 opacity-50'
                      : 'border-blue-200 bg-blue-50 text-blue-700 hover:border-blue-300 hover:bg-blue-100'
                  }`}
                  type="button"
                  title={webSearchEnabled ? 'Web検索中は使用できません' : '画像をアップロード'}
                >
                  <Camera className="h-4 w-4" />
                </Button>

                {/* 音声録音ボタン（将来の拡張用） */}
                <Button
                  onClick={toggleRecording}
                  className={`h-12 rounded-lg border px-3 transition-all duration-200 ${
                    isRecording
                      ? 'border-red-500 bg-red-500 text-white hover:bg-red-600'
                      : 'border-green-200 bg-green-50 text-green-700 hover:border-green-300 hover:bg-green-100'
                  }`}
                  type="button"
                >
                  {isRecording ? <IoStop className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </Button>

                <Button
                  onClick={sendMessage}
                  className="h-12 rounded-lg border-0 bg-gradient-to-r from-amber-500 to-orange-500 px-6 transition-all duration-200 hover:from-amber-600 hover:to-orange-600"
                  disabled={(!inputValue.trim() && !selectedImage) || hasActiveConfirmation || processingConfirmation}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* チャット履歴パネル */}
        {showHistory && (
          <div className="fixed inset-0 z-50 flex bg-black/50">
            <div className="flex-1" onClick={() => setShowHistory(false)} />
            <div className="h-full w-96 overflow-y-auto bg-white shadow-2xl">
              <div className="border-b bg-gradient-to-r from-amber-500 to-orange-600 p-6 text-white">
                <div className="flex items-center gap-3">
                  <History className="h-6 w-6" />
                  <h2 className="text-xl font-bold">チャット履歴</h2>
                </div>
                <p className="mt-1 text-sm text-amber-100">過去の相談を振り返る</p>
              </div>
              <div className="space-y-3 p-6">
                {historyLoading ? (
                  <LoadingSpinner
                    message="履歴を読み込み中..."
                    fullScreen={false}
                    className="py-8"
                  />
                ) : sessions.length === 0 ? (
                  <div className="py-8 text-center text-gray-500">
                    <MessageCircle className="mx-auto mb-3 h-12 w-12 text-gray-300" />
                    <p>履歴がありません</p>
                    <p className="mt-1 text-sm">新しい相談を始めてみましょう</p>
                  </div>
                ) : (
                  sessions.map(session => (
                    <Card
                      key={session.id}
                      className={`cursor-pointer border-0 shadow-sm transition-all duration-200 hover:shadow-md ${
                        currentSession?.id === session.id
                          ? 'bg-amber-50 ring-2 ring-amber-500'
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => loadChatFromHistory(session.id)}
                    >
                      <CardContent className="p-4">
                        <h3 className="truncate font-semibold text-gray-800">{session.title}</h3>
                        <div className="mt-2 flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            {session.messages.length}件のメッセージ
                          </span>
                          <span className="text-sm text-gray-500">
                            {new Date(session.updatedAt).toLocaleDateString('ja-JP')}
                          </span>
                        </div>
                        {session.tags && session.tags.length > 0 && (
                          <div className="mt-3 flex gap-1">
                            {session.tags.slice(0, 2).map((tag, index) => (
                              <span
                                key={index}
                                className="rounded-full bg-gradient-to-r from-amber-100 to-orange-100 px-2 py-1 text-xs text-amber-800"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
