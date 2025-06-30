'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/libs/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import {
  AiOutlineHome,
  AiOutlineMessage,
  AiOutlineCalendar,
  AiOutlineBarChart,
  AiOutlineLeft,
  AiOutlineRight,
  AiOutlineMenu,
  AiOutlineUser,
} from 'react-icons/ai'
import { FaBookOpen, FaHeart, FaMicrophone, FaUtensils } from 'react-icons/fa'
import { GiMagicLamp } from 'react-icons/gi'
import {
  HiOutlineSparkles,
  HiOutlineDocumentText,
  HiOutlineCog6Tooth,
  HiOutlineUsers,
} from 'react-icons/hi2'
import { UserProfile } from '@/components/features/auth/auth-check'
import { signOut } from 'next-auth/react'

const mainNavigation = [
  { name: 'ホーム', href: '/dashboard', icon: AiOutlineHome },
  { name: 'Genieと話す', href: '/chat', icon: GiMagicLamp, badge: 'AI Agent' },
  { name: 'GenieUs Agents', href: '/agents', icon: HiOutlineSparkles, badge: '15人の' },
]

const recordNavigation = [
  // { name: '撮影したメモリー', href: '/records', icon: FaBookOpen }, // 一時的に非表示
  { name: '記録した成長', href: '/tracking', icon: AiOutlineBarChart },
  { name: '食事記録', href: '/meal-records', icon: FaUtensils, badge: 'New' },
  { name: '立てた予定', href: '/schedule', icon: AiOutlineCalendar },
  { name: '頑張った軌跡', href: '/effort-report', icon: FaHeart },
]

const familyNavigation = [{ name: '家族情報', href: '/family', icon: HiOutlineUsers }]

