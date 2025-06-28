# Routing System Backup - 2025/06/27

## バックアップ内容

### 旧ルーティングシステム（独自実装）
- `enhanced_routing_backup.py` - Enhanced Routing Strategy実装
- `routing_strategy_backup.py` - ルーティング戦略インターフェース

### 特徴
- 複雑なパターンマッチング + 文脈分析
- ハイブリッドスコアリング（LLM + キーワード）
- 緊急度・感情分析機能
- 200行超の詳細な実装

### テスト結果
- 精度: 6/6 (100%)
- 対応エージェント: nutrition, sleep, development, behavior, work_life等

## 移行理由
ADK標準の`LlmAgent` + `sub_agents` + `transfer_to_agent()`パターンに移行

### 新システムメリット
- コード量1/20以下
- ADKフレームワーク準拠  
- 保守性向上
- LLMの真の活用

## 復元方法
```bash
# 旧システムに戻す場合
cp archive/routing_backup_20250627/enhanced_routing_backup.py src/agents/enhanced_routing.py
cp archive/routing_backup_20250627/routing_strategy_backup.py src/agents/routing_strategy.py
```

## 作成日時
2025-06-27 20:44 JST