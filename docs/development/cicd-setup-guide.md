# CI/CDセットアップガイド - 自動化スクリプト使用法

GenieUsのCI/CDパイプライン自動構築ガイド

## 🚀 ワンコマンドセットアップ

### entrypoint.sh 統合メニュー

```bash
./entrypoint.sh
```

**CI/CD関連メニュー**:
- **選択肢29**: GCP CI/CD環境自動構築
- **選択肢30**: GitHub Secrets自動設定  
- **選択肢31**: CI/CDパイプライン動作テスト

## 📋 事前準備

### 1. 必要ツールのインストール

```bash
# Google Cloud CLI
# macOS
brew install google-cloud-sdk

# Ubuntu
curl https://sdk.cloud.google.com | bash

# GitHub CLI
# macOS
brew install gh

# Ubuntu
sudo apt install gh
```

### 2. 認証設定

```bash
# GCP認証
gcloud auth login
gcloud auth application-default login

# GitHub認証
gh auth login --scopes repo,workflow
```

### 3. プロジェクト準備

```bash
# 既存GCPプロジェクト確認（blog-*）
gcloud projects list --filter="name:blog*"

# プロジェクト設定
gcloud config set project blog-your-project-id
```

## 🔧 ステップバイステップ実行

### Step 1: GCP CI/CD環境構築

```bash
# 方法1: entrypoint.sh メニューから
./entrypoint.sh
# → 選択肢29を選択

# 方法2: スクリプト直接実行
./scripts/setup-gcp-cicd.sh blog-your-project-id
```

**実行内容**:
- ✅ 必要なGCP API有効化
- ✅ サービスアカウント作成（genius-backend-sa, genius-cicd-sa）
- ✅ IAM権限設定
- ✅ サービスアカウントキー生成
- ✅ Artifact Registry作成
- ✅ GitHub Secrets用設定ファイル生成

**出力ファイル**:
- `gcp-cicd-key.json` - CI/CD用サービスアカウントキー
- `gcp-secrets.env` - GitHub Secrets設定用環境変数

### Step 2: GitHub Secrets設定

```bash
# 方法1: entrypoint.sh メニューから
./entrypoint.sh
# → 選択肢30を選択

# 方法2: スクリプト直接実行  
./scripts/setup-github-secrets.sh
```

**設定される内容**:
- ✅ `GCP_PROJECT_ID` - GCPプロジェクトID
- ✅ `GCP_SA_KEY` - CI/CD用サービスアカウントキー（Base64エンコード）
- ✅ `NEXTAUTH_SECRET` - NextAuth.js用ランダム文字列
- ✅ `GOOGLE_CLIENT_ID` - Google OAuth2設定（要手動設定）
- ✅ `GOOGLE_CLIENT_SECRET` - Google OAuth2設定（要手動設定）

**Repository Variables**:
- ✅ `GCP_REGION` - asia-northeast1
- ✅ `REGISTRY_LOCATION` - asia-northeast1
- ✅ `DOCKER_REGISTRY` - asia-northeast1-docker.pkg.dev

### Step 3: CI/CDパイプライン動作テスト

```bash
# 方法1: entrypoint.sh メニューから
./entrypoint.sh
# → 選択肢31を選択

# 方法2: 手動テスト
git checkout -b test-cicd
git commit --allow-empty -m "test: CI/CD pipeline test"
git push origin test-cicd
gh pr create --title "Test CI/CD Pipeline" --body "CI/CD動作テスト"
gh pr merge --merge
```

## 🔍 設定確認方法

### GCP設定確認

```bash
# プロジェクト設定確認
gcloud config get-value project

# サービスアカウント確認
gcloud iam service-accounts list --filter="displayName:Genius*"

# API有効化確認
gcloud services list --enabled --filter="name:run.googleapis.com OR name:cloudbuild.googleapis.com"

# Artifact Registry確認
gcloud artifacts repositories list --location=asia-northeast1
```

### GitHub設定確認

```bash
# Secrets一覧確認
gh secret list --repo shu-nagaoka/GenieUs

# Variables一覧確認
gh variable list --repo shu-nagaoka/GenieUs

# ワークフロー一覧確認
gh workflow list --repo shu-nagaoka/GenieUs
```

### ワークフロー実行確認

```bash
# 最新の実行確認
gh run list --repo shu-nagaoka/GenieUs --limit 5

# 特定実行の詳細
gh run view [RUN_ID] --repo shu-nagaoka/GenieUs

# 実行をリアルタイム監視
gh run watch --repo shu-nagaoka/GenieUs
```

