#!/bin/bash

# GenieUs統合エントリーポイント
# 既存スクリプトとの競合を避けつつ、番号選択で各機能にアクセス

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
    echo "   ____            _      _   _           _   "
    echo "  / ___| ___ _ __ (_) ___| \ | | ___  ___| |_ "
    echo " | |  _ / _ \ '_ \| |/ _ \|  \| |/ _ \/ __| __|"
    echo " | |_| |  __/ | | | |  __/ |\  |  __/\__ \ |_ "
    echo "  \____|\___|_| |_|_|\___|_| \_|\___||___/\__|"
    echo -e "${NC}"
    echo -e "${BLUE}🧞‍♂️ AI子育て支援アプリケーション - 開発統合メニュー${NC}"
    echo -e "${GREEN}✨ あなたの育児をサポートする魔法のジーニー ✨${NC}"
    echo ""
}

# メニュー表示
show_menu() {
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}           GenieUs 開発メニュー${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}🚀 開発環境 (ローカル)${NC}"
    echo -e "  ${YELLOW}1${NC}) 開発環境起動 (フロント+バック/ローカル)"
    echo -e "  ${YELLOW}2${NC}) 開発環境停止 (全プロセス停止)"
    echo ""
    echo -e "${BLUE}🐳 Docker環境${NC}"
    echo -e "  ${YELLOW}3${NC}) Docker開発環境起動 (./run.sh dev)"
    echo -e "  ${YELLOW}4${NC}) Docker本番環境起動 (./run.sh prod)"
    echo -e "  ${YELLOW}5${NC}) Dockerサービス停止 (./run.sh stop)"
    echo -e "  ${YELLOW}6${NC}) Dockerクリーンアップ (./run.sh clean)"
    echo ""
    echo -e "${CYAN}🔧 開発ツール${NC}"
    echo -e "  ${YELLOW}7${NC}) FastAPI単体起動 (バックエンドのみ)"
    echo -e "  ${YELLOW}8${NC}) ADK Web UI起動 (エージェントテスト)"
    echo -e "  ${YELLOW}9${NC}) ADK + FastAPI 同時起動 (統合開発)"
    echo -e "  ${YELLOW}10${NC}) API テスト (curl でエンドポイント確認)"
    echo -e "  ${YELLOW}11${NC}) ログ確認"
    echo ""
    echo -e "${GREEN}☁️  Cloud Run デプロイメント${NC}"
    echo -e "  ${YELLOW}12${NC}) Cloud Run ステージング デプロイ"
    echo -e "  ${YELLOW}13${NC}) Cloud Run 本番 デプロイ"
    echo -e "  ${YELLOW}14${NC}) Cloud Run サービス状態確認"
    echo -e "  ${YELLOW}15${NC}) Cloud Run ログ確認"
    echo -e "  ${YELLOW}16${NC}) Cloud Run 設定・環境確認"
    echo ""
    echo -e "${RED}🛑 その他${NC}"
    echo -e "  ${YELLOW}0${NC}) 終了"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
}

# 1. ローカル開発環境起動
start_local_dev() {
    echo -e "${GREEN}🚀 ローカル開発環境を起動します...${NC}"
    ./scripts/start_dev.sh
}

# 2. ローカル開発環境停止
stop_local_dev() {
    echo -e "${YELLOW}🛑 ローカル開発環境を停止します...${NC}"
    ./scripts/stop_dev.sh
}

# 3. Docker開発環境起動
start_docker_dev() {
    echo -e "${BLUE}🐳 Docker開発環境を起動します...${NC}"
    ./run.sh dev
}

# 4. Docker本番環境起動
start_docker_prod() {
    echo -e "${BLUE}🐳 Docker本番環境を起動します...${NC}"
    ./run.sh prod
}

# 5. Dockerサービス停止
stop_docker() {
    echo -e "${YELLOW}🐳 Dockerサービスを停止します...${NC}"
    ./run.sh stop
}

# 6. Dockerクリーンアップ
clean_docker() {
    echo -e "${RED}🧹 Dockerクリーンアップを実行します...${NC}"
    ./run.sh clean
}