function SidebarContent({ isCollapsed = false }: { isCollapsed?: boolean }) {
  const pathname = usePathname()

  return (
    <div className="flex h-screen flex-col border-r border-gray-200 bg-white">
      {/* ヘッダー */}
      <div
        className={cn(
          'flex items-center transition-all duration-300',
          isCollapsed ? 'justify-center p-4' : 'gap-3 p-6'
        )}
      >
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-400">
          <GiMagicLamp className="h-5 w-5 text-white" />
        </div>
        {!isCollapsed && (
          <Link href="/" className="ml-2 flex-1">
            <div className="cursor-pointer transition-opacity hover:opacity-80">
              <h2 className="font-heading text-xl font-semibold text-amber-800">GenieUs</h2>
              <p className="text-sm text-amber-600">Family Magic Lamp</p>
            </div>
          </Link>
        )}
      </div>

      {/* メインナビゲーション */}
      <div className="flex-1 p-4">
        <div className="space-y-1">
          {!isCollapsed && (
            <h3 className="mb-3 text-xs font-medium uppercase tracking-wider text-gray-500">
              メイン機能
            </h3>
          )}
          {mainNavigation.map(item => {
            const isActive = pathname === item.href
            return (
              <Button
                key={item.name}
                variant={isActive ? 'secondary' : 'ghost'}
                className={cn(
                  'h-10 w-full transition-all duration-300',
                  isCollapsed ? 'justify-center px-2' : 'justify-start gap-3',
                  isActive && 'bg-amber-100 text-amber-900 hover:bg-amber-100'
                )}
                asChild
                title={isCollapsed ? item.name : undefined}
              >
                <Link href={item.href}>
                  <item.icon className="h-4 w-4" />
                  {!isCollapsed && (
                    <>
                      <span>{item.name}</span>
                      {item.badge && (
                        <Badge className="ml-auto min-w-0 flex-shrink-0 border-0 bg-gradient-to-r from-blue-500 to-indigo-600 px-1.5 py-0.5 text-xs text-white shadow-sm transition-all duration-500 ease-in-out hover:scale-105 hover:from-blue-600 hover:to-purple-600 hover:shadow-lg hover:shadow-blue-300/50">
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}
                </Link>
              </Button>
            )
          })}
        </div>

        <Separator className="my-4" />

        {/* 記録機能セクション */}
        <div className="space-y-1">
          {!isCollapsed && (
            <h3 className="mb-3 text-xs font-medium uppercase tracking-wider text-gray-500">
              Genieといっしょに
            </h3>
          )}
          {recordNavigation.map(item => {
            const isActive = pathname === item.href
            return (
              <Button
                key={item.name}
                variant={isActive ? 'secondary' : 'ghost'}
                className={cn(
                  'h-10 w-full transition-all duration-300',
                  isCollapsed ? 'justify-center px-2' : 'justify-start gap-3',
                  isActive && 'bg-amber-100 text-amber-900 hover:bg-amber-100'
                )}
                asChild
                title={isCollapsed ? item.name : undefined}
              >
                <Link href={item.href}>
                  <item.icon
                    className={cn(
                      'h-4 w-4',
                      item.name === '撮影したメモリー' && 'text-blue-500',
                      item.name === '見守った成長' && 'text-teal-500',
                      item.name === '食事管理' && 'text-orange-500',
                      item.name === '予定を立てたこと' && 'text-cyan-600',
                      item.name === 'がんばったこと' && 'text-emerald-800'
                    )}
                  />
                  {!isCollapsed && (
                    <>
                      <span>{item.name}</span>
                      {item.badge && (
                        <Badge className="ml-auto min-w-0 flex-shrink-0 border-0 bg-gradient-to-r from-green-500 to-emerald-600 px-1.5 py-0.5 text-xs text-white shadow-sm transition-all duration-500 ease-in-out hover:scale-105 hover:from-green-600 hover:to-emerald-700 hover:shadow-lg hover:shadow-green-300/50">
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}
                </Link>
              </Button>
            )
          })}
        </div>

        <Separator className="my-4" />

        {/* 家族情報セクション */}
        <div className="space-y-1">
          {!isCollapsed && (
            <h3 className="mb-3 text-xs font-medium uppercase tracking-wider text-gray-500">
              家族
            </h3>
          )}
          {familyNavigation.map(item => {
            const isActive = pathname === item.href
            return (
              <Button
                key={item.name}
                variant={isActive ? 'secondary' : 'ghost'}
                className={cn(
                  'h-10 w-full transition-all duration-300',
                  isCollapsed ? 'justify-center px-2' : 'justify-start gap-3',
                  isActive && 'bg-amber-100 text-amber-900 hover:bg-amber-100'
                )}
                asChild
                title={isCollapsed ? item.name : undefined}
              >
                <Link href={item.href}>
                  <item.icon className="h-4 w-4" />
                  {!isCollapsed && (
                    <>
                      <span>{item.name}</span>
                      {item.badge && (
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}
                </Link>
              </Button>
            )
          })}
        </div>
      </div>

      {/* ユーザープロフィール - 固定表示 */}
      <div className="mt-auto border-t border-gray-200 p-4">
        {!isCollapsed ? (
          <UserProfile />
        ) : (
          <div className="flex justify-center">
            <UserProfile />
          </div>
        )}
      </div>
    </div>
  )
}

interface SidebarProps {
  onToggle?: (collapsed: boolean) => void
}

export function Sidebar({ onToggle }: SidebarProps = {}) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const handleToggle = () => {
    const newCollapsed = !isCollapsed
    setIsCollapsed(newCollapsed)
    onToggle?.(newCollapsed)
  }

  return (
    <>
      {/* デスクトップ用サイドバー */}
      <div
        className={cn(
          'hidden md:fixed md:inset-y-0 md:flex md:flex-col md:transition-all md:duration-300',
          isCollapsed ? 'md:w-16' : 'md:w-64'
        )}
      >
        <SidebarContent isCollapsed={isCollapsed} />

        {/* 折り畳みボタン */}
        <Button
          variant="ghost"
          size="sm"
          className="absolute -right-3 top-1/2 h-6 w-6 -translate-y-1/2 rounded-full border border-gray-200 bg-white opacity-60 shadow-sm transition-all hover:bg-gray-50 hover:opacity-100"
          onClick={handleToggle}
        >
          {isCollapsed ? (
            <AiOutlineRight className="h-3 w-3 text-gray-500" />
          ) : (
            <AiOutlineLeft className="h-3 w-3 text-gray-500" />
          )}
        </Button>
      </div>

      {/* モバイル用サイドバー */}
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="sm" className="fixed left-4 top-4 z-50 md:hidden">
            <AiOutlineMenu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <SidebarContent />
        </SheetContent>
      </Sheet>
    </>
  )
}
