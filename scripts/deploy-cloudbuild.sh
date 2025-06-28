#!/bin/bash

# GenieUs Cloud Build統合デプロイスクリプト
# ローカルDockerを使わずにCloud Buildで完結
# Usage: ./scripts/deploy-cloudbuild.sh [environment] [project-id]

set -e

# 引数とデフォルト値
ENVIRONMENT=${1:-staging}
PROJECT_ID=${2:-${GCP_PROJECT_ID:-"your-project-id"}}
REGION=${GCP_REGION:-"asia-northeast1"}
BUILD_TIMEOUT=${BUILD_TIMEOUT:-"20m"}

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_build() {
    echo -e "${PURPLE}[BUILD]${NC} $1"
}

# バナー表示
show_banner() {
    echo ""
    echo "🏗️ ========================================"
    echo "   GenieUs Cloud Build Deployment"
    echo "   Environment: $ENVIRONMENT"
    echo "   Project: $PROJECT_ID"
    echo "   Region: $REGION"
    echo "======================================== 🏗️"
    echo ""
}

# 前提条件チェック
check_prerequisites() {
    log_info "前提条件をチェック中..."
    
    # プロジェクトIDチェック
    if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
        log_error "プロジェクトIDが設定されていません"
        log_error "使用方法: $0 [environment] [project-id]"
        log_error "または: export GCP_PROJECT_ID=your-project-id"
        exit 1
    fi
    
    # gcloud CLIチェック
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLIがインストールされていません"
        log_error "インストール: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # 認証チェック
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "GCPにログインしていません"
        log_error "実行: gcloud auth login"
        exit 1
    fi
    
    log_success "前提条件チェック完了"
}

# GCPプロジェクト設定
setup_project() {
    log_info "GCPプロジェクト設定中..."
    
    # プロジェクト設定
    gcloud config set project "$PROJECT_ID"
    
    # Cloud Build API有効化
    log_info "Cloud Build APIを有効化中..."
    gcloud services enable cloudbuild.googleapis.com --quiet
    
    log_success "プロジェクト設定完了"
}

# 環境変数設定の収集
collect_env_vars() {
    log_info "環境変数を収集中..."
    
    # 必須環境変数のチェック
    ENV_VARS=""
    
    # Google API設定
    if [ -n "$GOOGLE_API_KEY" ]; then
        ENV_VARS="$ENV_VARS,_GOOGLE_API_KEY=$GOOGLE_API_KEY"
    fi
    
    if [ -n "$GOOGLE_AIPSK" ]; then
        ENV_VARS="$ENV_VARS,_GOOGLE_AIPSK=$GOOGLE_AIPSK"
    fi
    
    # OAuth設定
    if [ -n "$GOOGLE_CLIENT_ID" ]; then
        ENV_VARS="$ENV_VARS,_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID"
    fi
    
    if [ -n "$GOOGLE_CLIENT_SECRET" ]; then
        ENV_VARS="$ENV_VARS,_GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET"
    fi
    
    if [ -n "$NEXTAUTH_SECRET" ]; then
        ENV_VARS="$ENV_VARS,_NEXTAUTH_SECRET=$NEXTAUTH_SECRET"
    fi
    
    # その他の設定
    ROUTING_STRATEGY=${ROUTING_STRATEGY:-"enhanced"}
    LOG_LEVEL=${LOG_LEVEL:-"INFO"}
    
    ENV_VARS="$ENV_VARS,_ROUTING_STRATEGY=$ROUTING_STRATEGY,_LOG_LEVEL=$LOG_LEVEL"
    
    # 先頭のカンマを削除
    ENV_VARS=${ENV_VARS#,}
    
    log_success "環境変数収集完了"
}

# Cloud Buildでデプロイ実行
execute_cloud_build() {
    log_build "Cloud Buildでデプロイを開始..."
    log_build "ビルドログはCloud ConsoleのCloud Buildセクションで確認できます"
    
    # 置換変数の準備
    SUBSTITUTIONS="_GCP_PROJECT_ID=$PROJECT_ID,_ENVIRONMENT=$ENVIRONMENT,_GCP_REGION=$REGION"
    
    if [ -n "$ENV_VARS" ]; then
        SUBSTITUTIONS="$SUBSTITUTIONS,$ENV_VARS"
    fi
    
    log_info "置換変数: $SUBSTITUTIONS"
    log_info "タイムアウト: $BUILD_TIMEOUT"
    
    # Cloud Build実行
    BUILD_ID=$(gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions="$SUBSTITUTIONS" \
        --timeout="$BUILD_TIMEOUT" \
        --format="value(id)" \
        .)
    
    if [ $? -eq 0 ]; then
        log_success "Cloud Buildが完了しました"
        log_info "Build ID: $BUILD_ID"
        
        # ビルドログのURL
        log_info "詳細ログ: https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID"
        
        # デプロイされたサービスのURL取得
        get_service_urls
    else
        log_error "Cloud Buildが失敗しました"
        log_error "ログを確認してください: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
        exit 1
    fi
}

# デプロイされたサービスのURL取得
get_service_urls() {
    log_info "デプロイされたサービスのURLを取得中..."
    
    # サービス名の決定
    if [ "$ENVIRONMENT" = "production" ]; then
        BACKEND_SERVICE="genius-backend"
        FRONTEND_SERVICE="genius-frontend"
    else
        BACKEND_SERVICE="genius-backend-$ENVIRONMENT"
        FRONTEND_SERVICE="genius-frontend-$ENVIRONMENT"
    fi
    
    # URL取得
    BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" \
        --region="$REGION" \
        --format='value(status.url)' 2>/dev/null || echo "未取得")
    
    FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" \
        --region="$REGION" \
        --format='value(status.url)' 2>/dev/null || echo "未取得")
    
    # 結果表示
    show_deployment_summary
}

# デプロイサマリー表示
show_deployment_summary() {
    echo ""
    log_success "🎉 Cloud Buildデプロイ完了!"
    echo ""
    echo "📋 ========================================"
    echo "   Deployment Summary"
    echo "======================================== 📋"
    echo "Environment: $ENVIRONMENT"
    echo "Project: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Build Method: Cloud Build (No Local Docker)"
    echo ""
    echo "🌐 URLs:"
    echo "  Frontend:  $FRONTEND_URL"
    echo "  Backend:   $BACKEND_URL"
    echo "  API Docs:  $BACKEND_URL/docs"
    echo ""
    echo "🔧 管理リンク:"
    echo "  Cloud Run: https://console.cloud.google.com/run?project=$PROJECT_ID"
    echo "  Logs:      https://console.cloud.google.com/logs/query?project=$PROJECT_ID"
    echo "  Build:     https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
    echo ""
    echo "💡 次のステップ:"
    echo "  1. フロントエンドURLでアプリケーションにアクセス"
    echo "  2. Google OAuth設定でリダイレクトURIを更新"
    echo "  3. カスタムドメインの設定（オプション）"
    echo "======================================== 📋"
    echo ""
}

# ヘルプ表示
show_help() {
    echo "Usage: $0 [environment] [project-id]"
    echo ""
    echo "Arguments:"
    echo "  environment    Deployment environment (staging/production) [default: staging]"
    echo "  project-id     Google Cloud Project ID [default: \$GCP_PROJECT_ID]"
    echo ""
    echo "Environment variables:"
    echo "  GCP_PROJECT_ID      Google Cloud Project ID (required)"
    echo "  GCP_REGION          Deployment region [default: asia-northeast1]"
    echo "  GOOGLE_API_KEY      Gemini API key"
    echo "  GOOGLE_AIPSK        ADK API key"
    echo "  GOOGLE_CLIENT_ID    OAuth Client ID"
    echo "  GOOGLE_CLIENT_SECRET OAuth Client Secret"
    echo "  NEXTAUTH_SECRET     NextAuth Secret"
    echo "  ROUTING_STRATEGY    Agent routing strategy [default: enhanced]"
    echo "  LOG_LEVEL           Log level [default: INFO]"
    echo "  BUILD_TIMEOUT       Build timeout [default: 20m]"
    echo ""
    echo "Examples:"
    echo "  $0 staging my-project-id"
    echo "  $0 production"
    echo "  GCP_PROJECT_ID=my-project $0 staging"
    echo ""
    echo "Features:"
    echo "  ✅ No local Docker required"
    echo "  ✅ Parallel frontend/backend build"
    echo "  ✅ Automatic GCP setup"
    echo "  ✅ Health checks included"
    exit 0
}

# メイン実行
main() {
    # ヘルプチェック
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_help
    fi
    
    show_banner
    check_prerequisites
    setup_project
    collect_env_vars
    execute_cloud_build
}

# エラーハンドリング
trap 'log_error "デプロイ中にエラーが発生しました"; exit 1' ERR

# スクリプト実行
main "$@"