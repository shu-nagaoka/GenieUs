#!/bin/bash

# GenieUs Cloud Build デプロイメント (ステージング環境)
# Cloud Build を使用したサーバーレスデプロイメント

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
    echo -e "${GREEN}🏗️ Cloud Build デプロイメント開始 (ステージング)${NC}"
    echo "================================================"
    echo ""
    
    # 環境変数読み込み
    load_environment "$ENVIRONMENT"
    
    # デプロイ前確認
    pre_deploy_check "$ENVIRONMENT" "$GCP_PROJECT_ID"
    
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
    
    # Cloud Build実行
    execute_cloud_build
    
    # デプロイ後確認
    post_deploy_check "$BACKEND_SERVICE_NAME" "$REGION"
    post_deploy_check "$FRONTEND_SERVICE_NAME" "$REGION"
    
    echo ""
    echo -e "${GREEN}🎉 ステージング環境デプロイ完了${NC}"
    show_service_urls
}

# Cloud Build実行
execute_cloud_build() {
    log_info "Cloud Build でデプロイを実行中..."
    
    # Cloud Build設定ファイル確認
    local cloudbuild_file="$PROJECT_ROOT/cloudbuild.yaml"
    if [ ! -f "$cloudbuild_file" ]; then
        log_error "Cloud Build設定ファイルが見つかりません: $cloudbuild_file"
        exit 1
    fi
    
    # Cloud Build実行
    gcloud builds submit \
        --config="$cloudbuild_file" \
        --substitutions="\
_GCP_PROJECT_ID=$GCP_PROJECT_ID,\
_ENVIRONMENT=$ENVIRONMENT,\
_REGION=$REGION,\
_BACKEND_SERVICE_NAME=$BACKEND_SERVICE_NAME,\
_FRONTEND_SERVICE_NAME=$FRONTEND_SERVICE_NAME,\
_DATABASE_TYPE=$DATABASE_TYPE,\
_CLOUD_SQL_CONNECTION_NAME=${CLOUD_SQL_CONNECTION_NAME:-},\
_GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI:-True},\
_GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-us-central1},\
_LOG_LEVEL=${LOG_LEVEL:-INFO},\
_ROUTING_STRATEGY=${ROUTING_STRATEGY:-enhanced}" \
        "$PROJECT_ROOT"
    
    if [ $? -eq 0 ]; then
        log_success "Cloud Build デプロイ完了"
    else
        log_error "Cloud Build デプロイ失敗"
        exit 1
    fi
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
}

# エラーハンドリング
trap 'log_error "デプロイ中にエラーが発生しました"; exit 1' ERR

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi