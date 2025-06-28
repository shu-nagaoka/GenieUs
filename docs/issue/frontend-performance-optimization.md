# Issue: フロントエンド速度最適化実装

**Issue ID**: FEP-001
**優先度**: High  
**カテゴリ**: フロントエンド/パフォーマンス改善

## 📋 概要

GenieUsフロントエンドアプリケーションにおいて、CSRアーキテクチャを維持しながら、ユーザー体験を大幅に改善するための速度最適化を実装する。

## 🎯 目的

- 初期読み込み時間の30-40%短縮
- ページ遷移速度の50-60%高速化  
- API レスポンス体感速度の70-80%改善
- バンドルサイズの20-30%削減

## 🔍 現状分析

### 既存の最適化状況
✅ **実装済み**
- Next.js基本最適化（React Strict Mode、standalone出力）
- 部分的なコード分割（ReactMarkdown、GenieStyleProgressの lazy loading）
- TanStack React Query導入済み（**未活用**）

⚠️ **最適化の余地**
- React Query未活用（導入済みだが使用されていない）
- メモ化の不足（React.memo、useMemo、useCallbackの限定的使用）
- バンドルサイズ巨大（node_modules 946MB）
- 頻繁な再レンダリング（チャット画面で30以上のuseState/useEffect）

### パフォーマンスボトルネック
1. **API呼び出しの重複**: 家族情報、エージェント情報の重複取得
2. **不要な再レンダリング**: ChatMessage、GenieStyleProgress等の重要コンポーネント
3. **バンドルサイズ**: 最適化不足のライブラリインポート
4. **ローディング体験**: Skeleton UI未実装による体感速度低下

## 🚀 実装プラン

### Phase 1: 即効性・低リスク改善 (週内実装)

#### 1.1 React Query活用によるキャッシュ戦略
**対象ファイル**: 
- `frontend/src/libs/api/agents.ts`
- `frontend/src/libs/api/file-upload.ts`
- `frontend/src/app/chat/page.tsx`

**実装内容**:
```typescript
// API呼び出しをReact Queryでキャッシュ化
const { data: familyInfo, isLoading } = useQuery({
  queryKey: ['familyInfo', userId],
  queryFn: () => getFamilyInfo(userId),
  staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  cacheTime: 10 * 60 * 1000
})
```

#### 1.2 重要コンポーネントのメモ化
**対象ファイル**:
- `frontend/src/components/features/chat/conversation.tsx`
- `frontend/src/components/features/chat/genie-style-progress.tsx`

**実装内容**:
```typescript
export const ChatMessage = React.memo(({ message, ...props }) => {
  return <Card>...</Card>
})

const filteredMessages = useMemo(() => 
  messages.filter(msg => !msg.content.includes('こんにちは！**GenieUs**です')),
  [messages]
)
```

#### 1.3 バンドル最適化設定
**対象ファイル**: `frontend/next.config.ts`

**実装内容**:
```typescript
experimental: {
  optimizePackageImports: [
    // 既存に追加
    'framer-motion',
    'react-markdown', 
    'recharts',
    'date-fns'
  ]
}
```

### Phase 2: 中期改善 (月内実装)

#### 2.1 Skeleton UI導入
**対象ファイル**: 
- `frontend/src/components/ui/skeleton.tsx` (新規作成)
- 各ローディング画面

#### 2.2 Virtual Scrolling導入
**対象ファイル**: `frontend/src/hooks/use-chat-history.tsx`

#### 2.3 プリフェッチング戦略
**実装内容**: ルート間プリフェッチ、API データ先行取得

### Phase 3: 長期改善 (四半期実装)

#### 3.1 Service Worker + PWA化
#### 3.2 Critical CSS最適化

## 🧪 テストプラン

### 性能測定
1. **Lighthouse Score**: 実装前後の比較
2. **バンドルサイズ**: webpack-bundle-analyzerによる計測
3. **API レスポンス時間**: React Query DevToolsによる監視
4. **再レンダリング**: React DevTools Profilerによる分析

### 機能テスト
1. **チャット機能**: ストリーミング、画像アップロード、音声録音
2. **ページ遷移**: 全ページの正常動作確認
3. **認証フロー**: ログイン・ログアウト
4. **レスポンシブ**: モバイル・デスクトップ

### 回帰テスト
1. **既存機能**: 全機能の動作確認
2. **API統合**: バックエンドとの通信確認
3. **エラーハンドリング**: フォールバック動作

## 📊 成功指標

### 定量的指標
- **初期読み込み時間**: 現在値から30-40%短縮
- **Lighthouse Performance Score**: 70+ → 85+目標
- **バンドルサイズ**: 20-30%削減
- **API キャッシュヒット率**: 70%以上

### 定性的指標
- **ユーザー体感**: ページ遷移のスムーズさ
- **ローディング体験**: Skeleton UIによる改善
- **開発体験**: React Query DevToolsによる可視性向上

## ⚠️ リスク・注意事項

### 技術的リスク
1. **React Query導入**: 既存のuseState/useEffectとの競合
2. **メモ化**: 過度なメモ化による逆効果
3. **バンドル最適化**: 必要なライブラリの除外

### 対策
1. **段階的導入**: 1つずつ機能を移行
2. **性能監視**: 各段階での測定実施
3. **フォールバック**: 問題発生時の元戻し手順

## 🔄 ロールバック計画

### 緊急ロールバック
1. **Git revert**: 各Phase毎のcommitから戻し
2. **設定ファイル復元**: next.config.ts, package.jsonの復元

### 段階的ロールバック
1. **React Query無効化**: 既存APIコールに戻し
2. **メモ化解除**: React.memo削除
3. **バンドル設定復元**: optimizePackageImports無効化

## 🎯 実装スケジュール

- **Week 1**: Phase 1 実装・テスト
- **Week 2-3**: Phase 2 実装・テスト  
- **Week 4**: 統合テスト・微調整
- **Month 2-3**: Phase 3 実装（余裕がある場合）

## 📝 備考

- Issue駆動開発ルールに従い、各Phase完了時に進捗確認
- コーディング規約遵守（Import文先頭配置、型アノテーション完備）
- 実装中の継続的なパフォーマンス監視