## 🔐 セキュリティ対策

### 自動清掃機能

スクリプト実行後、機密ファイルの自動削除確認が表示されます:

```bash
# setup-github-secrets.sh 実行後
⚠️ ローカルのサービスアカウントキーファイルを削除しますか？ (y/N)
⚠️ ローカルの設定ファイルを削除しますか？ (y/N)
```

**推奨**: 必ず `y` を選択して機密ファイルを削除してください。

### 手動清掃

```bash
# 機密ファイル手動削除
rm -f gcp-cicd-key.json gcp-secrets.env

# .gitignore 確認
grep -E "(\.json|\.env)" .gitignore
```

## 🚨 トラブルシューティング

### よくあるエラーと解決方法

#### 1. gcloud認証エラー
```bash
# エラー: gcloud authentication required
# 解決方法:
gcloud auth login
gcloud auth application-default login
```

#### 2. GitHub CLI認証エラー
```bash
# エラー: gh authentication required  
# 解決方法:
gh auth login --scopes repo,workflow
gh auth status  # 認証状態確認
```

#### 3. GCPプロジェクト権限不足
```bash
# エラー: permission denied
# 確認方法:
gcloud projects get-iam-policy [PROJECT_ID] \
  --flatten="bindings[].members" \
  --filter="bindings.members:$(gcloud config get-value account)"
```

#### 4. API未有効化エラー
```bash
# エラー: API has not been used
# 解決方法:
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

#### 5. Secrets設定失敗
```bash
# エラー: could not create secret
# 確認方法:
gh auth status
gh api user  # GitHub API アクセス確認

# 再設定:
gh secret set GCP_PROJECT_ID --body "your-project-id" --repo shu-nagaoka/GenieUs
```

### デバッグ用コマンド

#### 詳細ログ出力
```bash
# GCP操作の詳細ログ
export CLOUDSDK_CORE_VERBOSITY=debug
./scripts/setup-gcp-cicd.sh blog-your-project-id

# GitHub CLI詳細ログ  
export GH_DEBUG=1
./scripts/setup-github-secrets.sh
```

#### 段階的実行
```bash
# 各ステップを個別実行
gcloud services enable run.googleapis.com
gcloud iam service-accounts create genius-cicd-sa
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:genius-cicd-sa@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

## 💡 カスタマイズ

### 環境固有の設定変更

#### リージョン変更
```bash
# scripts/setup-gcp-cicd.sh の REGION 変更
REGION="us-central1"  # デフォルト: asia-northeast1
```

#### サービスアカウント名変更
```bash
# scripts/setup-gcp-cicd.sh の SA名変更
BACKEND_SA="custom-backend-sa"
CICD_SA="custom-cicd-sa"
```

#### リポジトリ設定変更
```bash
# scripts/setup-github-secrets.sh のリポジトリ変更
REPO_OWNER="your-github-username"
REPO_NAME="your-repo-name"
```

### 追加の Secrets/Variables

```bash
# カスタムSecret追加
gh secret set CUSTOM_SECRET --body "custom-value" --repo shu-nagaoka/GenieUs

# カスタムVariable追加
gh variable set CUSTOM_VAR --body "custom-value" --repo shu-nagaoka/GenieUs
```

## 📝 設定記録テンプレート

CI/CD設定後、以下の情報を記録してください:

```yaml
# cicd-config-record.yml
project_info:
  gcp_project_id: "blog-your-project-id"
  region: "asia-northeast1"
  setup_date: "2025-06-28"

service_accounts:
  backend: "genius-backend-sa@blog-your-project-id.iam.gserviceaccount.com"
  cicd: "genius-cicd-sa@blog-your-project-id.iam.gserviceaccount.com"

repositories:
  artifact_registry: "asia-northeast1-docker.pkg.dev/blog-your-project-id/genius-registry"
  github: "shu-nagaoka/GenieUs"

services:
  frontend_prod: "genius-frontend-production"
  backend_prod: "genius-backend-production"
  frontend_staging: "genius-frontend-staging" 
  backend_staging: "genius-backend-staging"

monitoring:
  setup_completed: true
  alerts_configured: false  # Phase 4で設定
  backup_configured: false  # Phase 4で設定
```

---

**次のステップ**: [初回デプロイ実行](../deployment/initial-deployment.md)  
**関連ドキュメント**: [CI/CDパイプライン概要](../deployment/cicd-pipeline.md)