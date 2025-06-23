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
  onMinimize 
}: MultiAgentOrchestrationFullscreenProps) {
  if (!isActive) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative max-w-4xl w-full"
        >
          {/* Close button */}
          {onMinimize && (
            <button
              onClick={onMinimize}
              className="absolute -top-12 right-0 p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
            >
              <X className="h-6 w-6 text-white" />
            </button>
          )}

          {/* Orchestration component */}
          <div className="transform scale-110">
            <MultiAgentOrchestration
              isActive={isActive}
              userQuery={userQuery}
              onComplete={onComplete}
            />
          </div>

          {/* Additional effects */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-0 bg-gradient-to-t from-amber-500/20 to-transparent animate-pulse" />
          </div>

          {/* User query display */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-6 text-center"
          >
            <p className="text-white/60 text-sm">あなたの質問</p>
            <p className="text-white text-lg font-medium mt-1">&ldquo;{userQuery}&rdquo;</p>
          </motion.div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}