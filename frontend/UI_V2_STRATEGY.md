# GenieUs v2.0 UI戦略実装計画

## 現状分析

### 既存UI構造
- **ランディングページ**: GenieUs → 4機能カード（AI相談、成長記録、スケジュール、ダッシュボード）
- **既存機能**: 従来の記録・管理型UI
- **問題点**: v2.0コンセプト「予測的洞察・努力肯定・ゼロ努力記録」が反映されていない

### v2.0 バックエンド API実装済み
- `/api/v2/voice-record` - 音声記録（Zero-Effort Recording）
- `/api/v2/image-record` - 画像記録（Zero-Effort Recording）  
- `/api/v2/video-record` - 動画記録（Zero-Effort Recording）
- `/api/v2/prediction` - 予測生成（Proactive Insight）
- `/api/v2/effort-report` - 努力レポート（Effort Affirmation）
- `/api/v2/chat` - 統合チャット
- `/api/v2/health` - ヘルスチェック

## 段階的UI移行戦略

### Phase 1: ダッシュボード v2.0 変換 🔮 [優先度: 高]

**目標**: 既存ダッシュボードを「Proactive Insight Module」中心に変換

**新機能**:
1. **朝の予測セクション** (7:00 自動更新)
   - 今日の子供のコンディション予測
   - 根拠データ表示
   - 具体的対策アクション
   - 信頼度インジケーター

2. **リアルタイムインサイト**
   - 過去パターンとの比較
   - 今日起こりうる変化の予測
   - タイムライン式表示

**実装場所**: `/frontend/src/app/dashboard/page.tsx`

### Phase 2: 音声記録UI実装 🎤 [優先度: 高]

**目標**: 「Zero-Effort Recording Module」の音声インターフェース

**新機能**:
1. **常時音声ボタン**
   - フローティングアクション（全ページ共通）
   - ワンタップ録音開始
   - 自動NLU処理 → 構造化データ変換

2. **音声記録フィードバック**
   - リアルタイム解析状況表示
   - 抽出イベント確認UI
   - 修正・承認機能

**実装場所**: `/frontend/src/components/features/voice-recording/`

### Phase 3: 努力肯定レポートUI 💝 [優先度: 中]

**目標**: 「Parental Effort Affirmation Module」の可視化

**新機能**:
1. **夜のレポート表示** (21:00 自動生成)
   - その日の努力指標
   - 子供の成長エビデンス  
   - 肯定的フィードバックメッセージ
   - シェア機能

2. **努力ダッシュボード**
   - 週次・月次の努力推移
   - 成長の証拠タイムライン
   - 達成バッジシステム

**実装場所**: `/frontend/src/app/effort-report/page.tsx`

### Phase 4: チャット v2.0 強化 💬 [優先度: 中]

**目標**: 既存チャットをコンテキスト統合型に進化

**強化機能**:
1. **コンテキスト情報表示**
   - 関連する過去記録
   - パターン分析結果
   - 予測情報統合

2. **マルチモーダル入力**
   - 音声入力ボタン
   - 画像添付機能
   - リアルタイム解析

**実装場所**: `/frontend/src/app/chat/page.tsx`

### Phase 5: 新ランディングページ ✨ [優先度: 低]

**目標**: v2.0コンセプトを反映したブランド体験

**新要素**:
1. **コンセプト中心設計**
   - 「見えない成長に、光をあてる」
   - 3つのモジュール紹介
   - 体験フロー説明

2. **デモ機能**
   - 音声記録デモ
   - 予測例表示
   - 努力レポートサンプル

## 技術実装方針

### 1. コンポーネント設計
```typescript
// 新規コンポーネント構造
/src/components/v2/
├── prediction/
│   ├── DailyPredictionCard.tsx
│   ├── PredictionTimeline.tsx
│   └── ConfidenceIndicator.tsx
├── voice-recording/
│   ├── FloatingVoiceButton.tsx
│   ├── VoiceRecordingModal.tsx
│   └── ProcessingStatus.tsx
├── effort-affirmation/
│   ├── EffortReportCard.tsx
│   ├── AchievementBadge.tsx
│   └── GrowthEvidence.tsx
└── shared/
    ├── V2Layout.tsx
    └── ModuleHeader.tsx
```

### 2. API統合パターン
```typescript
// カスタムフック例
const useDailyPrediction = (childId: string) => {
  return useQuery(['dailyPrediction', childId], 
    () => fetch(`/api/v2/prediction`, {
      method: 'POST',
      body: JSON.stringify({ child_id: childId })
    })
  )
}

const useVoiceRecording = () => {
  return useMutation((voiceText: string) => 
    fetch('/api/v2/voice-record', {
      method: 'POST', 
      body: JSON.stringify({ voice_text: voiceText })
    })
  )
}
```

### 3. デザインシステム拡張
```css
/* v2.0 カラーパレット */
:root {
  --v2-prediction: #8B5CF6;  /* 予測 - パープル */
  --v2-effort: #F59E0B;      /* 努力 - アンバー */
  --v2-recording: #10B981;   /* 記録 - エメラルド */
  --v2-insight: #3B82F6;     /* 洞察 - ブルー */
}
```

### 4. 状態管理
```typescript
// Zustand store for v2.0 state
interface V2Store {
  // Prediction state
  dailyPredictions: PredictionResult[]
  
  // Recording state  
  isRecording: boolean
  processingStatus: 'idle' | 'processing' | 'completed'
  
  // Effort tracking
  weeklyEffortReport: EffortReport | null
  
  // Actions
  fetchDailyPredictions: (childId: string) => Promise<void>
  startVoiceRecording: () => void
  processVoiceText: (text: string) => Promise<void>
  generateEffortReport: (parentId: string) => Promise<void>
}
```

## スケジュール

### Week 1: Phase 1 - ダッシュボード v2.0
- [ ] DailyPredictionCard コンポーネント
- [ ] 予測API統合
- [ ] レスポンシブ対応
- [ ] ユニットテスト

### Week 2: Phase 2 - 音声記録UI
- [ ] FloatingVoiceButton実装
- [ ] Web Speech API統合
- [ ] /api/v2/voice-record 連携
- [ ] フィードバックUI

### Week 3: Phase 3 - 努力レポートUI
- [ ] EffortReportCard実装
- [ ] /api/v2/effort-report 連携
- [ ] 肯定的UX設計
- [ ] シェア機能

### Week 4: Phase 4-5 - チャット強化 & ランディング
- [ ] チャット v2.0 機能追加
- [ ] ランディングページ更新
- [ ] 全体統合テスト
- [ ] パフォーマンス最適化

## 成功指標

### UX指標
- **音声記録使用率**: 週次記録の50%以上が音声入力
- **予測精度実感**: ユーザーの80%が予測を「参考になる」と評価
- **努力肯定効果**: レポート閲覧後の満足度スコア4.5以上

### 技術指標
- **レスポンス時間**: 音声処理 < 3秒、予測生成 < 2秒
- **エラー率**: API呼び出し成功率 > 99%
- **モバイル対応**: 全機能がモバイルで正常動作

## リスク管理

### 高リスク
1. **Gemini API制限**: 代替NLU実装準備
2. **音声認識精度**: Web Speech API + 手動修正機能
3. **ユーザー慣れ**: 段階的機能解放 + オンボーディング

### 低リスク
1. **既存機能破壊**: 漸進的移行
2. **パフォーマンス**: 最適化とキャッシュ戦略
3. **セキュリティ**: 音声データ暗号化

---

**次のアクション**: Phase 1のダッシュボード v2.0 実装から開始します。