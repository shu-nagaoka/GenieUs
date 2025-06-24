'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { StreamingProgressDisplay } from '@/components/features/chat/streaming-progress-display'
import { 
  IoSend,
  IoSparkles,
  IoRefresh
} from 'react-icons/io5'
import { GiMagicLamp } from 'react-icons/gi'

interface Message {
  id: string
  content: string
  sender: 'user' | 'genie'
  timestamp: Date
  type?: 'text' | 'streaming'
}

export default function StreamingChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'こんにちは！私はGenieです ✨ リアルタイムでAgent処理状況をお見せしながら、子育て相談にお答えします！\n\n**新機能:**\n• Agentの思考過程をリアルタイム表示\n• ツール使用状況の可視化\n• 処理ステップの詳細確認\n\n何でもお気軽にお話しください！',
      sender: 'genie',
      timestamp: new Date(),
      type: 'text'
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStreamingId, setCurrentStreamingId] = useState<string | null>(null)

  // メッセージ送信
  const sendMessage = async () => {
    if (!inputValue.trim() || isProcessing) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    const query = inputValue
    setInputValue('')
    setIsProcessing(true)

    // ストリーミング用のプレースホルダーメッセージを追加
    const streamingMessageId = (Date.now() + 1).toString()
    setCurrentStreamingId(streamingMessageId)
    
    const streamingMessage: Message = {
      id: streamingMessageId,
      content: query, // ストリーミングコンポーネントに送信するクエリ
      sender: 'genie',
      timestamp: new Date(),
      type: 'streaming'
    }

    setMessages(prev => [...prev, streamingMessage])
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
    setIsProcessing(false)
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
    setIsProcessing(false)
  }

  // チャットリセット
  const resetChat = () => {
    setMessages([
      {
        id: '1',
        content: 'こんにちは！私はGenieです ✨ リアルタイムでAgent処理状況をお見せしながら、子育て相談にお答えします！\n\n**新機能:**\n• Agentの思考過程をリアルタイム表示\n• ツール使用状況の可視化\n• 処理ステップの詳細確認\n\n何でもお気軽にお話しください！',
        sender: 'genie',
        timestamp: new Date(),
        type: 'text'
      }
    ])
    setCurrentStreamingId(null)
    setIsProcessing(false)
  }

  const quickQuestions = [
    '画像を分析して',
    '夜泣きがひどくて困っています',
    '離乳食を食べてくれません',
    '発達が気になります'
  ]

  return (
    <AppLayout>
      <div className="flex flex-col h-screen">
        {/* ページヘッダー */}
        <div className="bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50">
          <div className="px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                  <IoSparkles className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-kiwi font-semibold text-gray-800">リアルタイム進捗チャット</h1>
                  <p className="text-sm text-gray-600">Agentの働きを可視化しながら相談</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  onClick={resetChat}
                  size="sm" 
                  className="bg-white/80 hover:bg-white border border-gray-200 hover:border-gray-300 text-gray-700 hover:text-gray-900 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 backdrop-blur-sm"
                >
                  <IoRefresh className="h-4 w-4 mr-1.5" />
                  リセット
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-3 space-y-4">
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
              
              <div className={`max-w-[85%] ${message.sender === 'user' ? 'order-first' : ''}`}>
                {message.type === 'streaming' ? (
                  // ストリーミング進捗表示
                  <StreamingProgressDisplay
                    message={message.content}
                    userId="frontend_user"
                    sessionId="streaming-session"
                    onComplete={handleStreamingComplete}
                    onError={handleStreamingError}
                  />
                ) : (
                  // 通常のメッセージ表示
                  <Card className={`${
                    message.sender === 'user' 
                      ? 'bg-indigo-500 text-white' 
                      : 'bg-white/80 backdrop-blur-sm border border-blue-200'
                  }`}>
                    <CardContent className="p-3">
                      {message.sender === 'genie' ? (
                        <div className="prose prose-sm max-w-none font-main text-sm prose-headings:font-bold prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-li:text-foreground prose-ul:text-foreground prose-ol:text-foreground prose-blockquote:text-gray-700 prose-blockquote:border-blue-300">
                          <div className="whitespace-pre-line">{message.content}</div>
                        </div>
                      ) : (
                        <p className="font-main text-sm whitespace-pre-line">{message.content}</p>
                      )}
                      
                      <p className={`text-xs mt-2 ${
                        message.sender === 'user' ? 'text-indigo-100' : 'text-gray-500'
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
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
                  <div className="h-4 w-4 bg-white rounded-full flex items-center justify-center">
                    <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Quick Questions */}
        {messages.length === 1 && (
          <div className="px-4 py-3 bg-gradient-to-r from-slate-50 to-blue-50/50">
            <div className="flex items-center gap-2 mb-2">
              <IoSparkles className="h-3 w-3 text-gray-500" />
              <p className="text-xs font-medium text-gray-600">デモ用の質問例</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  className="inline-flex items-center px-3 py-1.5 bg-white/90 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-full text-xs text-gray-700 hover:text-blue-700 transition-all duration-200 hover:shadow-sm"
                  onClick={() => setInputValue(question)}
                  disabled={isProcessing}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="何でも相談してください..."
                className="w-full h-12 max-h-[120px] resize-none px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 text-sm"
                rows={1}
                disabled={isProcessing}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
              />
            </div>
            
            <Button 
              onClick={sendMessage}
              className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 h-12 px-6 rounded-xl shadow-sm hover:shadow-md transition-all duration-200"
              disabled={!inputValue.trim() || isProcessing}
            >
              {isProcessing ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <IoSend className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}