# AgentManager リファクタリング計画

## 現状の問題点

### 1. コードの重複
- `agent_manager.py` (約1700行) と `routing_strategy.py` で同じルーティングロジックが重複
- 戦略パターン導入により、多くのメソッドが不要に

### 2. ハードコードされた定数
- 並列分析キーワード（15個）
- 順次分析キーワード（7個）
- エージェント応答検証パターン
- エラー判定キーワード
- フォールバック優先順位

### 3. 未使用のレガシーコード
- ルーティングメッセージ生成システム（約200行）
- 専門家名抽出ロジック
- 各種理由説明生成メソッド

## リファクタリング手順

### Phase 1: 定数の整理
1. `constants_additions.py`の内容を`constants.py`に統合
2. agent_manager.py内のハードコードされたリストを削除

### Phase 2: 重複コードの削除
1. 戦略パターンで実装済みのルーティングメソッドを削除
   - `_check_force_routing()`
   - `_is_parallel_analysis_requested()`
   - `_is_sequential_analysis_requested()`
   - `_determine_specialist_agent()`

### Phase 3: レガシーコードの削除
1. ルーティングメッセージ生成システムの削除
   - `_get_specialist_name_from_response()`
   - `_create_routing_message()`
   - 各種 `_get_*_reason()` メソッド

### Phase 4: メソッドの統合
1. 類似機能のメソッドを統合
   - `_validate_routing_decision()` + `_auto_correct_routing()`
   - `_route_to_specific_agent()` + `_route_to_specific_agent_with_fallback()`

## 期待される効果

- **コード削減**: 約1700行 → 約800-900行（約50%削減）
- **保守性向上**: 重複排除により変更箇所が1箇所に
- **テスタビリティ向上**: 戦略パターンにより個別テストが容易に
- **拡張性向上**: 新しいルーティング戦略の追加が簡単に

## 注意事項

- 既存のAPIインターフェースは維持
- ADKランナー管理機能は影響を受けない
- 段階的にリファクタリングを実施し、各段階でテストを確認