'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, Brain, CheckCircle, Clock } from 'lucide-react'

interface MultiAgentOrchestrationProps {
  isActive: boolean
  userQuery: string
  agentInfo?: any
  onComplete?: () => void
}

export function MultiAgentOrchestration({
  isActive,
  userQuery,
  agentInfo,
}: MultiAgentOrchestrationProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<number[]>([])

  // エージェント情報に基づいて動的にステップを生成
  const generateSteps = () => {
    const baseSteps = [
      {
        id: 'analyzing',
        text: 'ユーザーの質問を分析中...',
        icon: <Brain className="h-4 w-4" />,
        duration: 1500,
      },
    ]

    if (agentInfo?.agents && agentInfo.agents.length > 0) {
      // 実際のエージェント情報に基づくステップ
      const agentNames = agentInfo.agents.map((agent: any) => agent.name).join('、')
      baseSteps.push({
        id: 'agents',
        text: `${agentNames}が協調分析中...`,
        icon: <Clock className="h-4 w-4" />,
        duration: 2500,
      })

      // ツールが含まれている場合
      const hasSearchTools = agentInfo.agents.some(
        (agent: any) => agent.tools && agent.tools.some((tool: string) => tool.includes('search'))
      )

      if (hasSearchTools) {
        baseSteps.push({
          id: 'searching',
          text: '最新情報を検索中...',
          icon: <Search className="h-4 w-4" />,
          duration: 2000,
        })
      }
    } else {
      // フォールバック用の汎用ステップ
      baseSteps.push(
        {
          id: 'searching',
          text: '専門知識を検索中...',
          icon: <Search className="h-4 w-4" />,
          duration: 2000,
        },
        {
          id: 'consulting',
          text: '専門エージェントと相談中...',
          icon: <Clock className="h-4 w-4" />,
          duration: 2500,
        }
      )
    }

    baseSteps.push({
      id: 'generating',
      text: '回答を生成中...',
      icon: <Brain className="h-4 w-4" />,
      duration: 2000,
    })

    return baseSteps
  }

  const steps = generateSteps()

  useEffect(() => {
    if (!isActive) {
      setCurrentStep(0)
      setCompletedSteps([])
      return
    }

    let totalTime = 0
    const timers: NodeJS.Timeout[] = []

    steps.forEach((step, index) => {
      // Start the step
      const startTimer = setTimeout(() => {
        setCurrentStep(index)
      }, totalTime)
      timers.push(startTimer)

      // Complete the step
      const completeTimer = setTimeout(() => {
        setCompletedSteps(prev => [...prev, index])

        // If this is the last step, restart the cycle
        if (index === steps.length - 1 && isActive) {
          setTimeout(() => {
            setCurrentStep(0)
            setCompletedSteps([])
            // This will trigger the effect again and restart the cycle
          }, 500)
        }
      }, totalTime + step.duration)
      timers.push(completeTimer)

      totalTime += step.duration
    })

    return () => {
      timers.forEach(timer => clearTimeout(timer))
    }
  }, [isActive, currentStep === 0 && completedSteps.length === 0]) // Restart when cycle completes

  if (!isActive) return null

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-gray-50 p-4">
      {/* エージェント情報表示（デバッグ用） */}
      {agentInfo && (
        <div className="mb-2 text-xs text-gray-500">
          <span className="font-medium">{agentInfo.agent_type}</span>
          {agentInfo.agents && agentInfo.agents.length > 0 && (
            <span> • {agentInfo.agents.length}個のエージェントが協調中</span>
          )}
        </div>
      )}
      {steps.map((step, index) => {
        const isActive = currentStep === index
        const isCompleted = completedSteps.includes(index)
        const isPending = index > currentStep

        return (
          <motion.div
            key={step.id}
            initial={{ opacity: 0.3 }}
            animate={{
              opacity: isActive ? 1 : isCompleted ? 0.7 : 0.3,
            }}
            className="flex items-center gap-3"
          >
            {/* Status Icon */}
            <div
              className={`flex h-6 w-6 items-center justify-center rounded-full ${
                isCompleted
                  ? 'bg-green-100 text-green-600'
                  : isActive
                    ? 'bg-blue-100 text-blue-600'
                    : 'bg-gray-100 text-gray-400'
              } `}
            >
              {isCompleted ? (
                <CheckCircle className="h-4 w-4" />
              ) : isActive ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  {step.icon}
                </motion.div>
              ) : (
                step.icon
              )}
            </div>

            {/* Step Text */}
            <span
              className={`text-sm font-medium ${isActive ? 'text-gray-900' : 'text-gray-500'} `}
            >
              {step.text}
            </span>

            {/* Loading Dots for Active Step */}
            {isActive && (
              <div className="ml-auto flex gap-1">
                <motion.div
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  className="h-1 w-1 rounded-full bg-blue-500"
                />
                <motion.div
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  className="h-1 w-1 rounded-full bg-blue-500"
                />
                <motion.div
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  className="h-1 w-1 rounded-full bg-blue-500"
                />
              </div>
            )}
          </motion.div>
        )
      })}
    </div>
  )
}
