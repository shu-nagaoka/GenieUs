#!/bin/bash

# GenieUs Cloud Build デプロイメント (本番環境)
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
ENVIRONMENT="production"

main() {
    echo -e "${RED}🏗️ Cloud Build デプロイメント開始 (本番環境)${NC}"
    echo -e "${RED}⚠️  本番環境への重要なデプロイメントです⚠️${NC}"
    echo "================================================"
    echo ""
    
    # 本番デプロイ確認
    confirm_production_deployment
    
    # 環境変数読み込み
    load_environment "$ENVIRONMENT"
    
    # デプロイ前確認
    pre_deploy_check "$ENVIRONMENT" "$GCP_PROJECT_ID"
    
    # 本番環境必須チェック
    validate_production_environment
    
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
    
    # 最終確認
    final_production_confirmation
    
    # Cloud Build実行
    execute_cloud_build
    
    # デプロイ後確認
    post_deploy_check "$BACKEND_SERVICE_NAME" "$REGION"
    post_deploy_check "$FRONTEND_SERVICE_NAME" "$REGION"
    
    echo ""
    echo -e "${GREEN}🎉 本番環境デプロイ完了${NC}"
    show_service_urls
    
    # 本番デプロイ完了通知
    log_success "本番環境デプロイが正常に完了しました"
    log_warning "サービスの動作確認を実施してください"
}

# 本番デプロイ確認
confirm_production_deployment() {
    echo -e "${RED}⚠️  本番環境デプロイ確認 ⚠️${NC}"
    echo -e "${YELLOW}本番環境にデプロイします。この操作は取り消すことができません。${NC}"
    echo -e "${YELLOW}続行しますか？ (yes/no): ${NC}"
    read -p "" confirm
    
    if [ "$confirm" != "yes" ]; then
        log_warning "本番デプロイがキャンセルされました"
        exit 0
    fi
}

# 本番環境必須チェック
validate_production_environment() {
    log_info "本番環境設定の検証中..."
    
    # 必須環境変数確認
    local required_production_vars=(
        "NEXTAUTH_SECRET"
        "GOOGLE_CLIENT_ID"
        "GOOGLE_CLIENT_SECRET"
    )
    
    for var in "${required_production_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "本番環境で必須の環境変数が設定されていません: $var"
            exit 1
        fi
    done
    
    # データベース設定確認
    if [ "$DATABASE_TYPE" = "postgresql" ]; then
        if [ -z "$CLOUD_SQL_CONNECTION_NAME" ]; then
            log_error "PostgreSQL使用時にCLOUD_SQL_CONNECTION_NAMEが設定されていません"
            exit 1
        fi
        log_info "PostgreSQL (Cloud SQL) 設定確認完了"
    else
        log_warning "SQLite使用中 - 本番環境ではPostgreSQLの使用を推奨"
    fi
    
    # Secret Manager設定確認
    if is_secret_manager_enabled; then
        check_secret_manager_values
        log_info "Secret Manager統合設定確認完了"
    else
        log_warning "Secret Manager統合が無効 - 本番環境では有効化を推奨"
    fi
    
    log_success "本番環境設定検証完了"
}

# 最終確認
final_production_confirmation() {
    echo ""
    echo -e "${RED}🚨 最終確認 🚨${NC}"
    echo -e "${YELLOW}以下の設定で本番環境にデプロイします:${NC}"
    echo ""
    echo -e "プロジェクト: ${RED}$GCP_PROJECT_ID${NC}"
    echo -e "環境: ${RED}$ENVIRONMENT${NC}"
    echo -e "リージョン: ${RED}$REGION${NC}"
    echo -e "データベース: ${RED}$DATABASE_TYPE${NC}"
    echo ""
    echo -e "${YELLOW}本当にデプロイを実行しますか？ (YES/no): ${NC}"
    read -p "" final_confirm
    
    if [ "$final_confirm" != "YES" ]; then
        log_warning "本番デプロイがキャンセルされました"
        exit 0
    fi
}

# Cloud Build実行
execute_cloud_build() {
    log_info "Cloud Build で本番デプロイを実行中..."
    
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
        log_success "Cloud Build 本番デプロイ完了"
    else
        log_error "Cloud Build 本番デプロイ失敗"
        exit 1
    fi
}

# サービスURL表示
show_service_urls() {
    echo ""
    echo -e "${BLUE}📋 本番デプロイ済みサービス${NC}"
    echo "========================="
    
    # バックエンドURL
    local backend_url=$(gcloud run services describe "$BACKEND_SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "取得失敗")
    echo -e "バックエンド: ${YELLOW}$backend_url${NC}"
    
    # フロントエンドURL
    local frontend_url=$(gcloud run services describe "$FRONTEND_SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "取得失敗")
    echo -e "フロントエンド: ${YELLOW}$frontend_url${NC}"
    
    echo "========================="
    echo ""
    
    # APIドキュメント
    if [ "$backend_url" != "取得失敗" ]; then
        echo -e "${CYAN}💡 API仕様書: ${YELLOW}$backend_url/docs${NC}"
    fi
    
    # 本番環境注意事項
    echo -e "${RED}⚠️  本番環境注意事項:${NC}"
    echo -e "${YELLOW}- サービスの動作確認を実施してください${NC}"
    echo -e "${YELLOW}- ログ監視を有効にしてください${NC}"
    echo -e "${YELLOW}- パフォーマンス監視を確認してください${NC}"
}

# エラーハンドリング
trap 'log_error "本番デプロイ中にエラーが発生しました"; exit 1' ERR

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi