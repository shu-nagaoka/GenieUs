'use client'
import { useState } from 'react'
import { MagicLampInterface } from '@/components/features/chat/magic-lamp-interface'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowLeft, Sparkles } from 'lucide-react'

export default function MagicChatPage() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [chatHistory, setChatHistory] = useState<Array<{
    type: 'user' | 'genie'
    content: string
    timestamp: Date
    magicType?: 'voice' | 'photo' | 'text'
  }>>([
    {
      type: 'genie',
      content: 'こんにちは！私はあなたの魔法のジーニーです ✨ ランプを擦って、どんな願いでも叶えましょう！',
      timestamp: new Date()
    }
  ])

  const handleSendMessage = async (content: string, type: 'voice' | 'photo' | 'text') => {
    // ユーザーメッセージを追加
    setChatHistory(prev => [...prev, {
      type: 'user',
      content,
      timestamp: new Date(),
      magicType: type
    }])

    setIsProcessing(true)

    // 魔法の処理をシミュレート
    setTimeout(() => {
      const magicResponses = {
        voice: '🎤 音声の魔法を受け取りました！自動で記録を作成しています... \n\n**記録完了！** \n- 時間: ' + new Date().toLocaleTimeString() + '\n- 内容: ' + content + '\n\n何か他にお手伝いできることはありますか？',
        photo: '📸 写真の魔法を受け取りました！画像を分析中... \n\n**分析完了！** \n- 表情: 満足そう 😊\n- 食事量: 推定80%\n- 次回のアドバイス: 同じメニューがおすすめです\n\n素晴らしい記録ですね！',
        text: '💬 ご相談ありがとうございます！マルチエージェントが最適な解決策を考えています... \n\n**専門アドバイス:** \n' + content + 'についてですね。以下のアプローチをおすすめします：\n\n1. まずは深呼吸して、あなた自身をねぎらってください\n2. 年齢に応じた対処法をご提案します\n3. 必要に応じて専門家への相談も検討しましょう\n\n何でもお気軽にご相談くださいね！'
      }

      setChatHistory(prev => [...prev, {
        type: 'genie',
        content: magicResponses[type],
        timestamp: new Date()
      }])
      
      setIsProcessing(false)
    }, 2000)
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50">
        
        {/* ヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-purple-200 p-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  戻る
                </Button>
              </Link>
              <div className="text-3xl">🧞‍♂️</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">ジーニーに相談</h1>
                <p className="text-sm text-gray-600">話す・撮る・聞く で簡単記録</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-amber-600">
              <Sparkles className="h-4 w-4 animate-pulse" />
              <span className="text-sm font-medium">簡単モード</span>
            </div>
          </div>
        </div>

        <div className="max-w-4xl mx-auto p-6">
          
          {/* チャット履歴 */}
          {chatHistory.length > 1 && (
            <div className="mb-8">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span className="text-2xl">💬</span>
                魔法の会話履歴
              </h2>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {chatHistory.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.type === 'genie' && (
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center flex-shrink-0">
                        <span className="text-white text-lg">🧞‍♂️</span>
                      </div>
                    )}
                    
                    <Card className={`max-w-[70%] ${
                      message.type === 'user' 
                        ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white' 
                        : 'bg-white/90 backdrop-blur-sm border-amber-200'
                    }`}>
                      <CardContent className="p-4">
                        {message.magicType && (
                          <div className="mb-2">
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              message.magicType === 'voice' ? 'bg-emerald-100 text-emerald-800' :
                              message.magicType === 'photo' ? 'bg-blue-100 text-blue-800' :
                              'bg-purple-100 text-purple-800'
                            }`}>
                              {message.magicType === 'voice' ? '🗣️ 音声記録' :
                               message.magicType === 'photo' ? '📸 写真記録' :
                               '💬 相談'}
                            </span>
                          </div>
                        )}
                        <div className="whitespace-pre-line text-sm">
                          {message.content}
                        </div>
                        <div className={`text-xs mt-2 ${
                          message.type === 'user' ? 'text-purple-100' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </CardContent>
                    </Card>

                    {message.type === 'user' && (
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center flex-shrink-0">
                        <span className="text-white text-lg">👤</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 魔法のランプインターフェース */}
          <MagicLampInterface 
            onSendMessage={handleSendMessage}
            isProcessing={isProcessing}
          />

          {/* 魔法の説明 */}
          <div className="mt-8 p-6 bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl border border-amber-200">
            <h3 className="text-lg font-bold text-amber-800 mb-4 text-center">
              ✨ 3つの簡単な記録方法
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl mb-2">🗣️</div>
                <h4 className="font-medium text-emerald-800">話すだけで記録</h4>
                <p className="text-xs text-emerald-700">
                  「さっきミルク飲んだ」→自動で時間・量・記録完了
                </p>
              </div>
              <div>
                <div className="text-2xl mb-2">📸</div>
                <h4 className="font-medium text-blue-800">写真で成長記録</h4>
                <p className="text-xs text-blue-700">
                  離乳食や表情を撮影→食事量・発達を自動分析
                </p>
              </div>
              <div>
                <div className="text-2xl mb-2">💬</div>
                <h4 className="font-medium text-purple-800">ジーニーに相談</h4>
                <p className="text-xs text-purple-700">
                  夜泣き・イヤイヤ期の悩み→専門アドバイス提案
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}