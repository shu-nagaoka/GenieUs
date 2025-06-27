# CLAUDE.md

GenieUs開発ガイド - Claude Code用エントリーポイント

**「見えない成長に、光をあてる。不安な毎日を、自信に変える。」**

Google ADKを使用したAI子育て支援フルスタックアプリケーションの開発支援ドキュメント

## 🚀 すぐ始める

### 環境構築・起動
- **[開発クイックスタート](docs/development/quick-start.md)** - 3分で開発環境起動
- **[日常ワークフロー](docs/development/daily-workflow.md)** - 開発作業の流れ

### アクセスポイント
- **フロントエンドアプリ**: http://localhost:3000
- **チャット画面**: http://localhost:3000/chat
- **バックエンドAPI**: http://localhost:8000
- **API仕様書**: http://localhost:8000/docs
- **ADK Web UI**: http://localhost:8001

## 🏗️ アーキテクチャを理解する

### 設計思想
- **[アーキテクチャ概要](docs/architecture/overview.md)** - 全体設計の理解（**まずはここから**）
- **[ADKファースト設計](docs/architecture/adk-first-design.md)** - 核心思想
- **[Clean Architecture](docs/architecture/clean-architecture.md)** - 層責務と依存関係
- **[Composition Root設計](docs/architecture/composition-root-design.md)** - 中央集約型依存関係組み立て

### 現在の実装状況
```
✅ MVP実装完了
- 基本エージェント（シンプル子育て相談）
- 統合DIアーキテクチャ（Composition Root）
- RESTful API（チャット・ヘルス）
- Next.js基本UI
- 段階的エラーハンドリング

🔄 実装中・計画中
- 専門エージェント（睡眠・栄養・発達）
- マルチモーダル対応（音声・画像・動画）
- 予測インサイト・努力肯定システム
```

## 👨‍💻 実装時の必須参照

### コーディング規約（必読）
- **[コーディング規約](docs/development/coding-standards.md)** - **新規実装・レビュー時必読**
  - Import文配置規約（最重要）
  - 型アノテーション・エラーハンドリング
  - DI統合パターン
  - フロントエンド規約

### 技術詳細
- **[ADKベストプラクティス](docs/technical/adk-best-practices.md)** - ADK制約・パターン
- **[FastAPI DI統合](docs/technical/fastapi-di-integration.md)** - Depends + DIコンテナ統合
- **[エラーハンドリング戦略](docs/technical/error-handling.md)** - 段階的フォールバック
- **[ログ・モニタリング](docs/technical/logging-monitoring.md)** - 構造化ログ使用法

## 📖 新機能実装ガイド

### ステップバイステップガイド
- **[新エージェント作成](docs/guides/new-agent-creation.md)** - ADK統合エージェント実装
- **[新ツール開発](docs/guides/new-tool-development.md)** - FunctionTool開発手順
- **[新UseCase実装](docs/guides/new-usecase-impl.md)** - ビジネスロジック実装
- **[DI統合マイグレーション](docs/guides/di-migration-guide.md)** - ロガーDI化 + FastAPI Depends統合

### フロントエンド開発
- **[UIコンポーネントガイド](docs/guides/ui-component-guide.md)** - shadcn/ui + Tailwind

## 🔧 困ったときは

### トラブルシューティング
- **[トラブルシューティング](docs/guides/troubleshooting.md)** - よくある問題と解決策
- **[デバッグガイド](docs/development/debugging.md)** - デバッグ・ログ解析手法

### よくある質問
- **ポート使用中エラー**: `./scripts/stop_dev.sh` → `./scripts/start-dev.sh`
- **依存関係エラー**: バックエンド `uv sync`、フロントエンド `npm install`
- **ADKエラー**: `.env.dev`の環境変数設定確認

## 📋 重要コマンド

### 開発サーバー起動
```bash
# 🎯 推奨: ワンコマンド起動
./scripts/start-dev.sh        # 全サービス起動
./scripts/stop_dev.sh         # 全サービス停止
```

### 品質管理
```bash
# バックエンド
cd backend
uv run ruff check           # リンター
uv run ruff format          # フォーマット
uv run pytest              # テスト

# フロントエンド  
cd frontend
npm run lint                # ESLint
npm run format              # Prettier
npm run test                # Jestテスト
```

### API整合性管理
```bash
# 🎯 推奨: シンプルコマンド（プロジェクトルートから）
./check-api.sh                           # API URL整合性チェック
./update-api.sh                          # APIマッピング自動更新

# 🔍 詳細: Node.js直接実行
node scripts/check-api-consistency.js    # フロントエンド⇔バックエンド整合性検証
node scripts/update-api-mapping.js       # エンドポイント変更時の自動同期

# 📊 整合性統計表示
# - 総エンドポイント数、整合性率、不整合箇所を可視化
# - カラー出力で問題箇所を即座に特定
# - 自動バックアップ&復元機能付き
```

### ADK管理
```bash
# ADK Web UI単独起動
cd backend && python -m src.main adk
```

## 🎯 アーキテクチャ要点

### レイヤー構成
```
Agent Layer      ← ADK + Gemini（AI判断・ルーティング）
    ↓
Tools Layer      ← FunctionTool（薄いアダプター）
    ↓
Application Layer ← UseCase（ビジネスロジック）
    ↓
Infrastructure   ← 外部システム統合
```

### DI統合（Composition Root）
```python
# main.py - 中央集約組み立て
composition_root = CompositionRootFactory.create()
all_tools = composition_root.get_all_tools()
agent_manager = AgentManager(tools=all_tools, logger=composition_root.logger)
agent_manager.initialize_all_components()
```

