'use client'
import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { AppLayout } from '@/components/layout/app-layout'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChatHistory } from '@/hooks/use-chat-history'
import { MultiAgentOrchestration } from '@/components/features/chat/multi-agent-orchestration'
import { InlineProgressDisplay } from '@/components/features/chat/inline-progress-display'
import { PerplexityStyleProgress } from '@/components/features/chat/perplexity-style-progress'
import { TimelineStyleProgress } from '@/components/features/chat/timeline-style-progress'
import { GenieStyleProgress } from '@/components/features/chat/genie-style-progress'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { getFamilyInfo, formatFamilyInfoForChat } from '@/lib/api/family'
import { 
  IoSend,
  IoMic,
  IoCamera,
  IoStop,
  IoImage,
  IoVolumeHigh,
  IoBulbOutline,
  IoSparkles,
  IoTime
} from 'react-icons/io5'
import {
  AiOutlineMessage,
  AiOutlineHistory,
  AiOutlinePlus,
  AiOutlineSave,
  AiOutlineUser
} from 'react-icons/ai'
import {
  Sparkles,
  MessageCircle,
  Plus,
  History,
  Save,
  Camera,
  Mic,
  Send,
  User,
  Heart,
  Star
} from 'lucide-react'
import Link from 'next/link'
import {
  FaUserTie
} from 'react-icons/fa'
import { GiMagicLamp } from 'react-icons/gi'

interface Message {
  id: string
  content: string
  sender: 'user' | 'genie'
  timestamp: Date
  type?: 'text' | 'audio' | 'image' | 'streaming'
  followUpQuestions?: string[]
  debugInfo?: {
    workflow_used?: string
    agents_involved?: string[]
    processing_time?: number
  }
}

