# エージェントルーティング安定化改善報告書

## 🎯 問題分析と解決策

### 現在の問題点

1. **LLMベースルーティングの不安定性**
   - 温度設定0.7で決定論的でない結果
   - 睡眠相談で栄養専門家が回答するなどの誤ルーティング

2. **キーワードマッチングの脆弱性**
   - 単純な文字列マッチングで文脈を考慮しない
   - 複数専門領域の優先順位が曖昧
   - 否定形表現への対応不足

3. **フォールバック機能の不備**
   - エラー時の代替手段が限定的
   - 品質検証・リトライ機能の欠如

## 🛠️ 実装した解決策

### 1. キーワードベース事前フィルタリング強化

#### constants.py追加機能
- **AGENT_PRIORITY**: 専門領域ごとの優先度設定（健康・安全=5、発達・特別支援=4、栄養・睡眠・メンタル=3、行動・仕事両立=2、遊び=1）
- **FORCE_ROUTING_KEYWORDS**: 緊急性の高い強制ルーティングキーワード
- **拡張AGENT_KEYWORDS**: 否定形・具体表現を含む包括的キーワード

```python
# 強制ルーティング例
FORCE_ROUTING_KEYWORDS = {
    "health_specialist": ["熱", "発熱", "38度", "救急", "緊急"],
    "safety_specialist": ["事故", "転落", "誤飲", "やけど"],
    "special_support_specialist": ["自閉症", "発達障害", "ADHD"]
}
```

### 2. LLM設定安定化

#### 決定論的ルーティング実装
- **temperature: 0.7 → 0.2**: 決定論的出力のための調整
- **スコアベース決定**: マッチ数 × 優先度 × キーワード長さ重みの計算
- **競合ログ**: 複数候補がある場合の詳細ログ出力

```python
def _determine_specialist_agent(self, message_lower: str) -> str:
    """決定論的専門エージェント選択"""
    agent_scores = {}
    for agent_id, keywords in AGENT_KEYWORDS.items():
        if agent_id in AGENT_PRIORITY:
            matched_keywords = [kw for kw in keywords if kw in message_lower]
            if matched_keywords:
                keyword_weight = sum(len(kw) for kw in matched_keywords)
                score = len(matched_keywords) * AGENT_PRIORITY[agent_id] * (1 + keyword_weight * 0.1)
                agent_scores[agent_id] = {"score": score, "matched_keywords": matched_keywords}
```

### 3. ルールベース・フォールバック機能

#### 4段階フォールバック機能
1. **強制ルーティング**: 緊急性の高いキーワード
2. **決定論的専門選択**: スコアベース最適選択
3. **フォールバック階層**: nutrition → health → development
4. **最終フォールバック**: coordinator直接対応

#### 品質検証・リトライ機能
```python
async def _route_to_specific_agent_with_fallback(
    self, agent_id: str, message: str, ..., retry_count: int = 0, max_retries: int = 2
):
    """フォールバック機能付き専門エージェント実行"""
    # レスポンス品質検証
    if self._validate_agent_response(response, agent_id, message):
        return response
    else:
        # リトライまたはフォールバック実行
```

### 4. 検証・監視機能

#### ルーティング妥当性チェック
- **事前検証**: 明らかに不適切なルーティングの検出
- **自動修正**: 不適切な場合の自動ルーティング修正
- **詳細ログ**: ルーティング決定プロセスの完全可視化

```python
def _validate_routing_decision(self, message: str, selected_agent: str) -> bool:
    """不適切ルーティングの検出"""
    inappropriate_routing = {
        "sleep_specialist": ["食事", "離乳食", "栄養"],
        "nutrition_specialist": ["夜泣き", "寝ない", "睡眠"]
    }
```

## 📊 期待される改善効果

### 1. ルーティング精度向上
- **強制ルーティング**: 緊急性の高い相談で100%正確なルーティング
- **決定論的選択**: 同じ相談内容で常に同じ専門家選択
- **競合解決**: 複数専門領域にまたがる相談の適切な優先付け

### 2. 可用性向上
- **リトライ機能**: 一時的エラーからの自動回復
- **フォールバック**: エージェント障害時の代替対応
- **品質保証**: 不適切な回答の事前検出・修正

### 3. 運用監視強化
- **詳細ログ**: ルーティング決定の完全トレーサビリティ
- **性能監視**: ルーティング判定時間の測定
- **品質監視**: 専門性の妥当性チェック

## 🧪 テストケース

### 基本ルーティングテスト
```python
# 栄養相談
"離乳食を食べてくれません" → nutrition_specialist

# 睡眠相談  
"夜泣きがひどくて困っています" → sleep_specialist

# 緊急性（強制ルーティング）
"熱が38度あります" → health_specialist (強制)
"転落して頭を打ちました" → safety_specialist (強制)
```

### 複合的ケーステスト
```python
# 健康 > 栄養 (優先度ベース)
"熱があるときの離乳食はどうすればいい？" → health_specialist

# 否定形対応
"食べてくれない時はどうする？" → nutrition_specialist
"寝てくれないんです" → sleep_specialist
```

### 不適切ルーティング修正テスト
```python
# 自動修正例
Input: "離乳食について"
Inappropriate: sleep_specialist
Auto-correct: nutrition_specialist
```

## 🔧 実装ファイル

### 主要修正ファイル
1. **`src/agents/constants.py`**: キーワード・優先度・強制ルーティング設定
2. **`src/agents/agent_manager.py`**: ルーティングロジック・フォールバック・監視機能
3. **`src/agents/routing_test_cases.py`**: 包括的テストケース

### 新機能
- **決定論的ルーティング**: スコアベース専門家選択
- **強制ルーティング**: 緊急性対応
- **品質検証**: レスポンス妥当性チェック
- **自動修正**: 不適切ルーティングの検出・修正
- **詳細監視**: ルーティング決定の完全ログ

## 📈 今後の展開

### 1. 機械学習ベース改善（将来）
- ユーザーフィードバックによるルーティング精度向上
- 相談パターン学習による自動最適化

### 2. A/Bテスト
- 新旧ルーティングロジックの比較検証
- ユーザー満足度の定量評価

### 3. 継続的監視
- ルーティング精度の定期的測定
- 不適切ケースの継続的発見・改善

この改善により、エージェントルーティングの安定性と信頼性が大幅に向上し、ユーザーが適切な専門家から一貫性のあるアドバイスを受けられるようになります。