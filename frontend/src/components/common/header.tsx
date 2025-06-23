'use client'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { MessageSquare, BookOpen, Menu, LogOut } from 'lucide-react'

//ヘッダーコンポーネント

export const Header = () => (
  <div
    className="fixed z-50 flex h-16 w-screen items-center border-b border-gray-200/50 pl-4 pr-8 shadow-sm"
    style={{ background: 'linear-gradient(to right, #2dd4bf, #34d399)' }}
  >
    <a
      href="/"
      className="flex cursor-pointer items-center gap-3 transition-opacity duration-300 hover:opacity-80"
    >
      <img src="/img/Linx-rogo.png" alt="" className="h-11 w-11" />
      <h1 className="font-mono text-3xl font-light tracking-wider text-white">Linx</h1>
    </a>

    {/* 中央のナビゲーション */}
    <div className="absolute left-1/2 flex -translate-x-1/2 transform gap-8">
      <a
        href="/chat"
        className="group flex items-center gap-2 rounded-lg px-4 py-2 transition-all duration-300 ease-in-out hover:bg-white/20"
      >
        <MessageSquare className="h-4 w-4 text-gray-700 transition-colors group-hover:text-white" />
        <span className="text-sm font-medium tracking-wide text-gray-700 group-hover:text-white">
          AI Chat
        </span>
      </a>
      <a
        href="/knowledge"
        className="group flex items-center gap-2 rounded-lg px-4 py-2 transition-all duration-300 ease-in-out hover:bg-white/20"
      >
        <BookOpen className="h-4 w-4 text-gray-700 transition-colors group-hover:text-white" />
        <span className="text-sm font-medium tracking-wide text-gray-700 group-hover:text-white">
          Knowledge
        </span>
      </a>
    </div>

    <div className="ml-auto flex items-center gap-3">
      <button className="group rounded-lg bg-white/20 p-2 text-white transition-all duration-300 hover:scale-105 hover:bg-white/30">
        <LogOut className="h-5 w-5 transition-transform duration-300 group-hover:rotate-12" />
      </button>
      <Avatar className="ring-2 ring-white/30 transition-all duration-300 hover:ring-white/50">
        <AvatarImage src="https://github.com/shadcn.png" />
        <AvatarFallback className="bg-white/20 font-medium text-white">CN</AvatarFallback>
      </Avatar>
    </div>
  </div>
)

//一旦上記の上記の内容が綺麗になったら、プルリクエストを出す（配置とルーティングをダミーで実施）
