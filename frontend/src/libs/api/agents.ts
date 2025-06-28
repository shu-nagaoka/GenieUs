/**
 * エージェント情報を取得するAPIクライアント
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export interface Agent {
  id: string
  name: string
  description: string
  specialties: string[]
  icon: string
  color: string
  capabilities: string[]
  status: 'active' | 'inactive'
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
}

// バックエンドの実態に合わせたエージェント定義
const mockAgents: Agent[] = [
  {
    id: 'coordinator',
    name: '子育て総合相談',
    description: '基本的な子育ての悩みから複雑な相談まで、総合窓口として対応します',
    specialties: ['子育て相談', '育児アドバイス', 'エージェント紹介', '総合判断'],
    icon: '🧙‍♂️',
    color: 'from-blue-500 to-cyan-500',
    capabilities: ['24時間対応', 'エージェントルーティング', '包括的サポート'],
    status: 'active',
  },
  {
    id: 'nutrition_specialist',
    name: '栄養・食事エージェント',
    description: '離乳食から幼児食まで、栄養バランスを考えた食事をサポート',
    specialties: ['離乳食指導', '幼児食レシピ', 'アレルギー対応', '栄養相談'],
    icon: '🍎',
    color: 'from-green-500 to-emerald-500',
    capabilities: ['月齢別レシピ提案', 'アレルギー対応レシピ', '栄養バランス分析'],
    status: 'active',
  },
  {
    id: 'sleep_specialist',
    name: '睡眠エージェント',
    description: '夜泣きや寝かしつけなど、睡眠に関する悩みを解決',
    specialties: ['夜泣き対策', '寝かしつけ', '睡眠リズム', 'ネントレ'],
    icon: '🌙',
    color: 'from-purple-600 to-indigo-600',
    capabilities: ['睡眠パターン分析', '個別ネントレプラン', '夜泣き原因特定'],
    status: 'active',
  },
  {
    id: 'development_specialist',
    name: '発達支援エージェント',
    description: '運動能力、言語発達、社会性など、お子さんの発達をサポート',
    specialties: ['運動発達', '言語発達', '社会性発達', '発達相談'],
    icon: '🌱',
    color: 'from-teal-500 to-green-500',
    capabilities: ['発達段階チェック', '月齢別サポート', '発達促進アドバイス'],
    status: 'active',
  },
  {
    id: 'health_specialist',
    name: '健康管理エージェント',
    description: '体調管理や病気の対応、予防接種スケジュールをサポート',
    specialties: ['体調管理', '病気対応', '予防接種', '健診スケジュール'],
    icon: '🏥',
    color: 'from-red-500 to-pink-500',
    capabilities: ['症状チェック', '受診タイミング', 'スケジュール管理'],
    status: 'active',
  },
  {
    id: 'behavior_specialist',
    name: '行動・しつけエージェント',
    description: 'イヤイヤ期やしつけの悩みを優しくサポートします',
    specialties: ['イヤイヤ期対応', 'しつけ方法', '行動修正', '生活習慣'],
    icon: '🎯',
    color: 'from-purple-500 to-pink-500',
    capabilities: ['年齢別しつけ法', 'ポジティブ育児', '問題行動対策'],
    status: 'active',
  },
  {
    id: 'play_learning_specialist',
    name: '遊び・学習エージェント',
    description: '年齢に応じた遊びや学習活動、お出かけ先を提案します',
    specialties: ['知育遊び', '運動遊び', 'お出かけ先', '学習サポート'],
    icon: '🎨',
    color: 'from-orange-500 to-amber-500',
    capabilities: ['月齢別遊び提案', '室内・屋外活動', 'お出かけプラン'],
    status: 'active',
  },
  {
    id: 'safety_specialist',
    name: '安全・事故防止エージェント',
    description: '家庭内の安全対策と事故防止をサポートします',
    specialties: ['安全対策', '事故防止', 'チャイルドプルーフ', '応急処置'],
    icon: '🛡️',
    color: 'from-blue-500 to-cyan-500',
    capabilities: ['安全チェックリスト', 'リスク評価', '対策提案'],
    status: 'active',
  },
  {
    id: 'mental_care_specialist',
    name: '心理・メンタルケアエージェント',
    description: 'ママ・パパの心理面をサポートし、育児ストレスを軽減',
    specialties: ['ストレス管理', 'メンタルヘルス', '感情サポート', 'リラクゼーション'],
    icon: '💆‍♀️',
    color: 'from-slate-500 to-gray-600',
    capabilities: ['ストレス診断', 'リラックス法', '感情整理'],
    status: 'active',
  },
  {
    id: 'work_life_specialist',
    name: '社会復帰・仕事両立エージェント',
    description: '職場復帰や仕事と育児の両立をサポートします',
    specialties: ['職場復帰', '仕事両立', '保育園選び', 'ワークライフバランス'],
    icon: '💼',
    color: 'from-purple-600 to-indigo-600',
    capabilities: ['復帰プラン作成', '両立アドバイス', '保育園情報'],
    status: 'active',
  },
  {
    id: 'image_specialist',
    name: '画像分析エージェント',
    description: '写真から成長の記録や健康状態をチェックします',
    specialties: ['画像解析', '成長記録', '健康チェック', 'メモリー作成'],
    icon: '📸',
    color: 'from-cyan-500 to-blue-500',
    capabilities: ['AI画像認識', '成長分析', '写真整理'],
    status: 'active',
  },
  {
    id: 'voice_specialist',
    name: '音声分析エージェント',
    description: '赤ちゃんの泣き声や言葉の発達を分析します',
    specialties: ['泣き声分析', '言語発達', '音声認識', 'コミュニケーション'],
    icon: '🎤',
    color: 'from-pink-500 to-rose-500',
    capabilities: ['泣き声パターン認識', '発話分析', '感情認識'],
    status: 'active',
  },
  {
    id: 'record_specialist',
    name: '記録管理エージェント',
    description: 'お子さんの成長を記録し、発達の軌跡を可視化します',
    specialties: ['成長記録', 'データ分析', '発達グラフ', 'マイルストーン管理'],
    icon: '📊',
    color: 'from-orange-500 to-amber-500',
    capabilities: ['成長データ分析', 'グラフ作成', '発達予測'],
    status: 'active',
  },
  {
    id: 'file_specialist',
    name: 'ファイル管理エージェント',
    description: 'お子さんの大切な思い出や記録を安全に保存・管理します',
    specialties: ['ファイル保存', '写真管理', '動画管理', 'データ整理'],
    icon: '📁',
    color: 'from-gray-500 to-slate-600',
    capabilities: ['クラウド保存', 'ファイル検索', '思い出整理'],
    status: 'active',
  },
  {
    id: 'search_specialist',
    name: '検索エージェント',
    description: 'インターネット検索で最新の子育て情報や地域の施設・サービス情報をお調べします',
    specialties: ['情報検索', '地域情報', '施設案内', '最新情報'],
    icon: '🔍',
    color: 'from-blue-500 to-cyan-500',
    capabilities: ['リアルタイム検索', '地域密着情報', '信頼性確認'],
    status: 'active',
  },
]

/**
 * 全エージェント一覧を取得
 */
