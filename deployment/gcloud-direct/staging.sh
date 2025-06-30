#!/bin/bash

# GenieUs gcloud直接デプロイメント (ステージング環境)
# gcloudコマンド直接実行によるデプロイメント

set -e

# スクリプトディレクトリ取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 共通機能読み込み
source "$SCRIPT_DIR/../shared/common.sh"
source "$SCRIPT_DIR/../shared/env-loader.sh"
source "$SCRIPT_DIR/../shared/secret-manager.sh"

# 環境設定
ENVIRONMENT="staging"

main() {
    echo -e "${GREEN}🐳 gcloud直接デプロイメント開始 (ステージング)${NC}"
    echo "=============================================="
    echo ""
    
    # 環境変数読み込み
    load_environment "$ENVIRONMENT"
    
    # デプロイ前確認
    pre_deploy_check "$ENVIRONMENT" "$GCP_PROJECT_ID"
    
    # Docker確認
    check_docker_availability
    
    # 設定表示
    show_deploy_summary "$ENVIRONMENT" "$GCP_PROJECT_ID" "$BACKEND_SERVICE_NAME" "$FRONTEND_SERVICE_NAME"
    
    # Secret Manager統合確認
    if is_secret_manager_enabled; then
        echo -e "${CYAN}🔐 Secret Manager統合が有効です${NC}"
        echo -e "${YELLOW}Secret Manager値を更新しますか？ (y/N): ${NC}"
        read -p "" update_secrets
        
        if [[ $update_secrets =~ ^[Yy]$ ]]; then
            if ! update_secret_manager_from_env "$ENVIRONMENT"; then
                log_error "Secret Manager値の更新に失敗しました"
                exit 1
            fi
        fi
    fi
    
    # Artifact Registry準備
    setup_artifact_registry
    
    # バックエンドデプロイ
    deploy_backend
    
    # フロントエンドデプロイ
    deploy_frontend
    
    # デプロイ後確認
    post_deploy_check "$BACKEND_SERVICE_NAME" "$REGION"
    post_deploy_check "$FRONTEND_SERVICE_NAME" "$REGION"
    
    echo ""
    echo -e "${GREEN}🎉 ステージング環境デプロイ完了${NC}"
    show_service_urls
}

# Docker確認
check_docker_availability() {
    if ! docker info &>/dev/null; then
        log_error "Dockerが実行されていません。Dockerを起動してください。"
        exit 1
    fi
    log_info "Docker確認完了"
}

# Artifact Registry準備
setup_artifact_registry() {
    log_info "Artifact Registry準備中..."
    
    # Docker認証設定
    gcloud auth configure-docker "$REGISTRY" --quiet
    
    # リポジトリ存在確認・作成
    if ! gcloud artifacts repositories describe genieus --location="$GAR_LOCATION" &>/dev/null; then
        log_info "Artifact Registryリポジトリを作成中..."
        gcloud artifacts repositories create genieus \
            --repository-format=docker \
            --location="$GAR_LOCATION" \
            --description="GenieUs Docker images"
    fi
    
    log_success "Artifact Registry準備完了"
}

# バックエンドデプロイ
deploy_backend() {
    log_info "バックエンドデプロイ開始..."
    
    # Dockerイメージビルド
    log_info "バックエンドDockerイメージビルド中..."
    docker build \
        -t "$BACKEND_IMAGE:latest" \
        -f "$PROJECT_ROOT/backend/Dockerfile" \
        "$PROJECT_ROOT/backend"
    
    # イメージプッシュ
    log_info "バックエンドイメージプッシュ中..."
    docker push "$BACKEND_IMAGE:latest"
    
    # Cloud Runデプロイ
    log_info "バックエンドCloud Runデプロイ中..."
    
    # 環境変数準備
    local env_vars="GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID"
    env_vars="$env_vars,ENVIRONMENT=$ENVIRONMENT"
    env_vars="$env_vars,DATABASE_TYPE=$DATABASE_TYPE"
    env_vars="$env_vars,GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI:-True}"
    env_vars="$env_vars,GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-us-central1}"
    env_vars="$env_vars,LOG_LEVEL=${LOG_LEVEL:-INFO}"
    env_vars="$env_vars,ROUTING_STRATEGY=${ROUTING_STRATEGY:-enhanced}"
    
    # Cloud SQL設定
    local cloud_sql_args=""
    if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
        env_vars="$env_vars,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME"
        cloud_sql_args="--add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME"
    fi
    
    # Secret Manager統合
    local secret_args=""
    if is_secret_manager_enabled; then
        secret_args="--set-secrets=$(get_secret_env_vars)"
    fi
    
    # Cloud Runデプロイ実行
    gcloud run deploy "$BACKEND_SERVICE_NAME" \
        --image="$BACKEND_IMAGE:latest" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --set-env-vars="$env_vars" \
        $cloud_sql_args \
        $secret_args \
        --min-instances="$BACKEND_MIN_INSTANCES" \
        --max-instances="$BACKEND_MAX_INSTANCES" \
        --memory=2Gi \
        --cpu=1 \
        --timeout=300
    
    log_success "バックエンドデプロイ完了"
}

