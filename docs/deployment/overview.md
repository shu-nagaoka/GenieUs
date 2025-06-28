# Genius Cloud Run デプロイメントガイド

GeniusアプリケーションをGoogle Cloud Runにデプロイするためのガイドです。

## 🚀 クイックスタート

### 前提条件

1. **Google Cloud Project**: 有効なGCPプロジェクト
2. **gcloud CLI**: インストールと認証済み
3. **Docker**: ローカル環境にインストール済み
4. **必要な権限**: Cloud Run Admin, IAM Admin等

### 1. 環境変数設定

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="asia-northeast1"
```

### 2. ワンコマンドデプロイ

```bash
# ステージング環境
./scripts/deploy-cloud-run.sh staging

# 本番環境
./scripts/deploy-cloud-run.sh production
```

## 📋 詳細設定手順

### Step 1: Google Cloud Project設定

```bash
# プロジェクト作成（必要に応じて）
gcloud projects create your-project-id

# プロジェクト選択
gcloud config set project your-project-id

# 課金アカウント確認
gcloud billing projects describe your-project-id
```

### Step 2: OAuth認証設定

1. **Google Cloud Console** で OAuth 2.0クライアントID作成
2. **承認済みリダイレクトURI** に以下を追加:
   ```
   https://genius-frontend-staging.run.app/api/auth/callback/google
   https://genius-frontend-production.run.app/api/auth/callback/google
   ```

### Step 3: 環境変数設定

#### フロントエンド環境変数

```bash
# frontend/.env.production を作成
NEXTAUTH_URL=https://genius-frontend-{hash}.run.app
NEXTAUTH_SECRET=your-secret-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
BACKEND_API_URL=https://genius-backend-{hash}.run.app
```

#### バックエンド環境変数

```bash
# backend/.env.production を作成
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_AIPSK=your-adk-api-key
ENVIRONMENT=production
```

### Step 4: 手動デプロイ

#### バックエンドデプロイ

```bash
cd backend

gcloud run deploy genius-backend-production \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --service-account genius-backend-sa@your-project-id.iam.gserviceaccount.com \
  --set-env-vars ENVIRONMENT=production \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id \
  --cpu 1 \
  --memory 2Gi \
  --min-instances 1 \
  --max-instances 5
```

#### フロントエンドデプロイ

```bash
cd frontend

gcloud run deploy genius-frontend-production \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars NODE_ENV=production \
  --set-env-vars BACKEND_API_URL=https://genius-backend-production-xxx.run.app \
  --cpu 1 \
  --memory 1Gi \
  --min-instances 1 \
  --max-instances 10
```

## 🔧 CI/CD設定 (GitHub Actions)

### 必要なSecrets設定

GitHub リポジトリの Settings > Secrets で以下を設定:

```bash
GCP_PROJECT_ID=your-project-id
GCP_SA_KEY=your-service-account-json
NEXTAUTH_SECRET=your-nextauth-secret
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
```

### 自動デプロイフロー

```bash
# mainブランチ → production環境
git push origin main

# developブランチ → staging環境  
git push origin develop

# Pull Request → テスト実行のみ
```

## 🔐 セキュリティ設定

### IAM権限設定

```bash
# Cloud Run Invoker（必要に応じて）
gcloud run services add-iam-policy-binding genius-backend-production \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=asia-northeast1

# カスタムロール作成（最小権限）
gcloud iam roles create genius_backend_role \
  --project=your-project-id \
  --title="Genius Backend Role" \
  --permissions="aiplatform.endpoints.predict,storage.objects.create"
```

### VPCコネクタ設定（オプション）

```bash
# VPCコネクタ作成
gcloud compute networks vpc-access connectors create genius-connector \
  --region=asia-northeast1 \
  --subnet=default \
  --subnet-project=your-project-id \
  --min-instances=2 \
  --max-instances=10

# Cloud Runサービスに追加
--vpc-connector=genius-connector
--vpc-egress=private-ranges-only
```

## 📊 監視・ログ設定

### Cloud Loggingフィルタ

```bash
# フロントエンドログ
resource.type="cloud_run_revision"
resource.labels.service_name="genius-frontend-production"

# バックエンドログ
resource.type="cloud_run_revision"
resource.labels.service_name="genius-backend-production"
severity>=ERROR
```

### アラート設定

```bash
# レスポンス時間アラート
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/response-time-alert.yaml

# エラー率アラート
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/error-rate-alert.yaml
```

## 🔄 運用タスク

### 定期メンテナンス

```bash
# ログクリーンアップ
gcloud logging sinks create genius-logs-sink \
  bigquery.googleapis.com/projects/your-project-id/datasets/genius_logs

# コンテナイメージクリーンアップ
gcloud container images list-tags gcr.io/your-project-id/genius-frontend \
  --filter='timestamp.datetime < -P30D' \
  --format='get(digest)' | xargs -I {} gcloud container images delete gcr.io/your-project-id/genius-frontend@{}
```

### スケーリング調整

```bash
# 手動スケーリング
gcloud run services update genius-backend-production \
  --min-instances=2 \
  --max-instances=10 \
  --region=asia-northeast1
```

## 🐛 トラブルシューティング

### よくある問題

#### 1. 認証エラー
```bash
# サービスアカウントキー確認
gcloud iam service-accounts keys list \
  --iam-account=genius-backend-sa@your-project-id.iam.gserviceaccount.com
```

#### 2. メモリ不足
```bash
# メモリ使用量確認
gcloud run services describe genius-backend-production \
  --region=asia-northeast1 \
  --format='value(spec.template.spec.containers[0].resources.limits.memory)'
```

#### 3. Cold Start対策
```bash
# 最小インスタンス数を1に設定
gcloud run services update genius-backend-production \
  --min-instances=1 \
  --region=asia-northeast1
```

### ログ確認

```bash
# リアルタイムログ
gcloud run services logs tail genius-backend-production \
  --region=asia-northeast1

# エラーログのみ
gcloud run services logs read genius-backend-production \
  --region=asia-northeast1 \
  --filter='severity>=ERROR'
```

## 💰 コスト最適化

### リソース最適化チェックリスト

- [ ] **CPU制限**: 必要最小限のCPU設定
- [ ] **メモリ制限**: 実際の使用量に合わせた設定  
- [ ] **最小インスタンス**: 本番は1、開発は0
- [ ] **リクエストタイムアウト**: 適切なタイムアウト設定
- [ ] **イメージサイズ**: Dockerイメージの最適化

### 月次コスト見積もり

| リソース | 使用量 | 予想コスト |
|---------|--------|-----------|
| Cloud Run Frontend | 100K requests | $5-10 |
| Cloud Run Backend | 50K requests | $10-15 |
| Vertex AI (Gemini) | 100K tokens | $5-20 |
| Cloud Storage | 10GB | $2-3 |
| **合計** | | **$22-48** |

## 📚 参考リンク

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI in Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)