# GenieUs デプロイメント管理

統一されたデプロイメント管理システム

## 📁 ディレクトリ構造

```
deployment/
├── cloud-build/          # Cloud Build使用パターン
│   ├── staging.sh       # ステージング環境
│   ├── production.sh    # 本番環境
│   └── cloudbuild.yaml  # Cloud Build設定
├── gcloud-direct/        # gcloudコマンド直接パターン  
│   ├── staging.sh       # ステージング環境
│   └── production.sh    # 本番環境
├── shared/              # 共通機能
│   ├── common.sh        # 共通関数
│   ├── env-loader.sh    # 環境変数読み込み
│   └── secret-manager.sh# Secret Manager統合
└── README.md           # このファイル
```

## 🚀 デプロイ方式

### 1. Cloud Build デプロイ
**推奨方式**: ローカルDockerが不要、高速並行ビルド

```bash
# ステージング
./deployment/cloud-build/staging.sh

# 本番
./deployment/cloud-build/production.sh
```

**特徴**:
- ☁️ サーバーレスビルド
- 🚀 高速並行実行
- 💾 ローカルリソース消費なし
- 📊 Cloud Buildログで詳細確認

### 2. gcloud直接デプロイ
**詳細制御用**: ローカルDockerでビルド、リアルタイムログ

```bash
# ステージング
./deployment/gcloud-direct/staging.sh

# 本番
./deployment/gcloud-direct/production.sh
```

**特徴**:
- 🐳 ローカルDockerビルド
- 📋 リアルタイムログ出力
- 🔍 詳細なエラー情報
- 🏷️ タグ付きイメージ管理

## 🔐 Secret Manager統合

両方のデプロイ方式でSecret Manager統合をサポート:

### 対応シークレット
- `nextauth-secret`: NextAuth認証秘密鍵
- `google-oauth-client-id`: Google OAuth クライアントID
- `google-oauth-client-secret`: Google OAuth クライアントシークレット
- `postgres-password`: PostgreSQLパスワード

### 使用方法
1. デプロイ実行時にSecret Manager更新の確認
2. `y`で同意すると`environments/.env.staging`または`environments/.env.production`から値を反映
3. 自動的にCloud RunでSecret Manager参照設定

## 📋 環境設定

### 必須環境変数
```bash
# environments/.env.staging または environments/.env.production
GCP_PROJECT_ID=your-project-id
GCP_REGION=asia-northeast1
BACKEND_SERVICE_NAME=genius-backend-staging
FRONTEND_SERVICE_NAME=genius-frontend-staging
DATABASE_TYPE=postgresql  # または sqlite
CLOUD_SQL_CONNECTION_NAME=project:region:instance
```

### 本番環境追加必須
```bash
NEXTAUTH_SECRET=your-nextauth-secret
GOOGLE_CLIENT_ID=your-oauth-client-id
GOOGLE_CLIENT_SECRET=your-oauth-client-secret
```

## 🎯 entrypoint.sh統合

統合エントリーポイントから簡単実行:

```bash
./entrypoint.sh
```

- **Option 20**: インタラクティブCloud Build (環境選択 + Secret Manager統合)
- **Option 21**: Cloud Build 本番デプロイ
- **Option 22**: gcloud直接 ステージングデプロイ
- **Option 23**: gcloud直接 本番デプロイ
- **Option 33**: 詳細インタラクティブデプロイ (アカウント・プロジェクト選択含む)

## ⚠️ 本番デプロイ注意事項

### デプロイ前確認
- [ ] 環境変数設定完了
- [ ] Secret Manager値設定完了
- [ ] GCP認証確認
- [ ] プロジェクト権限確認

### デプロイ後確認
- [ ] サービス正常起動確認
- [ ] API動作確認
- [ ] ログ監視設定
- [ ] パフォーマンス監視

## 🔧 トラブルシューティング

### よくある問題

1. **Docker未起動** (gcloud直接デプロイ)
   ```bash
   # Dockerを起動
   sudo systemctl start docker  # Linux
   open -a Docker               # macOS
   ```

2. **GCP認証エラー**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Secret Manager権限不足**
   ```bash
   # 必要な権限を確認
   gcloud projects get-iam-policy YOUR_PROJECT_ID
   ```

### ログ確認
```bash
# Cloud Run ログ
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Cloud Build ログ
gcloud builds list --limit=10
```

## 📈 パフォーマンス比較

| 項目 | Cloud Build | gcloud直接 |
|------|-------------|------------|
| ビルド速度 | ⚡ 高速 | 🐢 中速 |
| ローカルリソース | 💾 不要 | 🐳 使用 |
| ログ詳細度 | 📊 中程度 | 📋 高 |
| デバッグ容易性 | 🔍 中程度 | 🐛 高 |
| 推奨用途 | 🚀 日常デプロイ | 🔧 開発・調査 |

---

## 🗑️ 削除された機能

- ❌ GitHub Actions CI/CD
- ❌ 旧scripts/配下の重複スクリプト
- ❌ 従来型デプロイ関数

新しい統一デプロイメントシステムを使用してください。