#!/bin/bash
# ローカル開発環境を環境変数ファイルを使って起動

set -e

# カラー出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting GenieUs Local Development${NC}"
echo -e "${BLUE}====================================${NC}"

# 環境変数を読み込み
source scripts/load-env.sh local

# フロントエンドとバックエンドの.envファイルを生成
echo -e "${BLUE}📝 Generating .env files for local development...${NC}"

# Backend .env.dev
cat > backend/.env.dev << EOF
# Auto-generated from environments/.env.local
# $(date)

APP_NAME=$APP_NAME
ENVIRONMENT=$ENVIRONMENT
PORT=$BACKEND_PORT

GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID
GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION
GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI

CORS_ORIGINS=$CORS_ORIGINS
DATABASE_URL=$DATABASE_URL

JWT_SECRET=$JWT_SECRET
JWT_EXPIRE_MINUTES=$JWT_EXPIRE_MINUTES

LOG_LEVEL=$LOG_LEVEL
ROUTING_STRATEGY=$ROUTING_STRATEGY

NEXTAUTH_URL=$NEXTAUTH_URL
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
NEXTAUTH_SECRET=$NEXTAUTH_SECRET

GOOGLE_API_KEY=$GOOGLE_API_KEY
EOF

# Frontend .env.local
cat > frontend/.env.local << EOF
# Auto-generated from environments/.env.local
# $(date)

NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
NEXTAUTH_URL=$NEXTAUTH_URL
NEXTAUTH_SECRET=$NEXTAUTH_SECRET
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
EOF

echo -e "${GREEN}✅ Environment files generated${NC}"

# OAuth設定のリマインダー
if [[ "$GOOGLE_CLIENT_ID" == *"your-"* ]]; then
    echo -e "${YELLOW}⚠️  OAuth Configuration Reminder:${NC}"
    echo "   1. Set up Google OAuth credentials in Google Cloud Console"
    echo "   2. Add http://localhost:3000/api/auth/callback/google to redirect URIs"
    echo "   3. Update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environments/.env.local"
    echo ""
fi

# 開発サーバー起動
echo -e "${BLUE}🏃 Starting development servers...${NC}"
echo -e "${BLUE}Backend: http://localhost:$BACKEND_PORT${NC}"
echo -e "${BLUE}Frontend: http://localhost:$FRONTEND_PORT${NC}"
echo ""

# 既存のstart-dev.shを使用
./scripts/start-dev.sh