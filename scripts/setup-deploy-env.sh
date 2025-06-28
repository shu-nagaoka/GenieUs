#!/bin/bash

# GenieUs Cloud Build デプロイ用環境変数設定ヘルパー
# Usage: ./scripts/setup-deploy-env.sh

set -e

# 色付きログ
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔧 GenieUs Cloud Build デプロイ用環境変数設定${NC}"
echo ""

# 現在の設定確認
echo -e "${YELLOW}=== 現在の設定 ===${NC}"
echo "GCP_PROJECT_ID: ${GCP_PROJECT_ID:-'未設定'}"
echo "GCP_REGION: ${GCP_REGION:-'asia-northeast1 (デフォルト)'}"
echo "NEXTAUTH_SECRET: ${NEXTAUTH_SECRET:+'設定済み'}"
echo "GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:+'設定済み'}"
echo "GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET:+'設定済み'}"
echo "GOOGLE_API_KEY: ${GOOGLE_API_KEY:+'設定済み'}"
echo "GOOGLE_AIPSK: ${GOOGLE_AIPSK:+'設定済み'}"
echo ""

# 設定レベル選択
echo -e "${BLUE}設定レベルを選択してください:${NC}"
echo "  1) 最小設定 (GCP_PROJECT_IDのみ - テスト用)"
echo "  2) 実用設定 (認証設定含む - 開発用)"
echo "  3) 完全設定 (AI機能含む - 本番用)"
echo "  4) 個別設定 (手動で各項目設定)"
echo "  0) キャンセル"
echo ""
read -p "選択 (0-4): " level_choice

