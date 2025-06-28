# 初回デプロイメントガイド

CI/CD環境構築後の初回デプロイメント実行手順

## 🎯 概要

CI/CD自動化スクリプトでGCP環境とGitHub Secretsの設定が完了した後、実際にCloud Runサービスを初回作成してデプロイメントパイプラインを動作確認します。

## 📋 前提条件確認

### 必須設定の確認

```bash
# 1. GitHub Secrets設定確認
gh secret list --repo shu-nagaoka/GenieUs

# 期待される出力:
# GCP_PROJECT_ID
# GCP_SA_KEY  
# NEXTAUTH_SECRET
# GOOGLE_CLIENT_ID
# GOOGLE_CLIENT_SECRET
```

```bash
# 2. GCP環境確認
gcloud config get-value project
gcloud iam service-accounts list --filter="displayName:Genius*"
gcloud artifacts repositories list --location=asia-northeast1
```

```bash
# 3. ワークフローファイル確認
ls -la .github/workflows/deploy-cloud-run.yml
```

## 🚀 初回デプロイ実行

### Method 1: GitHub Actions経由（推奨）

#### 1.1 テスト用PRでの動作確認

```bash
# テスト用ブランチ作成
git checkout -b test-initial-deploy

# 軽微な変更を追加（READMEなど）
echo "CI/CD Pipeline Test - $(date)" >> README.md
git add README.md
git commit -m "test: initial CI/CD pipeline deployment test"

# ブランチをプッシュ
git push origin test-initial-deploy

# PRを作成（staging環境へのデプロイがトリガーされる）
gh pr create \
  --title "Initial CI/CD Pipeline Test" \
  --body "CI/CDパイプラインの初回動作テスト

- [ ] Frontend staging デプロイ成功確認
- [ ] Backend staging デプロイ成功確認  
- [ ] サービス動作確認
- [ ] ヘルスチェック確認"
```

#### 1.2 GitHub Actions実行確認

```bash
# ワークフロー実行状況確認
gh run list --repo shu-nagaoka/GenieUs --limit 3

# 実行中のワークフローをリアルタイム監視
gh run watch --repo shu-nagaoka/GenieUs

# 特定実行の詳細ログ確認
gh run view [RUN_ID] --repo shu-nagaoka/GenieUs --log
```

#### 1.3 Staging環境動作確認

```bash
# Staging サービスURL取得
gcloud run services describe genius-frontend-staging \
  --region=asia-northeast1 \
  --format="value(status.url)"

gcloud run services describe genius-backend-staging \
  --region=asia-northeast1 \
  --format="value(status.url)"

# ヘルスチェック実行
curl -f https://genius-frontend-staging-[hash]-an.a.run.app || echo "Frontend health check failed"
curl -f https://genius-backend-staging-[hash]-an.a.run.app/health || echo "Backend health check failed"
```

#### 1.4 Production環境へのマージ

**Stagingでの動作確認が完了したら**:

```bash
# PRをmainブランチにマージ（production環境デプロイがトリガーされる）
gh pr merge --merge

# Production デプロイ確認
gh run watch --repo shu-nagaoka/GenieUs
```

### Method 2: 手動初回デプロイ（バックアップ手順）

GitHub Actionsでの初回デプロイが失敗する場合の手動手順:

#### 2.1 Backend手動デプロイ

```bash
cd backend

# Cloud Runサービス初回作成
gcloud run deploy genius-backend-production \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --service-account=genius-backend-sa@$(gcloud config get-value project).iam.gserviceaccount.com \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)" \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300
```

#### 2.2 Frontend手動デプロイ

```bash
cd frontend

# 環境変数設定
export NEXT_PUBLIC_API_URL="https://genius-backend-production-[hash]-an.a.run.app"

# Cloud Runサービス初回作成
gcloud run deploy genius-frontend-production \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=5 \
  --timeout=60
```

## 🔍 デプロイ成功確認

### サービス状態確認

```bash
# 全Cloud Runサービス一覧
gcloud run services list --region=asia-northeast1

# 個別サービス詳細確認
gcloud run services describe genius-backend-production \
  --region=asia-northeast1 \
  --format=export

gcloud run services describe genius-frontend-production \
  --region=asia-northeast1 \
  --format=export
```

### 動作確認テスト

#### Backend API確認

```bash
# BackendサービスURL取得
BACKEND_URL=$(gcloud run services describe genius-backend-production \
  --region=asia-northeast1 \
  --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"

# ヘルスチェック
curl -f ${BACKEND_URL}/health

# API動作確認
curl -f ${BACKEND_URL}/api/v1/agents

# OpenAPI仕様確認
curl -f ${BACKEND_URL}/docs
```

#### Frontend確認

```bash
# FrontendサービスURL取得
FRONTEND_URL=$(gcloud run services describe genius-frontend-production \
  --region=asia-northeast1 \
  --format="value(status.url)")

echo "Frontend URL: $FRONTEND_URL"

# ヘルスチェック
curl -f ${FRONTEND_URL}

# チャット画面アクセス確認
curl -f ${FRONTEND_URL}/chat
```

