'use client'

import { useState, useEffect } from 'react'
import { Sidebar } from './sidebar'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  useEffect(() => {
    const handleSidebarToggle = (event: CustomEvent) => {
      setIsCollapsed(event.detail.isCollapsed)
    }

    window.addEventListener('sidebarToggle', handleSidebarToggle as EventListener)

    return () => {
      window.removeEventListener('sidebarToggle', handleSidebarToggle as EventListener)
    }
  }, [])

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
      <Sidebar onToggle={setIsCollapsed} />

      <main
        className={`flex-1 transition-all duration-300 ${isCollapsed ? 'md:ml-16' : 'md:ml-64'}`}
      >
        {children}
      </main>
    </div>
  )
}
