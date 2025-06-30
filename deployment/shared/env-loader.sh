#!/bin/bash

# GenieUs 環境変数読み込み機能
# 各環境の .env ファイルから設定を読み込み、統一された環境変数を設定

set -e

# プロジェクトルート取得
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# 環境変数読み込み
load_environment() {
    local environment="$1"
    local env_file="$PROJECT_ROOT/environments/.env.$environment"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}❌ 環境ファイルが見つかりません: $env_file${NC}"
        exit 1
    fi
    
    echo -e "${CYAN}📋 環境設定読み込み: $environment${NC}"
    
    # 環境変数読み込み
    set -a
    source "$env_file"
    set +a
    
    # 必須変数確認
    check_required_env_vars "$environment"
    
    # デプロイ用変数設定
    setup_deploy_vars "$environment"
    
    echo -e "${GREEN}✅ 環境設定読み込み完了${NC}"
}

# 必須環境変数確認
check_required_env_vars() {
    local environment="$1"
    local required_vars=(
        "GCP_PROJECT_ID"
        "GCP_REGION"
        "BACKEND_SERVICE_NAME"
        "FRONTEND_SERVICE_NAME"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}❌ 必須環境変数が設定されていません: $var${NC}"
            exit 1
        fi
    done
    
    # 環境固有の確認
    if [ "$environment" = "production" ]; then
        local prod_required=(
            "NEXTAUTH_SECRET"
            "GOOGLE_CLIENT_ID"
            "GOOGLE_CLIENT_SECRET"
        )
        
        for var in "${prod_required[@]}"; do
            if [ -z "${!var}" ]; then
                echo -e "${RED}❌ 本番環境で必須の環境変数が設定されていません: $var${NC}"
                exit 1
            fi
        done
    fi
}

# デプロイ用変数設定
setup_deploy_vars() {
    local environment="$1"
    
    # リージョン設定
    export REGION="${GCP_REGION:-asia-northeast1}"
    
    # Artifact Registry設定
    export GAR_LOCATION="$REGION"
    export REGISTRY="$REGION-docker.pkg.dev"
    
    # イメージ名設定
    export BACKEND_IMAGE="$REGISTRY/$GCP_PROJECT_ID/genieus/$BACKEND_SERVICE_NAME"
    export FRONTEND_IMAGE="$REGISTRY/$GCP_PROJECT_ID/genieus/$FRONTEND_SERVICE_NAME"
    
    # Cloud Run設定
    export BACKEND_MIN_INSTANCES="${BACKEND_MIN_INSTANCES:-0}"
    export BACKEND_MAX_INSTANCES="${BACKEND_MAX_INSTANCES:-3}"
    export FRONTEND_MIN_INSTANCES="${FRONTEND_MIN_INSTANCES:-0}"
    export FRONTEND_MAX_INSTANCES="${FRONTEND_MAX_INSTANCES:-5}"
    
    # データベース設定統一
    if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
        export DATABASE_TYPE="postgresql"
    else
        export DATABASE_TYPE="${DATABASE_TYPE:-sqlite}"
    fi
    
    echo -e "${CYAN}📋 デプロイ変数設定完了${NC}"
    echo -e "  プロジェクト: $GCP_PROJECT_ID"
    echo -e "  リージョン: $REGION"
    echo -e "  バックエンド: $BACKEND_SERVICE_NAME"
    echo -e "  フロントエンド: $FRONTEND_SERVICE_NAME"
    echo -e "  データベース: $DATABASE_TYPE"
}

# 環境変数表示（デバッグ用）
show_environment_summary() {
    local environment="$1"
    
    echo ""
    echo -e "${BLUE}📋 環境変数サマリー ($environment)${NC}"
    echo "=================================="
    echo -e "GCP_PROJECT_ID: ${YELLOW}$GCP_PROJECT_ID${NC}"
    echo -e "REGION: ${YELLOW}$REGION${NC}"
    echo -e "DATABASE_TYPE: ${YELLOW}$DATABASE_TYPE${NC}"
    echo -e "BACKEND_SERVICE: ${YELLOW}$BACKEND_SERVICE_NAME${NC}"
    echo -e "FRONTEND_SERVICE: ${YELLOW}$FRONTEND_SERVICE_NAME${NC}"
    
    if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
        echo -e "CLOUD_SQL: ${YELLOW}$CLOUD_SQL_CONNECTION_NAME${NC}"
    fi
    
    echo "=================================="
    echo ""
}

# Secret Manager使用確認
check_secret_manager_usage() {
    local environment="$1"
    
    if [ "$DATABASE_TYPE" = "postgresql" ] && [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
        echo -e "${CYAN}🔐 Secret Manager統合が有効です${NC}"
        echo -e "  PostgreSQL接続でSecret Managerからパスワードを取得します"
        return 0
    else
        echo -e "${YELLOW}🔐 Secret Manager統合は無効です${NC}"
        echo -e "  SQLite使用またはCloud SQL接続が未設定"
        return 1
    fi
}