#### 統合動作確認

```bash
# Frontend → Backend API通信確認（実際のブラウザでテスト）
echo "ブラウザで以下をテスト:"
echo "1. Frontend URL: $FRONTEND_URL"
echo "2. チャット機能: $FRONTEND_URL/chat"
echo "3. API通信: デベロッパーツールでネットワークタブ確認"
```

## 📊 パフォーマンス確認

### レスポンス時間測定

```bash
# Backend API レスポンス時間
time curl -s ${BACKEND_URL}/health

# Frontend初期表示時間
time curl -s ${FRONTEND_URL}

# Cold Start時間測定（新リビジョンデプロイ後）
gcloud run services update genius-backend-production \
  --region=asia-northeast1 \
  --min-instances=0
  
# 5分待機後アクセスしてCold Start時間測定
sleep 300
time curl -s ${BACKEND_URL}/health
```

### リソース使用量確認

```bash
# Cloud Runメトリクス確認
gcloud monitoring metrics list --filter="resource.type=cloud_run_revision"

# 直近のメトリクス取得
gcloud logging read "resource.type=cloud_run_revision" \
  --format="csv(timestamp,resource.labels.service_name,severity)" \
  --limit=20
```

## 🚨 トラブルシューティング

### よくある初回デプロイエラー

#### 1. サービスアカウント権限不足

```bash
# エラー: Permission denied
# 解決方法: IAM権限の再確認・追加
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:genius-cicd-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

#### 2. Docker build失敗

```bash
# エラー: dockerfile build failed
# 解決方法: Dockerfileの構文確認
cd frontend && docker build -t test-frontend .
cd backend && docker build -t test-backend .
```

#### 3. GitHub Actions Secret不正

```bash
# エラー: Invalid service account key
# 解決方法: Secretの再生成・設定
./scripts/setup-gcp-cicd.sh $(gcloud config get-value project)
./scripts/setup-github-secrets.sh
```

#### 4. Cloud Runサービス作成失敗

```bash
# エラー: Cloud Run API not enabled
# 解決方法: API再有効化
gcloud services enable run.googleapis.com --project=$(gcloud config get-value project)

# エラー: Region not supported
# 解決方法: 利用可能リージョン確認
gcloud run regions list
```

### デバッグ手順

#### 1. ログ確認

```bash
# GitHub Actions ログ
gh run view [RUN_ID] --repo shu-nagaoka/GenieUs --log

# Cloud Build ログ
gcloud builds list --limit=5
gcloud builds log [BUILD_ID]

# Cloud Run ログ
gcloud logs read --service=genius-backend-production --limit=50
```

#### 2. 段階的デバッグ

```bash
# Step 1: Docker build ローカル確認
cd backend && docker build -t debug-backend .
cd frontend && docker build -t debug-frontend .

# Step 2: ローカル実行確認
docker run -p 8000:8000 -e GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) debug-backend
docker run -p 3000:3000 debug-frontend

# Step 3: 手動Cloud Runデプロイ
gcloud run deploy debug-backend-test \
  --source ./backend \
  --region=asia-northeast1 \
  --allow-unauthenticated
```

## ✅ デプロイ完了チェックリスト

### 必須確認項目

- [ ] GitHub Actions ワークフロー正常実行
- [ ] Backend Production サービス作成・稼働
- [ ] Frontend Production サービス作成・稼働
- [ ] Backend Staging サービス作成・稼働  
- [ ] Frontend Staging サービス作成・稼働
- [ ] ヘルスチェックエンドポイント応答正常
- [ ] Frontend → Backend API通信正常
- [ ] エラーログ無し

### パフォーマンス確認項目

- [ ] Cold Start時間 < 10秒
- [ ] API レスポンス時間 < 2秒
- [ ] Frontend初期表示時間 < 3秒
- [ ] メモリ使用率 < 80%
- [ ] CPU使用率 < 70%

### セキュリティ確認項目

- [ ] サービスアカウント最小権限設定
- [ ] HTTPS通信強制
- [ ] 機密情報の環境変数設定
- [ ] ローカル機密ファイル削除済み
- [ ] GitHub Secrets適切設定

## 🎯 次のステップ

初回デプロイが完了したら:

1. **[運用最適化](../deployment/optimization.md)** - パフォーマンス・コスト最適化
2. **[モニタリング設定](../deployment/monitoring.md)** - ログ・メトリクス・アラート
3. **[ドメイン設定](../deployment/custom-domain.md)** - カスタムドメイン・SSL証明書
4. **[バックアップ設定](../deployment/backup-strategy.md)** - データ・設定バックアップ

---

**関連ドキュメント**:
- [CI/CDセットアップガイド](../development/cicd-setup-guide.md)
- [CI/CDパイプライン概要](../deployment/cicd-pipeline.md)
- [トラブルシューティング](../guides/troubleshooting.md)