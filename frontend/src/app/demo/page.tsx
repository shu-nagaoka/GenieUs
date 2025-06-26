'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { signIn } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import {
  Clock,
  CheckCircle,
  Baby,
  Heart,
  Zap,
  ArrowRight,
  Play,
  Users,
  Shield,
  Sparkles,
  TrendingUp,
  Star,
  Award,
  Target,
  Lightbulb,
  ChevronDown,
} from 'lucide-react'

export default function HackathonLandingPage() {
  const router = useRouter()
  const [currentStats, setCurrentStats] = useState({ time: 0, stress: 100, confidence: 0 })
  const [isAnimating, setIsAnimating] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const startAnimation = () => {
    setIsAnimating(true)
    setCurrentStats({ time: 0, stress: 100, confidence: 0 })

    const interval = setInterval(() => {
      setCurrentStats(prev => {
        if (prev.time >= 15) {
          clearInterval(interval)
          return { time: 15, stress: 25, confidence: 90 }
        }
        return {
          time: prev.time + 1,
          stress: Math.max(25, 100 - prev.time * 5),
          confidence: Math.min(90, prev.time * 6),
        }
      })
    }, 200)

    setTimeout(() => setIsAnimating(false), 3500)
  }

  const handleStartNow = () => {
    router.push('/')
  }

  return (
    <div className="min-h-screen overflow-hidden bg-black text-white">
      {/* パーティクル背景 */}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-amber-500/10 via-orange-500/5 to-yellow-500/10" />
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute h-1 w-1 animate-pulse rounded-full bg-amber-400/30"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      {/* ヒーローセクション */}
      <section className="relative flex min-h-screen items-center justify-center">
        <div
          className="absolute inset-0 bg-gradient-to-br from-amber-600/20 via-orange-600/10 to-yellow-600/20"
          style={{ transform: `translateY(${scrollY * 0.3}px)` }}
        />

        <div className="relative z-10 mx-auto max-w-7xl px-6 text-center">
          <div className="mb-8">
            <Badge className="mb-6 border border-amber-500/30 bg-gradient-to-r from-amber-500/20 to-orange-500/20 px-6 py-3 text-sm font-medium text-amber-300 backdrop-blur-sm">
              <Award className="mr-2 h-4 w-4" />
              Zenn AI Agent Hackathon 2025 出品作品
            </Badge>
          </div>

          <h1 className="mb-8 text-7xl font-bold leading-tight md:text-8xl">
            <span className="animate-pulse bg-gradient-to-r from-amber-400 via-orange-400 to-yellow-400 bg-clip-text text-transparent">
              見えない成長に、
            </span>
            <br />
            <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              光をあてる。
            </span>
          </h1>

          <p className="mx-auto mb-6 max-w-4xl text-3xl leading-relaxed text-gray-300">
            不安な毎日を、自信に変える。
          </p>

          <p className="mx-auto mb-16 max-w-3xl text-xl text-gray-400">
            Google ADK × Gemini 2.5 Flash powered
            <br />
            次世代AI子育て支援システム「
            <span className="font-semibold text-amber-400">GenieUs</span>」
          </p>

          {/* 浮遊するKPI */}
          <div className="mx-auto mb-16 grid max-w-5xl grid-cols-1 gap-8 md:grid-cols-3">
            {[
              {
                value: '85%',
                label: '時短効果',
                icon: <Zap className="h-8 w-8" />,
                color: 'from-amber-500 to-orange-500',
              },
              {
                value: '15分',
                label: '平均解決時間',
                icon: <Clock className="h-8 w-8" />,
                color: 'from-green-500 to-emerald-500',
              },
              {
                value: '24/7',
                label: 'いつでも相談',
                icon: <Heart className="h-8 w-8" />,
                color: 'from-blue-500 to-purple-500',
              },
            ].map((stat, index) => (
              <div
                key={index}
                className="group relative"
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <div
                  className="absolute inset-0 rounded-2xl bg-gradient-to-r opacity-20 blur-xl transition-all duration-500 group-hover:opacity-40"
                  style={{
                    background: `linear-gradient(to right, ${stat.color.split(' ')[1]}, ${stat.color.split(' ')[3]})`,
                  }}
                />
                <Card className="relative border border-gray-700/50 bg-gray-900/50 backdrop-blur-lg transition-all duration-500 hover:bg-gray-800/50 group-hover:scale-105">
                  <CardContent className="p-8 text-center">
                    <div
                      className={`inline-flex rounded-full bg-gradient-to-r p-4 ${stat.color} mb-4`}
                    >
                      {stat.icon}
                    </div>
                    <div className="mb-3 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-5xl font-bold text-transparent">
                      {stat.value}
                    </div>
                    <div className="font-medium text-gray-400">{stat.label}</div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>

          <div className="space-y-6">
            {/* メインCTAボタン群 */}
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button
                onClick={handleStartNow}
                size="lg"
                className="group transform rounded-full bg-gradient-to-r from-amber-600 to-orange-600 px-12 py-6 text-xl font-semibold text-white shadow-2xl transition-all duration-500 hover:scale-105 hover:from-amber-500 hover:to-orange-500 hover:shadow-amber-500/25"
              >
                <ArrowRight className="mr-3 h-6 w-6 transition-transform group-hover:translate-x-1" />
                今すぐ始める
              </Button>
              
              <Button
                onClick={startAnimation}
                size="lg"
                variant="outline"
                className="group transform rounded-full border-2 border-amber-500 px-12 py-6 text-xl font-semibold text-amber-400 backdrop-blur-sm transition-all duration-500 hover:scale-105 hover:bg-amber-500 hover:text-black"
              >
                <Play className="mr-3 h-6 w-6 transition-transform group-hover:scale-110" />
                革命的デモを体験
              </Button>
            </div>

            <div className="flex items-center justify-center space-x-2 text-gray-400">
              <span>スクロールして詳細を見る</span>
              <ChevronDown className="h-5 w-5 animate-bounce" />
            </div>
          </div>
        </div>
      </section>

      {/* 問題提起セクション */}
      <section className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-black py-32">
        <div className="absolute inset-0 bg-red-500/5" />
        <div className="relative mx-auto max-w-7xl px-6">
          <div className="mb-20 text-center">
            <h2 className="mb-8 text-6xl font-bold">
              <span className="bg-gradient-to-r from-red-400 to-pink-400 bg-clip-text text-transparent">
                毎日の育児、
              </span>
              <br />
              <span className="text-white">こんな悩みありませんか？</span>
            </h2>
            <p className="mx-auto max-w-3xl text-xl text-gray-400">
              多くの親が抱える共通の不安。従来の方法では解決に時間がかかりすぎます。
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {[
              {
                icon: <Baby className="h-16 w-16" />,
                title: '夜泣きが止まらない',
                problems: [
                  'ネット検索で情報が多すぎて混乱',
                  '原因がわからず不安で眠れない',
                  '小児科の予約が取れない',
                  '家族全員が疲弊してしまう',
                ],
                time: '2時間調査しても解決せず...',
                gradient: 'from-red-500 to-pink-500',
              },
              {
                icon: <Heart className="h-16 w-16" />,
                title: '離乳食が心配',
                problems: [
                  'アレルギーが怖くて進められない',
                  '栄養バランスの計算が複雑',
                  '月齢に合っているか判断できない',
                  'レシピが実用的でない',
                ],
                time: '1.5時間かけても決められない...',
                gradient: 'from-orange-500 to-red-500',
              },
              {
                icon: <TrendingUp className="h-16 w-16" />,
                title: '発達が心配',
                problems: [
                  '他の子と比べて不安になる',
                  '専門医の情報が見つからない',
                  '一人で悩み続けてしまう',
                  '相談できる場所がない',
                ],
                time: '2時間調べても答えが出ない...',
                gradient: 'from-purple-500 to-pink-500',
              },
            ].map((item, index) => (
              <div key={index} className="group relative">
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${item.gradient} rounded-3xl opacity-10 blur-xl transition-all duration-500 group-hover:opacity-20`}
                />
                <Card className="relative h-full border border-gray-700/50 bg-gray-900/70 backdrop-blur-xl transition-all duration-500 hover:bg-gray-800/70 group-hover:scale-105">
                  <CardContent className="p-10">
                    <div className="mb-8 text-center">
                      <div
                        className={`inline-flex rounded-full bg-gradient-to-br p-6 ${item.gradient} mb-6`}
                      >
                        {item.icon}
                      </div>
                      <h3 className="mb-4 text-2xl font-bold text-white">{item.title}</h3>
                    </div>

                    <div className="mb-8 space-y-4">
                      {item.problems.map((problem, idx) => (
                        <div key={idx} className="flex items-start space-x-3">
                          <div
                            className={`h-2 w-2 rounded-full bg-gradient-to-r ${item.gradient} mt-2 flex-shrink-0`}
                          />
                          <p className="text-sm leading-relaxed text-gray-300">{problem}</p>
                        </div>
                      ))}
                    </div>

                    <div className="text-center">
                      <Badge
                        className={`bg-gradient-to-r ${item.gradient} border-none px-4 py-2 text-white`}
                      >
                        <Clock className="mr-2 h-4 w-4" />
                        {item.time}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>

          <div className="mt-16 text-center">
            <p className="mb-4 text-2xl text-gray-400">これらの悩み、すべて</p>
            <p className="text-4xl font-bold">
              <span className="bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
                15分で解決できます
              </span>
            </p>
          </div>
        </div>
      </section>

      {/* ソリューション+デモセクション */}
      <section className="relative bg-gradient-to-br from-black via-gray-900 to-emerald-900/20 py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-green-500/10" />
        <div className="relative mx-auto max-w-7xl px-6">
          <div className="mb-20 text-center">
            <h2 className="mb-8 text-6xl font-bold">
              <span className="bg-gradient-to-r from-emerald-400 to-green-400 bg-clip-text text-transparent">
                GenieUs
              </span>
              <span className="text-white"> が</span>
              <br />
              <span className="text-white">すべて解決します</span>
            </h2>
            <p className="mx-auto max-w-4xl text-2xl text-gray-300">
              Google ADK技術により、複数の専門エージェントが
              <br />
              <span className="font-semibold text-emerald-400">あなたの育児を革命的にサポート</span>
            </p>
          </div>

          {/* メガデモセクション */}
          <div className="relative mb-20">
            <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-emerald-500/10 to-green-500/10 blur-3xl" />
            <div className="relative rounded-3xl border border-gray-700/50 bg-gray-900/80 p-12 backdrop-blur-xl">
              <div className="mb-12 text-center">
                <h3 className="mb-6 text-4xl font-bold text-white">
                  リアルタイム変化デモンストレーション
                </h3>
                <p className="text-xl text-gray-300">
                  「2歳の夜泣きで困っています」と相談した瞬間の変化
                </p>
              </div>

              <div className="mb-12 grid grid-cols-1 gap-8 lg:grid-cols-3">
                {[
                  {
                    icon: <Clock className="h-12 w-12" />,
                    label: '解決時間',
                    value: currentStats.time,
                    unit: '分',
                    color: 'from-blue-500 to-cyan-500',
                    bgColor: 'from-blue-500/20 to-cyan-500/20',
                    max: 15,
                  },
                  {
                    icon: <Heart className="h-12 w-12" />,
                    label: '不安レベル',
                    value: currentStats.stress,
                    unit: '%',
                    color: 'from-red-500 to-pink-500',
                    bgColor: 'from-red-500/20 to-pink-500/20',
                    max: 100,
                    reverse: true,
                  },
                  {
                    icon: <CheckCircle className="h-12 w-12" />,
                    label: '自信レベル',
                    value: currentStats.confidence,
                    unit: '%',
                    color: 'from-emerald-500 to-green-500',
                    bgColor: 'from-emerald-500/20 to-green-500/20',
                    max: 100,
                  },
                ].map((stat, index) => (
                  <div key={index} className="group relative">
                    <div
                      className={`absolute inset-0 bg-gradient-to-br ${stat.bgColor} rounded-2xl opacity-50 blur-xl transition-all duration-500 group-hover:opacity-70`}
                    />
                    <Card className="relative border border-gray-600/50 bg-gray-800/50 backdrop-blur-xl transition-all duration-500 hover:bg-gray-700/50">
                      <CardContent className="p-8 text-center">
                        <div
                          className={`inline-flex rounded-full bg-gradient-to-br p-4 ${stat.color} mb-6`}
                        >
                          {stat.icon}
                        </div>
                        <div className="mb-3 text-5xl font-bold">
                          <span
                            className={`bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}
                          >
                            {stat.value}
                            {stat.unit}
                          </span>
                        </div>
                        <div className="mb-6 font-medium text-gray-300">{stat.label}</div>

                        {/* プログレスバー */}
                        <div className="h-3 w-full rounded-full bg-gray-700">
                          <div
                            className={`bg-gradient-to-r ${stat.color} relative h-3 overflow-hidden rounded-full transition-all duration-500`}
                            style={{
                              width: `${
                                stat.reverse
                                  ? 100 - (stat.value / stat.max) * 100
                                  : (stat.value / stat.max) * 100
                              }%`,
                            }}
                          >
                            <div className="absolute inset-0 animate-pulse bg-white/30" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ))}
              </div>

              <div className="text-center">
                <Button
                  onClick={startAnimation}
                  disabled={isAnimating}
                  className="group transform rounded-full bg-gradient-to-r from-emerald-600 to-green-600 px-12 py-6 text-xl font-semibold text-white shadow-2xl transition-all duration-500 hover:scale-105 hover:from-emerald-500 hover:to-green-500 hover:shadow-emerald-500/25"
                >
                  <Target className="mr-3 h-6 w-6 transition-transform duration-500 group-hover:rotate-90" />
                  {isAnimating ? '魔法が起きています...' : '革命的変化を体験'}
                </Button>
              </div>
            </div>
          </div>

          {/* VS比較セクション */}
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-2">
            {/* 従来の方法 */}
            <div className="group relative">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-red-500/20 to-pink-500/20 opacity-50 blur-xl transition-all duration-500 group-hover:opacity-70" />
              <Card className="relative h-full border border-red-500/30 bg-gray-900/70 backdrop-blur-xl">
                <CardContent className="p-10">
                  <div className="mb-8 text-center">
                    <div className="mb-6 inline-flex rounded-full bg-gradient-to-br from-red-500 to-pink-500 p-4">
                      <Clock className="h-12 w-12" />
                    </div>
                    <h3 className="mb-4 text-3xl font-bold text-white">従来の方法</h3>
                    <Badge className="border border-red-500/30 bg-red-500/20 px-4 py-2 text-red-300">
                      平均2時間でも解決せず
                    </Badge>
                  </div>

                  <div className="space-y-6">
                    {[
                      'Google検索で情報が散在・混乱',
                      '年齢に合わない情報が混在',
                      '専門医の予約が取れない',
                      '結局、具体的解決策なし',
                      '一人で悩み続ける',
                    ].map((item, idx) => (
                      <div key={idx} className="flex items-center space-x-4">
                        <div className="h-3 w-3 flex-shrink-0 rounded-full bg-red-500" />
                        <p className="text-gray-300">{item}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* GenieUs */}
            <div className="group relative">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-emerald-500/20 to-green-500/20 opacity-50 blur-xl transition-all duration-500 group-hover:opacity-70" />
              <Card className="relative h-full border border-emerald-500/30 bg-gray-900/70 backdrop-blur-xl">
                <CardContent className="p-10">
                  <div className="mb-8 text-center">
                    <div className="mb-6 inline-flex rounded-full bg-gradient-to-br from-emerald-500 to-green-500 p-4">
                      <Sparkles className="h-12 w-12" />
                    </div>
                    <h3 className="mb-4 text-3xl font-bold text-white">GenieUs</h3>
                    <Badge className="border border-emerald-500/30 bg-emerald-500/20 px-4 py-2 text-emerald-300">
                      わずか15分で完全解決
                    </Badge>
                  </div>

                  <div className="space-y-6">
                    {[
                      '年齢・状況に特化したAI分析',
                      '複数専門エージェントが連携',
                      '地域情報も含めた総合提案',
                      '今日から実行できる具体プラン',
                      '24/7いつでも専門サポート',
                    ].map((item, idx) => (
                      <div key={idx} className="flex items-center space-x-4">
                        <CheckCircle className="h-6 w-6 flex-shrink-0 text-emerald-400" />
                        <p className="text-gray-300">{item}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* 技術的優位性 */}
      <section className="relative bg-gradient-to-br from-black via-blue-900/20 to-purple-900/20 py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/10" />
        <div className="relative mx-auto max-w-7xl px-6">
          <div className="mb-20 text-center">
            <h2 className="mb-8 text-6xl font-bold">
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                圧倒的技術力
              </span>
              <br />
              <span className="text-white">による差別化</span>
            </h2>
            <p className="mx-auto max-w-4xl text-2xl text-gray-300">
              他のAIチャットボットとは次元が違う、
              <br />
              <span className="font-semibold text-blue-400">本格的エージェントシステム</span>
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: <Users className="h-12 w-12" />,
                title: 'マルチエージェント',
                desc: '睡眠・栄養・発達の専門エージェントが高度連携',
                gradient: 'from-blue-500 to-cyan-500',
              },
              {
                icon: <Shield className="h-12 w-12" />,
                title: 'Clean Architecture',
                desc: 'エンタープライズ級の堅牢システム設計',
                gradient: 'from-green-500 to-emerald-500',
              },
              {
                icon: <Sparkles className="h-12 w-12" />,
                title: 'Gemini 2.5 Flash',
                desc: '最新大規模言語モデルによる高精度分析',
                gradient: 'from-purple-500 to-pink-500',
              },
              {
                icon: <Lightbulb className="h-12 w-12" />,
                title: '完全パーソナライズ',
                desc: '個人状況に最適化された専門回答',
                gradient: 'from-amber-500 to-orange-500',
              },
            ].map((item, index) => (
              <div key={index} className="group relative">
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${item.gradient} rounded-2xl opacity-10 blur-xl transition-all duration-500 group-hover:opacity-30`}
                />
                <Card className="relative h-full border border-gray-700/50 bg-gray-900/70 backdrop-blur-xl transition-all duration-500 hover:bg-gray-800/70 group-hover:scale-105">
                  <CardContent className="p-8 text-center">
                    <div
                      className={`inline-flex rounded-full bg-gradient-to-br p-4 ${item.gradient} mb-6`}
                    >
                      {item.icon}
                    </div>
                    <h3 className="mb-4 text-xl font-bold text-white">{item.title}</h3>
                    <p className="text-sm leading-relaxed text-gray-300">{item.desc}</p>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>

          {/* 技術仕様 */}
          <div className="mt-20 text-center">
            <div className="mx-auto grid max-w-4xl grid-cols-2 gap-8 md:grid-cols-4">
              {[
                { label: 'Google ADK', value: '1.2.1' },
                { label: 'Gemini', value: '2.5 Flash' },
                { label: 'Response Time', value: '<2s' },
                { label: 'Uptime', value: '99.9%' },
              ].map((spec, index) => (
                <div key={index} className="text-center">
                  <div className="mb-2 text-3xl font-bold text-white">{spec.value}</div>
                  <div className="text-sm text-gray-400">{spec.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 最終CTA */}
      <section className="relative bg-gradient-to-br from-amber-600 via-orange-600 to-yellow-600 py-32">
        <div className="absolute inset-0 bg-black/20" />
        <div className="relative mx-auto max-w-5xl px-6 text-center">
          <h2 className="mb-8 text-6xl font-bold text-white">
            育児革命を
            <br />
            今すぐ体験
          </h2>
          <p className="mx-auto mb-12 max-w-3xl text-2xl text-white/90">
            あなたの育児の不安を、わずか15分で自信に変える。
            <br />
            <span className="font-semibold">GenieUsが子育ての未来を変えます。</span>
          </p>

          <div className="mb-12 flex flex-col justify-center gap-6 sm:flex-row">
            <Button
              onClick={handleStartNow}
              size="lg"
              className="transform rounded-full bg-white px-12 py-6 text-xl font-semibold text-amber-600 shadow-2xl transition-all duration-500 hover:scale-105 hover:bg-gray-100 hover:shadow-white/25"
            >
              <Star className="mr-3 h-6 w-6" />
              今すぐ始める
            </Button>
            <Button
              onClick={startAnimation}
              size="lg"
              variant="outline"
              className="rounded-full border-2 border-white px-12 py-6 text-xl font-semibold text-white backdrop-blur-sm hover:bg-white hover:text-amber-600"
            >
              <Sparkles className="mr-3 h-6 w-6" />
              デモを体験
            </Button>
          </div>

          <div className="text-center text-white/80">
            <p className="mb-4 text-lg">🏆 Zenn AI Agent Hackathon 2025</p>
            <p className="text-sm">Google ADK × Gemini 2.5 Flash powered</p>
          </div>
        </div>
      </section>
    </div>
  )
}
