# 環境変数設定ガイド

GenieUs の環境変数設定を一元管理するガイドです。開発環境から本番環境まで、すべての設定を体系的に説明します。

## 📁 設定ファイル構成

```bash
backend/
├── .env.dev                    # 開発環境（現在使用中）
└── .env.production.example     # 本番環境テンプレート
```

## 🔧 開発環境設定

### 基本セットアップ

1. **設定ファイルの確認**

   ```bash
   # 開発環境設定ファイルが存在することを確認
   ls backend/.env.dev
   ```

2. **現在の設定値を確認**
   ```bash
   cd backend
   python -c "from src.config.settings import get_settings; settings = get_settings(); print(f'APP_NAME: {settings.APP_NAME}', f'ROUTING_STRATEGY: {settings.ROUTING_STRATEGY}')"
   ```

### `.env.dev` 設定項目詳細

#### Core Application

```bash
APP_NAME=GenieUs                # アプリケーション名
ENVIRONMENT=development         # 環境識別子
PORT=8000                      # バックエンドサーバーポート
```

#### Google Cloud Configuration

```bash
GOOGLE_CLOUD_PROJECT=blog-sample-381923    # GCPプロジェクトID（必須）
GOOGLE_CLOUD_LOCATION=us-central1          # GCPリージョン
GOOGLE_GENAI_USE_VERTEXAI=True             # Vertex AI使用フラグ
```

#### Network Settings

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:30001  # CORS許可オリジン
```

#### Database Configuration

```bash
DATABASE_URL=sqlite:///./data/genieus.db   # データベース接続URL
DATABASE_TYPE=sqlite                       # データベース種別
```

#### Security Settings (Development)

```bash
JWT_SECRET=dev-jwt-secret-key              # JWT暗号化キー（開発用）
JWT_EXPIRE_MINUTES=1440                    # JWT有効期限（分）
```

#### File Storage

```bash
BUCKET_NAME=genieus-files-dev              # GCSバケット名
```

#### Logging

```bash
LOG_LEVEL=DEBUG                            # ログレベル（開発：DEBUG）
LOG_FORMAT=json                            # ログフォーマット
```

#### **🔀 Routing Strategy** (新機能)

```bash
ROUTING_STRATEGY=keyword                   # ルーティング戦略
HYBRID_KEYWORD_WEIGHT=0.4                 # キーワード重み
HYBRID_LLM_WEIGHT=0.6                     # LLM重み
ENABLE_AB_TEST=false                       # A/Bテスト有効化
AB_TEST_RATIO=0.5                         # A/Bテスト比率
ROUTING_LOG_LEVEL=INFO                    # ルーティングログレベル
COLLECT_ROUTING_METRICS=true              # メトリクス収集
```

#### NextAuth.js (Development)

```bash
NEXTAUTH_URL=http://localhost:3000        # NextAuth URL
# 以下は認証テスト時のみ設定
# GOOGLE_CLIENT_ID=your_client_id
# GOOGLE_CLIENT_SECRET=your_client_secret
# NEXTAUTH_SECRET=your_secret
```

#### Optional API Keys

```bash
# 以下は必要に応じて設定
# GOOGLE_API_KEY=your_api_key              # Gemini API直接利用時
# GOOGLE_AIPSK=your_adk_key                # ADK API利用時
```

## 🚀 本番環境設定

### `.env.production.example` から本番用設定作成

1. **テンプレートをコピー**

   ```bash
   cp backend/.env.production.example backend/.env.production
   ```

2. **本番用値に変更**
   ```bash
   # 以下の値を本番環境用に変更
   vim backend/.env.production
   ```

### 本番環境での主な違い

| 設定項目         | 開発環境           | 本番環境           |
| ---------------- | ------------------ | ------------------ |
| **PORT**         | 8000               | 8080 (Cloud Run)   |
| **LOG_LEVEL**    | DEBUG              | INFO               |
| **DATABASE**     | SQLite             | PostgreSQL         |
| **BUCKET_NAME**  | genieus-files-dev  | genieus-files-prod |
| **CORS_ORIGINS** | localhost          | 本番ドメイン       |
| **認証設定**     | 任意               | 必須               |
| **JWT_SECRET**   | dev-jwt-secret-key | 強力なシークレット |

### 本番環境必須設定

```bash
# 認証関連（必須）
GOOGLE_CLIENT_ID=your_google_oauth_client_id_prod
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret_prod
NEXTAUTH_SECRET=your_nextauth_secret_key_prod
JWT_SECRET=your_production_jwt_secret_key

