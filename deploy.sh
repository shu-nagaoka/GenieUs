#!/bin/bash

# GenieUs Simple Deploy Script
# 環境選択 → バックエンド → フロントエンド の順次実行

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ロゴ表示
print_logo() {
    echo -e "${YELLOW}"
    echo "   ____            _      _   _       "
    echo "  / ___| ___ _ __ (_) ___| | | |___   "
    echo " | |  _ / _ \ '_ \| |/ _ \ | | / __|  "
    echo " | |_| |  __/ | | | |  __/ |_| \__ \  "
    echo "  \____|\\___|_| |_|_|\\___|\\___/|___/  "
    echo -e "${NC}"
    echo -e "${BLUE}🚀 GenieUs Quick Deploy${NC}"
    echo -e "${GREEN}✨ 環境選択 → バックエンド → フロントエンド ✨${NC}"
    echo ""
}

# 環境ファイル選択
select_environment() {
    echo -e "${CYAN}📂 利用可能な環境:${NC}"
    echo ""
    
    local env_files=()
    local env_names=()
    local counter=1
    
    # environments/ ディレクトリの .env ファイルを検索
    for env_file in environments/.env.*; do
        if [ -f "$env_file" ]; then
            local env_name=$(basename "$env_file" | sed "s/^\.env\.//")
            env_files+=("$env_file")
            env_names+=("$env_name")
            
            # 環境ファイルの基本情報を表示
            local project_id=$(grep "^GCP_PROJECT_ID=" "$env_file" 2>/dev/null | cut -d"=" -f2)
            local region=$(grep "^GCP_REGION=" "$env_file" 2>/dev/null | cut -d"=" -f2)
            
            echo -e "  ${YELLOW}$counter${NC}) ${GREEN}$env_name${NC}"
            echo -e "     📋 プロジェクト: ${CYAN}${project_id:-未設定}${NC}"
            echo -e "     🌐 リージョン: ${CYAN}${region:-未設定}${NC}"
            echo -e "     📄 ファイル: ${BLUE}$env_file${NC}"
            echo ""
            
            ((counter++))
        fi
    done
    
    if [ ${#env_files[@]} -eq 0 ]; then
        echo -e "${RED}❌ environments/ ディレクトリに .env ファイルが見つかりません${NC}"
        echo -e "${YELLOW}💡 environments/.env.staging や environments/.env.production を作成してください${NC}"
        exit 1
    fi
    
    echo -e "  ${YELLOW}0${NC}) キャンセル"
    echo ""
    
    # 環境選択
    read -p "デプロイする環境を選択してください (0-$((${#env_files[@]})): " env_choice
    echo ""
    
    # 選択検証
    if [ "$env_choice" = "0" ]; then
        echo -e "${YELLOW}⚠️ デプロイがキャンセルされました${NC}"
        exit 0
    elif [ "$env_choice" -ge 1 ] && [ "$env_choice" -le "${#env_files[@]}" ]; then
        local selected_file="${env_files[$((env_choice-1))]}"
        local selected_name="${env_names[$((env_choice-1))]}"
        
        # 環境変数読み込み
        echo -e "${BLUE}📂 環境設定を読み込み中...${NC}"
        source "$selected_file"
        
        # グローバル変数に設定
        export SELECTED_ENVIRONMENT="$selected_name"
        export SELECTED_ENV_FILE="$selected_file"
        
        echo -e "${GREEN}✅ 環境変数読み込み完了${NC}"
        echo -e "   環境: ${CYAN}$selected_name${NC}"
        echo -e "   ファイル: ${BLUE}$selected_file${NC}"
        echo -e "   プロジェクト: ${CYAN}${GCP_PROJECT_ID:-未設定}${NC}"
        echo -e "   リージョン: ${CYAN}${GCP_REGION:-未設定}${NC}"
        echo ""
        
        return 0
    else
        echo -e "${RED}❌ 無効な選択です: $env_choice${NC}"
        exit 1
    fi
}

# 環境変数検証
validate_environment() {
    echo -e "${BLUE}🔍 環境設定を検証中...${NC}"
    
    local errors=0
    
    if [ -z "$GCP_PROJECT_ID" ]; then
        echo -e "${RED}❌ GCP_PROJECT_ID が設定されていません${NC}"
        ((errors++))
    fi
    
    if [ -z "$GCP_REGION" ]; then
        echo -e "${YELLOW}⚠️ GCP_REGION が未設定です。デフォルト: asia-northeast1${NC}"
        export GCP_REGION="asia-northeast1"
    fi
    
    if [ -z "$ENVIRONMENT" ]; then
        echo -e "${YELLOW}⚠️ ENVIRONMENT が未設定です。選択された環境名を使用: $SELECTED_ENVIRONMENT${NC}"
        export ENVIRONMENT="$SELECTED_ENVIRONMENT"
    fi
    
    if [ $errors -gt 0 ]; then
        echo -e "${RED}❌ 環境設定にエラーがあります。${SELECTED_ENV_FILE} を確認してください${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 環境設定検証完了${NC}"
    echo ""
}

# デプロイ設定確認
confirm_deployment() {
    echo -e "${CYAN}📋 デプロイ設定確認${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo -e "環境: ${YELLOW}$ENVIRONMENT${NC}"
    echo -e "プロジェクト: ${YELLOW}$GCP_PROJECT_ID${NC}"
    echo -e "リージョン: ${YELLOW}$GCP_REGION${NC}"
    echo -e "設定ファイル: ${BLUE}$SELECTED_ENV_FILE${NC}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo -e "サービス名: ${YELLOW}genius-backend, genius-frontend${NC}"
    else
        echo -e "サービス名: ${YELLOW}genius-backend-$ENVIRONMENT, genius-frontend-$ENVIRONMENT${NC}"
    fi
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo ""
    
    read -p "この設定でデプロイを開始しますか？ [y/N]: " confirm
    echo ""
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo -e "${YELLOW}⚠️ デプロイがキャンセルされました${NC}"
        exit 0
    fi
}

# バックエンドデプロイ
deploy_backend() {
    echo -e "${BLUE}🐍 バックエンドをデプロイ中...${NC}"
    
    cd backend
    
    local service_name
    if [ "$ENVIRONMENT" = "production" ]; then
        service_name="genius-backend"
    else
        service_name="genius-backend-$ENVIRONMENT"
    fi
    
    echo -e "   サービス名: ${CYAN}$service_name${NC}"
    echo -e "   リージョン: ${CYAN}$GCP_REGION${NC}"
    echo ""
    
    # 少し待機
    sleep 1
    
    gcloud run deploy "$service_name" \
        --source . \
        --platform managed \
        --region "$GCP_REGION" \
        --allow-unauthenticated \
        --port 8080 \
        --cpu 2 \
        --memory 2Gi \
        --min-instances 0 \
        --max-instances 5 \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID" \
        --set-env-vars "ENVIRONMENT=$ENVIRONMENT" \
        --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=True" \
        --set-env-vars "GOOGLE_CLOUD_LOCATION=us-central1" \
        --set-env-vars "ROUTING_STRATEGY=${ROUTING_STRATEGY:-enhanced}" \
        --set-env-vars "LOG_LEVEL=${LOG_LEVEL:-INFO}" \
        --set-env-vars "DATABASE_TYPE=${DATABASE_TYPE:-sqlite}" \
        --set-env-vars "CLOUD_SQL_CONNECTION_NAME=${CLOUD_SQL_CONNECTION_NAME:-}" \
        --set-env-vars "POSTGRES_USER=${POSTGRES_USER:-}" \
        --set-env-vars "POSTGRES_DB=${POSTGRES_DB:-}" \
        --timeout 1200
    
    # バックエンドURL取得（デプロイログから取得）
    # gcloud deployコマンドの出力から正確なURLを抽出
    echo ""
    echo -e "${BLUE}🔍 実際のバックエンドURLを確認中...${NC}"
    
    # より正確なURL取得方法
    BACKEND_URL=$(gcloud run services describe "$service_name" \
        --region="$GCP_REGION" \
        --format='value(status.url)')
    
    # Cloud Consoleで確認されている新しいURLパターンを考慮
    # ログから実際のURLを確認する場合の代替方法
    echo -e "   gcloud取得URL: ${CYAN}$BACKEND_URL${NC}"
    
    # 実際のURLが異なる場合の警告
    if [[ "$BACKEND_URL" == *"h2hu4abaaa"* ]]; then
        echo -e "${YELLOW}⚠️ 注意: Cloud Consoleと異なるURLの可能性があります${NC}"
        echo -e "   Cloud Console確認推奨: https://console.cloud.google.com/run?project=$GCP_PROJECT_ID${NC}"
    fi
    
    cd ..
    
    echo ""
    echo -e "${GREEN}✅ バックエンドデプロイ完了${NC}"
    echo -e "   URL: ${CYAN}$BACKEND_URL${NC}"
    echo ""
    
    # ヘルスチェック
    echo -e "${BLUE}🔍 バックエンドヘルスチェック...${NC}"
    sleep 5  # サービス起動待ち
    
    if curl -f "$BACKEND_URL/health" -m 30 -s > /dev/null 2>&1; then
        echo -e "${GREEN}✅ バックエンド正常稼働${NC}"
    else
        echo -e "${YELLOW}⚠️ ヘルスチェック失敗（サービスは起動中の可能性があります）${NC}"
    fi
    echo ""
}

# フロントエンドデプロイ
deploy_frontend() {
    echo -e "${BLUE}⚛️ フロントエンドをデプロイ中...${NC}"
    
    cd frontend
    
    local service_name
    if [ "$ENVIRONMENT" = "production" ]; then
        service_name="genius-frontend"
    else
        service_name="genius-frontend-$ENVIRONMENT"
    fi
    
    echo -e "   サービス名: ${CYAN}$service_name${NC}"
    echo -e "   リージョン: ${CYAN}$GCP_REGION${NC}"
    echo -e "   バックエンドURL: ${CYAN}$BACKEND_URL${NC}"
    echo ""
    
    # 少し待機
    sleep 1
    
    gcloud run deploy "$service_name" \
        --source . \
        --platform managed \
        --region "$GCP_REGION" \
        --allow-unauthenticated \
        --port 3000 \
        --cpu 2 \
        --memory 2Gi \
        --min-instances 0 \
        --max-instances 5 \
        --set-env-vars "NODE_ENV=production" \
        --set-env-vars "NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL" \
        --set-env-vars "NEXTAUTH_SECRET=${NEXTAUTH_SECRET:-wMZZquMg1ur7aLtT4QDBDqgVtZv6Nu8lZPZuiTyl74Q=}" \
        --set-env-vars "GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-}" \
        --set-env-vars "GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}" \
        --timeout 1200
    
    # フロントエンドURL取得
    echo ""
    echo -e "${BLUE}🔍 実際のフロントエンドURLを確認中...${NC}"
    
    FRONTEND_URL=$(gcloud run services describe "$service_name" \
        --region="$GCP_REGION" \
        --format='value(status.url)')
    
    echo -e "   gcloud取得URL: ${CYAN}$FRONTEND_URL${NC}"
    
    # 実際のURLが異なる場合の警告
    if [[ "$FRONTEND_URL" == *"h2hu4abaaa"* ]]; then
        echo -e "${YELLOW}⚠️ 注意: Cloud Consoleと異なるURLの可能性があります${NC}"
        echo -e "   Cloud Console確認推奨: https://console.cloud.google.com/run?project=$GCP_PROJECT_ID${NC}"
    fi
    
    cd ..
    
    echo ""
    echo -e "${GREEN}✅ フロントエンドデプロイ完了${NC}"
    echo -e "   URL: ${CYAN}$FRONTEND_URL${NC}"
    echo ""
    
    # ヘルスチェック
    echo -e "${BLUE}🔍 フロントエンドヘルスチェック...${NC}"
    sleep 5  # サービス起動待ち
    
    if curl -f "$FRONTEND_URL" -m 30 -s > /dev/null 2>&1; then
        echo -e "${GREEN}✅ フロントエンド正常稼働${NC}"
    else
        echo -e "${YELLOW}⚠️ ヘルスチェック失敗（サービスは起動中の可能性があります）${NC}"
    fi
    echo ""
}

# バックエンドのCORS設定更新
update_backend_cors() {
    echo -e "${BLUE}🔧 バックエンドのCORS設定を更新中...${NC}"
    
    local service_name
    if [ "$ENVIRONMENT" = "production" ]; then
        service_name="genius-backend"
    else
        service_name="genius-backend-$ENVIRONMENT"
    fi
    
    echo -e "   フロントエンドURL: ${CYAN}$FRONTEND_URL${NC}"
    
    gcloud run services update "$service_name" \
        --region="$GCP_REGION" \
        --update-env-vars "CORS_ORIGINS=$FRONTEND_URL" \
        --quiet
    
    echo -e "${GREEN}✅ CORS設定更新完了${NC}"
    echo ""
}

# 最終サマリー表示
show_summary() {
    echo -e "${GREEN}"
    echo "🎉 デプロイ完了！"
    echo -e "${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}           Deployment Summary${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo -e "環境: ${YELLOW}$ENVIRONMENT${NC}"
    echo -e "プロジェクト: ${YELLOW}$GCP_PROJECT_ID${NC}"
    echo -e "リージョン: ${YELLOW}$GCP_REGION${NC}"
    echo -e "設定ファイル: ${BLUE}$SELECTED_ENV_FILE${NC}"
    echo ""
    echo -e "🌐 ${GREEN}URLs:${NC}"
    echo -e "  フロントエンド: ${CYAN}$FRONTEND_URL${NC}"
    echo -e "  バックエンド:   ${CYAN}$BACKEND_URL${NC}"
    echo -e "  API Docs:      ${CYAN}$BACKEND_URL/docs${NC}"
    echo ""
    echo -e "🔧 ${GREEN}管理リンク:${NC}"
    echo -e "  Cloud Run: ${BLUE}https://console.cloud.google.com/run?project=$GCP_PROJECT_ID${NC}"
    echo -e "  Logs:      ${BLUE}https://console.cloud.google.com/logs/query?project=$GCP_PROJECT_ID${NC}"
    echo ""
    echo -e "💡 ${GREEN}次のステップ:${NC}"
    echo -e "  1. フロントエンドURLでアプリケーションにアクセス"
    echo -e "  2. バックエンドAPIドキュメントを確認"
    echo -e "  3. Google OAuth設定でリダイレクトURIを更新（必要に応じて）"
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
}

# メイン実行
main() {
    print_logo
    select_environment
    validate_environment
    confirm_deployment
    
    echo -e "${YELLOW}🚀 デプロイ開始...${NC}"
    echo ""
    
    deploy_backend
    deploy_frontend
    update_backend_cors
    show_summary
    
    # URL不一致の警告
    if [[ "$BACKEND_URL" == *"h2hu4abaaa"* ]] || [[ "$FRONTEND_URL" == *"h2hu4abaaa"* ]]; then
        echo ""
        echo -e "${YELLOW}⚠️ URL不一致に関する注意事項${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
        echo -e "gcloudコマンドとCloud Consoleで異なるURLが表示される場合があります。"
        echo -e "実際のURLは以下で確認してください："
        echo -e "  Cloud Console: ${BLUE}https://console.cloud.google.com/run?project=$GCP_PROJECT_ID${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    fi
}

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi