#!/bin/bash

# GenieUs デプロイメント共通関数
# Cloud Build と gcloud直接デプロイ両方で使用する共通機能

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 共通変数
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ログ関数
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

# 必須コマンド確認
check_required_commands() {
    local commands=("gcloud" "docker")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd が見つかりません。インストールしてください。"
            exit 1
        fi
    done
}

# GCP認証確認
check_gcp_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
        log_error "GCP認証が必要です: gcloud auth login"
        exit 1
    fi
    
    local account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    log_info "認証済みアカウント: $account"
}

# プロジェクト設定確認
check_gcp_project() {
    local project_id="$1"
    
    if [ -z "$project_id" ]; then
        log_error "GCP_PROJECT_ID が設定されていません"
        exit 1
    fi
    
    if ! gcloud projects describe "$project_id" &>/dev/null; then
        log_error "プロジェクト '$project_id' にアクセスできません"
        exit 1
    fi
    
    gcloud config set project "$project_id"
    log_info "プロジェクト設定: $project_id"
}

# サービス有効化確認
check_required_services() {
    local project_id="$1"
    local services=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "artifactregistry.googleapis.com"
        "secretmanager.googleapis.com"
    )
    
    log_info "必須サービスの有効化確認中..."
    
    for service in "${services[@]}"; do
        if ! gcloud services list --enabled --filter="name:$service" --format="value(name)" | grep -q "$service"; then
            log_warning "サービス $service が無効です。有効化中..."
            gcloud services enable "$service"
        fi
    done
    
    log_success "必須サービス確認完了"
}

# Cloud Run設定取得
get_cloud_run_config() {
    local service_name="$1"
    local region="${2:-asia-northeast1}"
    
    if gcloud run services describe "$service_name" --region="$region" &>/dev/null; then
        echo "exists"
    else
        echo "not_exists"
    fi
}

# デプロイ前確認
pre_deploy_check() {
    local environment="$1"
    local project_id="$2"
    
    log_info "デプロイ前確認: $environment"
    
    # 必須コマンド確認
    check_required_commands
    
    # GCP認証確認
    check_gcp_auth
    
    # プロジェクト確認
    check_gcp_project "$project_id"
    
    # サービス有効化確認
    check_required_services "$project_id"
    
    log_success "デプロイ前確認完了"
}

# デプロイ後確認
post_deploy_check() {
    local service_name="$1"
    local region="${2:-asia-northeast1}"
    
    log_info "デプロイ後確認: $service_name"
    
    # サービス状態確認
    local status=$(gcloud run services describe "$service_name" --region="$region" --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
    
    if [ "$status" = "True" ]; then
        local url=$(gcloud run services describe "$service_name" --region="$region" --format="value(status.url)")
        log_success "デプロイ成功: $url"
        return 0
    else
        log_error "デプロイ失敗: サービス状態 = $status"
        return 1
    fi
}

# 設定表示
show_deploy_summary() {
    local environment="$1"
    local project_id="$2"
    local backend_service="$3"
    local frontend_service="$4"
    
    echo ""
    echo -e "${BLUE}📋 デプロイ設定確認${NC}"
    echo "=========================="
    echo -e "環境: ${YELLOW}$environment${NC}"
    echo -e "プロジェクト: ${YELLOW}$project_id${NC}"
    echo -e "バックエンド: ${YELLOW}$backend_service${NC}"
    echo -e "フロントエンド: ${YELLOW}$frontend_service${NC}"
    echo "=========================="
    echo ""
}