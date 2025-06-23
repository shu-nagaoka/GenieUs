'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
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
  AiOutlineSetting,
  AiOutlineBell,
  AiOutlinePlus,
  AiOutlineLeft,
  AiOutlineRight,
  AiOutlineMenu,
  AiOutlineUser
} from 'react-icons/ai'
import {
  FaBookOpen,
  FaHeart,
  FaMicrophone
} from 'react-icons/fa'
import { GiMagicLamp } from 'react-icons/gi'
import {
  HiOutlineSparkles,
  HiOutlineDocumentText,
  HiOutlineCog6Tooth,
  HiOutlineUsers
} from 'react-icons/hi2'

const mainNavigation = [
  { name: 'ホーム', href: '/dashboard', icon: AiOutlineHome },
  { name: 'Genieと話す', href: '/chat', icon: GiMagicLamp, badge: 'AI Agent' },
]

const recordNavigation = [
  { name: 'がんばったこと', href: '/effort-report', icon: FaHeart },
  { name: '予定を立てたこと', href: '/schedule', icon: AiOutlineCalendar },
  { name: '見守った成長', href: '/tracking', icon: AiOutlineBarChart },
  { name: '撮影したメモリー', href: '/records', icon: FaBookOpen },
]

const familyNavigation = [
  { name: '家族情報', href: '/family', icon: HiOutlineUsers },
]

const systemNavigation = [
  { name: '通知', href: '/notifications', icon: AiOutlineBell, badge: '3' },
  { name: '設定', href: '/settings', icon: HiOutlineCog6Tooth },
]

function SidebarContent({ isCollapsed = false }: { isCollapsed?: boolean }) {
  const pathname = usePathname()

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200">
      {/* ヘッダー */}
      <div className={cn(
        "flex items-center transition-all duration-300",
        isCollapsed ? "p-4 justify-center" : "gap-3 p-6"
      )}>
        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center">
          <GiMagicLamp className="h-5 w-5 text-white" />
        </div>
        {!isCollapsed && (
          <Link href="/" className="flex-1 ml-2">
            <div className="cursor-pointer hover:opacity-80 transition-opacity">
              <h2 className="font-heading font-semibold text-amber-800 text-xl">GenieUs</h2>
              <p className="text-sm text-amber-600">Family Magic Lamp</p>
            </div>
          </Link>
        )}
      </div>

      {/* メインナビゲーション */}
      <div className="flex-1 p-4">
        <div className="space-y-1">
          {!isCollapsed && (
            <h3 className="mb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
              メイン機能
            </h3>
          )}
          {mainNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Button
                key={item.name}
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full h-10 transition-all duration-300",
                  isCollapsed ? "justify-center px-2" : "justify-start gap-3",
                  isActive && "bg-amber-100 text-amber-900 hover:bg-amber-100"
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
                        <Badge className="ml-auto text-xs px-1.5 py-0.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white border-0 hover:scale-105 hover:from-blue-600 hover:to-purple-600 transition-all duration-500 ease-in-out min-w-0 flex-shrink-0 shadow-sm hover:shadow-lg hover:shadow-blue-300/50">
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
            <h3 className="mb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
              Genieといっしょに
            </h3>
          )}
          {recordNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Button
                key={item.name}
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full h-10 transition-all duration-300",
                  isCollapsed ? "justify-center px-2" : "justify-start gap-3",
                  isActive && "bg-amber-100 text-amber-900 hover:bg-amber-100"
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

        <Separator className="my-4" />

        {/* 家族情報セクション */}
        <div className="space-y-1">
          {!isCollapsed && (
            <h3 className="mb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
              家族
            </h3>
          )}
          {familyNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Button
                key={item.name}
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full h-10 transition-all duration-300",
                  isCollapsed ? "justify-center px-2" : "justify-start gap-3",
                  isActive && "bg-amber-100 text-amber-900 hover:bg-amber-100"
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

        <Separator className="my-4" />

        {/* システム機能セクション */}
        <div className="space-y-1">
          {!isCollapsed && (
            <h3 className="mb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
              システム
            </h3>
          )}
          {systemNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Button
                key={item.name}
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full h-10 transition-all duration-300",
                  isCollapsed ? "justify-center px-2" : "justify-start gap-3",
                  isActive && "bg-amber-100 text-amber-900 hover:bg-amber-100"
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

        {/* クイックアクション */}
        {!isCollapsed && (
          <Card>
            <CardContent className="p-4">
              <h3 className="text-sm font-medium mb-3">クイックアクション</h3>
              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2" asChild>
                  <Link href="/chat">
                    <AiOutlineMessage className="h-4 w-4" />
                    Genieと話す
                  </Link>
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start gap-2" asChild>
                  <Link href="/chat">
                    <FaMicrophone className="h-4 w-4" />
                    音声で記録
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
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
      <div className={cn(
        "hidden md:flex md:flex-col md:fixed md:inset-y-0 md:transition-all md:duration-300",
        isCollapsed ? "md:w-16" : "md:w-64"
      )}>
        <SidebarContent isCollapsed={isCollapsed} />
        
        {/* 折り畳みボタン */}
        <Button
          variant="ghost"
          size="sm"
          className="absolute -right-3 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full border border-gray-200 bg-white shadow-sm hover:bg-gray-50 opacity-60 hover:opacity-100 transition-all"
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
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden fixed top-4 left-4 z-50"
          >
            <AiOutlineMenu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="p-0 w-64">
          <SidebarContent />
        </SheetContent>
      </Sheet>
    </>
  )
}