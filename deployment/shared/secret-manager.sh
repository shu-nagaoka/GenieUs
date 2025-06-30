#!/bin/bash

# GenieUs Secret Manager統合機能
# 環境変数からSecret Managerへの値反映機能

set -e

# Secret Manager値更新
update_secret_manager_from_env() {
    local environment="$1"
    local env_file="environments/.env.$environment"
    
    echo -e "${BLUE}🔐 Secret Manager値更新${NC}"
    echo "=============================="
    echo ""
    
    # 環境ファイル存在確認
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}❌ 環境ファイルが見つかりません: $env_file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}📋 環境ファイル: $env_file${NC}"
    echo ""
    
    # 環境変数読み込み（現在のセッションを汚染しないようにサブシェルで実行）
    (
        source "$env_file"
        
        # Secret Manager更新確認
        echo -e "${CYAN}🔄 以下の値をSecret Managerに反映しますか？${NC}"
        echo ""
        echo -e "NEXTAUTH_SECRET: ${YELLOW}${NEXTAUTH_SECRET:0:8}...${NC}"
        echo -e "GOOGLE_CLIENT_ID: ${YELLOW}${GOOGLE_CLIENT_ID:0:15}...${NC}"
        echo -e "GOOGLE_CLIENT_SECRET: ${YELLOW}${GOOGLE_CLIENT_SECRET:0:8}...${NC}"
        echo ""
        echo -e "${YELLOW}💡 Secret Managerの値を更新しますか？ (y/N): ${NC}"
        read -p "" confirm_secrets
        
        if [[ ! $confirm_secrets =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}⚠️ Secret Manager更新をスキップしました${NC}"
            echo -e "${CYAN}📄 現在のSecret Manager値を使用してデプロイを続行します${NC}"
            return 0
        fi
        
        echo -e "${CYAN}🔄 Secret Manager値を更新中...${NC}"
        echo ""
        
        # Secret Manager更新実行
        update_secret_if_present "nextauth-secret" "$NEXTAUTH_SECRET"
        update_secret_if_present "google-oauth-client-id" "$GOOGLE_CLIENT_ID"
        update_secret_if_present "google-oauth-client-secret" "$GOOGLE_CLIENT_SECRET"
        
        echo ""
        echo -e "${GREEN}✅ Secret Manager値の更新が完了しました${NC}"
        echo -e "${CYAN}🚀 デプロイを続行します...${NC}"
        echo ""
    )
    
    return $?
}

# Secret更新ヘルパー関数
update_secret_if_present() {
    local secret_name="$1"
    local secret_value="$2"
    
    if [ -z "$secret_value" ]; then
        echo -e "  ⚠️ ${YELLOW}$secret_name: 値が空のためスキップ${NC}"
        return 0
    fi
    
    echo "  📝 $secret_name 更新中..."
    if echo "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=- 2>/dev/null; then
        echo -e "    ✅ ${GREEN}$secret_name 更新完了${NC}"
    else
        echo -e "    ❌ ${RED}$secret_name 更新失敗${NC}"
        return 1
    fi
}

# Secret Manager値確認
check_secret_manager_values() {
    echo -e "${BLUE}🔍 Secret Manager値確認${NC}"
    echo "========================="
    
    local secrets=(
        "nextauth-secret"
        "google-oauth-client-id"
        "google-oauth-client-secret"
        "postgres-password"
        "jwt-secret"
    )
    
    for secret in "${secrets[@]}"; do
        if gcloud secrets describe "$secret" &>/dev/null; then
            local version_count=$(gcloud secrets versions list "$secret" --format="value(name)" | wc -l)
            echo -e "  ✅ ${GREEN}$secret${NC} (バージョン数: $version_count)"
        else
            echo -e "  ❌ ${RED}$secret${NC} (存在しません)"
        fi
    done
    
    echo "========================="
    echo ""
}

# Secret Manager値をCloud Run環境変数として設定
get_secret_env_vars() {
    local env_vars=""
    
    # Secret Manager参照の環境変数を生成
    local secrets=(
        "NEXTAUTH_SECRET=nextauth-secret:latest"
        "GOOGLE_CLIENT_ID=google-oauth-client-id:latest"
        "GOOGLE_CLIENT_SECRET=google-oauth-client-secret:latest"
    )
    
    for secret_mapping in "${secrets[@]}"; do
        if [ -n "$env_vars" ]; then
            env_vars="$env_vars,"
        fi
        env_vars="$env_vars$secret_mapping"
    done
    
    echo "$env_vars"
}

# Secret Manager統合の有効性確認
is_secret_manager_enabled() {
    # PostgreSQL使用時はSecret Manager統合を有効とする
    if [ "$DATABASE_TYPE" = "postgresql" ] && [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
        return 0
    else
        return 1
    fi
}