# 7. FastAPI単体起動
start_fastapi_only() {
    echo -e "${GREEN}🔧 FastAPI単体起動 (バックエンドのみ)${NC}"
    echo ""
    
    # 既存プロセス停止
    echo "📛 既存のポート8000プロセスを停止中..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8000を停止" || echo "   ポート8000: プロセスなし"
    
    sleep 2
    
    # FastAPI起動
    echo -e "${GREEN}🚀 FastAPI (ポート8000) を起動中...${NC}"
    cd backend
    
    # 環境チェック
    if [ ! -f .env.dev ]; then
        echo -e "${YELLOW}⚠️  .env.devファイルが見つかりません${NC}"
        echo -e "${YELLOW}   環境変数なしで起動します${NC}"
    fi
    
    # uv が利用可能かチェック
    if command -v uv &> /dev/null; then
        echo -e "${CYAN}uvでFastAPIを起動します...${NC}"
        uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
    else
        echo -e "${CYAN}Pythonで直接FastAPIを起動します...${NC}"
        python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
    fi
}

# 8. ADK Web UI起動 (単体テスト用)
start_adk_ui() {
    echo -e "${CYAN}🤖 ADK Web UI単体テストを起動します...${NC}"
    echo -e "${YELLOW}⚠️  FastAPIが起動中の場合、ポート競合のため停止します${NC}"
    echo ""
    
    # FastAPI停止
    lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ FastAPI (ポート8000) を停止しました" || echo "ポート8000: プロセスなし"
    
    echo ""
    echo "ADKエージェントのディレクトリを選択してください:"
    echo "  1) src/agents (メイン)"
    echo "  2) test_genie (テスト用)"
    echo ""
    read -p "選択 (1-2): " adk_choice
    
    case $adk_choice in
        1)
            echo -e "${GREEN}src/agentsでADK Web UI (ポート8000) を起動...${NC}"
            cd backend/src/agents && adk web
            ;;
        2)
            echo -e "${GREEN}test_genieでADK Web UI (ポート8000) を起動...${NC}"
            cd backend/test_genie && adk web
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            ;;
    esac
}

# 9. ADK + FastAPI 同時起動 (統合開発用)
start_integrated_dev() {
    echo -e "${CYAN}🚀 ADK + FastAPI 統合開発環境を起動します...${NC}"
    echo ""
    
    # 既存プロセス停止
    echo "📛 既存のプロセスを停止中..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "   ✅ ポート3000を停止" || echo "   ポート3000: プロセスなし"
    lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8000を停止" || echo "   ポート8000: プロセスなし"
    lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8001を停止" || echo "   ポート8001: プロセスなし"
    
    sleep 2
    
    # FastAPI起動 (ポート8000)
    echo -e "${GREEN}🔧 FastAPI (ポート8000) を起動中...${NC}"
    cd backend
    python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload &
    FASTAPI_PID=$!
    echo "   FastAPI PID: $FASTAPI_PID"
    cd ..
    
    sleep 3
    
    # フロントエンド起動 (ポート3000)
    echo -e "${GREEN}🎨 フロントエンド (ポート3000) を起動中...${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "   フロントエンド PID: $FRONTEND_PID"
    cd ..
    
    sleep 3
    
    # ADK Web UI起動 (ポート8001)
    echo -e "${GREEN}🤖 ADK Web UI (ポート8001) を起動中...${NC}"
    echo "ADKエージェントのディレクトリを選択してください:"
    echo "  1) src/agents (メイン)"
    echo "  2) test_genie (テスト用)"
    echo ""
    read -p "選択 (1-2): " adk_choice
    
    case $adk_choice in
        1)
            echo -e "${GREEN}src/agentsでADK Web UI (ポート8001) を起動...${NC}"
            cd backend/src/agents && adk web --port 8001 &
            ADK_PID=$!
            ;;
        2)
            echo -e "${GREEN}test_genieでADK Web UI (ポート8001) を起動...${NC}"
            cd backend/test_genie && adk web --port 8001 &
            ADK_PID=$!
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            return
            ;;
    esac
    
    echo "   ADK Web UI PID: $ADK_PID"
    cd ../../..
    
    echo ""
    echo -e "${GREEN}✅ 統合開発環境起動完了！${NC}"
    echo ""
    echo -e "${BLUE}📱 フロントエンド: http://localhost:3000${NC}"
    echo -e "${BLUE}🔌 FastAPI: http://localhost:8000${NC}"
    echo -e "${BLUE}📖 API ドキュメント: http://localhost:8000/docs${NC}"
    echo -e "${BLUE}🤖 ADK Web UI: http://localhost:8001${NC}"
    echo ""
    echo -e "${YELLOW}停止するには選択肢2で全停止してください${NC}"
}

