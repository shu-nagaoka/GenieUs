# GenieUs Documentation

GenieUs プロジェクトの包括的なドキュメント集

## 📚 ドキュメント構成

### 🏗️ [architecture/](architecture/) - アーキテクチャ設計思想
- `overview.md` - 全体アーキテクチャ概要
- `adk-first-design.md` - ADKファースト設計思想  
- `clean-architecture.md` - Clean Architecture適用方針
- `di-container-design.md` - DI設計とComposition Root
- `layer-responsibilities.md` - 各層の責務定義
- `future-roadmap.md` - 拡張性・将来展望

### 👨‍💻 [development/](development/) - 日常開発ガイド
- `quick-start.md` - 環境構築・起動コマンド
- `daily-workflow.md` - 開発ワークフロー
- `coding-standards.md` - コーディング規約・Import規約
- `testing-strategy.md` - テスト戦略・実行方法
- `environment-config.md` - 環境変数・設定管理
- `debugging.md` - デバッグ・トラブルシュート

### ⚙️ [technical/](technical/) - 技術詳細
- `adk-best-practices.md` - ADK制約・パターン
- `error-handling.md` - 段階的フォールバック戦略
- `logging-monitoring.md` - 構造化ログ・監視
- `performance.md` - パフォーマンス最適化
- `security.md` - セキュリティガイドライン

### 📖 [guides/](guides/) - 実装チュートリアル
- `new-agent-creation.md` - 新エージェント追加手順
- `new-tool-development.md` - 新ツール開発手順
- `new-usecase-impl.md` - 新UseCase実装手順
- `ui-component-guide.md` - フロントエンド開発
- `troubleshooting.md` - よくある問題と解決策

## 🎯 ドキュメント使用方法

### 目的別アクセス
```
🚀 すぐ開発開始     → development/quick-start.md
🏗️ 設計理解        → architecture/overview.md
👨‍💻 実装時の参照    → development/coding-standards.md
🔧 トラブル対応     → guides/troubleshooting.md
📖 新機能実装      → guides/{対応する実装ガイド}
```

### 学習パス
```
初心者  → development/quick-start.md → development/daily-workflow.md
中級者  → architecture/overview.md → technical/
上級者  → architecture/ 全体 → guides/implementation
```

## 🔗 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md) - Claude Code用エントリーポイント
- [DEVELOPMENT_GUIDELINES.md](../DEVELOPMENT_GUIDELINES.md) - レガシー開発ガイドライン（参考）
- [requirements.md](../requirements.md) - プロジェクト要求仕様

---

最終更新: $(date)
構成バージョン: v1.0