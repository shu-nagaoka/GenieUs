/**
 * API設定
 */

// 環境変数からAPIベースURLを取得（デフォルトはlocalhost）
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080'

// APIエンドポイント
export const API_ENDPOINTS = {
  // 認証
  AUTH_LOGIN_GOOGLE: `${API_BASE_URL}/api/auth/login/google`,
  
  // チャット
  CHAT: `${API_BASE_URL}/api/v1/chat`,
  STREAMING_CHAT: `${API_BASE_URL}/api/streaming/streaming-chat`,
  
  // エージェント
  AGENTS: `${API_BASE_URL}/api/v1/agents`,
  
  // スケジュール
  SCHEDULES: `${API_BASE_URL}/api/v1/schedules`,
  
  // 成長記録
  GROWTH_RECORDS: `${API_BASE_URL}/api/v1/growth-records`,
  
  // 努力記録
  EFFORT_RECORDS: `${API_BASE_URL}/api/v1/effort-records`,
  
  // 思い出
  MEMORIES: `${API_BASE_URL}/api/v1/memories`,
  
  // 食事
  MEAL_PLANS: `${API_BASE_URL}/api/v1/meal-plans`,
  MEAL_RECORDS: `${API_BASE_URL}/api/v1/meal-records`,
  
  // ファイルアップロード
  FILE_UPLOAD: `${API_BASE_URL}/api/v1/memories/upload`,
  
  // 家族情報
  FAMILY: `${API_BASE_URL}/api/v1/family`,
  
  // ヘルスチェック
  HEALTH: `${API_BASE_URL}/health`,
} as const