# 10. API テスト
test_api() {
    echo -e "${CYAN}🔍 API テストを実行します...${NC}"
    echo ""
    echo "テストするAPIを選択してください:"
    echo "  1) ヘルスチェック (GET /health)"
    echo "  2) エージェント一覧 (GET /api/adk/agents)"
    echo "  3) チャットテスト (POST /api/adk/chat)"
    echo "  4) 全部テスト"
    echo ""
    read -p "選択 (1-4): " api_choice
    
    BASE_URL="http://localhost:8000"
    
    case $api_choice in
        1)
            echo -e "${YELLOW}ヘルスチェック...${NC}"
            curl -X GET "$BASE_URL/health" | jq 2>/dev/null || curl -X GET "$BASE_URL/health"
            ;;
        2)
            echo -e "${YELLOW}エージェント一覧...${NC}"
            curl -X GET "$BASE_URL/api/adk/agents" | jq 2>/dev/null || curl -X GET "$BASE_URL/api/adk/agents"
            ;;
        3)
            echo -e "${YELLOW}チャットテスト...${NC}"
            curl -X POST "$BASE_URL/api/adk/chat" \
                -H "Content-Type: application/json" \
                -d '{"message": "夜泣きで困ってます", "agent_name": "childcare"}' | \
                jq 2>/dev/null || curl -X POST "$BASE_URL/api/adk/chat" \
                -H "Content-Type: application/json" \
                -d '{"message": "夜泣きで困ってます", "agent_name": "childcare"}'
            ;;
        4)
            echo -e "${YELLOW}全APIテスト実行...${NC}"
            echo "1. ヘルスチェック:"
            curl -X GET "$BASE_URL/health" | jq 2>/dev/null || curl -X GET "$BASE_URL/health"
            echo -e "\n2. エージェント一覧:"
            curl -X GET "$BASE_URL/api/adk/agents" | jq 2>/dev/null || curl -X GET "$BASE_URL/api/adk/agents"
            echo -e "\n3. チャットテスト:"
            curl -X POST "$BASE_URL/api/adk/chat" \
                -H "Content-Type: application/json" \
                -d '{"message": "夜泣きで困ってます", "agent_name": "childcare"}' | \
                jq 2>/dev/null || curl -X POST "$BASE_URL/api/adk/chat" \
                -H "Content-Type: application/json" \
                -d '{"message": "夜泣きで困ってます", "agent_name": "childcare"}'
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            ;;
    esac
    echo ""
}

# 11. ログ確認
show_logs() {
    echo -e "${CYAN}📝 ログを確認します...${NC}"
    echo ""
    echo "確認するログを選択してください:"
    echo "  1) Dockerログ (./run.sh logs)"
    echo "  2) ローカル開発ログ (リアルタイム確認)"
    echo ""
    read -p "選択 (1-2): " log_choice
    
    case $log_choice in
        1)
            ./run.sh logs
            ;;
        2)
            echo -e "${YELLOW}ポートの使用状況:${NC}"
            lsof -i :3000,8000 2>/dev/null || echo "ポート3000,8000で動作中のプロセスはありません"
            echo ""
            echo -e "${YELLOW}プロセス確認:${NC}"
            ps aux | grep -E "(uvicorn|next)" | grep -v grep || echo "該当プロセスはありません"
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            ;;
    esac
}

# 12. Cloud Run ステージング デプロイ
deploy_cloud_run_staging() {
    echo -e "${GREEN}☁️  Cloud Run ステージング環境にデプロイします...${NC}"
    echo ""
    
    # 環境変数チェック
    check_cloud_run_prerequisites
    
    echo -e "${BLUE}📦 ステージング環境デプロイを開始します...${NC}"
    echo -e "${YELLOW}プロジェクト: ${GCP_PROJECT_ID:-'未設定'}${NC}"
    echo -e "${YELLOW}リージョン: ${GCP_REGION:-'asia-northeast1'}${NC}"
    echo ""
    
    read -p "続行しますか？ (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        chmod +x ./scripts/deploy-cloud-run.sh
        ./scripts/deploy-cloud-run.sh staging
    else
        echo -e "${YELLOW}デプロイがキャンセルされました${NC}"
    fi
}

