'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { MultiAgentOrchestration } from './multi-agent-orchestration'

interface MultiAgentOrchestrationFullscreenProps {
  isActive: boolean
  userQuery: string
  onComplete?: () => void
  onMinimize?: () => void
}

export function MultiAgentOrchestrationFullscreen({
  isActive,
  userQuery,
  onComplete,
  onMinimize,
}: MultiAgentOrchestrationFullscreenProps) {
  if (!isActive) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-4xl"
        >
          {/* Close button */}
          {onMinimize && (
            <button
              onClick={onMinimize}
              className="absolute -top-12 right-0 rounded-full bg-white/20 p-2 transition-colors hover:bg-white/30"
            >
              <X className="h-6 w-6 text-white" />
            </button>
          )}

          {/* Orchestration component */}
          <div className="scale-110 transform">
            <MultiAgentOrchestration
              isActive={isActive}
              userQuery={userQuery}
              onComplete={onComplete}
            />
          </div>

          {/* Additional effects */}
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute inset-0 animate-pulse bg-gradient-to-t from-amber-500/20 to-transparent" />
          </div>

          {/* User query display */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-6 text-center"
          >
            <p className="text-sm text-white/60">あなたの質問</p>
            <p className="mt-1 text-lg font-medium text-white">&ldquo;{userQuery}&rdquo;</p>
          </motion.div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
