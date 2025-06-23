'use client'
import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sparkles, 
  Heart, 
  Star, 
  Wand2, 
  Baby,
  Mic,
  Camera,
  MessageCircle,
  Send,
  Upload
} from 'lucide-react'

interface MagicLampInterfaceProps {
  onSendMessage: (content: string, type: 'voice' | 'photo' | 'text') => void
  isProcessing?: boolean
}

export function MagicLampInterface({ onSendMessage, isProcessing = false }: MagicLampInterfaceProps) {
  const [isLampGlowing, setIsLampGlowing] = useState(false)
  const [activeWish, setActiveWish] = useState<'voice' | 'photo' | 'text' | null>(null)
  const [inputText, setInputText] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 魔法のランプのアニメーション制御
  const handleLampTouch = () => {
    setIsLampGlowing(true)
    setTimeout(() => setIsLampGlowing(false), 2000)
  }

  // ワンアクション魔法の実行
  const castMagic = (wishType: 'voice' | 'photo' | 'text') => {
    setActiveWish(wishType)
    handleLampTouch()

    switch (wishType) {
      case 'voice':
        startVoiceWish()
        break
      case 'photo':
        startPhotoWish()
        break
      case 'text':
        // テキスト入力は即座にアクティブ
        break
    }
  }

  const startVoiceWish = () => {
    setIsRecording(true)
    // 実際の音声録音処理をここに実装
    // 5秒後に自動停止（デモ用）
    setTimeout(() => {
      setIsRecording(false)
      onSendMessage('音声で子育ての相談をしました', 'voice')
      setActiveWish(null)
    }, 5000)
  }

  const startPhotoWish = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      onSendMessage('写真を送信して相談しました', 'photo')
      setActiveWish(null)
    }
  }

  const sendTextWish = () => {
    if (inputText.trim()) {
      onSendMessage(inputText, 'text')
      setInputText('')
      setActiveWish(null)
    }
  }

  // 簡単な魔法のショートカット
  const quickWishes = [
    { text: '夜泣きで困っています', icon: '🌙' },
    { text: '離乳食を食べてくれません', icon: '🍼' },
    { text: '発達が心配です', icon: '👶' },
    { text: 'イヤイヤ期がつらいです', icon: '😤' },
  ]

  return (
    <div className="relative">
      {/* 魔法のランプ - 中央のメインインタラクション */}
      <div className="flex flex-col items-center p-8 bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 rounded-2xl">
        
        {/* ランプの魔法エフェクト */}
        <div className="relative mb-6">
          <motion.div
            className={`relative z-10 w-24 h-24 rounded-full bg-gradient-to-br from-amber-400 via-yellow-400 to-orange-400 flex items-center justify-center cursor-pointer ${
              isLampGlowing ? 'shadow-2xl shadow-amber-300' : 'shadow-lg'
            }`}
            animate={{
              scale: isLampGlowing ? [1, 1.1, 1] : 1,
              rotate: isLampGlowing ? [0, 5, -5, 0] : 0,
            }}
            transition={{ duration: 0.6 }}
            onClick={handleLampTouch}
          >
            <Wand2 className="h-10 w-10 text-white" />
          </motion.div>

          {/* 魔法のエフェクトパーティクル */}
          <AnimatePresence>
            {isLampGlowing && (
              <>
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-2 h-2 bg-yellow-300 rounded-full"
                    initial={{ 
                      x: 48, 
                      y: 48, 
                      scale: 0,
                      opacity: 1 
                    }}
                    animate={{
                      x: 48 + Math.cos(i * 45 * Math.PI / 180) * 60,
                      y: 48 + Math.sin(i * 45 * Math.PI / 180) * 60,
                      scale: [0, 1, 0],
                      opacity: [1, 1, 0]
                    }}
                    exit={{ opacity: 0 }}
                    transition={{ 
                      duration: 1.5,
                      delay: i * 0.1 
                    }}
                  />
                ))}
              </>
            )}
          </AnimatePresence>

          {/* 魔法の煙エフェクト */}
          <AnimatePresence>
            {isLampGlowing && (
              <motion.div
                className="absolute -top-4 left-1/2 transform -translate-x-1/2"
                initial={{ opacity: 0, y: 0 }}
                animate={{ opacity: [0, 1, 0], y: -20 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 2 }}
              >
                <div className="text-2xl">✨</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* ジーニーのメッセージ */}
        <motion.div
          className="text-center mb-6"
          animate={{ scale: isLampGlowing ? [1, 1.02, 1] : 1 }}
        >
          <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
            3つの簡単な方法で記録・相談 ✨
          </h2>
          <p className="text-gray-600">
            {isProcessing 
              ? '🧞‍♂️ ジーニーが情報を整理中...' 
              : '話すだけ・撮るだけ・聞くだけ。忙しいときでも簡単に記録できます'}
          </p>
        </motion.div>

        {/* 3つの簡単な方法 - ワンアクション設計 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl">
          
          {/* 話すだけで記録 */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Card 
              className={`p-6 cursor-pointer transition-all duration-300 ${
                activeWish === 'voice' || isRecording
                  ? 'ring-4 ring-emerald-300 bg-emerald-50 border-emerald-200'
                  : 'hover:shadow-lg hover:border-emerald-200 bg-white/80 backdrop-blur-sm'
              }`}
              onClick={() => castMagic('voice')}
            >
              <div className="text-center">
                <div className={`w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${
                  isRecording 
                    ? 'bg-red-500 animate-pulse' 
                    : 'bg-gradient-to-br from-emerald-400 to-teal-400'
                }`}>
                  <Mic className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-800 mb-2">
                  {isRecording ? '🎤 録音中...' : '🗣️ 話すだけで記録'}
                </h3>
                <p className="text-sm text-gray-600">
                  {isRecording 
                    ? 'お話しください...' 
                    : '「さっきミルク飲んだ」→自動で時間・量・記録完了'}
                </p>
              </div>
            </Card>
          </motion.div>

          {/* 写真で成長記録 */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Card 
              className={`p-6 cursor-pointer transition-all duration-300 ${
                activeWish === 'photo'
                  ? 'ring-4 ring-blue-300 bg-blue-50 border-blue-200'
                  : 'hover:shadow-lg hover:border-blue-200 bg-white/80 backdrop-blur-sm'
              }`}
              onClick={() => castMagic('photo')}
            >
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center">
                  <Camera className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-800 mb-2">📸 写真で成長記録</h3>
                <p className="text-sm text-gray-600">
                  離乳食や表情を撮影→食事量・発達を自動分析
                </p>
              </div>
            </Card>
          </motion.div>

          {/* ジーニーに相談 */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Card 
              className={`p-6 cursor-pointer transition-all duration-300 ${
                activeWish === 'text'
                  ? 'ring-4 ring-purple-300 bg-purple-50 border-purple-200'
                  : 'hover:shadow-lg hover:border-purple-200 bg-white/80 backdrop-blur-sm'
              }`}
              onClick={() => castMagic('text')}
            >
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-400 to-indigo-400 flex items-center justify-center">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-800 mb-2">💬 ジーニーに相談</h3>
                <p className="text-sm text-gray-600">
                  夜泣き・イヤイヤ期の悩み→専門アドバイス提案
                </p>
              </div>
            </Card>
          </motion.div>
        </div>

        {/* テキスト入力 - 言葉の魔法がアクティブな時のみ表示 */}
        <AnimatePresence>
          {activeWish === 'text' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="w-full max-w-2xl mt-6"
            >
              <div className="flex gap-3">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="✨ どんなことでもお聞かせください..."
                  className="flex-1 px-4 py-3 border-2 border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      sendTextWish()
                    }
                  }}
                  autoFocus
                />
                <Button
                  onClick={sendTextWish}
                  disabled={!inputText.trim()}
                  className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 px-6"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 隠しファイル入力 */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />

        {/* よくある相談のショートカット */}
        <div className="w-full max-w-2xl mt-8">
          <h4 className="text-center text-sm font-medium text-gray-600 mb-4">
            ✨ よくある相談
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {quickWishes.map((wish, index) => (
              <Button
                key={index}
                variant="outline"
                onClick={() => onSendMessage(wish.text, 'text')}
                className="h-auto p-3 text-left justify-start bg-white/60 backdrop-blur-sm border-amber-200 hover:bg-amber-50 hover:border-amber-300"
              >
                <span className="mr-2 text-lg">{wish.icon}</span>
                <span className="text-sm">{wish.text}</span>
              </Button>
            ))}
          </div>
        </div>

        {/* ジーニーからの説明 */}
        <div className="mt-8 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200 max-w-2xl">
          <div className="text-center">
            <div className="text-2xl mb-2">🧞‍♂️</div>
            <p className="text-sm text-amber-800">
              <strong>私は忙しいパパママの育児サポーター、ジーニーです。</strong><br />
              話すだけ・撮るだけ・聞くだけ。たった一つの操作で<br />
              記録・分析・アドバイスまで全て自動で行います。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}