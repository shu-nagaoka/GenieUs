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
  FiHome
} from 'react-icons/fi'
import { 
  GiMagicLamp,
  GiSparkles
} from 'react-icons/gi'
import { 
  HiOutlineHeart,
  HiOutlineCalendar,
  HiOutlineChartBar,
  HiOutlineChatBubbleLeftEllipsis,
  HiOutlinePhoto,
  HiOutlineUserGroup,
  HiOutlineSparkles
} from 'react-icons/hi2'

export default function DashboardPage() {
  return (
    <AuthCheck>
      <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
        {/* シンプルで分かりやすいヘッダー */}
        <div className="px-4 py-8">
          <div className="text-center max-w-4xl mx-auto">
            {/* 魔法のランプアイコン */}
            <div className="relative mb-12">
              <div className="h-24 w-24 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center mx-auto shadow-xl">
                <GiMagicLamp className="h-12 w-12 text-white" />
              </div>
              <GiSparkles className="absolute -top-1 -right-1 h-6 w-6 text-yellow-400 animate-pulse" />
            </div>

            <h1 className="md:text-5xl font-bold text-gray-800 mb-4">
              <span className="text-orange-600">GenieUs</span>で
              <span className="text-gray-800">愛情ある子育てを</span>
            </h1>

            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              話すだけで <span className="text-orange-600 font-bold text-2xl">家族管理・成長記録・努力見える化</span> <br />
              <span className="text-orange-600 font-bold text-2xl">すべてがつながる子育てアシスタント✨</span>
            </p>

            <div className="mt-12 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 p-8 rounded-2xl shadow-2xl border-0 transform hover:scale-105 transition-all duration-300">
              <div className="bg-white/95 backdrop-blur-md rounded-xl p-6 shadow-inner">
                {/* 複数エージェントのアイコン表示 */}
                <div className="flex justify-center mb-4">
                  <div className="relative">
                    {/* 中央のメインエージェント */}
                    <div className="h-12 w-12 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg z-10 relative">
                      <HiOutlineSparkles className="h-6 w-6 text-white" />
                    </div>
                    {/* 周囲の専門エージェント */}
                    <div className="absolute -top-2 -left-8 h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-cyan-500 flex items-center justify-center shadow-md animate-bounce" style={{animationDelay: '0s'}}>
                      <HiOutlineHeart className="h-4 w-4 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-8 h-8 w-8 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center shadow-md animate-bounce" style={{animationDelay: '0.5s'}}>
                      <FiTrendingUp className="h-4 w-4 text-white" />
                    </div>
                    <div className="absolute -bottom-2 -left-6 h-8 w-8 rounded-full bg-gradient-to-br from-pink-400 to-rose-500 flex items-center justify-center shadow-md animate-bounce" style={{animationDelay: '1s'}}>
                      <FiStar className="h-4 w-4 text-white" />
                    </div>
                    <div className="absolute -bottom-2 -right-6 h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-violet-500 flex items-center justify-center shadow-md animate-bounce" style={{animationDelay: '1.5s'}}>
                      <FiZap className="h-4 w-4 text-white" />
                    </div>
                    <div className="absolute top-2 -left-12 h-6 w-6 rounded-full bg-gradient-to-br from-indigo-400 to-blue-500 flex items-center justify-center shadow-sm animate-pulse">
                      <FiUsers className="h-3 w-3 text-white" />
                    </div>
                    <div className="absolute top-2 -right-12 h-6 w-6 rounded-full bg-gradient-to-br from-teal-400 to-cyan-500 flex items-center justify-center shadow-sm animate-pulse" style={{animationDelay: '0.7s'}}>
                      <FiCalendar className="h-3 w-3 text-white" />
                    </div>
                  </div>
                </div>

                <p className="text-2xl font-bold text-gray-800 mb-3 text-center">
                  <span className="bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">18人の専門GenieUs Agents</span>
                  <span className="text-gray-800">が連携</span>
                </p>
                <p className="text-base text-gray-700 text-center leading-relaxed">
                  睡眠・栄養・夜泣き・離乳食・発達・遊び・しつけなど<br />
                  <span className="font-semibold text-orange-600">あらゆる分野の専門Agentsがチーム</span>であなたをサポート
                </p>
                <div className="flex justify-center mt-4">
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

        <div className="container mx-auto px-6 py-6 max-w-6xl">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-6">
          {/* 家族を管理・つながる */}
          <Card className="group cursor-pointer bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 hover:border-blue-300 hover:shadow-lg transition-all duration-200 hover:scale-[1.02] h-full">
            <CardContent className="p-8">
              <div className="h-16 w-16 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center mx-auto mb-6 shadow-lg">
                <HiOutlineUserGroup className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-blue-800 mb-4 text-center">家族を管理・つながる</h3>

              <div className="space-y-3 mb-6">
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-blue-700 mb-1 flex items-center gap-2">
                    <FiUsers className="h-3 w-3" />
                    「家族情報を登録」
                  </div>
                  <div className="text-blue-600">→ パパ・ママ・お子さんの情報をまとめて管理</div>
                </div>
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-blue-700 mb-1 flex items-center gap-2">
                    <HiOutlineChatBubbleLeftEllipsis className="h-3 w-3" />
                    「今日どうだった？」
                  </div>
                  <div className="text-blue-600">→ 複数の専門GenieUsエージェントがあなたの話を理解・記録</div>
                </div>
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-blue-700 mb-1 flex items-center gap-2">
                    <GiSparkles className="h-3 w-3" />
                    「15の専門エージェント連携」
                  </div>
                  <div className="text-blue-600">→ 睡眠・栄養・夜泣き・しつけなど各分野の専門エージェントがサポート</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-4">
                <Link href="/family" className="block">
                  <Button variant="outline" size="sm" className="w-full border-blue-300 text-blue-700 hover:bg-blue-50 text-xs">
                    <FiUsers className="h-3 w-3 mr-1" />
                    家族情報
                  </Button>
                </Link>
                <Link href="/chat" className="block">
                  <Button variant="outline" size="sm" className="w-full border-blue-300 text-blue-700 hover:bg-blue-50 text-xs">
                    <HiOutlineChatBubbleLeftEllipsis className="h-3 w-3 mr-1" />
                    会話で記録
                  </Button>
                </Link>
              </div>

              <Link href="/chat" className="block">
                <div className="flex items-center justify-center text-blue-600 group-hover:text-blue-700 font-semibold">
                  <span>Genieと話してみる</span>
                  <FiArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
                </div>
              </Link>
            </CardContent>
          </Card>

          {/* 成長を記録・振り返る */}
          <Card className="group cursor-pointer bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 hover:border-emerald-300 hover:shadow-lg transition-all duration-200 hover:scale-[1.02] h-full">
            <CardContent className="p-8">
              <div className="h-16 w-16 rounded-full bg-gradient-to-br from-emerald-400 to-teal-400 flex items-center justify-center mx-auto mb-6 shadow-lg">
                <FiTrendingUp className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-emerald-800 mb-4 text-center">成長を記録・振り返る</h3>

              <div className="space-y-3 mb-6">
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-emerald-700 mb-1 flex items-center gap-2">
                    <HiOutlinePhoto className="h-3 w-3" />
                    「初めて歩いた！」
                  </div>
                  <div className="text-emerald-600">→ 写真付きで大切な瞬間をメモリーズに保存</div>
                </div>
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-emerald-700 mb-1 flex items-center gap-2">
                    <FiTrendingUp className="h-3 w-3" />
                    「身長が伸びた」
                  </div>
                  <div className="text-emerald-600">→ からだ・ことば・社会性など成長記録を蓄積</div>
                </div>
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-emerald-700 mb-1 flex items-center gap-2">
                    <FiBook className="h-3 w-3" />
                    「成長を振り返りたい」
                  </div>
                  <div className="text-emerald-600">→ 月齢別・タイプ別でこれまでの成長を確認</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-4">
                <Link href="/records" className="block">
                  <Button variant="outline" size="sm" className="w-full border-emerald-300 text-emerald-700 hover:bg-emerald-50 text-xs">
                    <HiOutlinePhoto className="h-3 w-3 mr-1" />
                    メモリーズ
                  </Button>
                </Link>
                <Link href="/records" className="block">
                  <Button variant="outline" size="sm" className="w-full border-emerald-300 text-emerald-700 hover:bg-emerald-50 text-xs">
                    <FiTrendingUp className="h-3 w-3 mr-1" />
                    成長記録
                  </Button>
                </Link>
              </div>

              <Link href="/records" className="block">
                <div className="flex items-center justify-center text-emerald-600 group-hover:text-emerald-700 font-semibold">
                  <span>成長を記録する</span>
                  <FiArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
                </div>
              </Link>
            </CardContent>
          </Card>

          {/* 努力を見える化・実感する */}
          <Card className="group cursor-pointer bg-gradient-to-br from-pink-50 to-rose-50 border border-pink-200 hover:border-pink-300 hover:shadow-lg transition-all duration-200 hover:scale-[1.02] h-full">
            <CardContent className="p-8">
              <div className="h-16 w-16 rounded-full bg-gradient-to-br from-pink-400 to-rose-400 flex items-center justify-center mx-auto mb-6 shadow-lg">
                <HiOutlineSparkles className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-pink-800 mb-4 text-center">努力を見える化・実感する</h3>

              <div className="space-y-3 mb-6">
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-pink-700 mb-1 flex items-center gap-2">
                    <FiHeart className="h-3 w-3" />
                    「頑張ったことを教えて」
                  </div>
                  <div className="text-pink-600">→ あなたの愛情と努力をGenieが理解・認める</div>
                </div>
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-pink-700 mb-1 flex items-center gap-2">
                    <FiStar className="h-3 w-3" />
                    「今週の頑張り確認」
                  </div>
                  <div className="text-pink-600">→ 自動作成される努力レポートで実感</div>
                </div>
                <div className="bg-white/80 p-3 rounded-lg text-sm">
                  <div className="font-semibold text-pink-700 mb-1 flex items-center gap-2">
                    <HiOutlineChatBubbleLeftEllipsis className="h-3 w-3" />
                    「不安だけど大丈夫？」
                  </div>
                  <div className="text-pink-600">→ 努力を理解したGenieが温かくサポート</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-4">
                <Link href="/effort-report" className="block">
                  <Button variant="outline" size="sm" className="w-full border-pink-300 text-pink-700 hover:bg-pink-50 text-xs">
                    <FiStar className="h-3 w-3 mr-1" />
                    努力レポート
                  </Button>
                </Link>
                <Link href="/chat" className="block">
                  <Button variant="outline" size="sm" className="w-full border-pink-300 text-pink-700 hover:bg-pink-50 text-xs">
                    <FiHeart className="h-3 w-3 mr-1" />
                    相談・共感
                  </Button>
                </Link>
              </div>

              <Link href="/effort-report" className="block">
                <div className="flex items-center justify-center text-pink-600 group-hover:text-pink-700 font-semibold">
                  <span>頑張りを実感する</span>
                  <FiArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
                </div>
              </Link>
            </CardContent>
          </Card>
            </div>

          {/* メインCTA */}
          <div className="text-center mt-12">
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-4">
              <Link href="/chat">
                <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 px-12 py-6 text-xl font-bold shadow-xl hover:shadow-2xl transition-all duration-300">
                  <GiMagicLamp className="h-6 w-6 mr-3" />
                  GenieUsを始める
                  <GiSparkles className="h-5 w-5 ml-3 animate-pulse" />
                </Button>
              </Link>
              
              <Link href="/agents">
                <Button variant="outline" size="lg" className="border-orange-300 text-orange-700 hover:bg-orange-50 px-12 py-6 text-xl font-medium">
                  <HiOutlineSparkles className="h-5 w-5 mr-3" />
                  15人のAgentsを見る
                </Button>
              </Link>
            </div>
            <p className="text-lg text-gray-600 font-medium">話すだけで始まる、愛情ある子育てサポート</p>
          </div>
        </div>
      </div>
    </AppLayout>
    </AuthCheck>
  )
}