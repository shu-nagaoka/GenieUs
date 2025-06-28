# 📚 GenieUs Documentation

**「見えない成長に、光をあてる。不安な毎日を、自信に変える。」**

GenieUsプロジェクトの包括的なドキュメント集です。Google ADKを使用したAI子育て支援フルスタックアプリケーションの開発ドキュメントを、構造化されたWebビューアーで閲覧できます。

## 🚀 すぐ始める

### 推奨：高機能Webビューアー（自動更新対応）

```bash
# docsディレクトリから
./start-docs.sh                 # 高機能ビューアー
```

**アクセス先**: http://localhost:15080

**特徴**:
- 🔄 **マークダウン自動更新検知** (5秒間隔)
- 🔍 **リアルタイム検索** - ドキュメント全体から即座に検索
- 📋 **階層化ナビゲーション** - 構造化されたサイドバー
- 🎨 **シンタックスハイライト** - コードブロックの色分け
- 📱 **レスポンシブデザイン** - モバイル対応
- 📑 **ブラウザ履歴対応** - 戻る/進む操作

### 代替起動方法

```bash
# プロジェクトルートから（メイン開発環境と一緒）
./scripts/start-dev.sh docs     # ドキュメントサーバーのみ

# Pythonスクリプト直接実行
cd docs && python3 serve.py

# シンプル版HTML
./start-docs.sh simple
```

## 📖 ドキュメント構成

### 🏗️ [architecture/](architecture/) - アーキテクチャ設計思想
- **[overview.md](architecture/overview.md)** - 全体アーキテクチャ概要 ⭐ **（まずはここから）**
- [composition-root-design.md](architecture/composition-root-design.md) - Composition Root設計

### 👨‍💻 [development/](development/) - 日常開発ガイド
- **[quick-start.md](development/quick-start.md)** - 3分で環境構築 ⭐
- **[coding-standards.md](development/coding-standards.md)** - コーディング規約 ⭐ **（実装時必読）**
- [environment-setup.md](development/environment-setup.md) - 環境設定詳細
- [claude-code-integration.md](development/claude-code-integration.md) - Claude Code統合
- [refactoring-plans.md](development/refactoring-plans.md) - リファクタリング計画・完了報告

### ⚙️ [technical/](technical/) - 技術詳細・ベストプラクティス
- [adk-constraints-and-best-practices.md](technical/adk-constraints-and-best-practices.md) - ADKベストプラクティス
- [fastapi-di-integration.md](technical/fastapi-di-integration.md) - FastAPI DI統合
- [function-declaration-guide.md](technical/function-declaration-guide.md) - 関数宣言ガイド
- [layer-return-values.md](technical/layer-return-values.md) - レイヤー戻り値設計
- [usecase-design-rules.md](technical/usecase-design-rules.md) - UseCase設計ルール
- **[adk-routing-integration.md](technical/adk-routing-integration.md)** - ADK標準ルーティング統合ガイド ⭐
- [routing-stability-improvements.md](technical/routing-stability-improvements.md) - ルーティング安定化改善
- **[routing-system-migration.md](technical/routing-system-migration.md)** - ルーティングシステム移行完了報告 ⭐

### 📖 [guides/](guides/) - 実装チュートリアル
- [new-agent-creation.md](guides/new-agent-creation.md) - 新エージェント作成手順
- [di-migration-guide.md](guides/di-migration-guide.md) - DI統合マイグレーション
- [authentication-system-explained.md](guides/authentication-system-explained.md) - 認証システム解説
- [user-authentication-implementation.md](guides/user-authentication-implementation.md) - ユーザー認証実装
- [agent-manager-architecture-guide.md](guides/agent-manager-architecture-guide.md) - AgentManager設計ガイド

### 🚀 [deployment/](deployment/) - デプロイメント
- [overview.md](deployment/overview.md) - デプロイ概要
- [quickstart.md](deployment/quickstart.md) - クイックスタート
- [infrastructure.md](deployment/infrastructure.md) - インフラ構築
- [cloud-build-guide.md](deployment/cloud-build-guide.md) - Cloud Buildガイド
- [entrypoint-cloud-run-guide.md](deployment/entrypoint-cloud-run-guide.md) - entrypoint.sh Cloud Runガイド
- [checklist.md](deployment/checklist.md) - チェックリスト

### 📋 [plan/](plan/) - 実装プラン
- [parallel-agent-collaborative-reports.md](plan/parallel-agent-collaborative-reports.md) - 並列エージェント協調レポート

