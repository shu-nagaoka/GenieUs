#!/bin/bash
# GCP CI/CD環境自動セットアップスクリプト
# Usage: ./scripts/setup-gcp-cicd.sh [project-id]

set -e

# カラー出力設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 GCP CI/CD環境自動セットアップ開始${NC}"
echo "=================================="

# プロジェクトID確認
if [ -z "$1" ]; then
    echo -e "${YELLOW}📋 利用可能なGCPプロジェクト一覧:${NC}"
    gcloud projects list --filter="name:blog*" --format="table(projectId,name,lifecycleState)"
    echo ""
    echo -e "${YELLOW}💡 使用方法: ./scripts/setup-gcp-cicd.sh [project-id]${NC}"
    echo "例: ./scripts/setup-gcp-cicd.sh blog-example-123456"
    exit 1
fi

PROJECT_ID="$1"
REGION="${2:-asia-northeast1}"
REPO_NAME="GenieUs"
GITHUB_OWNER="shu-nagaoka"

echo -e "${GREEN}✅ プロジェクト設定${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Repository: $GITHUB_OWNER/$REPO_NAME"
echo ""

# 1. プロジェクト設定
echo -e "${BLUE}🔧 Step 1: プロジェクト設定${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ プロジェクト設定完了: $PROJECT_ID${NC}"
echo ""

# 2. 必要なAPI有効化
echo -e "${BLUE}🔌 Step 2: 必要なAPI有効化${NC}"
APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "containerregistry.googleapis.com"
    "artifactregistry.googleapis.com"
    "aiplatform.googleapis.com"
    "iam.googleapis.com"
    "storage.googleapis.com"
    "logging.googleapis.com"
    "monitoring.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api --quiet
done
echo -e "${GREEN}✅ API有効化完了${NC}"
echo ""

# 3. サービスアカウント作成
echo -e "${BLUE}👤 Step 3: サービスアカウント作成${NC}"

# バックエンド用サービスアカウント
BACKEND_SA="genius-backend-sa"
if ! gcloud iam service-accounts describe ${BACKEND_SA}@${PROJECT_ID}.iam.gserviceaccount.com &>/dev/null; then
    echo "Creating backend service account..."
    gcloud iam service-accounts create $BACKEND_SA \
        --display-name="Genius Backend Service Account" \
        --description="Service account for Genius backend Cloud Run service"
    echo -e "${GREEN}✅ バックエンドサービスアカウント作成完了${NC}"
else
    echo -e "${YELLOW}⚠️ バックエンドサービスアカウント既存${NC}"
fi

# CI/CD用サービスアカウント
CICD_SA="genius-cicd-sa"
if ! gcloud iam service-accounts describe ${CICD_SA}@${PROJECT_ID}.iam.gserviceaccount.com &>/dev/null; then
    echo "Creating CI/CD service account..."
    gcloud iam service-accounts create $CICD_SA \
        --display-name="Genius CI/CD Service Account" \
        --description="Service account for GitHub Actions CI/CD"
    echo -e "${GREEN}✅ CI/CDサービスアカウント作成完了${NC}"
else
    echo -e "${YELLOW}⚠️ CI/CDサービスアカウント既存${NC}"
fi
echo ""

# 4. IAM権限設定
echo -e "${BLUE}🔐 Step 4: IAM権限設定${NC}"

# バックエンドサービスアカウント権限
BACKEND_ROLES=(
    "roles/aiplatform.user"
    "roles/storage.objectAdmin"
    "roles/logging.logWriter"
    "roles/monitoring.metricWriter"
)

echo "Setting backend service account permissions..."
for role in "${BACKEND_ROLES[@]}"; do
    echo "Granting $role to backend SA..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${BACKEND_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="$role" \
        --quiet || true
done

# CI/CDサービスアカウント権限
CICD_ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/cloudbuild.builds.builder"
    "roles/storage.admin"
    "roles/artifactregistry.admin"
    "roles/serviceusage.serviceUsageConsumer"
    "roles/cloudbuild.serviceAgent"
    "roles/source.admin"
)

echo "Setting CI/CD service account permissions..."
for role in "${CICD_ROLES[@]}"; do
    echo "Granting $role to CI/CD SA..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${CICD_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="$role" \
        --quiet || true
done
echo -e "${GREEN}✅ IAM権限設定完了${NC}"
echo ""

# 5. サービスアカウントキー生成
echo -e "${BLUE}🔑 Step 5: サービスアカウントキー生成${NC}"
KEY_FILE="./gcp-cicd-key.json"
if [ -f "$KEY_FILE" ]; then
    echo -e "${YELLOW}⚠️ 既存のキーファイルを削除します${NC}"
    rm "$KEY_FILE"
fi

gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=${CICD_SA}@${PROJECT_ID}.iam.gserviceaccount.com

echo -e "${GREEN}✅ サービスアカウントキー生成完了: $KEY_FILE${NC}"
echo ""

# 6. GitHub Secrets用値の準備
echo -e "${BLUE}📝 Step 6: GitHub Secrets用値の準備${NC}"

# NextAuth Secret生成
NEXTAUTH_SECRET=$(openssl rand -base64 32)

# Google OAuth情報（既存設定があれば使用、なければプレースホルダー）
GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-your-google-client-id}"
GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET:-your-google-client-secret}"

# 設定ファイル出力
cat > ./gcp-secrets.env << EOF
# GitHub Secrets設定用環境変数
# このファイルをGitHub Actionsシークレットに登録してください

GCP_PROJECT_ID=$PROJECT_ID
GCP_SA_KEY=$(cat $KEY_FILE | base64 -w 0)
NEXTAUTH_SECRET=$NEXTAUTH_SECRET
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
EOF

echo -e "${GREEN}✅ GitHub Secrets設定ファイル生成: ./gcp-secrets.env${NC}"
echo ""

# 7. Artifact Registry作成
echo -e "${BLUE}📦 Step 7: Artifact Registry作成${NC}"
REGISTRY_NAME="genius-registry"

if ! gcloud artifacts repositories describe $REGISTRY_NAME --location=$REGION &>/dev/null; then
    echo "Creating Artifact Registry..."
    gcloud artifacts repositories create $REGISTRY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="GenieUs Docker images repository"
    echo -e "${GREEN}✅ Artifact Registry作成完了${NC}"
else
    echo -e "${YELLOW}⚠️ Artifact Registry既存${NC}"
fi
echo ""

# 8. 設定確認
echo -e "${BLUE}🔍 Step 8: 設定確認${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Backend SA: ${BACKEND_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "CI/CD SA: ${CICD_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Registry: $REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_NAME"
echo ""

# 9. 次のステップ案内
echo -e "${GREEN}🎉 GCP環境セットアップ完了！${NC}"
echo "=================================="
echo ""
echo -e "${YELLOW}📋 次のステップ:${NC}"
echo "1. GitHub Secrets設定:"
echo "   ./scripts/setup-github-secrets.sh"
echo ""
echo "2. 初回デプロイテスト:"
echo "   ./scripts/test-deploy.sh $PROJECT_ID"
echo ""
echo "3. CI/CD パイプラインテスト:"
echo "   git push origin main"
echo ""
echo -e "${RED}⚠️ 重要: gcp-cicd-key.json は機密情報です。Git管理対象外にしてください${NC}"
echo ""

# セキュリティ警告
echo -e "${RED}🔒 セキュリティ注意事項:${NC}"
echo "- gcp-cicd-key.json をGitにコミットしないでください"
echo "- GitHub Secrets設定後にローカルファイルを削除してください"
echo "- 定期的にサービスアカウントキーを更新してください"