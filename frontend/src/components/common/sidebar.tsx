'use client'

import * as React from 'react'
import {
  Sidebar,
} from '@/components/ui/sidebar'
import { Header } from '@/components/common/header'

// 課長とメンバーの進捗確認会話履歴データ
const chatHistory = [
  {
    id: '1',
    question: '今週の吉野さんの活動状況を教えて',
    timestamp: '15:30',
    date: '今日',
    preview: '生成AI活用プログラムの検討会議に参加し、GWS既存ユーザー向けの活用について...',
  },
  {
    id: '2',
    question: '蛯谷さんのWBS作成の進捗はどう？',
    timestamp: '14:25',
    date: '今日',
    preview: 'ソブリンクラウドチーム向けのWBS説明会を実施し、スプレッドシートを用いた...',
  },
  {
    id: '3',
    question: '長岡さんのGemini API調査は終わった？',
    timestamp: '11:45',
    date: '昨日',
    preview: 'Gemini API利用時のログ保存仕様について調査完了。データキャッシュの期間や...',
  },
  {
    id: '4',
    question: '清川さんのVideoDoc-AIマニュアル作成状況は？',
    timestamp: '16:20',
    date: '昨日',
    preview: 'VideoDoc-AIアプリケーションの利用マニュアル作成が完了。8ページの詳細な...',
  },
  {
    id: '5',
    question: '芦澤さんのAppSheet機能検討はどこまで進んだ？',
    timestamp: '10:15',
    date: '1/14',
    preview: 'AppSheet Step4のプレゼンテーション評価ツール機能案検討を実施。UI機能案や...',
  },
]

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {}

export function AppSidebar({ ...props }: AppSidebarProps) {
  return (
    <div className="fixed left-0 top-16 z-0 h-[calc(100vh-4rem)] w-64 border-r border-gray-200 bg-white">
      {/* 新規会話ボタン */}
      <div className="border-b border-gray-200 p-4">
        <button
          onClick={() => {
            // 新規会話の処理
            const url = new URL(window.location.href)
            url.searchParams.delete('conversation')
            window.history.pushState({}, '', url)

            // 新規会話イベントを発火
            window.dispatchEvent(new CustomEvent('newConversation'))
          }}
          className="group flex w-full transform items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-teal-400 to-emerald-400 px-4 py-3 font-medium tracking-wide text-white shadow-md transition-all duration-300 hover:scale-[1.02] hover:from-teal-500 hover:to-emerald-500 hover:shadow-lg"
        >
          <Plus className="h-4 w-4 transition-transform duration-300 group-hover:rotate-90" />
          <span className="text-sm">New Chat</span>
        </button>
      </div>

      {/* 会話履歴ヘッダー */}
      <div className="border-b border-gray-100 px-4 py-3">
        <h2 className="text-sm font-medium uppercase tracking-wider text-gray-600">Chat History</h2>
      </div>

      {/* 会話履歴リスト */}
      <div className="h-full overflow-y-auto pb-4">
        {chatHistory.map(conversation => (
          <div
            key={conversation.id}
            onClick={() => {
              // URLパラメータを更新
              const url = new URL(window.location.href)
              url.searchParams.set('conversation', conversation.id)
              window.history.pushState({}, '', url)

              // カスタムイベントを発火してChatページに通知
              window.dispatchEvent(
                new CustomEvent('conversationChange', {
                  detail: { conversationId: conversation.id },
                })
              )
            }}
            className="cursor-pointer border-b border-gray-100 p-4 hover:bg-gray-50"
          >
            <div className="mb-1 text-sm font-medium text-gray-900">{conversation.question}</div>
            <div className="mb-2 text-xs text-gray-500">{conversation.preview}</div>
            <div className="text-xs text-gray-400">{conversation.timestamp}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// サイドバーレイアウトコンポーネント
interface SidebarLayoutProps {
  children: React.ReactNode
  defaultOpen?: boolean
  onConversationSelect?: (conversationId: string) => void
}

export function SidebarLayout({ children, defaultOpen = true }: SidebarLayoutProps) {
  return (
    <div className="flex min-h-screen w-full flex-col">
      {/* ヘッダー */}
      <Header />

      <div className="flex flex-1 pt-16">
        <AppSidebar />
        <main className="ml-64 flex-1 overflow-hidden">
          <div className="flex-1 overflow-auto p-6">{children}</div>
        </main>
      </div>
    </div>
  )
}

export default AppSidebar