# データベース（PostgreSQL）
DATABASE_URL=postgresql://user:pass@host:port/genieus_prod
DATABASE_TYPE=postgresql

# 本番URL
NEXTAUTH_URL=https://genieus-frontend.run.app
CORS_ORIGINS=https://genieus-frontend.run.app
```

## 🔀 ルーティング戦略設定

### 利用可能な戦略

| 戦略       | 説明                               | 推奨環境   |
| ---------- | ---------------------------------- | ---------- |
| `keyword`  | キーワードマッチング（デフォルト） | 開発・本番 |
| `enhanced` | LLM ベース意図理解                 | 実験環境   |

### ルーティング設定の変更

1. **キーワードルーティング（推奨）**

   ```bash
   ROUTING_STRATEGY=keyword
   ```

2. **エンハンスドルーティング（実験的）**

   ```bash
   ROUTING_STRATEGY=enhanced
   HYBRID_KEYWORD_WEIGHT=0.3  # キーワード重み調整
   HYBRID_LLM_WEIGHT=0.7      # LLM重み調整
   ```

3. **A/B テスト（将来機能）**
   ```bash
   ENABLE_AB_TEST=true
   AB_TEST_RATIO=0.3          # 30%のユーザーで新戦略テスト
   ```

### ルーティング設定の確認

```bash
# 現在のルーティング戦略確認
python -c "from src.config.settings import get_settings; print(f'現在の戦略: {get_settings().ROUTING_STRATEGY}')"
```

## 🛠️ 環境別起動方法

### 開発環境起動

```bash
# 推奨：ワンコマンド起動
./scripts/start-dev.sh

# 個別起動
cd backend && uvicorn src.main:app --reload --port 8000
cd frontend && npm run dev
```

### 本番環境起動

```bash
# Cloud Run向け
PORT=8080 uvicorn src.main:app --host 0.0.0.0 --port 8080
```

## 🔍 トラブルシューティング

### よくあるエラーと解決策

#### 1. `GOOGLE_CLOUD_PROJECT` が設定されていない

```bash
# エラー例
ValueError: 必須フィールドが設定されていません: GOOGLE_CLOUD_PROJECT

# 解決策
echo 'GOOGLE_CLOUD_PROJECT=blog-sample-381923' >> backend/.env.dev
```

#### 2. ポート競合エラー

```bash
# エラー例
OSError: [Errno 48] Address already in use

# 解決策
./scripts/stop_dev.sh  # 既存プロセス停止
./scripts/start-dev.sh # 再起動
```

#### 3. 認証エラー（本番環境）

```bash
# エラー例
ValueError: 本番環境では認証設定が必須

# 解決策：本番環境では以下が必須
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
NEXTAUTH_SECRET=your_secret
JWT_SECRET=your_jwt_secret
```

#### 4. データベース接続エラー

```bash
# 開発環境：SQLiteファイル権限確認
ls -la backend/data/
chmod 664 backend/data/genieus.db

# 本番環境：PostgreSQL接続確認
psql $DATABASE_URL -c "SELECT 1;"
```

### 設定値検証

```bash
# 全設定値の確認
cd backend
python -c "
from src.config.settings import get_settings
import json
settings = get_settings()
config = {k: getattr(settings, k) for k in dir(settings) if not k.startswith('_')}
print(json.dumps(config, indent=2, default=str))
"
```

## 🔗 関連ドキュメント

- **[開発クイックスタート](quick-start.md)** - 基本的な開発環境構築
- **[デプロイメントガイド](../DEPLOYMENT.md)** - 本番環境デプロイ手順
- **[認証システム](../guides/authentication-system-explained.md)** - 認証設定詳細
- **[DI 統合ガイド](../guides/di-migration-guide.md)** - DI パターンと設定の関係

## 📝 設定変更時のチェックリスト

- [ ] 開発環境で動作確認
- [ ] 本番環境設定の更新
- [ ] 関連ドキュメントの更新
- [ ] チーム共有
- [ ] セキュリティ設定の確認（本番のみ）

---

**💡 ヒント**: 新しい環境変数を追加する場合は、必ず `src/config/settings.py` にフィールドを追加し、両方の `.env` ファイルを更新してください。