# 13. Cloud Run 本番 デプロイ
deploy_cloud_run_production() {
    echo -e "${RED}☁️  Cloud Run 本番環境にデプロイします...${NC}"
    echo -e "${RED}⚠️  本番環境への変更には十分注意してください！${NC}"
    echo ""
    
    # 環境変数チェック
    check_cloud_run_prerequisites
    
    echo -e "${BLUE}📦 本番環境デプロイを開始します...${NC}"
    echo -e "${YELLOW}プロジェクト: ${GCP_PROJECT_ID:-'未設定'}${NC}"
    echo -e "${YELLOW}リージョン: ${GCP_REGION:-'asia-northeast1'}${NC}"
    echo ""
    
    # 2重確認
    echo -e "${RED}本当に本番環境にデプロイしますか？${NC}"
    read -p "本番デプロイを実行する場合は 'production' と入力してください: " confirm
    if [ "$confirm" = "production" ]; then
        chmod +x ./scripts/deploy-cloud-run.sh
        ./scripts/deploy-cloud-run.sh production
    else
        echo -e "${YELLOW}本番デプロイがキャンセルされました${NC}"
    fi
}

# 14. Cloud Run サービス状態確認
check_cloud_run_status() {
    echo -e "${CYAN}☁️  Cloud Run サービス状態を確認します...${NC}"
    echo ""
    
    # gcloud認証チェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        return
    fi
    
    # 認証確認
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${RED}❌ GCPにログインしていません${NC}"
        echo -e "${YELLOW}   'gcloud auth login' を実行してください${NC}"
        return
    fi
    
    # プロジェクトID確認
    local project_id=${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}
    if [ -z "$project_id" ]; then
        echo -e "${RED}❌ GCPプロジェクトが設定されていません${NC}"
        return
    fi
    
    echo -e "${BLUE}プロジェクト: $project_id${NC}"
    echo -e "${BLUE}リージョン: ${GCP_REGION:-'asia-northeast1'}${NC}"
    echo ""
    
    # Cloud Runサービス一覧
    echo -e "${CYAN}📋 Cloud Run サービス一覧:${NC}"
    gcloud run services list --region=${GCP_REGION:-'asia-northeast1'} 2>/dev/null || echo "サービスが見つかりません"
    echo ""
    
    # 特定サービスの詳細確認
    echo "詳細を確認するサービスを選択してください:"
    echo "  1) genius-frontend-staging"
    echo "  2) genius-backend-staging"
    echo "  3) genius-frontend-production"
    echo "  4) genius-backend-production"
    echo "  5) すべて"
    echo "  0) スキップ"
    echo ""
    read -p "選択 (0-5): " service_choice
    
    local region=${GCP_REGION:-'asia-northeast1'}
    
    case $service_choice in
        1) show_service_details "genius-frontend-staging" "$region" ;;
        2) show_service_details "genius-backend-staging" "$region" ;;
        3) show_service_details "genius-frontend-production" "$region" ;;
        4) show_service_details "genius-backend-production" "$region" ;;
        5) 
            show_service_details "genius-frontend-staging" "$region"
            show_service_details "genius-backend-staging" "$region"
            show_service_details "genius-frontend-production" "$region"
            show_service_details "genius-backend-production" "$region"
            ;;
        0) echo -e "${YELLOW}詳細確認をスキップしました${NC}" ;;
        *) echo -e "${RED}無効な選択です${NC}" ;;
    esac
}

# 15. Cloud Run ログ確認
show_cloud_run_logs() {
    echo -e "${CYAN}☁️  Cloud Run ログを確認します...${NC}"
    echo ""
    
    # gcloud認証チェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        return
    fi
    
    echo "ログを確認するサービスを選択してください:"
    echo "  1) genius-frontend-staging"
    echo "  2) genius-backend-staging"
    echo "  3) genius-frontend-production"
    echo "  4) genius-backend-production"
    echo ""
    read -p "選択 (1-4): " log_choice
    
    local region=${GCP_REGION:-'asia-northeast1'}
    
    case $log_choice in
        1) show_service_logs "genius-frontend-staging" "$region" ;;
        2) show_service_logs "genius-backend-staging" "$region" ;;
        3) show_service_logs "genius-frontend-production" "$region" ;;
        4) show_service_logs "genius-backend-production" "$region" ;;
        *) echo -e "${RED}無効な選択です${NC}" ;;
    esac
}

