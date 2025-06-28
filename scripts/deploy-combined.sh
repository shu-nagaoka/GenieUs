#!/bin/bash

# GenieUs Combined Deployment Script for Cloud Run
# フロントエンド + バックエンド統合デプロイ

set -e

ENVIRONMENT=${1:-staging}
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"asia-northeast1"}

# 色付きログ
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 統合デプロイメント
deploy_combined() {
    log_info "🚀 統合アプリケーションをデプロイ中..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        SERVICE_NAME="genieus-app"
        MIN_INSTANCES=1
        MAX_INSTANCES=10
        MEMORY="4Gi"
        CPU="2"
    else
        SERVICE_NAME="genieus-app-${ENVIRONMENT}"
        MIN_INSTANCES=0
        MAX_INSTANCES=5
        MEMORY="2Gi"
        CPU="1"
    fi
    
    # 統合Dockerfileでデプロイ
    gcloud run deploy "$SERVICE_NAME" \
        --source . \
        --dockerfile Dockerfile.combined \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --port 8080 \
        --cpu "$CPU" \
        --memory "$MEMORY" \
        --min-instances "$MIN_INSTANCES" \
        --max-instances "$MAX_INSTANCES" \
        --set-env-vars "ENVIRONMENT=${ENVIRONMENT}" \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
        --timeout 300 \
        --quiet
    
    # URLを取得
    APP_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --platform managed \
        --region "$REGION" \
        --format 'value(status.url)')
    
    log_success "✅ 統合アプリケーションデプロイ完了: $APP_URL"
    
    return 0
}

# ヘルスチェック
health_check() {
    log_info "ヘルスチェック実行中..."
    
    if curl -f "${APP_URL}/health" &>/dev/null; then
        log_success "✅ バックエンドヘルスチェック OK"
    else
        log_warning "⚠️ バックエンドヘルスチェック失敗"
    fi
    
    if curl -f "$APP_URL" &>/dev/null; then
        log_success "✅ フロントエンドヘルスチェック OK"
    else
        log_warning "⚠️ フロントエンドヘルスチェック失敗"
    fi
}

# メイン実行
main() {
    log_info "🎯 GenieUs統合デプロイメント開始"
    log_info "Environment: $ENVIRONMENT"
    log_info "Project: $PROJECT_ID"
    
    deploy_combined
    health_check
    
    echo ""
    log_success "🎉 統合デプロイメント完了!"
    echo "Application URL: $APP_URL"
    echo "Frontend: $APP_URL"
    echo "Backend API: $APP_URL/api/"
    echo "Health Check: $APP_URL/health"
}

# スクリプト実行
main