export async function getAgents(): Promise<ApiResponse<Agent[]>> {
  // API fetch処理をコメントアウトし、ハードコーディングされたデータを使用
  /*
  try {
    const response = await fetch(`${API_BASE_URL}/agents`)
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`)
    }
    
    return data
  } catch (error) {
    console.error('エージェント取得エラー:', error)
    // フォールバック: モックデータを返す
    return {
      success: true,
      data: mockAgents,
      message: 'エージェント一覧を取得しました（フォールバック）'
    }
  }
  */

  // ハードコーディングされたデータを直接返す
  return {
    success: true,
    data: mockAgents,
    message: 'エージェント一覧を取得しました（ハードコーディング）',
  }
}

/**
 * 特定エージェントの詳細情報を取得
 */
export async function getAgent(agentId: string): Promise<ApiResponse<Agent>> {
  // API fetch処理をコメントアウトし、ハードコーディングされたデータを使用
  /*
  try {
    const response = await fetch(`${API_BASE_URL}/agents/${agentId}`)
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`)
    }
    
    return data
  } catch (error) {
    console.error('エージェント取得エラー:', error)
    // フォールバック: モックデータから検索
    const agent = mockAgents.find(a => a.id === agentId)
    if (agent) {
      return {
        success: true,
        data: agent,
        message: 'エージェント情報を取得しました（フォールバック）'
      }
    }
    
    return {
      success: false,
      message: 'エージェント情報の取得に失敗しました'
    }
  }
  */

  // ハードコーディングされたデータから検索
  const agent = mockAgents.find(a => a.id === agentId)
  if (agent) {
    return {
      success: true,
      data: agent,
      message: 'エージェント情報を取得しました（ハードコーディング）',
    }
  }

  return {
    success: false,
    message: 'エージェント情報の取得に失敗しました',
  }
}

/**
 * アクティブなエージェント数を取得
 */
export async function getActiveAgentCount(): Promise<number> {
  try {
    const result = await getAgents()
    if (result.success && result.data) {
      return result.data.filter(agent => agent.status === 'active').length
    }
    return 0
  } catch (error) {
    console.error('アクティブエージェント数取得エラー:', error)
    return 0
  }
}