# 16. Cloud Run 設定・環境確認
check_cloud_run_config() {
    echo -e "${CYAN}☁️  Cloud Run 設定・環境を確認します...${NC}"
    echo ""
    
    # 基本情報表示
    echo -e "${BLUE}=== 基本設定 ===${NC}"
    echo -e "GCP_PROJECT_ID: ${GCP_PROJECT_ID:-'❌ 未設定'}"
    echo -e "GCP_REGION: ${GCP_REGION:-'❌ 未設定 (デフォルト: asia-northeast1)'}"
    echo -e "GCP_SERVICE_ACCOUNT: ${GCP_SERVICE_ACCOUNT:-'❌ 未設定 (デフォルト: genius-backend-sa)'}"
    echo ""
    
    # gcloud設定確認
    echo -e "${BLUE}=== gcloud 設定 ===${NC}"
    if command -v gcloud &> /dev/null; then
        echo -e "✅ gcloud CLI: インストール済み"
        echo -e "バージョン: $(gcloud --version | head -n1)"
        
        if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
            echo -e "✅ 認証: ログイン済み"
            echo -e "アカウント: $(gcloud auth list --filter=status:ACTIVE --format="value(account)")"
        else
            echo -e "❌ 認証: 未ログイン"
        fi
        
        local current_project=$(gcloud config get-value project 2>/dev/null)
        if [ -n "$current_project" ]; then
            echo -e "✅ プロジェクト: $current_project"
        else
            echo -e "❌ プロジェクト: 未設定"
        fi
    else
        echo -e "❌ gcloud CLI: 未インストール"
    fi
    echo ""
    
    # Docker確認
    echo -e "${BLUE}=== Docker 設定 ===${NC}"
    if command -v docker &> /dev/null; then
        echo -e "✅ Docker: インストール済み"
        echo -e "バージョン: $(docker --version)"
        
        if docker info &>/dev/null; then
            echo -e "✅ Docker: 起動中"
        else
            echo -e "❌ Docker: 停止中"
        fi
    else
        echo -e "❌ Docker: 未インストール"
    fi
    echo ""
    
    # 環境ファイル確認
    echo -e "${BLUE}=== 環境ファイル確認 ===${NC}"
    check_env_file "frontend/.env.production" "フロントエンド本番環境"
    check_env_file "backend/.env.production" "バックエンド本番環境"
    check_env_file "frontend/.env.local" "フロントエンドローカル環境"
    check_env_file "backend/.env.dev" "バックエンド開発環境"
    echo ""
    
    # 必要なファイル確認
    echo -e "${BLUE}=== 重要ファイル確認 ===${NC}"
    check_file_exists "scripts/deploy-cloud-run.sh" "デプロイスクリプト"
    check_file_exists "frontend/Dockerfile" "フロントエンドDockerfile"
    check_file_exists "backend/Dockerfile" "バックエンドDockerfile"
    check_file_exists ".github/workflows/deploy-cloud-run.yml" "GitHub Actions設定"
    echo ""
    
    # 推奨設定表示
    echo -e "${YELLOW}=== 推奨設定 ===${NC}"
    echo "1. 環境変数設定:"
    echo "   export GCP_PROJECT_ID='your-project-id'"
    echo "   export GCP_REGION='asia-northeast1'"
    echo ""
    echo "2. gcloud認証:"
    echo "   gcloud auth login"
    echo "   gcloud config set project your-project-id"
    echo ""
    echo "3. Docker起動:"
    echo "   Docker Desktopを起動してください"
}

