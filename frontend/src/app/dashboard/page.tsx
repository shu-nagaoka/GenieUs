'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { AppLayout } from '@/components/layout/app-layout'
import { FloatingVoiceButton } from '@/components/v2/voice-recording/FloatingVoiceButton'
import { AuthCheck } from '@/components/features/auth/auth-check'
import {
  FiMessageCircle,
  FiMic,
  FiCamera,
  FiArrowRight,
  FiZap,
  FiPlay,
  FiUsers,
  FiTrendingUp,
  FiHeart,
  FiCalendar,
  FiStar,
  FiBook,
  FiHome,
} from 'react-icons/fi'
import { GiMagicLamp, GiSparkles } from 'react-icons/gi'
import {
  HiOutlineHeart,
  HiOutlineCalendar,
  HiOutlineChartBar,
  HiOutlineChatBubbleLeftEllipsis,
  HiOutlinePhoto,
  HiOutlineUserGroup,
  HiOutlineSparkles,
} from 'react-icons/hi2'

export default function DashboardPage() {
  return (
    <AuthCheck>
      <AppLayout>
        <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
          {/* シンプルで分かりやすいヘッダー */}
          <div className="px-4 py-8">
            <div className="mx-auto max-w-4xl text-center">
              {/* 魔法のランプアイコン */}
              <div className="relative mb-12">
                <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 shadow-xl">
                  <GiMagicLamp className="h-12 w-12 text-white" />
                </div>
                <GiSparkles className="absolute -right-1 -top-1 h-6 w-6 animate-pulse text-yellow-400" />
              </div>

              <h1 className="mb-4 font-bold text-gray-800 md:text-5xl">
                <span className="text-orange-600">GenieUs</span>で
                <span className="text-gray-800">愛情ある子育てを</span>
              </h1>

              <p className="mx-auto max-w-2xl text-xl text-gray-600">
                話すだけで{' '}
                <span className="text-2xl font-bold text-orange-600">
                  家族管理・成長記録・努力見える化
                </span>{' '}
                <br />
                <span className="text-2xl font-bold text-orange-600">
                  すべてがつながる子育てアシスタント✨
                </span>
              </p>

              <div className="mt-12 transform rounded-2xl border-0 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 p-8 shadow-2xl transition-all duration-300 hover:scale-105">
                <div className="rounded-xl bg-white/95 p-6 shadow-inner backdrop-blur-md">
                  {/* 複数エージェントのアイコン表示 */}
                  <div className="mb-4 flex justify-center">
                    <div className="relative">
                      {/* 中央のメインエージェント */}
                      <div className="relative z-10 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg">
                        <HiOutlineSparkles className="h-6 w-6 text-white" />
                      </div>
                      {/* 周囲の専門エージェント */}
                      <div
                        className="absolute -left-8 -top-2 flex h-8 w-8 animate-bounce items-center justify-center rounded-full bg-gradient-to-br from-blue-400 to-cyan-500 shadow-md"
                        style={{ animationDelay: '0s' }}
                      >
                        <HiOutlineHeart className="h-4 w-4 text-white" />
                      </div>
                      <div
                        className="absolute -right-8 -top-2 flex h-8 w-8 animate-bounce items-center justify-center rounded-full bg-gradient-to-br from-green-400 to-emerald-500 shadow-md"
                        style={{ animationDelay: '0.5s' }}
                      >
                        <FiTrendingUp className="h-4 w-4 text-white" />
                      </div>
                      <div
                        className="absolute -bottom-2 -left-6 flex h-8 w-8 animate-bounce items-center justify-center rounded-full bg-gradient-to-br from-pink-400 to-rose-500 shadow-md"
                        style={{ animationDelay: '1s' }}
                      >
                        <FiStar className="h-4 w-4 text-white" />
                      </div>
                      <div
                        className="absolute -bottom-2 -right-6 flex h-8 w-8 animate-bounce items-center justify-center rounded-full bg-gradient-to-br from-purple-400 to-violet-500 shadow-md"
                        style={{ animationDelay: '1.5s' }}
                      >
                        <FiZap className="h-4 w-4 text-white" />
                      </div>
                      <div className="absolute -left-12 top-2 flex h-6 w-6 animate-pulse items-center justify-center rounded-full bg-gradient-to-br from-indigo-400 to-blue-500 shadow-sm">
                        <FiUsers className="h-3 w-3 text-white" />
                      </div>
                      <div
                        className="absolute -right-12 top-2 flex h-6 w-6 animate-pulse items-center justify-center rounded-full bg-gradient-to-br from-teal-400 to-cyan-500 shadow-sm"
                        style={{ animationDelay: '0.7s' }}
                      >
                        <FiCalendar className="h-3 w-3 text-white" />
                      </div>
                    </div>
                  </div>

                  <p className="mb-3 text-center text-2xl font-bold text-gray-800">
                    <span className="bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                      15人の専門GenieUs Agents
                    </span>
                    <span className="text-gray-800">が連携</span>
                  </p>
                  <p className="text-center text-base leading-relaxed text-gray-700">
                    睡眠・栄養・夜泣き・離乳食・発達・遊び・しつけなど
                    <br />
                    <span className="font-semibold text-orange-600">
                      あらゆる分野の専門Agentsがチーム
                    </span>
                    であなたをサポート
                  </p>
                  <div className="mt-4 flex justify-center">
                    <div className="flex items-center gap-2 text-orange-600">
                      <GiSparkles className="h-5 w-5 animate-pulse" />
                      <span className="text-sm font-medium">AI駆動マルチエージェントシステム</span>
                      <GiSparkles className="h-5 w-5 animate-pulse" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="container mx-auto max-w-6xl px-6 py-6">
            <div className="mb-6 grid grid-cols-1 gap-8 lg:grid-cols-3">
              {/* 家族を管理・つながる */}
              <Card className="group h-full cursor-pointer border border-blue-200 bg-gradient-to-br from-blue-50 to-cyan-50 transition-all duration-200 hover:scale-[1.02] hover:border-blue-300 hover:shadow-lg">
                <CardContent className="p-8">
                  <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 shadow-lg">
                    <HiOutlineUserGroup className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="mb-4 text-center text-2xl font-bold text-blue-800">
                    家族を管理・つながる
                  </h3>

                  <div className="mb-6 space-y-3">
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-blue-700">
                        <FiUsers className="h-3 w-3" />
                        「家族情報を登録」
                      </div>
                      <div className="text-blue-600">
                        → パパ・ママ・お子さんの情報をまとめて管理
                      </div>
                    </div>
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-blue-700">
                        <HiOutlineChatBubbleLeftEllipsis className="h-3 w-3" />
                        「今日どうだった？」
                      </div>
                      <div className="text-blue-600">
                        → 複数の専門GenieUsエージェントがあなたの話を理解・記録
                      </div>
                    </div>
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-blue-700">
                        <GiSparkles className="h-3 w-3" />
                        「15の専門エージェント連携」
                      </div>
                      <div className="text-blue-600">
                        → 睡眠・栄養・夜泣き・しつけなど各分野の専門エージェントがサポート
                      </div>
                    </div>
                  </div>

                  <div className="mb-4 grid grid-cols-2 gap-2">
                    <Link href="/family" className="block">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full border-blue-300 text-xs text-blue-700 hover:bg-blue-50"
                      >
                        <FiUsers className="mr-1 h-3 w-3" />
                        家族情報
                      </Button>
                    </Link>
                    <Link href="/chat" className="block">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full border-blue-300 text-xs text-blue-700 hover:bg-blue-50"
                      >
                        <HiOutlineChatBubbleLeftEllipsis className="mr-1 h-3 w-3" />
                        会話で記録
                      </Button>
                    </Link>
                  </div>

                  <Link href="/chat" className="block">
                    <div className="flex items-center justify-center font-semibold text-blue-600 group-hover:text-blue-700">
                      <span>Genieと話してみる</span>
                      <FiArrowRight className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                    </div>
                  </Link>
                </CardContent>
              </Card>

              {/* 成長を記録・振り返る */}
              <Card className="group h-full cursor-pointer border border-emerald-200 bg-gradient-to-br from-emerald-50 to-teal-50 transition-all duration-200 hover:scale-[1.02] hover:border-emerald-300 hover:shadow-lg">
                <CardContent className="p-8">
                  <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-400 shadow-lg">
                    <FiTrendingUp className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="mb-4 text-center text-2xl font-bold text-emerald-800">
                    成長を記録・振り返る
                  </h3>

                  <div className="mb-6 space-y-3">
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-emerald-700">
                        <HiOutlinePhoto className="h-3 w-3" />
                        「初めて歩いた！」
                      </div>
                      <div className="text-emerald-600">
                        → 写真付きで大切な瞬間をメモリーズに保存
                      </div>
                    </div>
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-emerald-700">
                        <FiTrendingUp className="h-3 w-3" />
                        「身長が伸びた」
                      </div>
                      <div className="text-emerald-600">
                        → からだ・ことば・社会性など成長記録を蓄積
                      </div>
                    </div>
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-emerald-700">
                        <FiBook className="h-3 w-3" />
                        「成長を振り返りたい」
                      </div>
                      <div className="text-emerald-600">
                        → 月齢別・タイプ別でこれまでの成長を確認
                      </div>
                    </div>
                  </div>

                  <div className="mb-4 grid grid-cols-2 gap-2">
                    <Link href="/records" className="block">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full border-emerald-300 text-xs text-emerald-700 hover:bg-emerald-50"
                      >
                        <HiOutlinePhoto className="mr-1 h-3 w-3" />
                        メモリーズ
                      </Button>
                    </Link>
                    <Link href="/records" className="block">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full border-emerald-300 text-xs text-emerald-700 hover:bg-emerald-50"
                      >
                        <FiTrendingUp className="mr-1 h-3 w-3" />
                        成長記録
                      </Button>
                    </Link>
                  </div>

                  <Link href="/records" className="block">
                    <div className="flex items-center justify-center font-semibold text-emerald-600 group-hover:text-emerald-700">
                      <span>成長を記録する</span>
                      <FiArrowRight className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                    </div>
                  </Link>
                </CardContent>
              </Card>

              {/* 努力を見える化・実感する */}
              <Card className="group h-full cursor-pointer border border-pink-200 bg-gradient-to-br from-pink-50 to-rose-50 transition-all duration-200 hover:scale-[1.02] hover:border-pink-300 hover:shadow-lg">
                <CardContent className="p-8">
                  <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-pink-400 to-rose-400 shadow-lg">
                    <HiOutlineSparkles className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="mb-4 text-center text-2xl font-bold text-pink-800">
                    努力を見える化・実感する
                  </h3>

                  <div className="mb-6 space-y-3">
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-pink-700">
                        <FiHeart className="h-3 w-3" />
                        「頑張ったことを教えて」
                      </div>
                      <div className="text-pink-600">→ あなたの愛情と努力をGenieが理解・認める</div>
                    </div>
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-pink-700">
                        <FiStar className="h-3 w-3" />
                        「今週の頑張り確認」
                      </div>
                      <div className="text-pink-600">→ 自動作成される努力レポートで実感</div>
                    </div>
                    <div className="rounded-lg bg-white/80 p-3 text-sm">
                      <div className="mb-1 flex items-center gap-2 font-semibold text-pink-700">
                        <HiOutlineChatBubbleLeftEllipsis className="h-3 w-3" />
                        「不安だけど大丈夫？」
                      </div>
                      <div className="text-pink-600">→ 努力を理解したGenieが温かくサポート</div>
                    </div>
                  </div>

                  <div className="mb-4 grid grid-cols-2 gap-2">
                    <Link href="/effort-report" className="block">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full border-pink-300 text-xs text-pink-700 hover:bg-pink-50"
                      >
                        <FiStar className="mr-1 h-3 w-3" />
                        努力レポート
                      </Button>
                    </Link>
                    <Link href="/chat" className="block">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full border-pink-300 text-xs text-pink-700 hover:bg-pink-50"
                      >
                        <FiHeart className="mr-1 h-3 w-3" />
                        相談・共感
                      </Button>
                    </Link>
                  </div>

                  <Link href="/effort-report" className="block">
                    <div className="flex items-center justify-center font-semibold text-pink-600 group-hover:text-pink-700">
                      <span>頑張りを実感する</span>
                      <FiArrowRight className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                    </div>
                  </Link>
                </CardContent>
              </Card>
            </div>

            {/* メインCTA */}
            <div className="mt-12 text-center">
              <div className="mb-4 flex flex-col justify-center gap-4 sm:flex-row">
                <Link href="/chat">
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-amber-500 to-orange-500 px-12 py-6 text-xl font-bold shadow-xl transition-all duration-300 hover:from-amber-600 hover:to-orange-600 hover:shadow-2xl"
                  >
                    <GiMagicLamp className="mr-3 h-6 w-6" />
                    GenieUsを始める
                    <GiSparkles className="ml-3 h-5 w-5 animate-pulse" />
                  </Button>
                </Link>

                <Link href="/agents">
                  <Button
                    variant="outline"
                    size="lg"
                    className="border-orange-300 px-12 py-6 text-xl font-medium text-orange-700 hover:bg-orange-50"
                  >
                    <HiOutlineSparkles className="mr-3 h-5 w-5" />
                    15人のAgentsを見る
                  </Button>
                </Link>
              </div>
              <p className="text-lg font-medium text-gray-600">
                話すだけで始まる、愛情ある子育てサポート
              </p>
            </div>
          </div>
        </div>
      </AppLayout>
    </AuthCheck>
  )
}
