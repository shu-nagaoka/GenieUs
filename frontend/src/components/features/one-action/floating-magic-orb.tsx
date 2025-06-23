'use client'
import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, PanInfo } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { 
  Mic, 
  Camera, 
  MessageCircle, 
  Sparkles, 
  X, 
  Send,
  MicOff,
  Upload,
  Wand2
} from 'lucide-react'

interface FloatingMagicOrbProps {
  onAction: (type: 'voice' | 'photo' | 'text', content: string) => void
  className?: string
}

export function FloatingMagicOrb({ onAction, className = '' }: FloatingMagicOrbProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [activeMode, setActiveMode] = useState<'voice' | 'photo' | 'text' | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [textInput, setTextInput] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isGlowing, setIsGlowing] = useState(false)

  // 魔法のランダムな光る効果
  useEffect(() => {
    const interval = setInterval(() => {
      setIsGlowing(true)
      setTimeout(() => setIsGlowing(false), 1000)
    }, 5000 + Math.random() * 10000) // 5-15秒間隔でランダムに光る

    return () => clearInterval(interval)
  }, [])

  // ドラッグ可能な位置制御
  const handleDrag = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    setPosition({
      x: position.x + info.delta.x,
      y: position.y + info.delta.y
    })
  }

  // 魔法を実行
  const castMagic = (type: 'voice' | 'photo' | 'text') => {
    setActiveMode(type)
    setIsExpanded(true)
    
    if (type === 'voice') {
      startVoiceRecording()
    } else if (type === 'photo') {
      fileInputRef.current?.click()
    }
  }

  // 音声録音開始
  const startVoiceRecording = () => {
    setIsRecording(true)
    // 実際の音声録音処理をここに実装
    // デモ用に5秒後に自動停止
    setTimeout(() => {
      stopVoiceRecording()
    }, 5000)
  }

  // 音声録音停止
  const stopVoiceRecording = () => {
    setIsRecording(false)
    onAction('voice', '音声で記録を作成しました')
    closeOrb()
  }

  // 写真選択処理
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      onAction('photo', '写真を送信しました')
      closeOrb()
    }
  }

  // テキスト送信
  const sendText = () => {
    if (textInput.trim()) {
      onAction('text', textInput)
      setTextInput('')
      closeOrb()
    }
  }

  // オーブを閉じる
  const closeOrb = () => {
    setIsExpanded(false)
    setActiveMode(null)
    setIsRecording(false)
    setTextInput('')
    setSelectedFile(null)
  }

  return (
    <>
      {/* メインの魔法のオーブ */}
      <motion.div
        className={`fixed z-50 ${className}`}
        style={{
          right: '20px',
          bottom: '20px',
          x: position.x,
          y: position.y,
        }}
        drag
        onDrag={handleDrag}
        dragMomentum={false}
        dragElastic={0.1}
      >
        <motion.div
          className={`relative w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 via-indigo-500 to-blue-500 flex items-center justify-center cursor-pointer shadow-lg ${
            isGlowing ? 'shadow-2xl shadow-purple-400' : ''
          }`}
          animate={{
            scale: isGlowing ? [1, 1.1, 1] : isExpanded ? 0.9 : 1,
            rotate: isGlowing ? [0, 10, -10, 0] : 0,
          }}
          transition={{ duration: 0.8 }}
          onClick={() => setIsExpanded(!isExpanded)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {/* 魔法のアイコン */}
          <Wand2 className="h-8 w-8 text-white" />
          
          {/* 魔法のパーティクル効果 */}
          <AnimatePresence>
            {isGlowing && (
              <>
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-2 h-2 bg-yellow-300 rounded-full"
                    initial={{ 
                      x: 32, 
                      y: 32, 
                      scale: 0,
                      opacity: 1 
                    }}
                    animate={{
                      x: 32 + Math.cos(i * 60 * Math.PI / 180) * 40,
                      y: 32 + Math.sin(i * 60 * Math.PI / 180) * 40,
                      scale: [0, 1, 0],
                      opacity: [1, 1, 0]
                    }}
                    exit={{ opacity: 0 }}
                    transition={{ 
                      duration: 1.2,
                      delay: i * 0.1 
                    }}
                  />
                ))}
              </>
            )}
          </AnimatePresence>

          {/* 新着通知ドット */}
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
            <span className="text-xs text-white font-bold">3</span>
          </div>
        </motion.div>

        {/* 魔法の選択肢 - 展開時 */}
        <AnimatePresence>
          {isExpanded && !activeMode && (
            <motion.div
              className="absolute bottom-20 right-0 flex flex-col gap-3"
              initial={{ opacity: 0, y: 20, scale: 0.8 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.8 }}
              transition={{ duration: 0.3 }}
            >
              {/* 声の魔法 */}
              <motion.button
                className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-400 to-teal-400 flex items-center justify-center shadow-lg"
                onClick={() => castMagic('voice')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                <Mic className="h-6 w-6 text-white" />
              </motion.button>

              {/* 写真の魔法 */}
              <motion.button
                className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center shadow-lg"
                onClick={() => castMagic('photo')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Camera className="h-6 w-6 text-white" />
              </motion.button>

              {/* 相談の魔法 */}
              <motion.button
                className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center shadow-lg"
                onClick={() => castMagic('text')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <MessageCircle className="h-6 w-6 text-white" />
              </motion.button>

              {/* 閉じるボタン */}
              <motion.button
                className="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center shadow-lg mt-2"
                onClick={closeOrb}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                <X className="h-4 w-4 text-white" />
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* 全画面魔法インターフェース */}
      <AnimatePresence>
        {isExpanded && activeMode && (
          <motion.div
            className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeOrb}
          >
            <motion.div
              className="bg-white rounded-2xl p-8 max-w-md w-full"
              initial={{ opacity: 0, scale: 0.8, y: 50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 50 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* 音声録音モード */}
              {activeMode === 'voice' && (
                <div className="text-center">
                  <div className={`w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center ${
                    isRecording 
                      ? 'bg-red-500 animate-pulse' 
                      : 'bg-gradient-to-br from-emerald-400 to-teal-400'
                  }`}>
                    {isRecording ? (
                      <MicOff className="h-12 w-12 text-white" />
                    ) : (
                      <Mic className="h-12 w-12 text-white" />
                    )}
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-2">🗣️ 声の魔法</h3>
                  <p className="text-gray-600 mb-6">
                    {isRecording 
                      ? 'お話しください...' 
                      : '何でもお話しください。自動で記録します。'}
                  </p>

                  {isRecording && (
                    <div className="mb-6">
                      <div className="flex justify-center gap-1">
                        <div className="w-2 h-8 bg-emerald-400 rounded animate-pulse"></div>
                        <div className="w-2 h-6 bg-emerald-400 rounded animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-10 bg-emerald-400 rounded animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-4 bg-emerald-400 rounded animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                        <div className="w-2 h-8 bg-emerald-400 rounded animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-3">
                    {isRecording ? (
                      <Button 
                        onClick={stopVoiceRecording}
                        className="flex-1 bg-red-500 hover:bg-red-600"
                      >
                        <MicOff className="mr-2 h-4 w-4" />
                        完了
                      </Button>
                    ) : (
                      <Button 
                        onClick={startVoiceRecording}
                        className="flex-1 bg-emerald-500 hover:bg-emerald-600"
                      >
                        <Mic className="mr-2 h-4 w-4" />
                        録音開始
                      </Button>
                    )}
                    <Button variant="outline" onClick={closeOrb}>
                      キャンセル
                    </Button>
                  </div>
                </div>
              )}

              {/* テキスト入力モード */}
              {activeMode === 'text' && (
                <div>
                  <div className="text-center mb-6">
                    <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
                      <MessageCircle className="h-12 w-12 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-2">💬 相談の魔法</h3>
                    <p className="text-gray-600">
                      どんな悩みでもお聞かせください
                    </p>
                  </div>

                  <div className="space-y-4">
                    <textarea
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder="夜泣きで困っています..."
                      className="w-full h-32 p-4 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                      autoFocus
                    />
                    
                    <div className="flex gap-3">
                      <Button 
                        onClick={sendText}
                        disabled={!textInput.trim()}
                        className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                      >
                        <Send className="mr-2 h-4 w-4" />
                        魔法をかける
                      </Button>
                      <Button variant="outline" onClick={closeOrb}>
                        キャンセル
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
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
    </>
  )
}