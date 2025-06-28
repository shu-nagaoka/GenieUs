'use client'

import { useState, useEffect } from 'react'

interface Message {
  id: string
  content: string
  sender: 'user' | 'genie'
  timestamp: string
  type?: 'text' | 'audio' | 'image'
}

interface ChatSession {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messages: Message[]
  summary?: string
  tags?: string[]
}

const STORAGE_KEY = 'genie-chat-history'

export function useChatHistory() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // ローカルストレージから履歴を読み込み
  const loadSessions = async () => {
    setLoading(true)
    setError(null)
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored)
        setSessions(data.sessions || [])
      }
    } catch (err) {
      setError('履歴の読み込みに失敗しました')
      console.error('Failed to load chat sessions from localStorage:', err)
    } finally {
      setLoading(false)
    }
  }

  // 特定のセッションを取得
  const loadSession = async (sessionId: string) => {
    setLoading(true)
    setError(null)
    try {
      const session = sessions.find(s => s.id === sessionId)
      if (session) {
        setCurrentSession(session)
        return session
      } else {
        throw new Error('セッションが見つかりません')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました')
      console.error('Failed to load session:', err)
      return null
    } finally {
      setLoading(false)
    }
  }

  // ローカルストレージに保存
  const saveToStorage = (sessions: ChatSession[]) => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          sessions,
          metadata: {
            version: '1.0.0',
            lastUpdated: new Date().toISOString(),
            totalSessions: sessions.length,
          },
        })
      )
    } catch (err) {
      console.error('Failed to save to localStorage:', err)
    }
  }

  // 新しいセッションを作成
  const createSession = async (title: string, messages: Message[]) => {
    setLoading(true)
    setError(null)
    try {
      const newSession: ChatSession = {
        id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        title,
        messages,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        summary: `${messages.length}件のメッセージ`,
        tags: [],
      }

      const updatedSessions = [newSession, ...sessions]
      setSessions(updatedSessions)
      setCurrentSession(newSession)
      saveToStorage(updatedSessions)

      return newSession
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました')
      console.error('Failed to create session:', err)
      return null
    } finally {
      setLoading(false)
    }
  }

  // セッションを更新
  const updateSession = async (sessionId: string, messages: Message[]) => {
    setLoading(true)
    setError(null)
    try {
      const updatedSessions = sessions.map(session =>
        session.id === sessionId
          ? { ...session, messages, updatedAt: new Date().toISOString() }
          : session
      )

      setSessions(updatedSessions)
      saveToStorage(updatedSessions)

      if (currentSession?.id === sessionId) {
        setCurrentSession(prev =>
          prev ? { ...prev, messages, updatedAt: new Date().toISOString() } : null
        )
      }

      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました')
      console.error('Failed to update session:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  // セッションを削除
  const deleteSession = async (sessionId: string) => {
    setLoading(true)
    setError(null)
    try {
      const updatedSessions = sessions.filter(session => session.id !== sessionId)
      setSessions(updatedSessions)
      saveToStorage(updatedSessions)

      if (currentSession?.id === sessionId) {
        setCurrentSession(null)
      }

      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました')
      console.error('Failed to delete session:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  // 初回読み込み
  useEffect(() => {
    loadSessions()
  }, [])

  return {
    sessions,
    currentSession,
    loading,
    error,
    loadSessions,
    loadSession,
    createSession,
    updateSession,
    deleteSession,
    setCurrentSession,
  }
}
