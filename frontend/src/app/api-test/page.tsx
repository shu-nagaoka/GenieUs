'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface APITestResponse {
  response: string
  status: string
  user_id: string
  timestamp: string
}

export default function APITestPage() {
  const [message, setMessage] = useState('')
  const [userId, setUserId] = useState('test_user')
  const [response, setResponse] = useState<APITestResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const testPing = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://localhost:8000/api/v1/ping')
      const data = await res.json()
      setResponse({
        response: `Ping応答: ${data.message}`,
        status: 'success',
        user_id: userId,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      setError(`Pingエラー: ${err}`)
    } finally {
      setLoading(false)
    }
  }

  const testSimpleAPI = async () => {
    if (!message.trim()) {
      setError('メッセージを入力してください')
      return
    }

    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://localhost:8000/api/v1/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          user_id: userId,
        }),
      })

      if (!res.ok) {
        throw new Error(`HTTPエラー: ${res.status}`)
      }

      const data: APITestResponse = await res.json()
      setResponse(data)
    } catch (err) {
      setError(`APIエラー: ${err}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 p-6">
      <div className="mx-auto max-w-2xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-amber-800">🧪 API接続テスト</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="userId">ユーザーID</Label>
              <Input
                id="userId"
                value={userId}
                onChange={e => setUserId(e.target.value)}
                placeholder="test_user"
              />
            </div>

            <div>
              <Label htmlFor="message">テストメッセージ</Label>
              <Input
                id="message"
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="こんにちは"
              />
            </div>

            <div className="flex gap-3">
              <Button onClick={testPing} disabled={loading} variant="outline">
                {loading ? '実行中...' : 'Pingテスト'}
              </Button>

              <Button onClick={testSimpleAPI} disabled={loading || !message.trim()}>
                {loading ? '実行中...' : 'APIテスト'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <p className="font-medium text-red-600">❌ エラー:</p>
              <p className="text-red-700">{error}</p>
            </CardContent>
          </Card>
        )}

        {response && (
          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-green-800">✅ API応答</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="font-medium text-green-700">レスポンス:</p>
                <p className="rounded border bg-white p-3">{response.response}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-green-700">ステータス:</p>
                  <p className="text-green-600">{response.status}</p>
                </div>
                <div>
                  <p className="font-medium text-green-700">ユーザーID:</p>
                  <p className="text-green-600">{response.user_id}</p>
                </div>
              </div>

              <div>
                <p className="font-medium text-green-700">タイムスタンプ:</p>
                <p className="text-sm text-green-600">{response.timestamp}</p>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">📋 テスト手順</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <ol className="list-inside list-decimal space-y-2 text-sm">
              <li>まず「Pingテスト」でサーバー接続を確認</li>
              <li>メッセージを入力して「APIテスト」を実行</li>
              <li>「こんにちは」「ありがとう」等で条件分岐をテスト</li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