### 重要原則
1. **ADKファースト**: エージェント中心の設計
2. **段階的複雑性**: シンプル→複雑へ段階的発展
3. **Composition Root**: main.pyでの中央集約組み立て（DIContainer完全置換）
4. **Import文先頭配置**: 依存関係の明確化（最重要）
5. **段階的フォールバック**: プライマリ→セカンダリ→フォールバック
6. **開発ポート分離**: 開発者ローカル用(3000/8000)、テスト用(30001/8001)の併用

## 📚 ドキュメント構成

| ディレクトリ | 内容 | 用途 |
|-------------|------|------|
| **[docs/architecture/](docs/architecture/)** | 設計思想・アーキテクチャ | 設計理解・議論 |
| **[docs/development/](docs/development/)** | 開発ワークフロー・規約 | 日常開発作業 |
| **[docs/technical/](docs/technical/)** | 技術詳細・ベストプラクティス | 実装時参照 |
| **[docs/guides/](docs/guides/)** | 実装チュートリアル | 新機能開発 |

## 🆘 サポート

**問題解決の順序**:
1. [トラブルシューティング](docs/guides/troubleshooting.md)で該当問題を確認
2. [コーディング規約](docs/development/coding-standards.md)で実装方針を確認
3. [アーキテクチャ概要](docs/architecture/overview.md)で設計思想を確認
4. 解決しない場合はプロジェクトチームに相談

---

## 🤖 AI開発支援ツール向け自律参照ガイド

### **🚨 重要**: 実装前必読ドキュメント
**すべての実装タスクで以下を必ず参照してください**:

1. **[コーディング規約](docs/development/coding-standards.md)** - 実装開始前に**必読**
2. **[アーキテクチャ概要](docs/architecture/overview.md)** - 設計判断時に**必読**

### **📋 タスクタイプ別必須参照マトリックス**

| タスク | 必須参照ドキュメント | チェックポイント |
|--------|---------------------|------------------|
| **🤖 新エージェント実装** | [新エージェント作成](docs/guides/new-agent-creation.md) + [コーディング規約](docs/development/coding-standards.md) | DI統合、ADK制約、型アノテーション、**ロガー注入** |
| **🔧 新ツール開発** | [新ツール開発](docs/guides/new-tool-development.md) + [コーディング規約](docs/development/coding-standards.md) | Protocol定義、薄いアダプター、エラーハンドリング、**ロガー注入** |
| **📋 UseCase実装** | [新UseCase実装](docs/guides/new-usecase-impl.md) + [アーキテクチャ概要](docs/architecture/overview.md) | レイヤー責務、依存関係の方向 |
| **🌐 API実装** | [FastAPI DI統合](docs/technical/fastapi-di-integration.md) + [コーディング規約](docs/development/coding-standards.md) | **Depends統合**、エラーハンドリング、**@inject使用** |
| **🎨 UI実装** | [UIコンポーネントガイド](docs/guides/ui-component-guide.md) + [コーディング規約](docs/development/coding-standards.md) | shadcn/ui、TypeScript規約、シンプルヘッダー設計 |
| **🐛 バグ修正** | [トラブルシューティング](docs/guides/troubleshooting.md) + [デバッグガイド](docs/development/debugging.md) | 段階的フォールバック、ログ確認 |
| **🏗️ アーキテクチャ変更** | [アーキテクチャ概要](docs/architecture/overview.md) + [Composition Root設計](docs/architecture/composition-root-design.md) | 設計思想、影響範囲 |
| **⚡ DI統合・マイグレーション** | [DI統合マイグレーション](docs/guides/di-migration-guide.md) + [FastAPI DI統合](docs/technical/fastapi-di-integration.md) | **ロガーDI化**、**Depends統合**、グローバル変数削除 |

### **⚠️ 実装前チェックリスト**

**実装開始前に以下を確認**:
- [ ] 該当タスクの必須ドキュメントを読了
- [ ] Import文配置規約を理解（ファイル先頭配置）
- [ ] 型アノテーション規約を理解
- [ ] エラーハンドリング戦略を理解
- [ ] **ロガーDI注入パターンを理解**（個別初期化禁止）
- [ ] **FastAPI Dependsパターンを理解**（@inject + Depends(Provide[])）

### **🔄 実装中の継続的チェック**

**コード実装中は以下を継続的に確認**:
- [ ] Import文がファイル先頭に配置されている
- [ ] 型アノテーションが完備されている
- [ ] エラーハンドリングが実装されている
- [ ] **ロガーはDIコンテナから注入されている**（setup_logger個別呼び出し禁止）
- [ ] **FastAPI Dependsパターンが使用されている**（グローバル変数禁止）
- [ ] レイヤー責務が守られている

### **❌ 絶対回避事項**

以下は**絶対に実装してはいけません**:
- [ ] 関数内でのimport文
- [ ] 型アノテーションなしの関数
- [ ] エラーハンドリングなしの外部API呼び出し
- [ ] **個別ロガー初期化**（setup_logger(__name__), logging.getLogger(__name__)）
- [ ] **グローバル変数の使用**（_container, _agent等）
- [ ] **setup_routes関数の使用**（非推奨パターン）
- [ ] **@injectデコレータなしのDepends使用**
- [ ] レイヤー責務を無視した実装
- [ ] **ポート競合**: 開発者ローカル(3000/8000)とテスト(30001/8001)の混在使用

---

**💡 開発効率のコツ**: まず[アーキテクチャ概要](docs/architecture/overview.md)で全体を把握し、[コーディング規約](docs/development/coding-standards.md)を熟読してから実装開始することで、手戻りを防げます。

**📖 ドキュメント体系**: この文書は軽量なナビゲーター。詳細は各専門ドキュメントを参照してください。