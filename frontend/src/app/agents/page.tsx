'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { FiUsers, FiZap, FiStar, FiCheck, FiArrowRight } from 'react-icons/fi'
import { HiOutlineSparkles, HiOutlineChatBubbleLeftEllipsis } from 'react-icons/hi2'
import { GiMagicLamp, GiSparkles } from 'react-icons/gi'
import Link from 'next/link'
import { getAgents, Agent } from '@/libs/api/agents'

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [activeCount, setActiveCount] = useState(0)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      setLoading(true)
      const result = await getAgents()
      if (result.success && result.data) {
        setAgents(result.data)
        setActiveCount(result.data.filter(agent => agent.status === 'active').length)
      }
    } catch (error) {
      console.error('エージェント読み込みエラー:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
          <div className="inline-flex items-center gap-3">
            <div className="border-3 h-8 w-8 animate-spin rounded-full border-orange-500 border-t-transparent"></div>
            <span className="text-lg text-gray-600">エージェント情報を読み込み中...</span>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
        {/* ページヘッダー */}
        <div className="border-b border-orange-200 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500">
          <div className="container mx-auto px-6 py-12">
            <div className="text-center">
              <div className="mb-6 flex justify-center">
                <div className="relative">
                  <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/20 shadow-xl backdrop-blur-sm">
                    <HiOutlineSparkles className="h-10 w-10 text-white" />
                  </div>
                  <GiSparkles className="absolute -right-2 -top-2 h-8 w-8 text-yellow-300" />
                </div>
              </div>

              <h1 className="mb-4 text-4xl font-bold text-white md:text-5xl">GenieUs Agents</h1>
              <p className="mx-auto mb-6 max-w-3xl text-xl text-white/90">
                あらゆる子育ての場面で、専門性を持った{activeCount}人のAgentsがあなたをサポート
              </p>

              <div className="mx-auto max-w-4xl rounded-2xl bg-white/20 p-6 backdrop-blur-sm">
                <div className="grid grid-cols-1 gap-6 text-center md:grid-cols-3">
                  <div>
                    <div className="mb-2 text-3xl font-bold text-white">{activeCount}人</div>
                    <div className="text-sm text-white/80">アクティブAgents</div>
                  </div>
                  <div>
                    <div className="mb-2 text-3xl font-bold text-white">24/7</div>
                    <div className="text-sm text-white/80">いつでも対応可能</div>
                  </div>
                  <div>
                    <div className="mb-2 text-3xl font-bold text-white">∞</div>
                    <div className="text-sm text-white/80">専門知識の深さ</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-6 py-12">
          {/* エージェント紹介 */}
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-gray-800">あなたの子育てパートナー</h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              それぞれが独自の専門性を持ち、連携してあなたの育児をトータルサポートします
            </p>
          </div>

          {/* エージェントカード一覧 */}
          <div className="mb-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {agents.map(agent => (
              <Card
                key={agent.id}
                className="group overflow-hidden border-0 bg-white/80 shadow-lg backdrop-blur-sm"
              >
                <CardHeader className={`bg-gradient-to-r ${agent.color} relative text-white`}>
                  <div className="absolute right-2 top-2">
                    <Badge variant="secondary" className="border-0 bg-white/20 text-white">
                      専門Agent
                    </Badge>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="rounded-full bg-white/20 p-3 text-4xl backdrop-blur-sm">
                      {agent.icon}
                    </div>
                    <div>
                      <CardTitle className="text-lg font-bold text-white">{agent.name}</CardTitle>
                      <div className="mt-1 flex items-center gap-1">
                        <FiCheck className="h-3 w-3" />
                        <span className="text-xs text-white/90">オンライン</span>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="p-6">
                  <p className="mb-4 text-sm leading-relaxed text-gray-700">{agent.description}</p>

                  <div className="mb-4">
                    <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-gray-800">
                      <FiStar className="h-4 w-4" />
                      専門分野
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {agent.specialties.slice(0, 3).map((specialty, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className="border-gray-300 text-xs text-gray-600"
                        >
                          {specialty}
                        </Badge>
                      ))}
                      {agent.specialties.length > 3 && (
                        <Badge variant="outline" className="border-gray-300 text-xs text-gray-500">
                          +{agent.specialties.length - 3}つ
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="mb-4">
                    <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-gray-800">
                      <FiZap className="h-4 w-4" />
                      主な機能
                    </h4>
                    <div className="space-y-1">
                      {agent.capabilities.slice(0, 2).map((capability, index) => (
                        <div key={index} className="flex items-center gap-2 text-xs text-gray-600">
                          <div className="h-1 w-1 rounded-full bg-gray-400"></div>
                          {capability}
                        </div>
                      ))}
                    </div>
                  </div>

                  <Link href="/chat" className="block">
                    <Button
                      className={`w-full bg-gradient-to-r ${agent.color} border-0 text-white hover:opacity-90`}
                      size="sm"
                    >
                      <HiOutlineChatBubbleLeftEllipsis className="mr-2 h-4 w-4" />
                      相談してみる
                      <FiArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* CTA */}
          <div className="rounded-2xl border border-orange-200 bg-gradient-to-r from-amber-50 to-orange-50 p-8 text-center">
            <h3 className="mb-4 text-2xl font-bold text-gray-800">
              すべてのAgentsと話してみませんか？
            </h3>
            <p className="mx-auto mb-6 max-w-2xl text-gray-600">
              GenieUsでは、これらの専門Agentsが自動的に連携して、あなたの相談内容に最適な回答を提供します。
              まずは気軽に話しかけてみてください。
            </p>

            <div className="flex justify-center gap-4">
              <Link href="/chat">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-amber-500 to-orange-500 px-8 py-4 text-lg font-bold text-white shadow-xl hover:from-amber-600 hover:to-orange-600"
                >
                  <GiMagicLamp className="mr-3 h-6 w-6" />
                  GenieUsと話してみる
                  <GiSparkles className="ml-3 h-5 w-5" />
                </Button>
              </Link>

              <Link href="/dashboard">
                <Button
                  variant="outline"
                  size="lg"
                  className="border-orange-300 px-8 py-4 text-lg font-medium text-orange-700 hover:bg-orange-50"
                >
                  <FiUsers className="mr-2 h-5 w-5" />
                  ホームに戻る
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