### 🎫 [issue/](issue/) - Issue管理・完了報告
- [image-auto-prompt-and-ui-exclusivity.md](issue/image-auto-prompt-and-ui-exclusivity.md) - 画像自動プロンプト・UI排他性
- [frontend-performance-optimization-completed.md](issue/frontend-performance-optimization-completed.md) - フロントエンド性能最適化（Phase 1完了）
- [frontend-performance-optimization.md](issue/frontend-performance-optimization.md) - フロントエンド性能最適化（継続）

## 🎯 目的別アクセスガイド

### 🚀 すぐ開発開始
```
開発開始 → development/quick-start.md
規約確認 → development/coding-standards.md
```

### 🏗️ 設計理解
```
全体把握 → architecture/overview.md
DI理解  → architecture/composition-root-design.md
```

### 👨‍💻 実装時の参照
```
新エージェント → guides/new-agent-creation.md
新ツール      → guides/new-tool-development.md
トラブル対応   → guides/troubleshooting.md
```

### 🔧 技術詳細
```
ADK制約    → technical/adk-constraints-and-best-practices.md
DI統合     → technical/fastapi-di-integration.md
エラー処理  → technical/error-handling.md
```

## 🔧 技術仕様

### Webビューアー仕様
- **ポート**: 15080 (レアケースポート使用)
- **自動更新**: 5秒間隔でMarkdownファイル監視
- **プロトコル**: HTTP
- **CORS**: 有効（ローカル開発用）

### 使用技術
- **マークダウンパーサー**: [marked.js](https://marked.js.org/)
- **シンタックスハイライト**: [Prism.js](https://prismjs.com/)
- **HTTPサーバー**: Python `http.server`
- **フロントエンド**: バニラHTML/CSS/JavaScript

### ファイル構成
```
docs/
├── web/                        # 新世代Webビューアー
│   ├── index.html             # メインビューアー（自動更新対応）
│   ├── assets/
│   │   ├── styles.css         # CSS
│   │   └── viewer.js          # JavaScript  
│   └── config/
│       └── navigation.json    # ナビゲーション設定
├── index.html                 # レガシー版ビューアー
├── serve.py                   # ドキュメントサーバー
├── start-docs.sh             # 起動スクリプト
├── README.md                 # このファイル
├── docs.log                  # サーバーログ（自動生成）
├── .docs.pid                 # プロセスID（自動生成）
├── architecture/             # アーキテクチャドキュメント
├── development/              # 開発ガイド
├── technical/                # 技術詳細
├── guides/                   # 実装ガイド
├── deployment/               # デプロイメント
├── plan/                     # 実装プラン
└── issue/                    # Issue管理・完了報告
```

## 🛠️ カスタマイズ

### ナビゲーション追加
```json
// web/config/navigation.json
{
  "sections": [
    {
      "id": "new_section",
      "title": "🆕 新セクション",
      "items": [
        {
          "title": "📝 新ドキュメント",
          "file": "path/to/new-doc.md"
        }
      ]
    }
  ]
}
```

### 新しいドキュメント追加
1. `docs/` 以下に `.md` ファイルを配置
2. `web/config/navigation.json` に追加
3. 自動更新により即座に反映

## 🐛 トラブルシューティング

### ポート15080が使用中
```bash
# 使用中プロセス確認
lsof -i :15080

# 強制停止
./scripts/start-dev.sh stop
```

### 自動更新が動作しない
1. ブラウザの開発者ツールでエラー確認
2. ファイルパスが正しいか確認
3. サーバーログ確認: `tail -f docs/docs.log`

### Python3が見つからない
```bash
# macOS (Homebrew)
brew install python3

# Ubuntu/Debian
sudo apt install python3
```

## 🔗 関連ドキュメント

- **[CLAUDE.md](../CLAUDE.md)** - Claude Code用エントリーポイント（AI開発支援ツール向け）
- [requirements.md](../requirements.md) - プロジェクト要求仕様

## 💡 ドキュメント管理のコツ

- **マークダウン更新時**: サーバー再起動不要、自動反映
- **ナビゲーション変更時**: `navigation.json`編集後、ブラウザリロード
- **モバイル閲覧**: レスポンシブ対応で快適に閲覧可能
- **検索活用**: サイドバーの検索でドキュメント横断検索

---

**最終更新**: 2025-06-27  
**構成バージョン**: v2.0 (自動更新対応)