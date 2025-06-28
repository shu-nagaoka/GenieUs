'use client'

import { GiSparkles } from 'react-icons/gi'
import { FaBookOpen } from 'react-icons/fa'

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="text-center">
        <div className="relative">
          <FaBookOpen className="mx-auto h-16 w-16 animate-bounce text-blue-500" />
          <GiSparkles className="absolute -right-2 -top-2 h-6 w-6 animate-pulse text-yellow-400" />
        </div>

        <p className="mt-6 animate-pulse text-lg font-medium text-amber-700">
          メモリーを取り出し中...
        </p>
      </div>
    </div>
  )
}
