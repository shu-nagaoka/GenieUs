'use client'

import { GiSparkles } from 'react-icons/gi'
import { AiOutlineBarChart } from 'react-icons/ai'

export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="text-center">
        <div className="relative">
          <AiOutlineBarChart className="h-16 w-16 text-teal-500 animate-bounce mx-auto" />
          <GiSparkles className="absolute -top-2 -right-2 h-6 w-6 text-yellow-400 animate-pulse" />
        </div>
        
        <p className="mt-6 text-lg font-medium text-amber-700 animate-pulse">
          成長データを分析中...
        </p>
      </div>
    </div>
  )
}