'use client'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { User, Settings, LogOut } from 'lucide-react'

interface AppHeaderProps {
  title?: string
  showSidebarTrigger?: boolean
}

export function AppHeader({ title = 'Linx Chat', showSidebarTrigger = true }: AppHeaderProps) {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b bg-green-50 px-4">
      <div className="flex items-center gap-2">
        {showSidebarTrigger && <SidebarTrigger className="-ml-1" />}
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded bg-primary">
            <span className="text-sm font-bold text-primary-foreground">L</span>
          </div>
          <h1 className="text-xl font-semibold">{title}</h1>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon">
          <Settings className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon">
          <Avatar className="h-8 w-8">
            <AvatarFallback>
              <User className="h-4 w-4" />
            </AvatarFallback>
          </Avatar>
        </Button>
        <Button variant="ghost" size="icon">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}