# ヘルパー関数: Cloud Run前提条件チェック
check_cloud_run_prerequisites() {
    echo -e "${BLUE}🔍 デプロイ前チェック...${NC}"
    
    local has_error=false
    
    # gcloud CLIチェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        has_error=true
    else
        echo -e "${GREEN}✅ gcloud CLI: OK${NC}"
    fi
    
    # Docker チェック
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Dockerがインストールされていません${NC}"
        has_error=true
    elif ! docker info &>/dev/null; then
        echo -e "${RED}❌ Dockerが起動していません${NC}"
        has_error=true
    else
        echo -e "${GREEN}✅ Docker: OK${NC}"
    fi
    
    # gcloud認証チェック
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${RED}❌ GCPにログインしていません${NC}"
        echo -e "${YELLOW}   'gcloud auth login' を実行してください${NC}"
        has_error=true
    else
        echo -e "${GREEN}✅ GCP認証: OK${NC}"
    fi
    
    # プロジェクトIDチェック
    if [ -z "${GCP_PROJECT_ID:-}" ]; then
        echo -e "${YELLOW}⚠️  GCP_PROJECT_ID環境変数が未設定です${NC}"
        echo -e "${YELLOW}   export GCP_PROJECT_ID='your-project-id' を実行してください${NC}"
    else
        echo -e "${GREEN}✅ GCP Project ID: ${GCP_PROJECT_ID}${NC}"
    fi
    
    if [ "$has_error" = true ]; then
        echo ""
        echo -e "${RED}❌ 必要な前提条件が満たされていません${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 前提条件チェック完了${NC}"
    echo ""
    return 0
}

# ヘルパー関数: サービス詳細表示
show_service_details() {
    local service_name=$1
    local region=$2
    
    echo -e "${CYAN}📋 $service_name の詳細:${NC}"
    gcloud run services describe "$service_name" \
        --region="$region" \
        --format="yaml(metadata.name,status.url,status.conditions,spec.template.spec.containers[0].image)" \
        2>/dev/null || echo "  サービスが見つかりません"
    echo ""
}

# ヘルパー関数: サービスログ表示
show_service_logs() {
    local service_name=$1
    local region=$2
    
    echo -e "${CYAN}📝 $service_name のログ (最新50行):${NC}"
    echo ""
    echo "ログタイプを選択してください:"
    echo "  1) リアルタイムログ (tail)"
    echo "  2) 最新ログ (最新50行)"
    echo "  3) エラーログのみ"
    echo ""
    read -p "選択 (1-3): " log_type
    
    case $log_type in
        1)
            echo -e "${YELLOW}リアルタイムログを表示します (Ctrl+Cで停止)...${NC}"
            gcloud run services logs tail "$service_name" --region="$region"
            ;;
        2)
            gcloud run services logs read "$service_name" --region="$region" --limit=50
            ;;
        3)
            echo -e "${YELLOW}エラーログのみ表示...${NC}"
            gcloud run services logs read "$service_name" --region="$region" --filter='severity>=ERROR' --limit=20
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            ;;
    esac
}

# ヘルパー関数: 環境ファイル確認
check_env_file() {
    local file_path=$1
    local description=$2
    
    if [ -f "$file_path" ]; then
        echo -e "✅ $description: $file_path"
    else
        echo -e "❌ $description: $file_path (ファイルなし)"
    fi
}

# ヘルパー関数: ファイル存在確認
check_file_exists() {
    local file_path=$1
    local description=$2
    
    if [ -f "$file_path" ]; then
        echo -e "✅ $description: $file_path"
    else
        echo -e "❌ $description: $file_path (ファイルなし)"
    fi
}

# メイン処理
main() {
    while true; do
        clear
        print_logo
        show_menu
        
        read -p "選択してください (0-16): " choice
        echo ""
        
        case $choice in
            1) start_local_dev ;;
            2) stop_local_dev ;;
            3) start_docker_dev ;;
            4) start_docker_prod ;;
            5) stop_docker ;;
            6) clean_docker ;;
            7) start_fastapi_only ;;
            8) start_adk_ui ;;
            9) start_integrated_dev ;;
            10) test_api ;;
            11) show_logs ;;
            0) 
                echo -e "${GREEN}👋 お疲れ様でした！${NC}"
                exit 0
                ;;
            12) deploy_cloud_run_staging ;;
            13) deploy_cloud_run_production ;;
            14) check_cloud_run_status ;;
            15) show_cloud_run_logs ;;
            16) check_cloud_run_config ;;
            *)
                echo -e "${RED}❌ 無効な選択です。0-16の数字を入力してください。${NC}"
                ;;
        esac
        
        echo ""
        read -p "Enterキーを押して続行..."
    done
}

# スクリプト実行
main "$@"