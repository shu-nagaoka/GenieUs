'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Progress } from '@/components/ui/progress'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Users,
  Brain,
  Heart,
  Moon,
  Apple,
  Baby,
  Shield,
  Briefcase,
  Search,
  X,
  CheckCircle2,
} from 'lucide-react'

interface Agent {
  id: string
  name: string
  description: string
  has_tools: boolean
  confidence_rating: string
}

interface AgentSelectorModalProps {
  isOpen: boolean
  onClose: () => void
  onAgentsSelected: (agents: string[]) => void
  availableAgents?: Agent[]
}

// デフォルトエージェント（APIで取得できない場合のフォールバック）
const DEFAULT_AGENTS: Agent[] = [
  {
    id: 'nutrition_specialist',
    name: '栄養専門家',
    description: '栄養バランス、食事内容、離乳食などの食事に関する専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'sleep_specialist',
    name: '睡眠専門家',
    description: '睡眠リズム、夜泣き対策、寝かしつけなどの睡眠に関する専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'development_specialist',
    name: '発達専門家',
    description: '発達段階、成長マイルストーン、知育などの発達に関する専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'health_specialist',
    name: '健康専門家',
    description: '健康管理、病気対応、予防接種などの健康に関する専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'behavior_specialist',
    name: '行動専門家',
    description: 'しつけ、問題行動、習慣形成などの行動に関する専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'play_learning_specialist',
    name: '遊び・学習専門家',
    description: '遊び方、学習方法、おもちゃ選びなどの遊び・学習に関する専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'safety_specialist',
    name: '安全専門家',
    description: '事故防止、安全対策、危険回避などの安全に関する専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'work_life_specialist',
    name: '仕事両立専門家',
    description: '仕事と育児の両立、時間管理、ストレス対処などの専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'mental_care_specialist',
    name: 'メンタルケア専門家',
    description: '親のメンタルケア、ストレス解消、心理的サポートなどの専門的なアドバイス',
    has_tools: false,
    confidence_rating: '中',
  },
  {
    id: 'search_specialist',
    name: '検索専門家',
    description: '情報検索、地域情報、サービス案内などの調査・検索に関する専門的なサポート',
    has_tools: true,
    confidence_rating: '高',
  },
]

const getAgentIcon = (agentId: string) => {
  const iconMap: Record<string, React.ReactNode> = {
    nutrition_specialist: <Apple className="h-5 w-5" />,
    sleep_specialist: <Moon className="h-5 w-5" />,
    development_specialist: <Baby className="h-5 w-5" />,
    health_specialist: <Heart className="h-5 w-5" />,
    behavior_specialist: <Brain className="h-5 w-5" />,
    play_learning_specialist: <CheckCircle2 className="h-5 w-5" />,
    safety_specialist: <Shield className="h-5 w-5" />,
    work_life_specialist: <Briefcase className="h-5 w-5" />,
    mental_care_specialist: <Heart className="h-5 w-5" />,
    search_specialist: <Search className="h-5 w-5" />,
  }
  return iconMap[agentId] || <Users className="h-5 w-5" />
}

const getConfidenceColor = (rating: string) => {
  switch (rating) {
    case '高':
      return 'bg-emerald-500'
    case '中':
      return 'bg-yellow-500'
    case '低':
      return 'bg-red-500'
    default:
      return 'bg-gray-500'
  }
}

export function AgentSelectorModal({
  isOpen,
  onClose,
  onAgentsSelected,
  availableAgents = DEFAULT_AGENTS,
}: AgentSelectorModalProps) {
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const maxAgents = 3

  // モーダルが開かれたときにリセット
  useEffect(() => {
    if (isOpen) {
      setSelectedAgents([])
    }
  }, [isOpen])

  const handleAgentToggle = (agentId: string) => {
    setSelectedAgents(current => {
      if (current.includes(agentId)) {
        // 選択解除
        return current.filter(id => id !== agentId)
      } else if (current.length < maxAgents) {
        // 選択追加（最大3人まで）
        return [...current, agentId]
      }
      return current
    })
  }

  const handleConfirm = () => {
    if (selectedAgents.length === 0) return
    
    setLoading(true)
    // 少し待機してからコールバック実行（UX向上）
    setTimeout(() => {
      onAgentsSelected(selectedAgents)
      setLoading(false)
      onClose()
    }, 500)
  }

  const handleCancel = () => {
    setSelectedAgents([])
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Users className="h-6 w-6 text-purple-600" />
            マルチエージェント分析モード
          </DialogTitle>
          <DialogDescription className="text-base">
            複数の専門家による協働分析を行います。最大{maxAgents}人の専門家を選択してください。
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* 選択状況 */}
          <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="font-medium">選択中:</span>
              <Badge variant="outline" className="bg-purple-100">
                {selectedAgents.length} / {maxAgents}人
              </Badge>
            </div>
            <Progress 
              value={(selectedAgents.length / maxAgents) * 100} 
              className="w-32"
            />
          </div>

          {/* エージェント一覧 */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableAgents.map(agent => {
              const isSelected = selectedAgents.includes(agent.id)
              const isDisabled = !isSelected && selectedAgents.length >= maxAgents

              return (
                <Card
                  key={agent.id}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                    isSelected
                      ? 'ring-2 ring-purple-500 bg-purple-50'
                      : isDisabled
                      ? 'opacity-50 cursor-not-allowed'
                      : 'hover:border-purple-300'
                  }`}
                  onClick={() => !isDisabled && handleAgentToggle(agent.id)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getAgentIcon(agent.id)}
                        <CardTitle className="text-sm">{agent.name}</CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        {agent.has_tools && (
                          <Badge variant="secondary" className="text-xs">
                            ツール
                          </Badge>
                        )}
                        <Checkbox 
                          checked={isSelected}
                          disabled={isDisabled}
                          className="pointer-events-none"
                        />
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-xs text-gray-600 mb-3">
                      {agent.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">信頼度</span>
                      <div className="flex items-center gap-1">
                        <div
                          className={`h-2 w-8 rounded-full ${getConfidenceColor(
                            agent.confidence_rating
                          )}`}
                        />
                        <span className="text-xs text-gray-600">
                          {agent.confidence_rating}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* 説明 */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">
              📊 マルチエージェント分析について
            </h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• 選択した専門家が同時並列で分析を行います</li>
              <li>• 各専門家の意見が統合されて総合的な回答が生成されます</li>
              <li>• 処理時間は通常より長くなりますが、より詳細な分析が得られます</li>
              <li>• 画像分析・Web検索機能は使用できません</li>
            </ul>
          </div>

          {/* アクションボタン */}
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={handleCancel}
              className="flex-1"
              disabled={loading}
            >
              <X className="mr-2 h-4 w-4" />
              キャンセル
            </Button>
            <Button
              onClick={handleConfirm}
              disabled={selectedAgents.length === 0 || loading}
              className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
            >
              {loading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  設定中...
                </>
              ) : (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  {selectedAgents.length}人の専門家で開始
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}