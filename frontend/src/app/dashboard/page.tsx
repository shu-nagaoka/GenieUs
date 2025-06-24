'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { AppLayout } from '@/components/layout/app-layout'
import { FloatingVoiceButton } from '@/components/v2/voice-recording/FloatingVoiceButton'
import { 
  FiMessageCircle, 
  FiMic,
  FiCamera,
  FiArrowRight,
  FiZap,
  FiPlay
} from 'react-icons/fi'
import { 
  GiMagicLamp,
  GiSparkles
} from 'react-icons/gi'
import { 
  HiOutlineHeart,
  HiOutlineCalendar,
  HiOutlineChartBar
} from 'react-icons/hi2'

export default function DashboardPage() {
  return (
    <AppLayout>
      {/* シンプルで分かりやすいヘッダー */}
      <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 border-b border-orange-100">
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
              <span className="text-orange-600">Genie ＋ Us</span>で
              <span className="text-gray-800">子育てをもっと楽に</span>
            </h1>

            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              話すだけで <span className="text-orange-600 font-bold text-3xl">記録・相談・予定管理</span> が全部できる<br />
              <span className="text-orange-600 font-bold text-3xl">あなただけの魔法のランプ✨️</span>
            </p>
          </div>
        </div>
      </div>

        <div className="container mx-auto px-6 py-6 max-w-6xl">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-6">
          {/* 記録する */}
          <Link href="/chat">
            <Card className="group cursor-pointer bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 hover:border-blue-300 hover:shadow-lg transition-all duration-200 hover:scale-[1.02] h-full">
              <CardContent className="p-8">
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center mx-auto mb-6 shadow-lg">
              <HiOutlineChartBar className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-blue-800 mb-4 text-center">記録する</h3>

            <div className="space-y-3 mb-6">
              <div className="bg-white/80 p-3 rounded-lg text-sm">
                <div className="font-semibold text-blue-700 mb-1">「今日の様子は？」</div>
                <div className="text-blue-600">→ 食事・睡眠・機嫌を自動記録</div>
              </div>
              <div className="bg-white/80 p-3 rounded-lg text-sm">
                <div className="font-semibold text-blue-700 mb-1">「写真を撮ったよ」</div>
                <div className="text-blue-600">→ 成長記録として保存</div>
              </div>
            </div>

            <div className="flex items-center justify-center text-blue-600 group-hover:text-blue-700 font-semibold">
              <span>記録を始める</span>
              <FiArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
            </div>
              </CardContent>
            </Card>
          </Link>

          {/* 相談する */}
          <Link href="/chat">
            <Card className="group cursor-pointer bg-gradient-to-br from-pink-50 to-rose-50 border border-pink-200 hover:border-pink-300 hover:shadow-lg transition-all duration-200 hover:scale-[1.02] h-full">
              <CardContent className="p-8">
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-pink-400 to-rose-400 flex items-center justify-center mx-auto mb-6 shadow-lg">
              <HiOutlineHeart className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-pink-800 mb-4 text-center">相談する</h3>

            <div className="space-y-3 mb-6">
              <div className="bg-white/80 p-3 rounded-lg text-sm">
                <div className="font-semibold text-pink-700 mb-1">「夜泣きがひどい」</div>
                <div className="text-pink-600">→ 原因と対策をアドバイス</div>
              </div>
              <div className="bg-white/80 p-3 rounded-lg text-sm">
                <div className="font-semibold text-pink-700 mb-1">「離乳食のレシピは？」</div>
                <div className="text-pink-600">→ 月齢に合わせて提案</div>
              </div>
            </div>

            <div className="flex items-center justify-center text-pink-600 group-hover:text-pink-700 font-semibold">
              <span>相談してみる</span>
              <FiArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
            </div>
              </CardContent>
            </Card>
          </Link>

          {/* 管理する */}
          <Link href="/chat">
            <Card className="group cursor-pointer bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:scale-[1.02] h-full">
              <CardContent className="p-8">
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-green-400 to-emerald-400 flex items-center justify-center mx-auto mb-6 shadow-lg">
              <HiOutlineCalendar className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-green-800 mb-4 text-center">管理する</h3>

            <div className="space-y-3 mb-6">
              <div className="bg-white/80 p-3 rounded-lg text-sm">
                <div className="font-semibold text-green-700 mb-1">「次の予防接種は？」</div>
                <div className="text-green-600">→ スケジュールを確認</div>
              </div>
              <div className="bg-white/80 p-3 rounded-lg text-sm">
                <div className="font-semibold text-green-700 mb-1">「健診を忘れずに」</div>
                <div className="text-green-600">→ 自動でリマインド</div>
              </div>
            </div>

            <div className="flex items-center justify-center text-green-600 group-hover:text-green-700 font-semibold">
              <span>予定を確認</span>
              <FiArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
            </div>
              </CardContent>
            </Card>
          </Link>
            </div>

          {/* メインCTA */}
          <div className="text-center">
            <Link href="/chat">
              <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 px-12 py-6 text-xl font-bold shadow-xl hover:shadow-2xl transition-all duration-300">
                <GiMagicLamp className="h-6 w-6 mr-3" />
                Genieと話してみる
                <GiSparkles className="h-5 w-5 ml-3 animate-pulse" />
              </Button>
            </Link>
            <p className="text-sm text-gray-500 mt-3">無料で今すぐ始められます</p>
          </div>
        </div>

    </AppLayout>
  )
}