# フロントエンドデプロイ
deploy_frontend() {
    log_info "フロントエンドデプロイ開始..."
    
    # バックエンドURL取得
    local backend_url=$(gcloud run services describe "$BACKEND_SERVICE_NAME" --region="$REGION" --format="value(status.url)")
    if [ -z "$backend_url" ]; then
        log_error "バックエンドURLが取得できません"
        exit 1
    fi
    
    # フロントエンド環境変数準備
    local frontend_env_vars="NEXT_PUBLIC_API_BASE_URL=$backend_url"
    frontend_env_vars="$frontend_env_vars,NEXTAUTH_URL=https://placeholder-will-be-updated"
    frontend_env_vars="$frontend_env_vars,NODE_ENV=production"
    
    # Secret Manager統合（フロントエンド用）
    local frontend_secret_args=""
    if is_secret_manager_enabled; then
        frontend_secret_args="--set-secrets=NEXTAUTH_SECRET=nextauth-secret:latest,GOOGLE_CLIENT_ID=google-oauth-client-id:latest,GOOGLE_CLIENT_SECRET=google-oauth-client-secret:latest"
    fi
    
    # Dockerイメージビルド
    log_info "フロントエンドDockerイメージビルド中..."
    docker build \
        -t "$FRONTEND_IMAGE:latest" \
        -f "$PROJECT_ROOT/frontend/Dockerfile" \
        "$PROJECT_ROOT/frontend" \
        --build-arg NEXT_PUBLIC_API_BASE_URL="$backend_url"
    
    # イメージプッシュ
    log_info "フロントエンドイメージプッシュ中..."
    docker push "$FRONTEND_IMAGE:latest"
    
    # Cloud Runデプロイ
    log_info "フロントエンドCloud Runデプロイ中..."
    gcloud run deploy "$FRONTEND_SERVICE_NAME" \
        --image="$FRONTEND_IMAGE:latest" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --set-env-vars="$frontend_env_vars" \
        $frontend_secret_args \
        --min-instances="$FRONTEND_MIN_INSTANCES" \
        --max-instances="$FRONTEND_MAX_INSTANCES" \
        --memory=1Gi \
        --cpu=1 \
        --timeout=300
    
    # NEXTAUTH_URL更新
    local frontend_url=$(gcloud run services describe "$FRONTEND_SERVICE_NAME" --region="$REGION" --format="value(status.url)")
    if [ -n "$frontend_url" ]; then
        log_info "NEXTAUTH_URL更新中..."
        gcloud run services update "$FRONTEND_SERVICE_NAME" \
            --region="$REGION" \
            --update-env-vars="NEXTAUTH_URL=$frontend_url"
        
        # CORS設定更新
        log_info "バックエンドCORS設定更新中..."
        gcloud run services update "$BACKEND_SERVICE_NAME" \
            --region="$REGION" \
            --update-env-vars="CORS_ORIGINS=$frontend_url"
    fi
    
    log_success "フロントエンドデプロイ完了"
}

# サービスURL表示
show_service_urls() {
    echo ""
    echo -e "${BLUE}📋 デプロイ済みサービス${NC}"
    echo "===================="
    
    # バックエンドURL
    local backend_url=$(gcloud run services describe "$BACKEND_SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "取得失敗")
    echo -e "バックエンド: ${YELLOW}$backend_url${NC}"
    
    # フロントエンドURL
    local frontend_url=$(gcloud run services describe "$FRONTEND_SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "取得失敗")
    echo -e "フロントエンド: ${YELLOW}$frontend_url${NC}"
    
    echo "===================="
    echo ""
    
    # APIドキュメント
    if [ "$backend_url" != "取得失敗" ]; then
        echo -e "${CYAN}💡 API仕様書: ${YELLOW}$backend_url/docs${NC}"
    fi
    
    # gcloud直接デプロイの特徴
    echo -e "${BLUE}📋 gcloud直接デプロイの特徴:${NC}"
    echo -e "${YELLOW}- ローカルDockerでビルド実行${NC}"
    echo -e "${YELLOW}- リアルタイムログ出力${NC}"
    echo -e "${YELLOW}- 詳細なエラー情報表示${NC}"
}

# エラーハンドリング
trap 'log_error "gcloud直接デプロイ中にエラーが発生しました"; exit 1' ERR

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi