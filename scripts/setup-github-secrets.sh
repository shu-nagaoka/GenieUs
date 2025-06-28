#!/bin/bash
# GitHub Secrets自動設定スクリプト
# Usage: ./scripts/setup-github-secrets.sh

set -e

# カラー出力設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 GitHub Secrets自動設定開始${NC}"
echo "=================================="

# 必要なツール確認
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) がインストールされていません${NC}"
    echo ""
    echo -e "${YELLOW}📦 インストール方法:${NC}"
    echo "macOS: brew install gh"
    echo "Ubuntu: sudo apt install gh"
    echo "Windows: winget install GitHub.CLI"
    echo ""
    echo "インストール後、以下を実行してください:"
    echo "gh auth login"
    exit 1
fi

# GitHub認証確認
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}🔑 GitHub認証が必要です${NC}"
    echo "以下のコマンドを実行してログインしてください:"
    echo "gh auth login"
    exit 1
fi

# リポジトリ情報確認
REPO_OWNER="shu-nagaoka"
REPO_NAME="GenieUs"
REPO_FULL="${REPO_OWNER}/${REPO_NAME}"

echo -e "${GREEN}✅ GitHub認証確認完了${NC}"
echo "Repository: $REPO_FULL"
echo ""

# 設定ファイル存在確認
SECRETS_FILE="./gcp-secrets.env"
if [ ! -f "$SECRETS_FILE" ]; then
    echo -e "${RED}❌ gcp-secrets.env ファイルが見つかりません${NC}"
    echo "先に ./scripts/setup-gcp-cicd.sh を実行してください"
    exit 1
fi

echo -e "${BLUE}📝 Step 1: 設定ファイル読み込み${NC}"
source $SECRETS_FILE
echo -e "${GREEN}✅ 設定ファイル読み込み完了${NC}"
echo ""

# 2. GitHub Secrets設定
echo -e "${BLUE}🔐 Step 2: GitHub Secrets設定${NC}"

# Secret設定用配列
declare -A SECRETS=(
    ["GCP_PROJECT_ID"]="$GCP_PROJECT_ID"
    ["GCP_SA_KEY"]="$GCP_SA_KEY"
    ["NEXTAUTH_SECRET"]="$NEXTAUTH_SECRET"
    ["GOOGLE_CLIENT_ID"]="$GOOGLE_CLIENT_ID"
    ["GOOGLE_CLIENT_SECRET"]="$GOOGLE_CLIENT_SECRET"
)

# 各Secretを設定
for secret_name in "${!SECRETS[@]}"; do
    secret_value="${SECRETS[$secret_name]}"
    
    echo "Setting secret: $secret_name"
    
    # 既存Secret確認（エラーは無視）
    if gh secret list --repo $REPO_FULL | grep -q "^$secret_name"; then
        echo "  Updating existing secret..."
        echo "$secret_value" | gh secret set $secret_name --repo $REPO_FULL
    else
        echo "  Creating new secret..."
        echo "$secret_value" | gh secret set $secret_name --repo $REPO_FULL
    fi
    
    echo -e "  ${GREEN}✅ $secret_name 設定完了${NC}"
done
echo ""

# 3. 設定確認
echo -e "${BLUE}🔍 Step 3: 設定確認${NC}"
echo "GitHub Secrets一覧:"
gh secret list --repo $REPO_FULL
echo ""

# 4. Environment Variables設定（オプション）
echo -e "${BLUE}🌍 Step 4: Environment Variables設定${NC}"
echo "GitHub Environment Variables:"

# Repository Variables設定
declare -A VARIABLES=(
    ["GCP_REGION"]="asia-northeast1"
    ["REGISTRY_LOCATION"]="asia-northeast1"
    ["DOCKER_REGISTRY"]="asia-northeast1-docker.pkg.dev"
)

for var_name in "${!VARIABLES[@]}"; do
    var_value="${VARIABLES[$var_name]}"
    
    echo "Setting variable: $var_name = $var_value"
    gh variable set $var_name --body "$var_value" --repo $REPO_FULL
    echo -e "  ${GREEN}✅ $var_name 設定完了${NC}"
done
echo ""

# 5. ワークフロー設定確認
echo -e "${BLUE}⚙️ Step 5: ワークフロー設定確認${NC}"
WORKFLOW_FILE=".github/workflows/deploy-cloud-run.yml"

if [ -f "$WORKFLOW_FILE" ]; then
    echo -e "${GREEN}✅ GitHub Actions ワークフローファイル存在確認${NC}"
    echo "File: $WORKFLOW_FILE"
    
    # ワークフロー有効化確認
    if gh workflow list --repo $REPO_FULL | grep -q "Deploy to Cloud Run"; then
        echo -e "${GREEN}✅ ワークフロー有効化確認${NC}"
    else
        echo -e "${YELLOW}⚠️ ワークフローが見つからない、または無効化されています${NC}"
    fi
else
    echo -e "${RED}❌ GitHub Actions ワークフローファイルが見つかりません${NC}"
    echo "Expected: $WORKFLOW_FILE"
fi
echo ""

# 6. 成功報告と次ステップ
echo -e "${GREEN}🎉 GitHub Secrets設定完了！${NC}"
echo "=================================="
echo ""
echo -e "${YELLOW}📋 設定完了項目:${NC}"
echo "✅ GCP_PROJECT_ID: $GCP_PROJECT_ID"
echo "✅ GCP_SA_KEY: [設定済み]"
echo "✅ NEXTAUTH_SECRET: [設定済み]"
echo "✅ GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID"
echo "✅ GOOGLE_CLIENT_SECRET: [設定済み]"
echo ""
echo -e "${YELLOW}📋 次のステップ:${NC}"
echo "1. テスト用PRを作成してCI/CDをテスト:"
echo "   git checkout -b test-cicd"
echo "   git commit --allow-empty -m 'test: CI/CD pipeline test'"
echo "   git push origin test-cicd"
echo "   gh pr create --title 'Test CI/CD Pipeline' --body 'CI/CD動作テスト'"
echo ""
echo "2. または直接mainブランチにプッシュ:"
echo "   git push origin main"
echo ""
echo "3. GitHub Actions実行確認:"
echo "   gh run list --repo $REPO_FULL"
echo "   gh run watch --repo $REPO_FULL"
echo ""

# セキュリティ清掃
echo -e "${BLUE}🧹 Step 6: セキュリティ清掃${NC}"
if [ -f "./gcp-cicd-key.json" ]; then
    echo -e "${YELLOW}⚠️ ローカルのサービスアカウントキーファイルを削除しますか？ (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm ./gcp-cicd-key.json
        echo -e "${GREEN}✅ gcp-cicd-key.json 削除完了${NC}"
    else
        echo -e "${YELLOW}⚠️ 手動でキーファイルを削除してください: ./gcp-cicd-key.json${NC}"
    fi
fi

if [ -f "./gcp-secrets.env" ]; then
    echo -e "${YELLOW}⚠️ ローカルの設定ファイルを削除しますか？ (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm ./gcp-secrets.env
        echo -e "${GREEN}✅ gcp-secrets.env 削除完了${NC}"
    else
        echo -e "${YELLOW}⚠️ 手動で設定ファイルを削除してください: ./gcp-secrets.env${NC}"
    fi
fi
echo ""

echo -e "${GREEN}🔒 GitHub Secrets設定とセキュリティ対策完了！${NC}"