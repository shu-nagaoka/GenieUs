'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { IoSparkles } from 'react-icons/io5'

interface FollowupQuestionsProps {
  questions: string[]
  onQuestionClick: (question: string) => void
  className?: string
}

export function FollowupQuestions({
  questions,
  onQuestionClick,
  className = ""
}: FollowupQuestionsProps) {
  if (questions.length === 0) {
    return null
  }

  return (
    <div className={`bg-gray-50/50 border border-gray-200/60 rounded-md p-2.5 ${className}`}>
      <div className="flex items-center gap-1.5 mb-2">
        <IoSparkles className="h-2.5 w-2.5 text-gray-400" />
        <span className="text-xs text-gray-500">続けて相談する</span>
      </div>
      <div className="grid grid-cols-3 gap-1.5">
        {questions.slice(0, 3).map((question, index) => (
          <Button
            key={index}
            variant="ghost"
            size="sm"
            className="h-auto py-2 px-3 text-sm bg-white/70 hover:bg-gray-100/80 border border-gray-200/80 hover:border-gray-300 text-gray-600 hover:text-gray-700 rounded text-left justify-start transition-all duration-150"
            onClick={() => onQuestionClick(question)}
          >
            <span className="text-sm leading-relaxed truncate">{question}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}