export default function ChatPage() {
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
      content: 'こんにちは！私はGenieです ✨ 子育ての記録・分析・相談をお手伝いします！\n\n**できること:**\n• 音声で話すだけで授乳・睡眠・食事を記録\n• 写真を送るだけで食事量・表情を分析\n• 夜泣き・離乳食・発達の相談に24時間対応\n\n何でもお気軽にお話しください！',
      sender: 'genie',
      timestamp: new Date(),
      type: 'text'
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [unsavedChanges, setUnsavedChanges] = useState(false)
  const [isOrchestrating, setIsOrchestrating] = useState(false)
  const [currentQuery, setCurrentQuery] = useState('')
  const [currentAgentInfo, setCurrentAgentInfo] = useState<any>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [useStreamingProgress] = useState(true)
  const [progressStyle] = useState<'genie' | 'timeline' | 'modern' | 'simple'>('genie')
  const [currentStreamingId, setCurrentStreamingId] = useState<string | null>(null)
  const [familyInfo, setFamilyInfo] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = (smooth = true) => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: smooth ? 'smooth' : 'auto',
      block: 'end',
      inline: 'nearest'
    })
  }

  const sendMessage = async () => {
    if (!inputValue.trim() && !selectedImage) return

    // メッセージタイプを決定
    let messageType: 'text' | 'audio' | 'image' = 'text'
    let messageContent = inputValue
    
    if (selectedImage) {
      messageType = 'image'
      messageContent = inputValue || '画像を送信しました'
    } else if (isRecording) {
      messageType = 'audio'
    }
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent,
      sender: 'user',
      timestamp: new Date(),
      type: messageType
    }

    setMessages(prev => [...prev, userMessage])
    const query = inputValue
    setCurrentQuery(query)
    setInputValue('')
    
    // 画像や音声状態をリセット
    removeImage()
    setIsRecording(false)
    
    // 会話履歴を準備（ストリーミング・従来共通）
    const conversationHistory = messages
      .filter(msg => {
        // 初期の挨拶メッセージを除外（内容で判定）
        const isInitialMessage = msg.content.includes('こんにちは！私はGenieです') || 
                                msg.content.includes('こんにちは！私はジーニーです')
        return !isInitialMessage
      })
      .map(msg => ({
        id: msg.id,
        content: msg.content,
        sender: msg.sender,
        timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString(),
        type: msg.type
      }))

    // セッションIDを決定
    const sessionId = currentSession ? currentSession.id : 'default-session'

    // ストリーミング進捗を使用する場合（現在はGenieスタイル固定）
    if (useStreamingProgress) {
      // ストリーミング用のプレースホルダーメッセージを追加
      const streamingMessageId = (Date.now() + 1).toString()
      setCurrentStreamingId(streamingMessageId)
      
      const streamingMessage: Message = {
        id: streamingMessageId,
        content: JSON.stringify({
          message: query,
          conversation_history: conversationHistory,
          session_id: sessionId,
          user_id: 'frontend_user',
          family_info: familyInfo
        }), // 会話履歴と家族情報も含めて送信
        sender: 'genie',
        timestamp: new Date(),
        type: 'streaming'
      }

      setMessages(prev => [...prev, streamingMessage])
      setTimeout(scrollToBottom, 100)
      return // 従来のAPI呼び出しはスキップ
    }

    // 従来のマルチエージェント演出を開始
    setIsOrchestrating(true)
    
    // ユーザーメッセージ追加後にスクロール
    setTimeout(scrollToBottom, 100)

    try {
      // 会話履歴を準備（初期メッセージと新しく追加するユーザーメッセージを除く）
      const conversationHistory = messages
        .filter(msg => {
          // 初期の挨拶メッセージを除外（内容で判定）
          const isInitialMessage = msg.content.includes('こんにちは！私はGenieです') || 
                                  msg.content.includes('こんにちは！私はジーニーです')
          return !isInitialMessage
        })
        .map(msg => ({
          id: msg.id,
          content: msg.content,
          sender: msg.sender,
          timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString(),
          type: msg.type
        }))

      // セッションIDを決定（履歴から続ける場合は既存のセッションID、新規の場合はデフォルト）
      const sessionId = currentSession ? currentSession.id : 'default-session'

      // デバッグログ
      console.log('Sending chat message:', {
        sessionId,
        hasCurrentSession: !!currentSession,
        historyLength: conversationHistory.length,
        messageContent,
        historyPreview: conversationHistory.slice(-2).map(msg => ({
          sender: msg.sender,
          contentPreview: msg.content.substring(0, 50) + '...'
        }))
      })

      // 実際のAPIを呼び出し（バックエンドAPIエンドポイントに合わせて修正）
      const response = await fetch('http://localhost:8000/api/v1/multiagent/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: query,
          user_id: 'frontend_user',
          session_id: sessionId,
          conversation_history: conversationHistory.length > 0 ? conversationHistory : null,
          family_info: familyInfo,
          message_type: messageType,
          has_image: !!selectedImage,
          image_path: selectedImage ? imagePreview : null, // Base64データを送信
          multimodal_context: {
            type: messageType,
            voice_input: isRecording,
            image_description: selectedImage ? 'ユーザーが画像をアップロードしました' : null
          }
        })
      })

      if (!response.ok) {
        throw new Error('APIリクエストが失敗しました')
      }

      const data = await response.json()

      // デバッグ情報をコンソールに出力
      if (data.debug_info) {
        console.log('Backend debug info:', data.debug_info)
      }

      // フォローアップ質問をログに出力
      if (data.follow_up_questions) {
        console.log('Follow-up questions:', data.follow_up_questions)
      }

      // エージェント情報を保存
      if (data.agent_info) {
        setCurrentAgentInfo(data.agent_info)
      }

      const genieMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        sender: 'genie',
        timestamp: new Date(),
        type: 'text',
        followUpQuestions: data.follow_up_questions || [],
        debugInfo: {
          workflow_used: data.debug_info?.session_info?.workflow_used,
          agents_involved: data.debug_info?.session_info?.agents_involved || [],
          processing_time: data.debug_info?.session_info?.processing_time
        }
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
        content: '申し訳ございません。現在サーバーに接続できません。しばらく時間をおいて再度お試しください。\n\n開発中のため、バックエンドサーバーが起動していない可能性があります。',
        sender: 'genie',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, errorMessage])
      setIsOrchestrating(false)
      
      // エラーメッセージ追加後にもスクロール
      setTimeout(scrollToBottom, 100)
    } finally {
      setIsTyping(false)
    }
  }

  // マルチエージェント演出完了後の処理
  const handleOrchestrationComplete = () => {
    setIsOrchestrating(false)
    setIsTyping(true)
  }

  // ストリーミング完了時の処理
  const handleStreamingComplete = (response: string) => {
    setMessages(prev => 
      prev.map(msg => 
        msg.id === currentStreamingId 
          ? { ...msg, content: response, type: 'text' as const }
          : msg
      )
    )
    setCurrentStreamingId(null)
    setIsTyping(false)
  }

  // ストリーミングエラー時の処理
  const handleStreamingError = (error: string) => {
    setMessages(prev => 
      prev.map(msg => 
        msg.id === currentStreamingId 
          ? { ...msg, content: `申し訳ございません。エラーが発生しました: ${error}`, type: 'text' as const }
          : msg
      )
    )
    setCurrentStreamingId(null)
    setIsTyping(false)
  }

  // チャットを保存
  const saveChat = async () => {
    if (messages.length <= 1) return // 初期メッセージのみの場合は保存しない

    try {
      const firstUserMessage = messages.find(msg => msg.sender === 'user')
      const title = firstUserMessage ? 
        (firstUserMessage.content.length > 50 ? 
          firstUserMessage.content.substring(0, 50) + '...' : 
          firstUserMessage.content
        ) : '新しいチャット'

      const sessionMessages = messages.map(msg => ({
        ...msg,
        timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString()
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
        content: 'こんにちは！私はGenieです ✨ 子育ての記録・分析・相談をお手伝いします！\n\n**できること:**\n• 音声で話すだけで授乳・睡眠・食事を記録\n• 写真を送るだけで食事量・表情を分析\n• 夜泣き・離乳食・発達の相談に24時間対応\n\n何でもお気軽にお話しください！',
        sender: 'genie',
        timestamp: new Date(),
        type: 'text'
      }
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
      setMessages(session.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })))
      
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
        messageCount: session.messages.length
      })
    }
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
  const resizeImage = (file: File, maxWidth: number = 800, maxHeight: number = 600, quality: number = 0.8): Promise<string> => {
    return new Promise((resolve) => {
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
      reader.onload = (e) => {
        img.src = e.target?.result as string
      }
      reader.readAsDataURL(file)
    })
  }

  // 画像選択処理
  const handleImageSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // 画像形式チェック
      if (!file.type.startsWith('image/')) {
        alert('画像ファイルを選択してください。')
        return
      }
      
      try {
        // 画像をリサイズしてプレビュー設定
        const resizedImage = await resizeImage(file, 800, 600, 0.8)
        setImagePreview(resizedImage)
        setSelectedImage(file) // 元ファイルも保持
      } catch (error) {
        console.error('画像処理エラー:', error)
        alert('画像の処理中にエラーが発生しました。')
      }
    }
  }

  // 画像削除
  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // フォローアップ質問をクリックしたときの処理
  const handleFollowUpClick = (question: string) => {
    setInputValue(question)
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

  // オーケストレーション開始/終了時もスクロール
  useEffect(() => {
    if (isOrchestrating) {
      setTimeout(scrollToBottom, 200)
    }
  }, [isOrchestrating])

  const quickQuestions = [
    '夜泣きがひどくて困っています',
    '離乳食を食べてくれません',
    '発達が気になります',
    '授乳のタイミングがわかりません'
  ]

  return (
    <AppLayout>
      <div className="flex flex-col h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
        {/* ページヘッダー（固定） */}
        <div className="flex-shrink-0 bg-white/80 backdrop-blur-sm border-b border-amber-100">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
                  <GiMagicLamp className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">Genieと話す</h1>
                  <p className="text-gray-600">あなただけの魔法のランプが子育てをサポート</p>
                  {currentSession && (
                    <p className="text-sm text-amber-600 mt-1 truncate max-w-[300px]">{currentSession.title}</p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Button 
                  onClick={startNewChat}
                  className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Genieに相談
                </Button>
                <Button 
                  onClick={() => setShowHistory(!showHistory)}
                  variant="outline"
                  className="border-amber-300 text-amber-700 hover:bg-amber-50"
                >
                  <History className="h-4 w-4 mr-2" />
                  履歴
                </Button>
                {unsavedChanges && (
                  <Button 
                    onClick={saveChat}
                    className="bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white shadow-lg"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    保存
                  </Button>
                )}
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-amber-200">
                  <GiMagicLamp className="h-4 w-4 text-amber-600" />
                  <span className="text-sm text-amber-700 font-medium">24時間対応</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Messages（スクロール可能エリア） */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto p-6 space-y-6 pb-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.sender === 'genie' && (
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                <GiMagicLamp className="h-5 w-5 text-white" />
              </div>
            )}
            
            <div className={`${
              message.type === 'streaming' ? 'max-w-[90%] w-full' : 'max-w-[85%]'
            } ${message.sender === 'user' ? 'order-first' : ''}`}>
              {message.type === 'streaming' ? (
                // ストリーミング進捗表示（Genieスタイル固定）
                <GenieStyleProgress
                  message={message.content}
                  userId="frontend_user"
                  sessionId={currentSession ? currentSession.id : 'default-session'}
                  onComplete={handleStreamingComplete}
                  onError={handleStreamingError}
                />
              ) : (
                // 通常のメッセージ表示
                <Card className={`shadow-lg border-0 ${
                  message.sender === 'user' 
                    ? 'bg-gradient-to-br from-amber-500 to-orange-500 text-white' 
                    : 'bg-white/90 backdrop-blur-sm border border-amber-100'
                }`}>
                  <CardContent className="p-4">
                    {message.sender === 'genie' ? (
                      <div className="prose prose-sm max-w-none text-gray-800 prose-headings:font-bold prose-headings:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-800 prose-li:text-gray-700 prose-ul:text-gray-700 prose-ol:text-gray-700 prose-blockquote:text-gray-600 prose-blockquote:border-amber-300">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-white whitespace-pre-line">{message.content}</p>
                    )}
                  
                  {/* フォローアップ質問ボタン */}
                  {message.sender === 'genie' && message.followUpQuestions && message.followUpQuestions.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs text-gray-600 font-medium">💡 こんなことも気になりませんか？</p>
                      <div className="space-y-2">
                        {message.followUpQuestions.map((question, index) => (
                          <button
                            key={index}
                            onClick={() => handleFollowUpClick(question)}
                            className="block w-full text-left text-sm px-4 py-3 bg-gradient-to-r from-amber-50 to-orange-50 hover:from-amber-100 hover:to-orange-100 text-amber-800 rounded-lg border border-amber-200 hover:border-amber-300 transition-all duration-200 hover:shadow-md"
                          >
                            <Heart className="h-3 w-3 inline mr-2 text-amber-600" />
                            {question}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* デバッグ情報表示（開発時のみ） */}
                  {message.sender === 'genie' && message.debugInfo?.workflow_used && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {message.debugInfo.workflow_used}エージェント使用
                      </span>
                      {message.debugInfo.processing_time && (
                        <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                          {message.debugInfo.processing_time}ms
                        </span>
                      )}
                    </div>
                  )}
                  
                  <p className={`text-xs mt-3 ${
                    message.sender === 'user' ? 'text-amber-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString('ja-JP', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                  </CardContent>
                </Card>
              )}
            </div>

            {message.sender === 'user' && (
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                <User className="h-5 w-5 text-white" />
              </div>
            )}
          </div>
        ))}

        {/* マルチエージェント協調演出 - 回答生成中に表示 */}
        {isOrchestrating && (
          <div className="px-6">
            <MultiAgentOrchestration 
              isActive={isOrchestrating}
              userQuery={currentQuery}
              agentInfo={currentAgentInfo}
              onComplete={handleOrchestrationComplete}
            />
          </div>
        )}

        {isTyping && !isOrchestrating && (
          <div className="flex gap-4 justify-start">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center flex-shrink-0 shadow-lg">
              <GiMagicLamp className="h-5 w-5 text-white" />
            </div>
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <CardContent className="p-4">
                <div className="flex gap-1">
                  <div className="w-3 h-3 bg-amber-400 rounded-full animate-bounce"></div>
                  <div className="w-3 h-3 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-3 h-3 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
            
            {/* スクロール用の参照点 */}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* 固定インプットエリア */}
        <div className="flex-shrink-0">
          {/* よくある相談 */}
          {messages.length === 1 && (
            <div className="max-w-4xl mx-auto px-6 py-3">
              <div className="bg-white/60 backdrop-blur-sm rounded-lg border border-amber-200 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Star className="h-4 w-4 text-amber-600" />
                  <h3 className="text-sm font-medium text-gray-700">よくある相談</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {quickQuestions.map((question, index) => (
                    <button
                      key={index}
                      className="text-left p-3 bg-white hover:bg-amber-50 border border-amber-100 hover:border-amber-300 rounded-md text-sm text-gray-700 hover:text-amber-800 transition-all duration-200"
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
          <div className="max-w-4xl mx-auto p-4">
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border border-amber-200 p-4 shadow-lg">
              {/* 画像プレビュー */}
              {imagePreview && (
                <div className="mb-3 relative inline-block">
                  <img 
                    src={imagePreview} 
                    alt="選択された画像" 
                    className="max-h-32 rounded-lg border border-amber-200"
                  />
                  <button
                    onClick={removeImage}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 transition-colors"
                  >
                    ×
                  </button>
                </div>
              )}
              
              <div className="flex gap-2 items-center">
                <div className="flex-1">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="何でも相談してください... ✨"
                    className="w-full h-12 max-h-[100px] resize-none px-4 py-3 border border-amber-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-400 transition-all duration-200 text-sm bg-white"
                    rows={1}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                        e.preventDefault()
                        sendMessage()
                      }
                    }}
                  />
                </div>
                
                {/* 画像アップロードボタン */}
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleImageSelect}
                  accept="image/*"
                  className="hidden"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  className="h-12 px-3 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 hover:border-blue-300 rounded-lg transition-all duration-200"
                  type="button"
                >
                  <Camera className="h-4 w-4" />
                </Button>
                
                {/* 音声録音ボタン（将来の拡張用） */}
                <Button
                  onClick={toggleRecording}
                  className={`h-12 px-3 rounded-lg transition-all duration-200 border ${
                    isRecording 
                      ? 'bg-red-500 hover:bg-red-600 text-white border-red-500'
                      : 'bg-green-50 hover:bg-green-100 text-green-700 border-green-200 hover:border-green-300'
                  }`}
                  type="button"
                >
                  {isRecording ? <IoStop className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </Button>
                
                <Button 
                  onClick={sendMessage}
                  className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 h-12 px-6 rounded-lg transition-all duration-200 border-0"
                  disabled={!inputValue.trim() && !selectedImage}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

      {/* チャット履歴パネル */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/50 z-50 flex">
          <div 
            className="flex-1" 
            onClick={() => setShowHistory(false)}
          />
          <div className="w-96 bg-white h-full overflow-y-auto shadow-2xl">
            <div className="p-6 border-b bg-gradient-to-r from-amber-500 to-orange-600 text-white">
              <div className="flex items-center gap-3">
                <History className="h-6 w-6" />
                <h2 className="text-xl font-bold">チャット履歴</h2>
              </div>
              <p className="text-amber-100 text-sm mt-1">過去の相談を振り返る</p>
            </div>
            <div className="p-6 space-y-3">
              {historyLoading ? (
                <LoadingSpinner 
                  message="履歴を読み込み中..." 
                  fullScreen={false}
                  className="py-8"
                />
              ) : sessions.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <MessageCircle className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>履歴がありません</p>
                  <p className="text-sm mt-1">新しい相談を始めてみましょう</p>
                </div>
              ) : (
                sessions.map((session) => (
                  <Card 
                    key={session.id}
                    className={`cursor-pointer hover:shadow-md transition-all duration-200 border-0 shadow-sm ${
                      currentSession?.id === session.id ? 'ring-2 ring-amber-500 bg-amber-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => loadChatFromHistory(session.id)}
                  >
                    <CardContent className="p-4">
                      <h3 className="font-semibold text-gray-800 truncate">{session.title}</h3>
                      <div className="flex justify-between items-center mt-2">
                        <span className="text-sm text-gray-600">
                          {session.messages.length}件のメッセージ
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(session.updatedAt).toLocaleDateString('ja-JP')}
                        </span>
                      </div>
                      {session.tags && session.tags.length > 0 && (
                        <div className="flex gap-1 mt-3">
                          {session.tags.slice(0, 2).map((tag, index) => (
                            <span 
                              key={index}
                              className="text-xs bg-gradient-to-r from-amber-100 to-orange-100 text-amber-800 px-2 py-1 rounded-full"
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