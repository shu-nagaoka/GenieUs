#!/bin/bash
# 環境変数ファイルを使用してCloud Buildデプロイを実行

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 使用方法
usage() {
    echo "Usage: $0 <environment> [project-id]"
    echo ""
    echo "Environments:"
    echo "  staging     - Staging環境にデプロイ"
    echo "  production  - Production環境にデプロイ"
    echo ""
    echo "Examples:"
    echo "  $0 staging"
    echo "  $0 production blog-sample-381923"
    exit 1
}

# 引数チェック
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
fi

ENVIRONMENT=$1
PROJECT_ID=${2:-""}

# 環境変数を読み込み
source scripts/load-env.sh "$ENVIRONMENT"

# プロジェクトIDの設定
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$GCP_PROJECT_ID
fi

echo -e "${BLUE}🚀 GenieUs Deployment with Environment File${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "Project: ${GREEN}$PROJECT_ID${NC}"
echo -e "Region: ${GREEN}$GCP_REGION${NC}"
echo ""

# デプロイ確認
if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${YELLOW}⚠️  WARNING: You are about to deploy to PRODUCTION!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

# 置換変数を生成
echo -e "${BLUE}🔧 Generating Cloud Build substitutions...${NC}"
EXPORT_SUBSTITUTIONS=true
SUBSTITUTIONS=$(source scripts/load-env.sh "$ENVIRONMENT" | grep -v "^🔧\|^✅\|^⚠️" | tail -1)

# Cloud Build用の追加設定は load-env.sh で処理済み

echo -e "${GREEN}✅ Substitutions generated${NC}"

# Cloud Buildトリガー
echo -e "${BLUE}🏗️  Starting Cloud Build deployment...${NC}"
gcloud builds submit \
    --config cloudbuild-env.yaml \
    --substitutions="$SUBSTITUTIONS" \
    --project="$PROJECT_ID" \
    --timeout=30m

# デプロイ結果を確認
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}🔍 Checking deployed services...${NC}"
    
    # サービスURLを取得
    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE_NAME" \
        --region="$GCP_REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)" 2>/dev/null || echo "Not found")
    
    FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE_NAME" \
        --region="$GCP_REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)" 2>/dev/null || echo "Not found")
    
    echo ""
    echo -e "${GREEN}🎉 Deployment Summary${NC}"
    echo -e "${GREEN}====================${NC}"
    echo -e "Frontend: ${BLUE}$FRONTEND_URL${NC}"
    echo -e "Backend: ${BLUE}$BACKEND_URL${NC}"
    echo -e "API Docs: ${BLUE}$BACKEND_URL/docs${NC}"
    echo ""
    
    # OAuth設定のリマインダー
    if [[ "$GOOGLE_CLIENT_ID" == *"your-"* ]]; then
        echo -e "${YELLOW}⚠️  Remember to set up Google OAuth:${NC}"
        echo "   1. Go to Google Cloud Console > APIs & Services > Credentials"
        echo "   2. Add these redirect URIs:"
        echo "      - $FRONTEND_URL/api/auth/callback/google"
        echo ""
    fi
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    exit 1
fi