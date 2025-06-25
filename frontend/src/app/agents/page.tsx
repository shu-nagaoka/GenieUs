'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  FiUsers,
  FiZap,
  FiStar,
  FiHeart,
  FiCheck,
  FiArrowRight
} from 'react-icons/fi'
import { 
  HiOutlineSparkles,
  HiOutlineChatBubbleLeftEllipsis
} from 'react-icons/hi2'
import { GiMagicLamp, GiSparkles } from 'react-icons/gi'
import Link from 'next/link'
import { getAgents, Agent } from '@/lib/api/agents'

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
        <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 flex items-center justify-center">
          <div className="inline-flex items-center gap-3">
            <div className="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
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
        <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 border-b border-orange-200">
          <div className="container mx-auto px-6 py-12">
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="relative">
                  <div className="h-20 w-20 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-xl">
                    <HiOutlineSparkles className="h-10 w-10 text-white" />
                  </div>
                  <GiSparkles className="absolute -top-2 -right-2 h-8 w-8 text-yellow-300 animate-pulse" />
                </div>
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                GenieUs Agents
              </h1>
              <p className="text-xl text-white/90 mb-6 max-w-3xl mx-auto">
                あらゆる子育ての場面で、専門性を持った{activeCount}人のAgentsがあなたをサポート
              </p>
              
              <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-6 max-w-4xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                  <div>
                    <div className="text-3xl font-bold text-white mb-2">{activeCount}人</div>
                    <div className="text-white/80 text-sm">アクティブAgents</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-white mb-2">24/7</div>
                    <div className="text-white/80 text-sm">いつでも対応可能</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-white mb-2">∞</div>
                    <div className="text-white/80 text-sm">専門知識の深さ</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-6 py-12">
          {/* エージェント紹介 */}
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">あなたの子育てパートナー</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              それぞれが独自の専門性を持ち、連携してあなたの育児をトータルサポートします
            </p>
          </div>

          {/* エージェントカード一覧 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {agents.map((agent) => (
              <Card 
                key={agent.id} 
                className="group hover:shadow-xl transition-all duration-300 hover:scale-105 border-0 shadow-lg bg-white/80 backdrop-blur-sm overflow-hidden"
              >
                <CardHeader className={`bg-gradient-to-r ${agent.color} text-white relative`}>
                  <div className="absolute top-2 right-2">
                    <Badge variant="secondary" className="bg-white/20 text-white border-0">
                      専門Agent
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <div className="text-4xl bg-white/20 rounded-full p-3 backdrop-blur-sm">
                      {agent.icon}
                    </div>
                    <div>
                      <CardTitle className="text-white text-lg font-bold">
                        {agent.name}
                      </CardTitle>
                      <div className="flex items-center gap-1 mt-1">
                        <FiCheck className="h-3 w-3" />
                        <span className="text-xs text-white/90">オンライン</span>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="p-6">
                  <p className="text-gray-700 text-sm mb-4 leading-relaxed">
                    {agent.description}
                  </p>
                  
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <FiStar className="h-4 w-4" />
                      専門分野
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {agent.specialties.slice(0, 3).map((specialty, index) => (
                        <Badge key={index} variant="outline" className="text-xs text-gray-600 border-gray-300">
                          {specialty}
                        </Badge>
                      ))}
                      {agent.specialties.length > 3 && (
                        <Badge variant="outline" className="text-xs text-gray-500 border-gray-300">
                          +{agent.specialties.length - 3}つ
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <FiZap className="h-4 w-4" />
                      主な機能
                    </h4>
                    <div className="space-y-1">
                      {agent.capabilities.slice(0, 2).map((capability, index) => (
                        <div key={index} className="flex items-center gap-2 text-xs text-gray-600">
                          <div className="w-1 h-1 rounded-full bg-gray-400"></div>
                          {capability}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <Link href="/chat" className="block">
                    <Button 
                      className={`w-full bg-gradient-to-r ${agent.color} hover:opacity-90 text-white border-0 group-hover:shadow-lg transition-all duration-300`}
                      size="sm"
                    >
                      <HiOutlineChatBubbleLeftEllipsis className="h-4 w-4 mr-2" />
                      相談してみる
                      <FiArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* CTA */}
          <div className="text-center bg-gradient-to-r from-amber-50 to-orange-50 p-8 rounded-2xl border border-orange-200">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">
              すべてのAgentsと話してみませんか？
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              GenieUsでは、これらの専門Agentsが自動的に連携して、あなたの相談内容に最適な回答を提供します。
              まずは気軽に話しかけてみてください。
            </p>
            
            <div className="flex justify-center gap-4">
              <Link href="/chat">
                <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white px-8 py-4 text-lg font-bold shadow-xl hover:shadow-2xl transition-all duration-300">
                  <GiMagicLamp className="h-6 w-6 mr-3" />
                  GenieUsと話してみる
                  <GiSparkles className="h-5 w-5 ml-3 animate-pulse" />
                </Button>
              </Link>
              
              <Link href="/dashboard">
                <Button variant="outline" size="lg" className="border-orange-300 text-orange-700 hover:bg-orange-50 px-8 py-4 text-lg font-medium">
                  <FiUsers className="h-5 w-5 mr-2" />
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