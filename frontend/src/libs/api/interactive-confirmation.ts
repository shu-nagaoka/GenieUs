/**
 * Interactive Confirmation API Client
 * Human-in-the-Loop確認処理のためのAPI関数
 */

import { API_BASE_URL } from '@/config/api'

export interface ConfirmationResponseRequest {
  confirmation_id: string
  user_response: string
  user_id: string
  session_id: string
  response_metadata?: Record<string, any>
}

export interface ConfirmationResponseResponse {
  success: boolean
  message: string
  followup_action: Record<string, any>
  confirmation_id: string
  timestamp: string
}

/**
 * ユーザーの確認応答を送信する
 */
export async function sendConfirmationResponse(
  request: ConfirmationResponseRequest
): Promise<ConfirmationResponseResponse> {
  try {
    console.log('📤 送信する確認応答:', request)

    const response = await fetch(`${API_BASE_URL}/api/streaming/process-confirmation-response`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`確認応答送信に失敗しました: ${response.status} ${errorText}`)
    }

    const data = await response.json()
    console.log('📥 確認応答レスポンス:', data)

    return data
  } catch (error) {
    console.error('❌ 確認応答送信エラー:', error)
    throw error
  }
}

/**
 * レスポンスからインタラクティブ確認データを抽出する
 */
export interface InteractiveConfirmationData {
  type: 'interactive_confirmation'
  confirmation_id: string
  question: string
  options: string[]
  context_data?: any
  timeout_seconds?: number
}

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

    // requires_user_response フラグを含む応答を検出
    const responseFlagMatch = response.match(/\{[\s\S]*?"requires_user_response"\s*:\s*true[\s\S]*?\}/);
    if (responseFlagMatch) {
      const data = JSON.parse(responseFlagMatch[0]);
      if (data.requires_user_response) {
        return {
          type: 'interactive_confirmation',
          confirmation_id: data.confirmation_data?.confirmation_id || `confirm_${Date.now()}`,
          question: data.confirmation_data?.question || data.message || '確認をお願いします',
          options: data.confirmation_data?.options || ['はい', 'いいえ'],
          context_data: data.context_data || data.confirmation_data?.context_data,
          timeout_seconds: data.confirmation_data?.timeout_seconds || 300
        };
      }
    }

    return null;
  } catch (error) {
    console.error('Interactive confirmation parsing error:', error);
    return null;
  }
}

/**
 * メッセージ内容が確認を必要とするかチェック
 */
export function requiresConfirmation(content: string): boolean {
  // 確認が必要なパターンを検出
  const confirmationPatterns = [
    'requires_user_response',
    'confirmation_id',
    '確認が必要です',
    '登録しますか',
    'interactive_confirmation'
  ]

  return confirmationPatterns.some(pattern => content.includes(pattern))
}