case $level_choice in
    1)
        echo -e "${GREEN}📦 最小設定モード${NC}"
        read -p "GCPプロジェクトIDを入力: " project_id
        
        if [ -n "$project_id" ]; then
            echo "export GCP_PROJECT_ID=\"$project_id\"" >> ~/.bashrc
            export GCP_PROJECT_ID="$project_id"
            echo -e "${GREEN}✅ 最小設定完了${NC}"
        fi
        ;;
        
    2)
        echo -e "${GREEN}🔐 実用設定モード${NC}"
        read -p "GCPプロジェクトIDを入力: " project_id
        read -p "NextAuth Secret (32文字、空白で自動生成): " nextauth_secret
        read -p "Google Client ID: " client_id
        read -p "Google Client Secret: " client_secret
        
        # NextAuth Secret自動生成
        if [ -z "$nextauth_secret" ]; then
            nextauth_secret=$(openssl rand -base64 32 2>/dev/null || echo "auto-generated-secret-$(date +%s)")
            echo -e "${YELLOW}自動生成されたNextAuth Secret: $nextauth_secret${NC}"
        fi
        
        # 設定保存
        {
            echo "export GCP_PROJECT_ID=\"$project_id\""
            echo "export NEXTAUTH_SECRET=\"$nextauth_secret\""
            echo "export GOOGLE_CLIENT_ID=\"$client_id\""
            echo "export GOOGLE_CLIENT_SECRET=\"$client_secret\""
        } >> ~/.bashrc
        
        # 即座に適用
        export GCP_PROJECT_ID="$project_id"
        export NEXTAUTH_SECRET="$nextauth_secret"
        export GOOGLE_CLIENT_ID="$client_id"
        export GOOGLE_CLIENT_SECRET="$client_secret"
        
        echo -e "${GREEN}✅ 実用設定完了${NC}"
        ;;
        
    3)
        echo -e "${GREEN}🤖 完全設定モード${NC}"
        read -p "GCPプロジェクトIDを入力: " project_id
        read -p "NextAuth Secret (32文字、空白で自動生成): " nextauth_secret
        read -p "Google Client ID: " client_id
        read -p "Google Client Secret: " client_secret
        read -p "Gemini API Key: " api_key
        read -p "ADK API Key: " aipsk
        
        # NextAuth Secret自動生成
        if [ -z "$nextauth_secret" ]; then
            nextauth_secret=$(openssl rand -base64 32 2>/dev/null || echo "auto-generated-secret-$(date +%s)")
            echo -e "${YELLOW}自動生成されたNextAuth Secret: $nextauth_secret${NC}"
        fi
        
        # 設定保存
        {
            echo "export GCP_PROJECT_ID=\"$project_id\""
            echo "export NEXTAUTH_SECRET=\"$nextauth_secret\""
            echo "export GOOGLE_CLIENT_ID=\"$client_id\""
            echo "export GOOGLE_CLIENT_SECRET=\"$client_secret\""
            echo "export GOOGLE_API_KEY=\"$api_key\""
            echo "export GOOGLE_AIPSK=\"$aipsk\""
            echo "export ROUTING_STRATEGY=\"enhanced\""
            echo "export LOG_LEVEL=\"INFO\""
        } >> ~/.bashrc
        
        # 即座に適用
        export GCP_PROJECT_ID="$project_id"
        export NEXTAUTH_SECRET="$nextauth_secret"
        export GOOGLE_CLIENT_ID="$client_id"
        export GOOGLE_CLIENT_SECRET="$client_secret"
        export GOOGLE_API_KEY="$api_key"
        export GOOGLE_AIPSK="$aipsk"
        export ROUTING_STRATEGY="enhanced"
        export LOG_LEVEL="INFO"
        
        echo -e "${GREEN}✅ 完全設定完了${NC}"
        ;;
        
    4)
        echo -e "${GREEN}⚙️ 個別設定モード${NC}"
        echo "各項目を個別に設定します（空白でスキップ）"
        
        read -p "GCP_PROJECT_ID: " project_id
        read -p "GCP_REGION (default: asia-northeast1): " region
        read -p "NEXTAUTH_SECRET: " nextauth_secret
        read -p "GOOGLE_CLIENT_ID: " client_id
        read -p "GOOGLE_CLIENT_SECRET: " client_secret
        read -p "GOOGLE_API_KEY: " api_key
        read -p "GOOGLE_AIPSK: " aipsk
        read -p "ROUTING_STRATEGY (default: enhanced): " routing_strategy
        read -p "LOG_LEVEL (default: INFO): " log_level
        
        # 設定保存
        env_file="$HOME/.genieus_deploy_env"
        echo "# GenieUs Deploy Environment Variables" > "$env_file"
        echo "# Generated on $(date)" >> "$env_file"
        
        [ -n "$project_id" ] && echo "export GCP_PROJECT_ID=\"$project_id\"" >> "$env_file"
        [ -n "$region" ] && echo "export GCP_REGION=\"$region\"" >> "$env_file"
        [ -n "$nextauth_secret" ] && echo "export NEXTAUTH_SECRET=\"$nextauth_secret\"" >> "$env_file"
        [ -n "$client_id" ] && echo "export GOOGLE_CLIENT_ID=\"$client_id\"" >> "$env_file"
        [ -n "$client_secret" ] && echo "export GOOGLE_CLIENT_SECRET=\"$client_secret\"" >> "$env_file"
        [ -n "$api_key" ] && echo "export GOOGLE_API_KEY=\"$api_key\"" >> "$env_file"
        [ -n "$aipsk" ] && echo "export GOOGLE_AIPSK=\"$aipsk\"" >> "$env_file"
        [ -n "$routing_strategy" ] && echo "export ROUTING_STRATEGY=\"$routing_strategy\"" >> "$env_file"
        [ -n "$log_level" ] && echo "export LOG_LEVEL=\"$log_level\"" >> "$env_file"
        
        echo -e "${GREEN}✅ 個別設定完了${NC}"
        echo -e "${YELLOW}設定ファイル: $env_file${NC}"
        echo -e "${YELLOW}読み込み: source $env_file${NC}"
        ;;
        
    0)
        echo -e "${YELLOW}キャンセルされました${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}無効な選択です${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}=== 設定完了後の確認 ===${NC}"
echo "現在の環境変数:"
echo "  GCP_PROJECT_ID: ${GCP_PROJECT_ID:-'未設定'}"
echo "  GCP_REGION: ${GCP_REGION:-'asia-northeast1'}"
echo "  NEXTAUTH_SECRET: ${NEXTAUTH_SECRET:+'設定済み'}"
echo "  GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:+'設定済み'}"
echo ""

echo -e "${GREEN}🚀 デプロイ準備完了！${NC}"
echo "デプロイ実行方法:"
echo "  1) ./entrypoint.sh → 14 (Cloud Build ステージング)"
echo "  2) ./entrypoint.sh → 15 (Cloud Build 本番)"
echo "  3) ./scripts/deploy-cloudbuild.sh staging"
echo ""

# 設定の永続化確認
echo -e "${YELLOW}設定を永続化しますか？ (y/N): ${NC}"
read -p "" persist_choice
if [[ $persist_choice =~ ^[Yy]$ ]]; then
    echo "source ~/.bashrc" >> ~/.bash_profile 2>/dev/null || true
    echo -e "${GREEN}✅ 設定が永続化されました${NC}"
else
    echo -e "${YELLOW}現在のセッションでのみ有効です${NC}"
fi