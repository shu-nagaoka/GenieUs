# Quick Start Guide

GenieUs プロジェクトの環境構築から開発開始まで。**3分で開発環境を起動**します。

## 🚀 最速スタートアップ

### Step 1: リポジトリクローン・移動
```bash
git clone <repository-url>
cd GieieNest
```

### Step 2: 開発環境起動（推奨）
```bash
# 🎯 ワンコマンドで全サービス起動
./scripts/start-dev.sh        # 開発環境起動

# 停止時
./scripts/stop_dev.sh         # 全サービス停止
```

### Step 3: アクセス確認
起動完了後、以下のURLにアクセス：

| サービス | URL | 説明 |
|---------|-----|------|
| **フロントエンドアプリ** | http://localhost:3000 | メインアプリケーション |
| **チャット画面** | http://localhost:3000/chat | 子育て相談チャット |
| **バックエンドAPI** | http://localhost:8000 | FastAPI サーバー |
| **API仕様書** | http://localhost:8000/docs | SwaggerUI ドキュメント |
| **ADK Web UI** | http://localhost:8001 | Google ADK 管理画面 |

## 🛠️ 個別サービス開発

### バックエンド開発
```bash
cd backend

# 依存関係セットアップ
uv sync                      # 依存関係インストール

# 開発サーバー起動（手動）
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# テスト・品質管理
uv run pytest              # テスト実行
uv run pytest tests/test_specific.py  # 単体テスト実行
uv run ruff check           # リンター実行
uv run ruff format          # コードフォーマット

# ADK Web UI起動（エージェント管理）
python -m src.main adk
```

### フロントエンド開発
```bash
cd frontend

# 依存関係セットアップ
npm install                 # 依存関係インストール

# 開発サーバー起動
npm run dev                 # 開発サーバー起動（Turbopack使用）

# ビルド・デプロイ
npm run build               # 本番ビルド（Prisma migrations含む）

# テスト・品質管理
npm run test                # Jestテスト実行
npm run test:coverage       # カバレッジ付きテスト実行
npm run test:e2e            # Playwright E2Eテスト実行

# コード品質
npm run lint                # ESLint実行
npm run lint:fix            # リント問題の自動修正
npm run format              # Prettierフォーマット
```

## 🔧 代替起動方法

### Docker Compose使用
```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up -d

# 本番環境
docker-compose -f docker-compose.yml up -d
```

## ⚠️ トラブルシューティング

### よくある問題

#### ポートが使用中のエラー
```bash
./scripts/stop_dev.sh  # 全サービス停止後
./scripts/start-dev.sh # 再起動
```

#### 依存関係の問題
```bash
# バックエンド
cd backend && uv sync

# フロントエンド  
cd frontend && npm install
```

#### 環境変数未設定
```bash
# .env.dev ファイルが存在するか確認
ls backend/.env.dev

# サンプルファイルからコピー（存在しない場合）
cp backend/.env.example backend/.env.dev
```

## 📋 開発環境要件

### 必須ツール
- **Python 3.12+** - バックエンド実行環境
- **uv** - Python パッケージマネージャー
- **Node.js 18+** - フロントエンド実行環境
- **npm** - Node.js パッケージマネージャー
- **Docker & Docker Compose** - コンテナ環境（オプション）

### 推奨ツール
- **Google Cloud CLI** - ADK統合用
- **VS Code** - 開発エディタ
- **Claude Code Extension** - Claude統合

## 🎯 次のステップ

✅ 環境起動完了後の推奨アクション：

1. **アーキテクチャ理解** → [architecture/overview.md](../architecture/overview.md)
2. **コーディング規約確認** → [development/coding-standards.md](./coding-standards.md) 
3. **実装チュートリアル** → [guides/new-agent-creation.md](../guides/new-agent-creation.md)

## 🆘 サポート

問題が解決しない場合：
- [トラブルシューティングガイド](../guides/troubleshooting.md)
- [デバッグガイド](./debugging.md)
- プロジェクトチームへの問い合わせ

---

**💡 Tip**: 開発効率を上げるため、IDE設定とClaude Code統合も設定することを推奨します。