'use client'
import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { AppLayout } from '@/components/layout/app-layout'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChatHistory } from '@/hooks/use-chat-history'
import { MultiAgentOrchestration } from '@/components/features/chat/multi-agent-orchestration'
import { 
  IoSend,
  IoMic,
  IoCamera,
  IoStop,
  IoImage,
  IoVolumeHigh,
  IoBulbOutline
} from 'react-icons/io5'
import {
  AiOutlineMessage,
  AiOutlineHistory,
  AiOutlinePlus,
  AiOutlineSave,
  AiOutlineUser
} from 'react-icons/ai'
import {
  FaUserTie
} from 'react-icons/fa'
import { GiMagicLamp } from 'react-icons/gi'

interface Message {
  id: string
  content: string
  sender: 'user' | 'genie'
  timestamp: Date
  type?: 'text' | 'audio' | 'image'
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
    
    // マルチエージェント演出を開始
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
      <div className="flex flex-col h-screen">
        {/* ページヘッダー */}
        <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
          <div className="px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center">
                  <AiOutlineMessage className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-kiwi font-semibold text-gray-800">Genieとチャット</h1>
                  <p className="text-sm text-gray-600">子育ての記録・分析・相談をサポート</p>
                  {currentSession && (
                    <p className="text-xs text-gray-500 truncate max-w-[200px] mt-1">{currentSession.title}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {unsavedChanges && (
                  <Button 
                    onClick={saveChat}
                    size="sm" 
                    className="bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white border-0 rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                  >
                    <AiOutlineSave className="h-4 w-4 mr-1.5" />
                    保存
                  </Button>
                )}
                <Button 
                  onClick={() => setShowHistory(!showHistory)}
                  size="sm" 
                  className="bg-white/80 hover:bg-white border border-gray-200 hover:border-gray-300 text-gray-700 hover:text-gray-900 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 backdrop-blur-sm"
                >
                  <AiOutlineHistory className="h-4 w-4 mr-1.5" />
                  履歴
                </Button>
                <Button 
                  onClick={startNewChat}
                  size="sm" 
                  className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white border-0 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 font-kiwi font-semibold"
                >
                  <AiOutlinePlus className="h-4 w-4 mr-1.5" />
                  新規チャット
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.sender === 'genie' && (
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                <GiMagicLamp className="h-4 w-4 text-white" />
              </div>
            )}
            
            <div className={`max-w-[80%] ${message.sender === 'user' ? 'order-first' : ''}`}>
              <Card className={`${
                message.sender === 'user' 
                  ? 'bg-amber-500 text-white' 
                  : 'bg-white/80 backdrop-blur-sm border border-amber-200'
              }`}>
                <CardContent className="p-3">
                  {message.sender === 'genie' ? (
                    <div className="prose prose-sm max-w-none font-main text-sm prose-headings:font-bold prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-li:text-foreground prose-ul:text-foreground prose-ol:text-foreground prose-blockquote:text-gray-700 prose-blockquote:border-amber-300">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="font-main text-sm whitespace-pre-line">{message.content}</p>
                  )}
                  
                  {/* フォローアップ質問ボタン */}
                  {message.sender === 'genie' && message.followUpQuestions && message.followUpQuestions.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs text-gray-600 font-medium">💡 こんなことも気になりませんか？</p>
                      <div className="space-y-1">
                        {message.followUpQuestions.map((question, index) => (
                          <button
                            key={index}
                            onClick={() => handleFollowUpClick(question)}
                            className="block w-full text-left text-xs px-3 py-2 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded-md border border-amber-200 transition-colors duration-200"
                          >
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
                  
                  <p className={`text-xs mt-2 ${
                    message.sender === 'user' ? 'text-amber-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString('ja-JP', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </CardContent>
              </Card>
            </div>

            {message.sender === 'user' && (
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
                <FaUserTie className="h-4 w-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {/* マルチエージェント協調演出 - 回答生成中に表示 */}
        {isOrchestrating && (
          <div className="px-4">
            <MultiAgentOrchestration 
              isActive={isOrchestrating}
              userQuery={currentQuery}
              agentInfo={currentAgentInfo}
              onComplete={handleOrchestrationComplete}
            />
          </div>
        )}

        {isTyping && !isOrchestrating && (
          <div className="flex gap-3 justify-start">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
              <GiMagicLamp className="h-4 w-4 text-white" />
            </div>
            <Card className="bg-white/80 backdrop-blur-sm border border-amber-200">
              <CardContent className="p-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        {/* スクロール用の参照点 */}
        <div ref={messagesEndRef} />
      </div>

      {/* チャット履歴パネル */}
      {showHistory && (
        <div className="absolute inset-0 bg-black/50 z-50 flex">
          <div 
            className="flex-1" 
            onClick={() => setShowHistory(false)}
          />
          <div className="w-80 bg-white h-full overflow-y-auto">
            <div className="p-4 border-b">
              <h2 className="font-semibold text-gray-800">チャット履歴</h2>
            </div>
            <div className="p-4 space-y-2">
              {historyLoading ? (
                <div className="text-center text-gray-500">読み込み中...</div>
              ) : sessions.length === 0 ? (
                <div className="text-center text-gray-500">履歴がありません</div>
              ) : (
                sessions.map((session) => (
                  <Card 
                    key={session.id}
                    className={`cursor-pointer hover:bg-gray-50 transition-colors ${
                      currentSession?.id === session.id ? 'ring-2 ring-amber-500' : ''
                    }`}
                    onClick={() => loadChatFromHistory(session.id)}
                  >
                    <CardContent className="p-3">
                      <h3 className="font-medium text-sm truncate">{session.title}</h3>
                      <div className="flex justify-between items-center mt-1">
                        <span className="text-xs text-gray-500">
                          {session.messages.length}件のメッセージ
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(session.updatedAt).toLocaleDateString('ja-JP')}
                        </span>
                      </div>
                      {session.tags && session.tags.length > 0 && (
                        <div className="flex gap-1 mt-2">
                          {session.tags.slice(0, 2).map((tag, index) => (
                            <span 
                              key={index}
                              className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded"
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

      {/* Quick Questions - Compact & Stylish */}
      {messages.length === 1 && (
        <div className="px-4 py-3 bg-gradient-to-r from-slate-50 to-blue-50/50">
          <div className="flex items-center gap-2 mb-2">
            <IoBulbOutline className="h-3 w-3 text-gray-500" />
            <p className="text-xs font-medium text-gray-600">よくある相談</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                className="inline-flex items-center px-3 py-1.5 bg-white/90 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-full text-xs text-gray-700 hover:text-blue-700 transition-all duration-200 hover:shadow-sm"
                onClick={() => setInputValue(question)}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area - With Image Upload */}
      <div className="p-4 border-t border-gray-200 bg-white">
        {/* 画像プレビュー */}
        {imagePreview && (
          <div className="mb-3 relative inline-block">
            <img 
              src={imagePreview} 
              alt="選択された画像" 
              className="max-h-32 rounded-lg border border-gray-200"
            />
            <button
              onClick={removeImage}
              className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 transition-colors"
            >
              ×
            </button>
          </div>
        )}
        
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="何でも相談してください..."
              className="w-full h-12 max-h-[120px] resize-none px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-200 text-sm"
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
            className="h-12 px-3 bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-700 rounded-xl transition-all duration-200"
            type="button"
          >
            <IoCamera className="h-5 w-5" />
          </Button>
          
          {/* 音声録音ボタン（将来の拡張用） */}
          <Button
            onClick={toggleRecording}
            className={`h-12 px-3 rounded-xl transition-all duration-200 ${
              isRecording 
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-700'
            }`}
            type="button"
          >
            {isRecording ? <IoStop className="h-5 w-5" /> : <IoMic className="h-5 w-5" />}
          </Button>
          
          <Button 
            onClick={sendMessage}
            className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 h-12 px-6 rounded-xl shadow-sm hover:shadow-md transition-all duration-200"
            disabled={!inputValue.trim() && !selectedImage}
          >
            <IoSend className="h-5 w-5" />
          </Button>
        </div>
      </div>
      </div>
      
    </AppLayout>
  )
}