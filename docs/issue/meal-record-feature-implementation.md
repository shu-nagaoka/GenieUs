# Issue: 個別食事記録機能の実装

**Issue ID**: MEAL-001  
**優先度**: High  
**カテゴリ**: フルスタック機能追加  

## 📋 概要

Human-in-the-Loop機能と連携して、画像解析結果から個別の食事記録を作成・管理する機能を実装する。既存の食事プラン機能とは別に、実際に食べた食事の履歴・ログを管理する新機能として追加する。

## 🎯 目的

- **画像解析からの自動食事記録**: AI分析結果をユーザー確認後に食事ログとして保存
- **手動食事記録**: ユーザーが直接食事情報を入力・編集可能
- **栄養追跡**: 日々の食事から栄養バランスを可視化
- **成長記録連携**: 食事記録を子どもの成長データと関連付け
- **サイドバーUI**: フロントエンドのサイドバーから簡単にアクセス可能

## 🔍 現状分析

### 既存機能との差分

**既存: 食事プラン機能** (`meal_plan_management_usecase.py`)
- 週間の食事計画を事前に立てる機能
- 将来の食事の計画・管理
- MealPlan エンティティ

**新規: 食事記録機能** (今回実装)
- 実際に食べた食事の記録・履歴
- 過去の食事データの蓄積・分析
- MealRecord エンティティ

### 技術的課題

1. **Human-in-the-Loop統合**: 画像解析 → 確認 → 記録の一連フロー
2. **データ構造設計**: 栄養情報、検出精度、時系列データの適切な管理
3. **UI/UX設計**: サイドバーでの直感的な食事記録・履歴表示
4. **パフォーマンス**: 大量の食事記録データの効率的な処理

## 🚀 実装プラン

### Phase 1: バックエンド基盤構築

#### 1.1 ドメイン層
```python
# MealRecord エンティティ追加
@dataclass
class MealRecord:
    id: str
    child_id: str
    meal_name: str
    meal_type: MealType  # breakfast, lunch, dinner, snack
    detected_foods: list[str]
    nutrition_info: dict[str, Any]
    timestamp: datetime
    detection_source: FoodDetectionSource  # manual, image_ai, voice_ai
    confidence: float
    image_path: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
```

#### 1.2 Application層
```python
# MealRecordUseCase 実装
class MealRecordUseCase:
    - create_meal_record()
    - get_meal_records()
    - update_meal_record()
    - delete_meal_record()
    - get_nutrition_summary()
    - search_meal_records()
```

#### 1.3 Infrastructure層
```python
# MealRecordRepository 実装
- SQLite対応
- CRUD操作
- 日付範囲検索
- 栄養情報集計
```

#### 1.4 API層
```python
# /api/meal-records エンドポイント
- POST /api/meal-records (作成)
- GET /api/meal-records (一覧・検索)
- PUT /api/meal-records/{id} (更新)
- DELETE /api/meal-records/{id} (削除)
- GET /api/meal-records/nutrition-summary (栄養サマリー)
```

### Phase 2: Human-in-the-Loop統合

#### 2.1 Interactive Confirmation UseCase 修正
- `process_confirmation_response()` で食事記録作成を呼び出し
- 食事プラン作成から食事記録作成に変更

#### 2.2 Meal Management Integration Tool 修正
- 食事記録専用の確認フローに変更
- コンテキストデータに検出精度・画像パス等を含める

### Phase 3: フロントエンド実装

#### 3.1 サイドバーメニュー追加
```typescript
// sidebar-nav.tsx に食事記録メニュー追加
{
  title: "食事記録",
  href: "/meal-records",
  icon: UtensilsIcon,
}
```

#### 3.2 食事記録ページ作成
```
/frontend/src/app/meal-records/
├── page.tsx (食事記録一覧・追加)
├── components/
│   ├── meal-record-form.tsx (手動入力フォーム)
│   ├── meal-record-list.tsx (記録一覧)
│   ├── nutrition-summary.tsx (栄養サマリー)
│   └── meal-record-card.tsx (個別記録カード)
```

#### 3.3 Interactive Confirmation 表示更新
- 食事記録向けのメッセージに変更
- 「食事プランに追加」→「食事記録として保存」

### Phase 4: 高度な機能

#### 4.1 栄養分析・可視化
- 日別・週別・月別の栄養バランス表示
- カロリー・主要栄養素のトラッキング
- 成長曲線との相関分析

#### 4.2 検索・フィルタリング
- 食材別検索
- 期間絞り込み
- 栄養素フィルタ

## 🧪 テストプラン

### 単体テスト
- [ ] MealRecord エンティティのバリデーション
- [ ] MealRecordUseCase の各メソッド
- [ ] MealRecordRepository の CRUD操作
- [ ] API エンドポイントのレスポンス

### 結合テスト
- [ ] 画像解析 → 確認 → 食事記録作成フロー
- [ ] 手動食事記録作成・編集・削除
- [ ] 栄養サマリー集計の正確性
- [ ] フロントエンド・バックエンド連携

### E2Eテスト
- [ ] サイドバーから食事記録ページアクセス
- [ ] 食事画像アップロード → AI解析 → 確認 → 記録保存
- [ ] 食事記録一覧表示・検索・フィルタリング
- [ ] 栄養サマリー・グラフ表示

## 📊 成功指標

### 技術指標
- [ ] API レスポンス時間 < 500ms
- [ ] 食事記録作成成功率 > 95%
- [ ] UI操作レスポンシビリティ確保

### 機能指標
- [ ] Human-in-the-Loop確認 → 記録保存成功率 > 90%
- [ ] 手動食事記録作成の直感性確認
- [ ] 栄養データ集計の正確性確認

### UX指標
- [ ] サイドバーからの食事記録アクセス導線確認
- [ ] 食事記録一覧の視認性・操作性確認
- [ ] モバイル対応確認

## ⚠️ リスク・注意事項

### 技術的リスク
1. **大量データ処理**: 食事記録の蓄積によるパフォーマンス劣化
   - **対策**: 適切なインデックス設計、ページネーション実装

2. **栄養情報の精度**: AI解析結果の栄養データ信頼性
   - **対策**: 信頼度スコア表示、手動修正機能提供

3. **既存機能との混同**: 食事プランと食事記録の違いの明確化
   - **対策**: UI上での明確な区別、用語統一

### UX/UI リスク
1. **操作複雑性**: 食事記録入力の煩雑さ
   - **対策**: シンプルなフォーム設計、AI支援入力

2. **データ可視化**: 栄養情報の分かりやすい表示
   - **対策**: 直感的なグラフ・チャート使用

## 🔄 ロールバック計画

### Phase 1 ロールバック
- 新規エンティティ・UseCase・API削除
- Composition Root設定元に戻し

### Phase 2 ロールバック  
- Interactive Confirmation UseCase を元の食事プラン連携に戻し
- Meal Management Integration Tool 無効化

### Phase 3 ロールバック
- フロントエンド新規ページ・コンポーネント削除
- サイドバーメニュー項目削除

### 完全ロールバック
- データベーステーブル削除（データ移行スクリプト準備）
- 既存システムの動作確認

## 📝 参考資料

- **Human-in-the-Loop機能実装**: `docs/guides/new-tool-development.md`
- **Clean Architecture設計**: `docs/architecture/clean-architecture.md`  
- **API実装ガイド**: `docs/development/coding-standards.md`
- **フロントエンド規約**: `docs/development/coding-standards.md`

---

**実装担当**: Claude Code  
**レビュー要求**: フルスタック実装完了後  
**完了予定**: Phase毎の段階的実装