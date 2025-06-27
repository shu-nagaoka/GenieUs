# ルーティング戦略移行ガイド

## 概要

新しいルーティングシステムは、キーワードベース、LLM ベース、ハイブリッドの 3 つの戦略を簡単に切り替えられるように設計されています。

## 移行手順

### 1. 環境変数の設定

詳細な環境変数設定については **[環境変数設定ガイド](../../docs/development/environment-setup.md#-routing-strategy-新機能)** を参照してください。

基本設定：
```bash
ROUTING_STRATEGY=keyword    # キーワードベース（デフォルト、推奨）
ROUTING_STRATEGY=enhanced  # LLMベース（実験的）
```

### 2. AgentManager の切り替え

#### 方法 1: 最小限の変更（推奨）

`src/main.py`で：

```python
# 既存のインポートを変更
# from src.agents.agent_manager import AgentManager
from src.agents.agent_manager_v2 import AgentManagerV2 as AgentManager

# 残りのコードは変更不要
```

#### 方法 2: 段階的移行

```python
import os
from src.agents.agent_manager import AgentManager
from src.agents.agent_manager_v2 import AgentManagerV2

# 環境変数で切り替え
if os.getenv("USE_NEW_ROUTING", "false").lower() == "true":
    agent_manager = AgentManagerV2(tools=all_tools)
else:
    agent_manager = AgentManager(tools=all_tools)
```

### 3. A/B テストの実施

```python
import random
from src.agents.agent_manager import AgentManager
from src.agents.agent_manager_v2 import AgentManagerV2

# A/Bテスト用のマネージャー
class ABTestAgentManager:
    def __init__(self, tools, ab_ratio=0.5):
        self.manager_a = AgentManager(tools)  # 既存
        self.manager_b = AgentManagerV2(tools, routing_strategy="hybrid")  # 新戦略
        self.ab_ratio = ab_ratio

    async def run_agent(self, message, **kwargs):
        # ランダムに戦略を選択
        use_new = random.random() < self.ab_ratio

        if use_new:
            logger.info("🧪 A/Bテスト: 新戦略使用")
            result = await self.manager_b.run_agent(message, **kwargs)
            # メトリクス記録
            self._record_metrics("new_strategy", result)
        else:
            logger.info("🧪 A/Bテスト: 既存戦略使用")
            result = await self.manager_a.run_agent(message, **kwargs)
            self._record_metrics("old_strategy", result)

        return result
```

## 戦略比較テストの実行

### コマンドラインから：

```bash
# テストスクリプトの実行
python -m src.agents.test_routing_strategies

# 特定のメッセージでテスト
python -c "
from src.agents.agent_manager_v2 import AgentManagerV2
import asyncio

manager = AgentManagerV2(tools=[])
message = '離乳食を食べてくれません'

async def test():
    results = await manager.compare_routing_strategies(message)
    for strategy, result in results.items():
        print(f'{strategy}: {result['agent_name']}')

asyncio.run(test())
"
```

### プログラムから：

```python
# ルーティング精度の比較
async def compare_routing_accuracy():
    manager = AgentManagerV2(tools=all_tools)

    test_cases = [
        ("熱が38度あります", "health_specialist"),
        ("離乳食のレシピを教えて", "nutrition_specialist"),
        ("近くの小児科を検索", "search_specialist"),
        ("夜泣きがひどい", "sleep_specialist"),
    ]

    strategies = ["keyword", "llm", "hybrid"]
    results = {s: {"correct": 0, "total": 0} for s in strategies}

    for message, expected_agent in test_cases:
        comparison = await manager.compare_routing_strategies(message, strategies)

        for strategy, result in comparison.items():
            actual_agent = result["agent_id"]
            results[strategy]["total"] += 1
            if actual_agent == expected_agent:
                results[strategy]["correct"] += 1

    # 精度を表示
    print("\n📊 ルーティング精度比較:")
    for strategy, metrics in results.items():
        accuracy = metrics["correct"] / metrics["total"] * 100
        print(f"{strategy}: {accuracy:.1f}% ({metrics['correct']}/{metrics['total']})")
```

## メトリクスとモニタリング

### ルーティングメトリクスの確認：

```python
# メトリクスの取得
metrics = agent_manager.get_routing_metrics()
print(f"現在の戦略: {metrics['strategy']}")
print(f"総ルーティング数: {metrics['total_routings']}")
print(f"成功率: {metrics['success_rate']:.1%}")
print(f"平均確信度: {metrics['average_confidence']:.1%}")
```

### ログの確認：

```bash
# ルーティング決定の詳細ログ
grep "ルーティング決定" logs/app.log

# 戦略比較ログ
grep "ルーティング戦略比較" logs/app.log

# エラーログ
grep "ルーティングエラー" logs/app.log
```

## トラブルシューティング

### LLM ルーティングが機能しない

1. LLM クライアントが正しく設定されているか確認
2. `.env`で LLM 関連の環境変数を確認
3. フォールバック戦略が有効になっているか確認

### パフォーマンスが遅い

1. LLM ルーティングのタイムアウト設定を調整
2. ハイブリッド戦略の重みを調整（キーワード重視に）
3. キャッシュの有効化を検討

### 予期しないルーティング

1. ルーティングログで詳細を確認
2. 該当メッセージで戦略比較を実行
3. キーワード辞書の更新を検討

## ベストプラクティス

1. **段階的移行**: まずキーワードベースで動作確認してから新戦略を試す
2. **A/B テスト**: 本番環境では必ず A/B テストで効果を測定
3. **メトリクス監視**: ルーティング精度と応答時間を継続的に監視
4. **フィードバック収集**: ユーザーフィードバックを活用して精度向上
5. **定期的な評価**: 月次でルーティング精度を評価し、戦略を調整

## 今後の拡張

- ユーザーフィードバックによる自動学習
- カスタムルーティング戦略の追加
- ルーティング結果のキャッシュ
- 複数エージェントの並列実行最適化
