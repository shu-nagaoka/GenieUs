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
  className = '',
}: FollowupQuestionsProps) {
  if (questions.length === 0) {
    return null
  }

  return (
    <div className={`rounded-md border border-gray-200/60 bg-gray-50/50 p-2.5 ${className}`}>
      <div className="mb-2 flex items-center gap-1.5">
        <IoSparkles className="h-2.5 w-2.5 text-gray-400" />
        <span className="text-xs text-gray-500">続けて相談する</span>
      </div>
      <div className="grid grid-cols-3 gap-1.5">
        {questions.slice(0, 3).map((question, index) => (
          <Button
            key={index}
            variant="ghost"
            size="sm"
            className="h-auto justify-start rounded border border-gray-200/80 bg-white/70 px-3 py-2 text-left text-sm text-gray-600 transition-all duration-150 hover:border-gray-300 hover:bg-gray-100/80 hover:text-gray-700"
            onClick={() => onQuestionClick(question)}
          >
            <span className="truncate text-sm leading-relaxed">{question}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}
