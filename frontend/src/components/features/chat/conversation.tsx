'use client'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ConversationProps {
  messages?: Message[]
  isLoading?: boolean
}

export function Conversation({ messages = [], isLoading = false }: ConversationProps) {
  return (
    <div className="h-full overflow-auto">
      <div className="flex flex-col gap-4 p-4">
        {messages.map(message => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.type === 'assistant' && (
              <Avatar className="h-8 w-8">
                <AvatarFallback>
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
            )}

            <Card
              className={`max-w-[80%] ${
                message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
              }`}
            >
              <CardContent className="p-3">
                {message.type === 'assistant' ? (
                  <div className="prose prose-sm max-w-none text-sm font-medium leading-relaxed tracking-wide prose-headings:font-bold prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-ol:text-foreground prose-ul:text-foreground prose-li:text-foreground">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap text-sm font-medium leading-relaxed tracking-wide">
                    {message.content}
                  </p>
                )}
                <time className="mt-2 block font-mono text-xs tracking-wider opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString('ja-JP', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </time>
              </CardContent>
            </Card>

            {message.type === 'user' && (
              <Avatar className="h-8 w-8">
                <AvatarFallback>
                  <User className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start gap-3">
            <Avatar className="h-8 w-8">
              <AvatarFallback>
                <Bot className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <Card className="bg-muted">
              <CardContent className="p-3">
                <div className="flex space-x-1">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500 [animation-delay:-0.3s]"></div>
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500 [animation-delay:-0.15s]"></div>
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500"></div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

interface ConversationInputProps {
  onSendMessage?: (message: string) => void
  isLoading?: boolean
}

export function ConversationInput({ onSendMessage, isLoading = false }: ConversationInputProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const message = formData.get('message') as string
    if (message.trim() && onSendMessage) {
      onSendMessage(message.trim())
      e.currentTarget.reset()
    }
  }

  return (
    <div className="border-t p-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          name="message"
          placeholder="メッセージを入力..."
          className="flex-1 rounded-md border px-3 py-2 font-medium tracking-wide focus:outline-none focus:ring-2 focus:ring-primary"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-md bg-primary px-4 py-2 font-medium tracking-wide text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          送信
        </button>
      </form>
    </div>
  )
}
