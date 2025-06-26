'use client'

import { signOut } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'

interface LogoutButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  showIcon?: boolean
}

export function LogoutButton({ 
  variant = 'ghost', 
  size = 'sm', 
  showIcon = true 
}: LogoutButtonProps) {
  const handleLogout = () => {
    signOut({ callbackUrl: '/' })
  }

  return (
    <Button
      onClick={handleLogout}
      variant={variant}
      size={size}
      className="flex items-center gap-2"
    >
      {showIcon && <LogOut className="h-4 w-4" />}
      ログアウト
    </Button>
  )
}