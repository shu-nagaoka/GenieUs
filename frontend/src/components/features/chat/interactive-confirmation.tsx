'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle, XCircle, Clock } from 'lucide-react'

export interface InteractiveConfirmationProps {
  confirmationId: string
  question: string
  options: string[]
  contextData?: any
  onConfirm: (response: string, confirmationId: string) => void
  timeout?: number
}

export function InteractiveConfirmation({
  confirmationId,
  question,
  options,
  contextData,
  onConfirm,
  timeout = 300000 // 5分デフォルト
}: InteractiveConfirmationProps) {
  const [isResponded, setIsResponded] = useState(false)
  const [selectedResponse, setSelectedResponse] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleResponse = async (response: string) => {
    if (isResponded) return

    setIsLoading(true)
    setSelectedResponse(response)
    setIsResponded(true)

    try {
      await onConfirm(response, confirmationId)
    } catch (error) {
      console.error('確認応答エラー:', error)
      // エラー時は状態をリセット
      setIsLoading(false)
      setIsResponded(false)
      setSelectedResponse(null)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 shadow-lg">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* アイコンとタイトル */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500 text-white">
              {isResponded ? (
                selectedResponse === options[0] ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <XCircle className="h-5 w-5" />
                )
              ) : (
                <Clock className="h-5 w-5" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {isResponded ? '応答完了' : '確認が必要です'}
              </h3>
              <p className="text-sm text-gray-600">
                確認ID: {confirmationId}
              </p>
            </div>
          </div>

          {/* 質問内容 */}
          <div className="rounded-lg bg-white/80 p-4">
            <p className="text-gray-700 whitespace-pre-line">{question}</p>
          </div>

          {/* コンテキストデータ表示（食事情報など） */}
          {contextData && (
            <div className="rounded-lg bg-blue-50 p-3 border border-blue-200">
              <p className="text-sm font-medium text-blue-800 mb-2">検出された内容:</p>
              <div className="text-sm text-blue-700">
                {contextData.meal_name && (
                  <p>• 食事名: {contextData.meal_name}</p>
                )}
                {contextData.detected_foods && (
                  <p>• 検出された食べ物: {contextData.detected_foods.join(', ')}</p>
                )}
                {contextData.estimated_meal_time && (
                  <p>• 推定食事時間: {contextData.estimated_meal_time}</p>
                )}
                {contextData.nutrition_balance && (
                  <p>• 栄養バランス: {contextData.nutrition_balance.balance_score}/4</p>
                )}
              </div>
            </div>
          )}

          {/* 応答ボタン */}
          {!isResponded ? (
            <div className="flex gap-3">
              {options.map((option, index) => (
                <Button
                  key={index}
                  onClick={() => handleResponse(option)}
                  disabled={isLoading}
                  className={`flex-1 transition-all duration-200 ${
                    index === 0
                      ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white hover:from-emerald-600 hover:to-green-600'
                      : 'bg-gradient-to-r from-gray-400 to-gray-500 text-white hover:from-gray-500 hover:to-gray-600'
                  }`}
                >
                  {isLoading && selectedResponse === option ? (
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      処理中...
                    </div>
                  ) : (
                    option
                  )}
                </Button>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2 rounded-lg bg-gray-100 p-3">
              <div className="flex items-center gap-2 text-gray-700">
                {selectedResponse === options[0] ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-gray-600" />
                )}
                <span>「{selectedResponse}」を選択されました</span>
              </div>
            </div>
          )}

          {/* タイムアウト表示（オプション） */}
          {!isResponded && timeout && (
            <p className="text-xs text-gray-500 text-center">
              この確認は {Math.floor(timeout / 60000)} 分後に自動的に期限切れになります
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// ストリーミングレスポンス用のデータ型
export interface InteractiveConfirmationData {
  type: 'interactive_confirmation'
  confirmation_id: string
  question: string
  options: string[]
  context_data?: any
  timeout_seconds?: number
}

// 確認レスポンスを判定するヘルパー関数
export function parseInteractiveConfirmation(response: string): InteractiveConfirmationData | null {
  try {
    // JSON形式の確認データを検出
    const jsonMatch = response.match(/\{[\s\S]*?"type"\s*:\s*"interactive_confirmation"[\s\S]*?\}/);
    if (jsonMatch) {
      const data = JSON.parse(jsonMatch[0]);
      if (data.type === 'interactive_confirmation') {
        return data;
      }
    }

    // マークダウン形式の確認データを検出
    const confirmationMatch = response.match(/\*\*確認が必要です\*\*[\s\S]*?選択してください/);
    if (confirmationMatch) {
      // 簡易的なパース（実装は文脈に応じて調整）
      return {
        type: 'interactive_confirmation',
        confirmation_id: `confirm_${Date.now()}`,
        question: '確認をお願いします',
        options: ['はい', 'いいえ'],
        context_data: null
      };
    }

    return null;
  } catch (error) {
    console.error('Interactive confirmation parsing error:', error);
    return null;
  }
}