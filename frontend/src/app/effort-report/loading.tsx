'use client'

import { GiSparkles } from 'react-icons/gi'
import { FaHeart } from 'react-icons/fa'

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="text-center">
        <div className="relative">
          <FaHeart className="mx-auto h-16 w-16 animate-pulse text-emerald-800" />
          <GiSparkles className="absolute -right-2 -top-2 h-6 w-6 animate-pulse text-yellow-400" />
        </div>

        <p className="mt-6 animate-pulse text-lg font-medium text-amber-700">努力を集計中...</p>
      </div>
    </div>
  )
}
