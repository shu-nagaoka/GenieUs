'use client'

import { MessageSquare, Plus, Trash2 } from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInput,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSkeleton,
  SidebarMenuAction,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'

interface ChatSidebarProps {
  conversations?: Array<{
    thread_id: string
    question: string
    answer: string
  }>
  isLoading?: boolean
  onDeleteConversation?: (thread_id: string) => void
  onSelectConversation?: (thread_id: string) => void
  selectedConversationId?: string
}

export function ChatSidebar({
  conversations = [],
  isLoading = false,
  onDeleteConversation,
  onSelectConversation,
  selectedConversationId,
}: ChatSidebarProps) {
  return (
    <Sidebar side="left" variant="sidebar" className="top-16 border-emerald-200 bg-emerald-50">
      <SidebarHeader className="bg-emerald-50">
        <Button className="w-full bg-emerald-700 py-2.5 font-mono font-medium uppercase tracking-wider text-white shadow-sm transition-all duration-150 hover:bg-emerald-800 hover:shadow-md">
          <Plus className="mr-2 h-4 w-4" />
          新規会話
        </Button>
        <SidebarInput
          placeholder="Search conversations..."
          className="border-emerald-200 font-medium tracking-wide focus:border-emerald-400"
        />
      </SidebarHeader>

      <SidebarContent className="bg-emerald-50">
        <SidebarGroup>
          <SidebarGroupLabel className="font-mono text-xs font-medium uppercase tracking-wider text-emerald-700">
            Conversations
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {isLoading
                ? Array.from({ length: 5 }).map((_, index) => (
                    <SidebarMenuItem key={index}>
                      <SidebarMenuSkeleton showIcon />
                    </SidebarMenuItem>
                  ))
                : conversations.map(conversation => (
                    <SidebarMenuItem key={conversation.thread_id}>
                      <SidebarMenuButton
                        isActive={selectedConversationId === conversation.thread_id}
                        onClick={() => onSelectConversation?.(conversation.thread_id)}
                        className="hover:bg-emerald-100 data-[active=true]:bg-emerald-200 data-[active=true]:text-emerald-800"
                      >
                        <MessageSquare className="h-4 w-4 text-emerald-600" />
                        <span className="truncate font-medium tracking-wide">
                          {conversation.question}
                        </span>
                      </SidebarMenuButton>
                      <SidebarMenuAction
                        onClick={() => onDeleteConversation?.(conversation.thread_id)}
                        showOnHover
                        className="text-emerald-600 hover:bg-emerald-200"
                      >
                        <Trash2 className="h-4 w-4" />
                      </SidebarMenuAction>
                    </SidebarMenuItem>
                  ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
