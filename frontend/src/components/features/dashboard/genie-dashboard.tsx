'use client'
import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  Heart,
  Star,
  Wand2,
  Baby,
  Clock,
  TrendingUp,
  Award,
  Camera,
  Mic,
  MessageCircle,
  CalendarDays,
  Activity,
  Sun,
  Moon,
  Utensils,
} from 'lucide-react'
import Link from 'next/link'

interface GenieWish {
  id: string
  type: 'prediction' | 'record' | 'insight' | 'milestone'
  title: string
  description: string
  icon: string
  action: string
  urgent?: boolean
  completed?: boolean
}

export function GenieDashboard() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isLampGlowing, setIsLampGlowing] = useState(false)
  const [activeWishes, setActiveWishes] = useState<GenieWish[]>([])

  // 時間に基づく動的なウィッシュリスト
  useEffect(() => {
    const hour = currentTime.getHours()
    let newWishes: GenieWish[] = []

    // 朝 (6-11時)
    if (hour >= 6 && hour < 12) {
      newWishes = [
        {
          id: '1',
          type: 'prediction',
          title: '今日のコンディション予報',
          description: 'ゆうちゃんは今日はご機嫌さん♪ お昼寝は14:30頃がベストタイミングです',
          icon: '🌞',
          action: '詳細を見る',
        },
        {
          id: '2',
          type: 'record',
          title: '朝の記録をさっと',
          description: '「朝6時に起きました」と話すだけで自動記録',
          icon: '🗣️',
          action: '声で記録',
        },
      ]
    }
    // 昼 (12-17時)
    else if (hour >= 12 && hour < 18) {
      newWishes = [
        {
          id: '3',
          type: 'record',
          title: '離乳食の様子を記録',
          description: '写真を撮るだけで食べた量と表情を自動分析',
          icon: '📸',
          action: '写真で記録',
        },
        {
          id: '4',
          type: 'insight',
          title: 'お昼寝のベストタイミング',
          description: '眠そうなサインが出ています。今がチャンス！',
          icon: '😴',
          action: '記録する',
          urgent: true,
        },
      ]
    }
    // 夜 (18-23時)
    else if (hour >= 18 && hour < 24) {
      newWishes = [
        {
          id: '5',
          type: 'insight',
          title: '今日のがんばりレポート',
          description: '今日もお疲れさまでした！あなたの愛情が数字で見える',
          icon: '❤️',
          action: '見る',
        },
        {
          id: '6',
          type: 'prediction',
          title: '明日の準備アドバイス',
          description: '明日は少し機嫌が悪そう。おもちゃを準備しておきましょう',
          icon: '🔮',
          action: '詳細を見る',
        },
      ]
    }
    // 深夜・早朝 (0-5時)
    else {
      newWishes = [
        {
          id: '7',
          type: 'record',
          title: '夜泣きの記録',
          description: '辛い夜泣きも、話すだけで記録完了',
          icon: '🌙',
          action: '声で記録',
        },
        {
          id: '8',
          type: 'insight',
          title: '夜泣き対策アドバイス',
          description: 'パターンから最適な対処法をご提案',
          icon: '💡',
          action: '相談する',
          urgent: true,
        },
      ]
    }

    setActiveWishes(newWishes)
  }, [currentTime])

  // 1分ごとに時間を更新
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 60000)
    return () => clearInterval(timer)
  }, [])

  // ランプを擦るアニメーション
  const handleLampRub = () => {
    setIsLampGlowing(true)
    setTimeout(() => setIsLampGlowing(false), 3000)
  }

  const getGreeting = () => {
    const hour = currentTime.getHours()
    if (hour < 6) return '夜中もお疲れさまです'
    if (hour < 12) return 'おはようございます'
    if (hour < 18) return 'こんにちは'
    return 'お疲れさまです'
  }

  const getTimeIcon = () => {
    const hour = currentTime.getHours()
    if (hour < 6) return '🌙'
    if (hour < 12) return '🌅'
    if (hour < 18) return '☀️'
    return '🌆'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 p-4">
      <div className="mx-auto max-w-4xl">
        {/* ヒーローセクション - ジーニーのランプ */}
        <div className="mb-8 text-center">
          <motion.div
            className="relative mb-6 inline-block"
            animate={{
              scale: isLampGlowing ? [1, 1.05, 1] : 1,
            }}
            transition={{ duration: 2, repeat: isLampGlowing ? 2 : 0 }}
          >
            {/* 魔法のランプ */}
            <div
              className={`relative mx-auto flex h-32 w-32 cursor-pointer items-center justify-center rounded-full bg-gradient-to-br from-amber-400 via-yellow-400 to-orange-400 transition-all duration-500 ${
                isLampGlowing ? 'shadow-2xl shadow-amber-400' : 'shadow-lg'
              }`}
              onClick={handleLampRub}
            >
              <Wand2 className="h-16 w-16 text-white" />

              {/* 魔法のパーティクル */}
              <AnimatePresence>
                {isLampGlowing && (
                  <>
                    {[...Array(12)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="absolute h-3 w-3 rounded-full bg-yellow-300"
                        initial={{
                          x: 64,
                          y: 64,
                          scale: 0,
                          opacity: 1,
                        }}
                        animate={{
                          x: 64 + Math.cos((i * 30 * Math.PI) / 180) * 80,
                          y: 64 + Math.sin((i * 30 * Math.PI) / 180) * 80,
                          scale: [0, 1, 0],
                          opacity: [1, 1, 0],
                        }}
                        exit={{ opacity: 0 }}
                        transition={{
                          duration: 2,
                          delay: i * 0.1,
                        }}
                      />
                    ))}
                  </>
                )}
              </AnimatePresence>
            </div>

            {/* ジーニーの登場エフェクト */}
            <AnimatePresence>
              {isLampGlowing && (
                <motion.div
                  className="absolute -top-8 left-1/2 -translate-x-1/2 transform"
                  initial={{ opacity: 0, y: 0, scale: 0 }}
                  animate={{
                    opacity: [0, 1, 1, 0],
                    y: [-10, -30, -40, -60],
                    scale: [0, 1, 1.1, 0.8],
                  }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 3 }}
                >
                  <div className="text-4xl">🧞‍♂️</div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* 挨拶とコンセプト */}
          <motion.div
            animate={{ scale: isLampGlowing ? [1, 1.02, 1] : 1 }}
            transition={{ duration: 1 }}
          >
            <h1 className="mb-2 text-3xl font-bold">
              <span className="mr-2">{getTimeIcon()}</span>
              {getGreeting()}！
            </h1>
            <p className="mb-4 text-xl text-gray-700">
              私はあなたの育児の<span className="font-bold text-purple-600">魔法使い</span> ✨
            </p>
            <p className="mb-6 text-gray-600">
              ランプを擦って、今のあなたに必要な魔法を見つけましょう
            </p>
          </motion.div>
        </div>

        {/* 今すぐ叶えられる願い */}
        <div className="mb-8">
          <h2 className="mb-6 text-center text-2xl font-bold text-gray-800">
            🌟 今すぐ叶えられる願い
          </h2>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {activeWishes.map((wish, index) => (
              <motion.div
                key={wish.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card
                  className={`relative overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-xl ${
                    wish.urgent
                      ? 'bg-gradient-to-r from-amber-50 to-orange-50 ring-2 ring-amber-400'
                      : 'bg-white/80 backdrop-blur-sm hover:bg-white/90'
                  }`}
                >
                  {/* 緊急度インジケーター */}
                  {wish.urgent && (
                    <div className="absolute right-3 top-3 h-3 w-3 animate-pulse rounded-full bg-red-500"></div>
                  )}

                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 text-3xl">{wish.icon}</div>
                      <div className="flex-1">
                        <h3 className="mb-2 text-lg font-bold text-gray-800">{wish.title}</h3>
                        <p className="mb-4 text-sm leading-relaxed text-gray-600">
                          {wish.description}
                        </p>

                        {/* アクションボタン */}
                        <Button
                          className={`w-full ${
                            wish.urgent
                              ? 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600'
                              : 'bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600'
                          }`}
                        >
                          <Sparkles className="mr-2 h-4 w-4" />
                          {wish.action}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* 魔法のクイックアクション */}
        <div className="mb-8">
          <h2 className="mb-6 text-center text-2xl font-bold text-gray-800">
            ⚡ ワンアクション魔法
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {/* 声の魔法 */}
            <Link href="/chat">
              <Card className="h-full cursor-pointer bg-white/80 backdrop-blur-sm transition-all duration-300 hover:scale-105 hover:border-emerald-300 hover:bg-emerald-50">
                <CardContent className="flex h-full flex-col p-6 text-center">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-400">
                    <Mic className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="mb-2 text-lg font-bold text-gray-800">🗣️ 声の魔法</h3>
                  <p className="mb-4 flex-1 text-sm text-gray-600">
                    「さっきミルク飲んだ」
                    <br />
                    話すだけで全て記録
                  </p>
                  <div className="text-xs font-medium text-emerald-600">ワンタッチで開始 →</div>
                </CardContent>
              </Card>
            </Link>

            {/* 写真の魔法 */}
            <Link href="/chat">
              <Card className="h-full cursor-pointer bg-white/80 backdrop-blur-sm transition-all duration-300 hover:scale-105 hover:border-blue-300 hover:bg-blue-50">
                <CardContent className="flex h-full flex-col p-6 text-center">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-400 to-indigo-400">
                    <Camera className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="mb-2 text-lg font-bold text-gray-800">📸 写真の魔法</h3>
                  <p className="mb-4 flex-1 text-sm text-gray-600">
                    離乳食や子どもの様子
                    <br />
                    撮るだけで自動分析
                  </p>
                  <div className="text-xs font-medium text-blue-600">カメラで撮影 →</div>
                </CardContent>
              </Card>
            </Link>

            {/* 相談の魔法 */}
            <Link href="/chat">
              <Card className="h-full cursor-pointer bg-white/80 backdrop-blur-sm transition-all duration-300 hover:scale-105 hover:border-purple-300 hover:bg-purple-50">
                <CardContent className="flex h-full flex-col p-6 text-center">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-purple-400 to-indigo-400">
                    <MessageCircle className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="mb-2 text-lg font-bold text-gray-800">💬 相談の魔法</h3>
                  <p className="mb-4 flex-1 text-sm text-gray-600">
                    夜泣き、イヤイヤ期
                    <br />
                    どんな悩みも即解決
                  </p>
                  <div className="text-xs font-medium text-purple-600">ジーニーと話す →</div>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>

        {/* 魔法の記録 - 最近の活動 */}
        <div className="mb-8">
          <h2 className="mb-6 text-center text-2xl font-bold text-gray-800">📜 最近の魔法の記録</h2>

          <Card className="bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="space-y-4">
                {/* サンプルの魔法記録 */}
                {[
                  {
                    time: '2時間前',
                    action: '夜泣きの相談',
                    result: '効果的な寝かしつけ方法を習得',
                    icon: '🌙',
                  },
                  {
                    time: '4時間前',
                    action: '離乳食の写真記録',
                    result: '食べた量：80% 表情：満足',
                    icon: '📸',
                  },
                  {
                    time: '6時間前',
                    action: '授乳記録（音声）',
                    result: '150ml 10分間 記録完了',
                    icon: '🗣️',
                  },
                ].map((record, index) => (
                  <div key={index} className="flex items-center gap-4 rounded-lg bg-gray-50 p-3">
                    <div className="text-xl">{record.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-gray-800">{record.action}</p>
                          <p className="text-sm text-gray-600">{record.result}</p>
                        </div>
                        <span className="text-xs text-gray-500">{record.time}</span>
                      </div>
                    </div>
                  </div>
                ))}

                <Button variant="outline" className="mt-4 w-full">
                  魔法の記録をもっと見る
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* ジーニーからのメッセージ */}
        <div className="text-center">
          <Card className="border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50">
            <CardContent className="p-6">
              <div className="mb-4 text-4xl">🧞‍♂️</div>
              <h3 className="mb-2 text-xl font-bold text-gray-800">
                あなたはとても素晴らしい親です
              </h3>
              <p className="text-gray-700">
                毎日の小さな記録が、大きな愛情の証。
                <br />
                困った時はいつでもランプを擦って、私を呼んでくださいね。
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
