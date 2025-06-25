#!/bin/bash

# GeniusCloud Run deployment script
# Usage: ./scripts/deploy-cloud-run.sh [environment]

set -e

# デフォルト設定
ENVIRONMENT=${1:-staging}
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"asia-northeast1"}
SERVICE_ACCOUNT=${GCP_SERVICE_ACCOUNT:-"genius-backend-sa"}

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 必要な環境変数チェック
check_prerequisites() {
    log_info "Prerequisites チェック中..."
    
    if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
        log_error "GCP_PROJECT_ID環境変数を設定してください"
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLIがインストールされていません"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Dockerがインストールされていません"
        exit 1
    fi
    
    log_success "Prerequisites OK"
}

# GCP認証確認
check_auth() {
    log_info "GCP認証チェック中..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "GCPにログインしていません。'gcloud auth login'を実行してください"
        exit 1
    fi
    
    # プロジェクト設定
    gcloud config set project "$PROJECT_ID"
    
    log_success "GCP認証 OK (Project: $PROJECT_ID)"
}

# 必要なAPIの有効化
enable_apis() {
    log_info "必要なGCP APIを有効化中..."
    
    apis=(
        "run.googleapis.com"
        "containerregistry.googleapis.com"
        "artifactregistry.googleapis.com"
        "aiplatform.googleapis.com"
        "storage-api.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable "$api" --quiet
    done
    
    log_success "GCP APIs有効化完了"
}

# IAMサービスアカウント作成
setup_service_account() {
    log_info "サービスアカウント設定中..."
    
    # サービスアカウント作成（既に存在する場合はスキップ）
    if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" &>/dev/null; then
        log_info "サービスアカウント作成中: $SERVICE_ACCOUNT"
        gcloud iam service-accounts create "$SERVICE_ACCOUNT" \
            --display-name="Genius Backend Service Account" \
            --description="Service account for Genius backend Cloud Run service"
    else
        log_info "サービスアカウント既存: $SERVICE_ACCOUNT"
    fi
    
    # 必要な権限付与
    roles=(
        "roles/aiplatform.user"
        "roles/storage.objectAdmin"
        "roles/logging.logWriter"
        "roles/monitoring.metricWriter"
    )
    
    for role in "${roles[@]}"; do
        log_info "Granting role: $role"
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="$role" \
            --quiet
    done
    
    log_success "サービスアカウント設定完了"
}

# フロントエンドビルド・デプロイ
deploy_frontend() {
    log_info "フロントエンドデプロイ開始..."
    
    cd frontend
    
    # 環境別設定
    if [ "$ENVIRONMENT" = "production" ]; then
        SERVICE_NAME="genius-frontend"
        MIN_INSTANCES=1
        MAX_INSTANCES=10
    else
        SERVICE_NAME="genius-frontend-${ENVIRONMENT}"
        MIN_INSTANCES=0
        MAX_INSTANCES=5
    fi
    
    log_info "Building and deploying $SERVICE_NAME..."
    
    # Cloud Runデプロイ
    gcloud run deploy "$SERVICE_NAME" \
        --source . \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --port 3000 \
        --cpu 1 \
        --memory 1Gi \
        --min-instances "$MIN_INSTANCES" \
        --max-instances "$MAX_INSTANCES" \
        --set-env-vars "NODE_ENV=production" \
        --set-env-vars "BACKEND_API_URL=https://genius-backend-${ENVIRONMENT}-${PROJECT_ID}.run.app" \
        --quiet
    
    # URLを取得
    FRONTEND_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --platform managed \
        --region "$REGION" \
        --format 'value(status.url)')
    
    log_success "フロントエンドデプロイ完了: $FRONTEND_URL"
    
    cd ..
}

# バックエンドビルド・デプロイ
deploy_backend() {
    log_info "バックエンドデプロイ開始..."
    
    cd backend
    
    # 環境別設定
    if [ "$ENVIRONMENT" = "production" ]; then
        SERVICE_NAME="genius-backend"
        MIN_INSTANCES=1
        MAX_INSTANCES=5
    else
        SERVICE_NAME="genius-backend-${ENVIRONMENT}"
        MIN_INSTANCES=0
        MAX_INSTANCES=3
    fi
    
    log_info "Building and deploying $SERVICE_NAME..."
    
    # Cloud Runデプロイ
    gcloud run deploy "$SERVICE_NAME" \
        --source . \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --port 8000 \
        --cpu 1 \
        --memory 2Gi \
        --min-instances "$MIN_INSTANCES" \
        --max-instances "$MAX_INSTANCES" \
        --service-account "${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
        --set-env-vars "ENVIRONMENT=${ENVIRONMENT}" \
        --timeout 300 \
        --quiet
    
    # URLを取得
    BACKEND_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --platform managed \
        --region "$REGION" \
        --format 'value(status.url)')
    
    log_success "バックエンドデプロイ完了: $BACKEND_URL"
    
    cd ..
}

# デプロイ後のヘルスチェック
health_check() {
    log_info "ヘルスチェック実行中..."
    
    # バックエンドヘルスチェック
    if curl -f "${BACKEND_URL}/health" &>/dev/null; then
        log_success "バックエンドヘルスチェック OK"
    else
        log_warning "バックエンドヘルスチェック失敗"
    fi
    
    # フロントエンドヘルスチェック
    if curl -f "$FRONTEND_URL" &>/dev/null; then
        log_success "フロントエンドヘルスチェック OK"
    else
        log_warning "フロントエンドヘルスチェック失敗"
    fi
}

# デプロイサマリー表示
show_summary() {
    log_success "🚀 デプロイ完了!"
    echo ""
    echo "=========================="
    echo "Deployment Summary"
    echo "=========================="
    echo "Environment: $ENVIRONMENT"
    echo "Project: $PROJECT_ID"
    echo "Region: $REGION"
    echo ""
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL: $BACKEND_URL"
    echo ""
    echo "Next steps:"
    echo "1. Google OAuth設定でコールバックURLを更新"
    echo "2. 環境変数の設定"
    echo "3. カスタムドメインの設定（必要に応じて）"
    echo "=========================="
}

# メイン実行
main() {
    log_info "🚀 Genius Cloud Run deployment starting..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Project: $PROJECT_ID"
    log_info "Region: $REGION"
    
    check_prerequisites
    check_auth
    enable_apis
    setup_service_account
    deploy_backend
    deploy_frontend
    health_check
    show_summary
}

# エラーハンドリング
trap 'log_error "デプロイ中にエラーが発生しました"; exit 1' ERR

# 引数チェック
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [environment]"
    echo ""
    echo "Arguments:"
    echo "  environment    Deployment environment (staging/production) [default: staging]"
    echo ""
    echo "Environment variables:"
    echo "  GCP_PROJECT_ID     Google Cloud Project ID (required)"
    echo "  GCP_REGION         Deployment region [default: asia-northeast1]"
    echo "  GCP_SERVICE_ACCOUNT Service account name [default: genius-backend-sa]"
    echo ""
    echo "Examples:"
    echo "  $0 staging"
    echo "  $0 production"
    echo "  GCP_PROJECT_ID=my-project $0 staging"
    exit 0
fi

# スクリプト実行
main