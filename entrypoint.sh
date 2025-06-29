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
    echo "   ____            _      _   _       "
    echo "  / ___| ___ _ __ (_) ___| | | |___   "
    echo " | |  _ / _ \ '_ \| |/ _ \ | | / __|  "
    echo " | |_| |  __/ | | | |  __/ |_| \__ \  "
    echo "  \____|\___|_| |_|_|\___|\\___/|___/  "
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
    echo -e "${GREEN}🚀 開発環境 (よく使う)${NC}"
    echo -e "  ${YELLOW}1${NC}) 開発環境起動 (フロント:3000+バック:8080)"
    echo -e "  ${YELLOW}2${NC}) テスト環境起動 (フロント:3001+バック:8001)"
    echo -e "  ${YELLOW}3${NC}) インタラクティブ起動メニュー (環境選択)"
    echo -e "  ${YELLOW}4${NC}) 開発環境停止 (全プロセス停止)"
    echo ""
    echo -e "${CYAN}🔧 開発ツール${NC}"
    echo -e "  ${YELLOW}5${NC}) FastAPI単体起動 (バックエンドのみ)"
    echo -e "  ${YELLOW}6${NC}) ADK Web UI起動 (エージェントテスト)"
    echo -e "  ${YELLOW}7${NC}) ADK + FastAPI 同時起動 (統合開発)"
    echo -e "  ${YELLOW}8${NC}) API テスト (curl でエンドポイント確認)"
    echo -e "  ${YELLOW}9${NC}) ログ確認"
    echo ""
    echo -e "${GREEN}📚 ドキュメント${NC}"
    echo -e "  ${YELLOW}10${NC}) ドキュメント自動更新 (ワンショット)"
    echo -e "  ${YELLOW}11${NC}) ドキュメント監視モード (リアルタイム自動更新)"
    echo -e "  ${YELLOW}12${NC}) ドキュメントサーバー起動 (Web版)"
    echo -e "  ${YELLOW}13${NC}) ドキュメントサーバー停止"
    echo ""
    echo -e "${CYAN}🔗 API整合性管理${NC}"
    echo -e "  ${YELLOW}14${NC}) API URL整合性チェック (フロント⇔バック)"
    echo -e "  ${YELLOW}15${NC}) APIマッピング自動更新"
    echo ""
    echo -e "${BLUE}🐳 Docker環境${NC}"
    echo -e "  ${YELLOW}16${NC}) Docker開発環境起動 (./run.sh dev)"
    echo -e "  ${YELLOW}17${NC}) Docker本番環境起動 (./run.sh prod)"
    echo -e "  ${YELLOW}18${NC}) Dockerサービス停止 (./run.sh stop)"
    echo -e "  ${YELLOW}19${NC}) Dockerクリーンアップ (./run.sh clean)"
    echo ""
    echo -e "${GREEN}☁️  Cloud Run デプロイメント${NC}"
    echo -e "  ${YELLOW}20${NC}) 🏗️  Cloud Build デプロイ (ステージング) - ローカルDockerなし"
    echo -e "  ${YELLOW}21${NC}) 🏗️  Cloud Build デプロイ (本番) - ローカルDockerなし"
    echo -e "  ${YELLOW}22${NC}) 🐳 従来型デプロイ (ステージング) - ローカルDockerあり"
    echo -e "  ${YELLOW}23${NC}) 🐳 従来型デプロイ (本番) - ローカルDockerあり"
    echo -e "  ${YELLOW}24${NC}) Cloud Run サービス状態確認"
    echo -e "  ${YELLOW}25${NC}) Cloud Run ログ確認"
    echo -e "  ${YELLOW}26${NC}) Cloud Run 設定・環境確認"
    echo ""
    echo -e "${GREEN}☁️  GCP管理${NC}"
    echo -e "  ${YELLOW}27${NC}) GCPプロジェクト切り替え"
    echo -e "  ${YELLOW}28${NC}) GCP認証・設定確認"
    echo -e "  ${YELLOW}29${NC}) GCP権限・API詳細調査"
    echo ""
    echo -e "${GREEN}🔧 CI/CD セットアップ${NC}"
    echo -e "  ${YELLOW}30${NC}) 🎯 GCP CI/CD環境自動構築 (インタラクティブ)"
    echo -e "  ${YELLOW}31${NC}) 🔐 GitHub Secrets自動設定"
    echo -e "  ${YELLOW}32${NC}) 🧪 CI/CDパイプライン動作テスト"
    echo -e "  ${YELLOW}33${NC}) 🚀 インタラクティブデプロイメント"
    echo ""
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

# 2. ローカル開発環境停止 (全ポート対応)
stop_local_dev() {
    echo -e "${YELLOW}🛑 全開発環境を停止します...${NC}"
    echo "停止するポートを選択してください:"
    echo "  1) 通常の開発環境 (3000/8080)"
    echo "  2) AI開発支援テスト環境 (30001/8001)"
    echo "  3) 全ポート停止 (3000/8080/30001/8001)"
    echo "  4) スクリプト使用 (./scripts/stop_dev.sh)"
    echo ""
    read -p "選択 (1-4): " stop_choice
    
    case $stop_choice in
        1)
            echo "開発環境 (3000/8080) を停止中..."
            lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "   ✅ ポート3000を停止" || echo "   ポート3000: プロセスなし"
            lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8080を停止" || echo "   ポート8080: プロセスなし"
            ;;
        2)
            echo "テスト環境 (3001/8001) を停止中..."
            lsof -ti:3001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート3001を停止" || echo "   ポート3001: プロセスなし"
            lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8001を停止" || echo "   ポート8001: プロセスなし"
            
            # .env.localを復元
            if [ -f frontend/.env.local.backup ]; then
                cd frontend
                mv .env.local.backup .env.local
                echo "   ✅ 元の.env.localを復元"
                cd ..
            fi
            ;;
        3)
            echo "全ポート (3000/8080/3001/8001) を停止中..."
            lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "   ✅ ポート3000を停止" || echo "   ポート3000: プロセスなし"
            lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8080を停止" || echo "   ポート8080: プロセスなし"
            lsof -ti:3001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート3001を停止" || echo "   ポート3001: プロセスなし"
            lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8001を停止" || echo "   ポート8001: プロセスなし"
            
            # .env.localを復元
            if [ -f frontend/.env.local.backup ]; then
                cd frontend
                mv .env.local.backup .env.local
                echo "   ✅ 元の.env.localを復元"
                cd ..
            fi
            ;;
        4)
            echo "スクリプトで停止中..."
            ./scripts/stop_dev.sh
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            ;;
    esac
    echo -e "${GREEN}停止処理完了${NC}"
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
    echo "📛 既存のポート8080プロセスを停止中..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8080を停止" || echo "   ポート8080: プロセスなし"
    
    sleep 2
    
    # FastAPI起動
    echo -e "${GREEN}🚀 FastAPI (ポート8080) を起動中...${NC}"
    cd backend
    
    # 環境チェック
    if [ ! -f .env.dev ]; then
        echo -e "${YELLOW}⚠️  .env.devファイルが見つかりません${NC}"
        echo -e "${YELLOW}   環境変数なしで起動します${NC}"
    fi
    
    # uv が利用可能かチェック
    if command -v uv &> /dev/null; then
        echo -e "${CYAN}uvでFastAPIを起動します...${NC}"
        uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
    else
        echo -e "${CYAN}Pythonで直接FastAPIを起動します...${NC}"
        python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
    fi
}

# 8. ADK Web UI起動 (単体テスト用)
start_adk_ui() {
    echo -e "${CYAN}🤖 ADK Web UI単体テストを起動します...${NC}"
    echo -e "${YELLOW}⚠️  FastAPIが起動中の場合、ポート競合のため停止します${NC}"
    echo ""
    
    # FastAPI停止
    lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "✅ FastAPI (ポート8080) を停止しました" || echo "ポート8080: プロセスなし"
    
    echo ""
    echo "ADKエージェントのディレクトリを選択してください:"
    echo "  1) src/agents (メイン)"
    echo "  2) test_genie (テスト用)"
    echo ""
    read -p "選択 (1-2): " adk_choice
    
    case $adk_choice in
        1)
            echo -e "${GREEN}src/agentsでADK Web UI (ポート8080) を起動...${NC}"
            cd backend/src/agents && adk web
            ;;
        2)
            echo -e "${GREEN}test_genieでADK Web UI (ポート8080) を起動...${NC}"
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
    lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8080を停止" || echo "   ポート8080: プロセスなし"
    lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8001を停止" || echo "   ポート8001: プロセスなし"
    
    sleep 2
    
    # FastAPI起動 (ポート8080)
    echo -e "${GREEN}🔧 FastAPI (ポート8080) を起動中...${NC}"
    cd backend
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload &
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
    echo -e "${BLUE}🔌 FastAPI: http://localhost:8080${NC}"
    echo -e "${BLUE}📖 API ドキュメント: http://localhost:8080/docs${NC}"
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
    
    BASE_URL="http://localhost:8080"
    
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
            lsof -i :3000,8080 2>/dev/null || echo "ポート3000,8080で動作中のプロセスはありません"
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

# 14. Cloud Build デプロイ (ステージング) - ローカルDockerなし
deploy_cloudbuild_staging() {
    echo -e "${GREEN}🏗️  Cloud Build ステージング環境にデプロイします...${NC}"
    echo -e "${CYAN}✨ ローカルDockerは不要です - すべてクラウドで処理${NC}"
    echo ""
    
    # 環境変数チェック
    if ! check_cloudbuild_prerequisites; then
        return 1
    fi
    
    echo -e "${BLUE}📦 Cloud Build ステージング環境デプロイを開始します...${NC}"
    echo -e "${YELLOW}プロジェクト: ${GCP_PROJECT_ID:-'未設定'}${NC}"
    echo -e "${YELLOW}リージョン: ${GCP_REGION:-'asia-northeast1'}${NC}"
    echo -e "${YELLOW}方式: Cloud Build (No Local Docker)${NC}"
    echo ""
    
    chmod +x ./scripts/deploy-cloudbuild.sh
    ./scripts/deploy-cloudbuild.sh staging "${GCP_PROJECT_ID}"
}

# 15. Cloud Build デプロイ (本番) - ローカルDockerなし
deploy_cloudbuild_production() {
    echo -e "${RED}🏗️  Cloud Build 本番環境にデプロイします...${NC}"
    echo -e "${RED}⚠️  本番環境への変更には十分注意してください！${NC}"
    echo -e "${CYAN}✨ ローカルDockerは不要です - すべてクラウドで処理${NC}"
    echo ""
    
    # 環境変数チェック
    if ! check_cloudbuild_prerequisites; then
        return 1
    fi
    
    echo -e "${BLUE}📦 Cloud Build 本番環境デプロイを開始します...${NC}"
    echo -e "${YELLOW}プロジェクト: ${GCP_PROJECT_ID:-'未設定'}${NC}"
    echo -e "${YELLOW}リージョン: ${GCP_REGION:-'asia-northeast1'}${NC}"
    echo -e "${YELLOW}方式: Cloud Build (No Local Docker)${NC}"
    echo ""
    
    # 2重確認
    echo -e "${RED}本当に本番環境にデプロイしますか？${NC}"
    read -p "本番デプロイを実行する場合は 'production' と入力してください: " confirm
    if [ "$confirm" = "production" ]; then
        chmod +x ./scripts/deploy-cloudbuild.sh
        ./scripts/deploy-cloudbuild.sh production "${GCP_PROJECT_ID}"
    else
        echo -e "${YELLOW}本番デプロイがキャンセルされました${NC}"
    fi
}

# 16. 従来型デプロイ (ステージング) - ローカルDockerあり
deploy_traditional_staging() {
    echo -e "${GREEN}🐳 従来型 ステージング環境にデプロイします...${NC}"
    echo -e "${YELLOW}⚠️  ローカルDockerが必要です${NC}"
    echo ""
    
    # 環境変数チェック
    if ! check_cloud_run_prerequisites; then
        return 1
    fi
    
    echo -e "${BLUE}📦 従来型ステージング環境デプロイを開始します...${NC}"
    echo -e "${YELLOW}プロジェクト: ${GCP_PROJECT_ID:-'未設定'}${NC}"
    echo -e "${YELLOW}リージョン: ${GCP_REGION:-'asia-northeast1'}${NC}"
    echo ""
    
    chmod +x ./scripts/deploy-cloud-run.sh
    ./scripts/deploy-cloud-run.sh staging
}

# 17. 従来型デプロイ (本番) - ローカルDockerあり
deploy_traditional_production() {
    echo -e "${RED}🐳 従来型 本番環境にデプロイします...${NC}"
    echo -e "${RED}⚠️  本番環境への変更には十分注意してください！${NC}"
    echo -e "${YELLOW}⚠️  ローカルDockerが必要です${NC}"
    echo ""
    
    # 環境変数チェック
    if ! check_cloud_run_prerequisites; then
        return 1
    fi
    
    echo -e "${BLUE}📦 従来型本番環境デプロイを開始します...${NC}"
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

# 18. Cloud Run サービス状態確認
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

# ヘルパー関数: Cloud Build前提条件チェック（ローカルDockerは不要）
check_cloudbuild_prerequisites() {
    echo -e "${BLUE}🔍 Cloud Build デプロイ前チェック...${NC}"
    
    local has_error=false
    
    # gcloud CLIチェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        echo -e "${YELLOW}   https://cloud.google.com/sdk/docs/install${NC}"
        has_error=true
    else
        echo -e "${GREEN}✅ gcloud CLI: インストール済み${NC}"
    fi
    
    # gcloud認証チェック
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${RED}❌ GCPにログインしていません${NC}"
        echo -e "${YELLOW}   実行: gcloud auth login${NC}"
        has_error=true
    else
        echo -e "${GREEN}✅ GCP認証: 認証済み${NC}"
        local account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
        echo -e "${BLUE}   アカウント: ${account}${NC}"
    fi
    
    # プロジェクトIDチェック
    if [ -z "${GCP_PROJECT_ID:-}" ]; then
        echo -e "${RED}❌ GCP_PROJECT_ID環境変数が未設定です${NC}"
        echo -e "${YELLOW}   設定: export GCP_PROJECT_ID='your-project-id'${NC}"
        echo -e "${YELLOW}   ヘルパー: ./scripts/setup-deploy-env.sh${NC}"
        has_error=true
    else
        echo -e "${GREEN}✅ GCP Project ID: ${GCP_PROJECT_ID}${NC}"
        
        # プロジェクトアクセス確認
        if gcloud projects describe "${GCP_PROJECT_ID}" &>/dev/null; then
            echo -e "${GREEN}✅ プロジェクトアクセス: OK${NC}"
        else
            echo -e "${RED}❌ プロジェクト '${GCP_PROJECT_ID}' にアクセスできません${NC}"
            echo -e "${YELLOW}   プロジェクトIDまたは権限を確認してください${NC}"
            has_error=true
        fi
    fi
    
    # Cloud Build の利点を表示
    echo -e "${CYAN}✨ Cloud Build の利点:${NC}"
    echo -e "${CYAN}   🚫 ローカルDockerは不要${NC}"
    echo -e "${CYAN}   ⚡ 並行ビルドで高速${NC}"
    echo -e "${CYAN}   ☁️  すべてクラウドで処理${NC}"
    
    if [ "$has_error" = true ]; then
        echo ""
        echo -e "${RED}❌ 必要な前提条件が満たされていません${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Cloud Build デプロイ準備完了${NC}"
    echo ""
    return 0
}

# ヘルパー関数: 従来型Cloud Run前提条件チェック（ローカルDocker必要）
check_cloud_run_prerequisites() {
    echo -e "${BLUE}🔍 従来型デプロイ前チェック...${NC}"
    
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
        echo -e "${GREEN}✅ Docker: 起動中${NC}"
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
    
    echo -e "${GREEN}✅ 従来型デプロイ準備完了${NC}"
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

# 17. テスト環境起動 (AI開発支援用ポート3001+8001)
start_test_environment() {
    echo -e "${CYAN}🤖 AI開発支援用テスト環境を起動します...${NC}"
    echo -e "${YELLOW}⚠️  開発者ローカル環境(3000/8080)との競合を避けるため、3001/8001ポートを使用します${NC}"
    echo ""
    
    # 既存プロセス停止
    echo "📛 既存のテスト環境プロセスを停止中..."
    lsof -ti:3001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート3001を停止" || echo "   ポート3001: プロセスなし"
    lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8001を停止" || echo "   ポート8001: プロセスなし"
    
    sleep 2
    
    # FastAPI起動 (ポート8001)
    echo -e "${GREEN}🔧 FastAPI (ポート8001) を起動中...${NC}"
    cd backend
    
    # 環境チェック
    if [ ! -f .env.dev ]; then
        echo -e "${YELLOW}⚠️  .env.devファイルが見つかりません${NC}"
        echo -e "${YELLOW}   環境変数なしで起動します${NC}"
    fi
    
    # 環境変数を設定してバックエンド起動
    echo -e "${CYAN}バックエンド (ポート8001) を起動中...${NC}"
    PORT=8001 FRONTEND_PORT=3001 LOG_LEVEL=info uv run python -m src.main &
    
    FASTAPI_PID=$!
    echo "   FastAPI PID: $FASTAPI_PID"
    cd ..
    
    sleep 3
    
    # フロントエンド起動 (ポート3001)
    echo -e "${GREEN}🎨 フロントエンド (ポート3001) を起動中...${NC}"
    cd frontend
    
    # 元の.env.localをバックアップしてテスト環境設定を適用
    if [ -f .env.test ]; then
        if [ -f .env.local ]; then
            cp .env.local .env.local.backup
            echo "   元の.env.localをバックアップ"
        fi
        cp .env.test .env.local
        echo "   テスト環境設定(.env.test)を適用"
    fi
    
    # Next.js開発サーバーをポート3001で起動（API URLも設定）
    NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1 npm run dev -- -p 3001 &
    FRONTEND_PID=$!
    echo "   フロントエンド PID: $FRONTEND_PID"
    cd ..
    
    sleep 3
    
    echo ""
    echo -e "${GREEN}✅ AI開発支援用テスト環境起動完了！${NC}"
    echo ""
    echo -e "${BLUE}📱 フロントエンド (テスト): http://localhost:3001${NC}"
    echo -e "${BLUE}🔌 FastAPI (テスト): http://localhost:8001${NC}"
    echo -e "${BLUE}📖 API ドキュメント (テスト): http://localhost:8001/docs${NC}"
    echo ""
    echo -e "${CYAN}💡 開発者ローカル環境との分離：${NC}"
    echo -e "   📍 開発者用: フロント 3000、バック 8080"
    echo -e "   🤖 AI支援用: フロント 3001、バック 8001"
    echo ""
    echo -e "${YELLOW}停止するには選択肢2で全停止してください${NC}"
}

# 18. GCPプロジェクト切り替え
switch_gcp_project() {
    echo -e "${CYAN}☁️  GCPプロジェクト切り替え${NC}"
    echo ""
    
    # gcloud CLIチェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        echo -e "${YELLOW}   https://cloud.google.com/sdk/docs/install からインストールしてください${NC}"
        return 1
    fi
    
    # 現在の設定表示
    echo -e "${BLUE}=== 現在の設定 ===${NC}"
    local current_project=$(gcloud config get-value project 2>/dev/null || echo "未設定")
    local current_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "未ログイン")
    
    echo -e "現在のプロジェクト: ${YELLOW}$current_project${NC}"
    echo -e "現在のアカウント: ${YELLOW}$current_account${NC}"
    echo ""
    
    # 認証チェック
    if [ "$current_account" = "未ログイン" ]; then
        echo -e "${RED}❌ GCPにログインしていません${NC}"
        echo -e "${YELLOW}先にログインしますか？ (y/N): ${NC}"
        read -p "" login_choice
        if [[ $login_choice =~ ^[Yy]$ ]]; then
            echo -e "${CYAN}ログイン中...${NC}"
            gcloud auth login
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ ログインに失敗しました${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}ログインがキャンセルされました${NC}"
            return 1
        fi
    fi
    
    # プロジェクト選択
    echo -e "${BLUE}=== プロジェクト選択 ===${NC}"
    echo "切り替え方法を選択してください:"
    echo "  1) プロジェクト一覧から選択"
    echo "  2) プロジェクトIDを直接入力"
    echo "  3) よく使うプロジェクト（プリセット）"
    echo "  0) キャンセル"
    echo ""
    read -p "選択 (0-3): " switch_choice
    
    case $switch_choice in
        1)
            echo -e "${CYAN}プロジェクト一覧を取得中...${NC}"
            echo ""
            
            # プロジェクト一覧を取得
            local projects=$(gcloud projects list --format="table(projectId,name)" --sort-by=projectId 2>/dev/null)
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ プロジェクト一覧の取得に失敗しました${NC}"
                return 1
            fi
            
            echo "$projects"
            echo ""
            read -p "プロジェクトIDを入力してください: " project_id
            ;;
        2)
            read -p "プロジェクトIDを入力してください: " project_id
            ;;
        3)
            echo -e "${CYAN}よく使うプロジェクト:${NC}"
            echo "  1) team-sa-labo"
            echo "  2) genius-dev"
            echo "  3) genius-staging"
            echo "  4) genius-production"
            echo ""
            read -p "選択 (1-4): " preset_choice
            
            case $preset_choice in
                1) project_id="team-sa-labo" ;;
                2) project_id="genius-dev" ;;
                3) project_id="genius-staging" ;;
                4) project_id="genius-production" ;;
                *) 
                    echo -e "${RED}無効な選択です${NC}"
                    return 1
                    ;;
            esac
            ;;
        0)
            echo -e "${YELLOW}キャンセルされました${NC}"
            return 0
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            return 1
            ;;
    esac
    
    # プロジェクトIDの検証
    if [ -z "$project_id" ]; then
        echo -e "${RED}❌ プロジェクトIDが入力されていません${NC}"
        return 1
    fi
    
    # プロジェクト切り替え実行
    echo -e "${CYAN}プロジェクトを '$project_id' に切り替え中...${NC}"
    gcloud config set project "$project_id"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ プロジェクト切り替え完了${NC}"
        echo ""
        
        # 切り替え後の確認
        echo -e "${BLUE}=== 切り替え後の設定 ===${NC}"
        echo -e "プロジェクト: ${GREEN}$(gcloud config get-value project 2>/dev/null)${NC}"
        echo -e "アカウント: ${GREEN}$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)${NC}"
        
        # アカウント・プロジェクト適合性チェック
        echo ""
        echo -e "${YELLOW}アカウント・プロジェクト適合性をチェックしますか？ (y/N): ${NC}"
        read -p "" check_compatibility
        if [[ $check_compatibility =~ ^[Yy]$ ]]; then
            check_account_project_compatibility "$project_id"
        fi
    else
        echo -e "${RED}❌ プロジェクト切り替えに失敗しました${NC}"
        echo -e "${YELLOW}   プロジェクトIDが正しいか、権限があるか確認してください${NC}"
        return 1
    fi
}

# 19. GCP認証・設定確認
check_gcp_auth_config() {
    echo -e "${CYAN}☁️  GCP認証・設定確認${NC}"
    echo ""
    
    # gcloud CLIチェック
    echo -e "${BLUE}=== gcloud CLI ===${NC}"
    if command -v gcloud &> /dev/null; then
        echo -e "✅ gcloud CLI: インストール済み"
        local gcloud_version=$(gcloud --version | head -n1)
        echo -e "   バージョン: $gcloud_version"
    else
        echo -e "❌ gcloud CLI: 未インストール"
        echo -e "${YELLOW}   https://cloud.google.com/sdk/docs/install からインストールしてください${NC}"
        return 1
    fi
    echo ""
    
    # 認証状態確認
    echo -e "${BLUE}=== 認証状態 ===${NC}"
    local auth_accounts=$(gcloud auth list --format="table(account,status)" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "$auth_accounts"
        
        local active_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
        if [ -n "$active_account" ]; then
            echo -e "✅ アクティブアカウント: ${GREEN}$active_account${NC}"
        else
            echo -e "❌ アクティブアカウント: なし"
            echo -e "${YELLOW}   'gcloud auth login' でログインしてください${NC}"
        fi
    else
        echo -e "❌ 認証情報の取得に失敗しました"
    fi
    echo ""
    
    # プロジェクト設定確認
    echo -e "${BLUE}=== プロジェクト設定 ===${NC}"
    local current_project=$(gcloud config get-value project 2>/dev/null)
    if [ -n "$current_project" ]; then
        echo -e "✅ 現在のプロジェクト: ${GREEN}$current_project${NC}"
        
        # プロジェクト詳細取得
        local project_info=$(gcloud projects describe "$current_project" --format="value(name,projectNumber)" 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo -e "   プロジェクト詳細: $project_info"
        fi
    else
        echo -e "❌ プロジェクト: 未設定"
        echo -e "${YELLOW}   'gcloud config set project PROJECT_ID' で設定してください${NC}"
    fi
    echo ""
    
    # 設定一覧
    echo -e "${BLUE}=== gcloud設定一覧 ===${NC}"
    gcloud config list 2>/dev/null | head -20
    echo ""
    
    # 利用可能なプロジェクト（権限チェック）
    echo -e "${BLUE}=== 利用可能なプロジェクト ===${NC}"
    echo -e "${CYAN}アクセス可能なプロジェクト一覧を取得中...${NC}"
    local projects=$(gcloud projects list --format="table(projectId,name,projectNumber)" --limit=10 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "$projects"
    else
        echo -e "${YELLOW}プロジェクト一覧の取得に失敗しました（権限不足の可能性）${NC}"
    fi
    echo ""
    
    # ADC (Application Default Credentials) 確認
    echo -e "${BLUE}=== Application Default Credentials ===${NC}"
    if gcloud auth application-default print-access-token &>/dev/null; then
        echo -e "✅ ADC: 設定済み"
        local adc_account=$(gcloud auth application-default print-access-token | head -c 20 2>/dev/null)
        echo -e "   アクセストークン: ${adc_account}... (一部のみ表示)"
    else
        echo -e "❌ ADC: 未設定"
        echo -e "${YELLOW}   'gcloud auth application-default login' で設定してください${NC}"
    fi
    echo ""
    
    # アカウント・プロジェクト適合性チェック
    if [ -n "$current_project" ] && [ "$active_account" != "未ログイン" ]; then
        echo -e "${BLUE}=== アカウント・プロジェクト適合性 ===${NC}"
        check_account_project_compatibility "$current_project"
        echo ""
    fi
    
    # クイックアクション
    echo -e "${BLUE}=== クイックアクション ===${NC}"
    echo "実行したいアクションを選択してください:"
    echo "  1) 新しいアカウントでログイン"
    echo "  2) ADC設定"
    echo "  3) プロジェクト切り替え"
    echo "  4) 設定をリセット"
    echo "  5) アカウント・プロジェクト適合性詳細チェック"
    echo "  0) 戻る"
    echo ""
    read -p "選択 (0-5): " action_choice
    
    case $action_choice in
        1)
            echo -e "${CYAN}新しいアカウントでログイン中...${NC}"
            gcloud auth login
            ;;
        2)
            echo -e "${CYAN}ADC設定中...${NC}"
            gcloud auth application-default login
            ;;
        3)
            switch_gcp_project
            ;;
        4)
            echo -e "${RED}設定をリセットしますか？ (y/N): ${NC}"
            read -p "" reset_confirm
            if [[ $reset_confirm =~ ^[Yy]$ ]]; then
                echo -e "${CYAN}設定リセット中...${NC}"
                gcloud auth revoke --all
                gcloud config unset project
                echo -e "${GREEN}✅ 設定がリセットされました${NC}"
            fi
            ;;
        5)
            if [ -n "$current_project" ]; then
                check_account_project_compatibility "$current_project" "detailed"
            else
                echo -e "${YELLOW}プロジェクトが設定されていません${NC}"
            fi
            ;;
        0)
            echo -e "${YELLOW}戻ります${NC}"
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            ;;
    esac
}

# アカウント・プロジェクト適合性チェック
check_account_project_compatibility() {
    local project_id=$1
    local mode=${2:-"simple"}  # simple or detailed
    
    if [ -z "$project_id" ]; then
        echo -e "${RED}❌ プロジェクトIDが指定されていません${NC}"
        return 1
    fi
    
    local current_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
    if [ -z "$current_account" ]; then
        echo -e "${RED}❌ アクティブなアカウントが見つかりません${NC}"
        return 1
    fi
    
    echo -e "${CYAN}🔍 アカウント・プロジェクト適合性チェック中...${NC}"
    echo -e "アカウント: ${YELLOW}$current_account${NC}"
    echo -e "プロジェクト: ${YELLOW}$project_id${NC}"
    echo ""
    
    # 1. プロジェクトアクセス権チェック
    echo -e "${BLUE}📋 プロジェクトアクセス権:${NC}"
    if gcloud projects describe "$project_id" &>/dev/null; then
        echo -e "✅ プロジェクトにアクセス可能"
        
        # プロジェクト詳細情報
        local project_info=$(gcloud projects describe "$project_id" --format="value(name,projectNumber,lifecycleState)" 2>/dev/null)
        if [ -n "$project_info" ]; then
            echo -e "   プロジェクト情報: $project_info"
        fi
    else
        echo -e "❌ プロジェクトにアクセス不可"
        echo -e "${YELLOW}   権限がないか、プロジェクトが存在しません${NC}"
        return 1
    fi
    echo ""
    
    # 2. IAM権限チェック
    echo -e "${BLUE}🔐 IAM権限:${NC}"
    local iam_roles=$(gcloud projects get-iam-policy "$project_id" \
        --flatten="bindings" \
        --format="value(bindings.role)" \
        --filter="bindings.members:user:$current_account" 2>/dev/null | sort | uniq)
    
    if [ -n "$iam_roles" ]; then
        echo -e "✅ IAM権限あり"
        echo -e "${CYAN}   付与されている役割:${NC}"
        while IFS= read -r role; do
            if [ -n "$role" ]; then
                echo -e "   - $role"
            fi
        done <<< "$iam_roles"
    else
        echo -e "❌ IAM権限なし"
        echo -e "${YELLOW}   このアカウントにはプロジェクトの明示的な権限がありません${NC}"
    fi
    echo ""
    
    # 3. アカウントドメインチェック
    echo -e "${BLUE}📧 アカウントドメイン分析:${NC}"
    local account_domain=$(echo "$current_account" | cut -d'@' -f2)
    echo -e "   ドメイン: ${YELLOW}$account_domain${NC}"
    
    # 推奨ドメインチェック
    case "$account_domain" in
        "gmail.com")
            echo -e "   📱 個人アカウント (Gmail)"
            ;;
        "googlemail.com")
            echo -e "   📱 個人アカウント (Gmail)"
            ;;
        *)
            echo -e "   🏢 組織アカウント ($account_domain)"
            ;;
    esac
    echo ""
    
    # 4. プロジェクト・アカウント適合性判定
    echo -e "${BLUE}🎯 適合性判定:${NC}"
    
    # プロジェクト名からの推測
    local compatibility_score=0
    local recommendations=()
    
    case "$project_id" in
        *"team-sa-labo"*)
            if [[ "$account_domain" == "gmail.com" || "$account_domain" == "googlemail.com" ]]; then
                echo -e "✅ 個人開発プロジェクト + 個人アカウント: 適合"
                compatibility_score=$((compatibility_score + 2))
            else
                echo -e "⚠️  個人開発プロジェクト + 組織アカウント: 注意"
                recommendations+=("個人プロジェクトには個人アカウントを推奨")
            fi
            ;;
        *"genius"*|*"production"*|*"staging"*)
            if [[ "$account_domain" != "gmail.com" && "$account_domain" != "googlemail.com" ]]; then
                echo -e "✅ 本番/ステージング環境 + 組織アカウント: 適合"
                compatibility_score=$((compatibility_score + 2))
            else
                echo -e "⚠️  本番/ステージング環境 + 個人アカウント: 注意"
                recommendations+=("本番環境には組織アカウントを推奨")
            fi
            ;;
        *)
            echo -e "🔍 プロジェクト種別を特定できません"
            compatibility_score=$((compatibility_score + 1))
            ;;
    esac
    
    # 権限レベルによる判定
    if echo "$iam_roles" | grep -q "roles/owner"; then
        echo -e "✅ オーナー権限: 完全なアクセス権限"
        compatibility_score=$((compatibility_score + 2))
    elif echo "$iam_roles" | grep -q "roles/editor"; then
        echo -e "✅ 編集者権限: 開発作業に適切"
        compatibility_score=$((compatibility_score + 2))
    elif echo "$iam_roles" | grep -q "roles/viewer"; then
        echo -e "⚠️  閲覧者権限: 読み取り専用"
        recommendations+=("開発作業には編集者権限以上が必要")
    elif [ -n "$iam_roles" ]; then
        echo -e "ℹ️  カスタム権限: 個別設定"
        compatibility_score=$((compatibility_score + 1))
    fi
    
    # 総合判定
    echo ""
    if [ $compatibility_score -ge 4 ]; then
        echo -e "${GREEN}🎉 総合判定: 適合 (スコア: $compatibility_score/4)${NC}"
        echo -e "${GREEN}   このアカウント・プロジェクトの組み合わせは適切です${NC}"
    elif [ $compatibility_score -ge 2 ]; then
        echo -e "${YELLOW}⚠️  総合判定: 注意 (スコア: $compatibility_score/4)${NC}"
        echo -e "${YELLOW}   使用可能ですが、以下の推奨事項を確認してください${NC}"
    else
        echo -e "${RED}❌ 総合判定: 不適合 (スコア: $compatibility_score/4)${NC}"
        echo -e "${RED}   アカウントまたはプロジェクトの見直しを推奨します${NC}"
    fi
    
    # 推奨事項表示
    if [ ${#recommendations[@]} -gt 0 ]; then
        echo ""
        echo -e "${BLUE}📝 推奨事項:${NC}"
        for rec in "${recommendations[@]}"; do
            echo -e "   • $rec"
        done
    fi
    
    # 詳細モードの場合は追加情報
    if [ "$mode" = "detailed" ]; then
        echo ""
        echo -e "${BLUE}🔍 詳細情報:${NC}"
        
        # API有効化状況
        echo -e "${CYAN}API有効化状況:${NC}"
        local enabled_apis=$(gcloud services list --enabled --format="value(config.name)" --limit=10 2>/dev/null | head -5)
        if [ -n "$enabled_apis" ]; then
            echo -e "   有効なAPI (上位5つ):"
            while IFS= read -r api; do
                if [ -n "$api" ]; then
                    echo -e "   - $api"
                fi
            done <<< "$enabled_apis"
        else
            echo -e "   API情報を取得できませんでした"
        fi
        
        # 利用量・課金情報（権限があれば）
        echo ""
        echo -e "${CYAN}プロジェクト利用状況:${NC}"
        if gcloud compute instances list --format="value(name)" --limit=1 &>/dev/null; then
            local compute_count=$(gcloud compute instances list --format="value(name)" 2>/dev/null | wc -l)
            echo -e "   Compute Engine インスタンス: $compute_count台"
        fi
        
        if gcloud run services list --format="value(metadata.name)" --limit=1 &>/dev/null; then
            local run_count=$(gcloud run services list --format="value(metadata.name)" 2>/dev/null | wc -l)
            echo -e "   Cloud Run サービス: $run_count個"
        fi
    fi
    
    echo ""
    return 0
}

# 20. GCP権限・API詳細調査
check_gcp_permissions_detailed() {
    echo -e "${CYAN}🔍 GCP権限・API詳細調査${NC}"
    echo ""
    
    # gcloud CLIチェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        return 1
    fi
    
    # プロジェクト確認
    local current_project=$(gcloud config get-value project 2>/dev/null)
    local current_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
    
    if [ -z "$current_project" ] || [ -z "$current_account" ]; then
        echo -e "${RED}❌ プロジェクトまたはアカウントが設定されていません${NC}"
        return 1
    fi
    
    echo -e "${BLUE}=== 基本情報 ===${NC}"
    echo -e "プロジェクト: ${YELLOW}$current_project${NC}"
    echo -e "アカウント: ${YELLOW}$current_account${NC}"
    echo ""
    
    # 調査項目選択
    echo -e "${BLUE}調査項目を選択してください:${NC}"
    echo "  1) 全体権限サマリー（推奨）"
    echo "  2) IAM権限詳細"
    echo "  3) API有効化状況"
    echo "  4) Vertex AI / Gemini 権限"
    echo "  5) Cloud Run 権限"
    echo "  6) 必要権限診断"
    echo "  7) 全調査実行"
    echo "  0) 戻る"
    echo ""
    read -p "選択 (0-7): " investigation_choice
    
    case $investigation_choice in
        1) check_permissions_summary "$current_project" "$current_account" ;;
        2) check_iam_permissions_detailed "$current_project" "$current_account" ;;
        3) check_api_status_detailed "$current_project" ;;
        4) check_vertex_ai_permissions "$current_project" "$current_account" ;;
        5) check_cloud_run_permissions "$current_project" "$current_account" ;;
        6) diagnose_required_permissions "$current_project" "$current_account" ;;
        7) 
            check_permissions_summary "$current_project" "$current_account"
            echo ""
            check_api_status_detailed "$current_project"
            echo ""
            check_vertex_ai_permissions "$current_project" "$current_account"
            echo ""
            check_cloud_run_permissions "$current_project" "$current_account"
            echo ""
            diagnose_required_permissions "$current_project" "$current_account"
            ;;
        0) echo -e "${YELLOW}戻ります${NC}" ;;
        *) echo -e "${RED}無効な選択です${NC}" ;;
    esac
}

# 権限サマリー
check_permissions_summary() {
    local project_id=$1
    local account=$2
    
    echo -e "${CYAN}📋 全体権限サマリー${NC}"
    echo ""
    
    # プロジェクトアクセス確認
    if gcloud projects describe "$project_id" &>/dev/null; then
        echo -e "✅ プロジェクトアクセス: OK"
    else
        echo -e "❌ プロジェクトアクセス: NG"
        return 1
    fi
    
    # 主要な権限チェック
    local basic_roles=$(gcloud projects get-iam-policy "$project_id" \
        --flatten="bindings" \
        --format="value(bindings.role)" \
        --filter="bindings.members:user:$account" 2>/dev/null | grep -E "(owner|editor|viewer)" | head -3)
    
    if [ -n "$basic_roles" ]; then
        echo -e "✅ 基本権限: $(echo "$basic_roles" | tr '\n' ' ')"
    else
        echo -e "⚠️  基本権限: カスタム権限のみ"
    fi
    
    # 重要API確認
    local critical_apis=("aiplatform.googleapis.com" "run.googleapis.com" "cloudbuild.googleapis.com")
    local enabled_critical=0
    
    for api in "${critical_apis[@]}"; do
        if gcloud services list --enabled --filter="config.name:$api" --format="value(config.name)" 2>/dev/null | grep -q "$api"; then
            enabled_critical=$((enabled_critical + 1))
        fi
    done
    
    echo -e "✅ 重要API有効化: $enabled_critical/${#critical_apis[@]}"
    
    # 開発環境適合性
    if echo "$basic_roles" | grep -q "editor\|owner"; then
        echo -e "✅ 開発環境適合性: 良好"
    else
        echo -e "⚠️  開発環境適合性: 権限不足の可能性"
    fi
    
    echo ""
}

# IAM権限詳細
check_iam_permissions_detailed() {
    local project_id=$1
    local account=$2
    
    echo -e "${CYAN}🔐 IAM権限詳細${NC}"
    echo ""
    
    # すべての権限取得
    local all_roles=$(gcloud projects get-iam-policy "$project_id" \
        --flatten="bindings" \
        --format="value(bindings.role)" \
        --filter="bindings.members:user:$account" 2>/dev/null | sort)
    
    if [ -z "$all_roles" ]; then
        echo -e "❌ 明示的な権限が見つかりません"
        echo -e "${YELLOW}   継承された権限または組織レベルの権限がある可能性${NC}"
        return 1
    fi
    
    echo -e "${BLUE}付与されている権限:${NC}"
    local role_count=0
    while IFS= read -r role; do
        if [ -n "$role" ]; then
            role_count=$((role_count + 1))
            
            # 権限の説明を追加
            case "$role" in
                "roles/owner")
                    echo -e "   $role_count. ${GREEN}$role${NC} - 完全なアクセス権限"
                    ;;
                "roles/editor")
                    echo -e "   $role_count. ${GREEN}$role${NC} - 読み取り・書き込み権限"
                    ;;
                "roles/viewer")
                    echo -e "   $role_count. ${YELLOW}$role${NC} - 読み取り専用"
                    ;;
                *"aiplatform"*)
                    echo -e "   $role_count. ${CYAN}$role${NC} - Vertex AI 関連"
                    ;;
                *"run"*)
                    echo -e "   $role_count. ${CYAN}$role${NC} - Cloud Run 関連"
                    ;;
                *"cloudbuild"*)
                    echo -e "   $role_count. ${CYAN}$role${NC} - Cloud Build 関連"
                    ;;
                *)
                    echo -e "   $role_count. $role"
                    ;;
            esac
        fi
    done <<< "$all_roles"
    
    echo ""
    echo -e "${BLUE}権限総数: $role_count${NC}"
    echo ""
}

# API有効化状況詳細
check_api_status_detailed() {
    local project_id=$1
    
    echo -e "${CYAN}🔌 API有効化状況詳細${NC}"
    echo ""
    
    # 開発に必要な主要API一覧
    local required_apis=(
        "aiplatform.googleapis.com:Vertex AI (Gemini)"
        "run.googleapis.com:Cloud Run"
        "cloudbuild.googleapis.com:Cloud Build"
        "containerregistry.googleapis.com:Container Registry"
        "storage.googleapis.com:Cloud Storage"
        "logging.googleapis.com:Cloud Logging"
        "monitoring.googleapis.com:Cloud Monitoring"
    )
    
    echo -e "${BLUE}重要API確認:${NC}"
    local enabled_count=0
    
    for api_info in "${required_apis[@]}"; do
        local api_name=$(echo "$api_info" | cut -d':' -f1)
        local api_desc=$(echo "$api_info" | cut -d':' -f2)
        
        if gcloud services list --enabled --filter="config.name:$api_name" --format="value(config.name)" 2>/dev/null | grep -q "$api_name"; then
            echo -e "   ✅ $api_desc ($api_name)"
            enabled_count=$((enabled_count + 1))
        else
            echo -e "   ❌ $api_desc ($api_name)"
        fi
    done
    
    echo ""
    echo -e "${BLUE}有効化状況: $enabled_count/${#required_apis[@]}${NC}"
    
    if [ $enabled_count -lt ${#required_apis[@]} ]; then
        echo ""
        echo -e "${YELLOW}📝 未有効化APIを有効にする方法:${NC}"
        echo -e "   gcloud services enable [API名]"
        echo -e "   例: gcloud services enable aiplatform.googleapis.com"
    fi
    
    # 全体のAPI数確認
    local total_enabled=$(gcloud services list --enabled --format="value(config.name)" 2>/dev/null | wc -l)
    echo ""
    echo -e "${BLUE}総有効化API数: $total_enabled${NC}"
    echo ""
}

# Vertex AI / Gemini 権限
check_vertex_ai_permissions() {
    local project_id=$1
    local account=$2
    
    echo -e "${CYAN}🤖 Vertex AI / Gemini 権限調査${NC}"
    echo ""
    
    # Vertex AI API確認
    echo -e "${BLUE}Vertex AI API状況:${NC}"
    if gcloud services list --enabled --filter="config.name:aiplatform.googleapis.com" --format="value(config.name)" 2>/dev/null | grep -q "aiplatform.googleapis.com"; then
        echo -e "✅ Vertex AI API: 有効"
    else
        echo -e "❌ Vertex AI API: 無効"
        echo -e "${YELLOW}   有効化コマンド: gcloud services enable aiplatform.googleapis.com${NC}"
    fi
    
    # Vertex AI 関連権限確認
    echo ""
    echo -e "${BLUE}Vertex AI 権限:${NC}"
    local ai_roles=$(gcloud projects get-iam-policy "$project_id" \
        --flatten="bindings" \
        --format="value(bindings.role)" \
        --filter="bindings.members:user:$account" 2>/dev/null | grep -i aiplatform)
    
    if [ -n "$ai_roles" ]; then
        echo -e "✅ Vertex AI専用権限:"
        while IFS= read -r role; do
            if [ -n "$role" ]; then
                echo -e "   - $role"
            fi
        done <<< "$ai_roles"
    else
        echo -e "⚠️  Vertex AI専用権限なし"
        
        # 基本権限でカバーされているかチェック
        local basic_roles=$(gcloud projects get-iam-policy "$project_id" \
            --flatten="bindings" \
            --format="value(bindings.role)" \
            --filter="bindings.members:user:$account" 2>/dev/null | grep -E "(owner|editor)")
        
        if [ -n "$basic_roles" ]; then
            echo -e "✅ 基本権限でカバー: $(echo "$basic_roles" | head -1)"
        else
            echo -e "❌ 基本権限も不足"
        fi
    fi
    
    # 実際にVertex AIにアクセステスト
    echo ""
    echo -e "${BLUE}Vertex AI アクセステスト:${NC}"
    echo -e "${CYAN}モデル一覧取得を試行中...${NC}"
    
    local test_result=$(gcloud ai models list --region=us-central1 --limit=1 2>&1)
    if echo "$test_result" | grep -q "PERMISSION_DENIED"; then
        echo -e "❌ アクセス拒否: 権限不足"
        echo -e "${YELLOW}   必要権限: aiplatform.models.list${NC}"
    elif echo "$test_result" | grep -q "API.*not enabled"; then
        echo -e "❌ API未有効化"
    else
        echo -e "✅ アクセス可能"
    fi
    
    # Gemini特有のエラーチェック
    echo ""
    echo -e "${BLUE}Gemini アクセス診断:${NC}"
    if echo "$test_result" | grep -q "403"; then
        echo -e "❌ 403エラー: 権限またはAPI設定の問題"
        echo -e "${YELLOW}   解決策:${NC}"
        echo -e "   1. gcloud services enable aiplatform.googleapis.com"
        echo -e "   2. 編集者権限以上の付与"
        echo -e "   3. プロジェクトでのVertex AI有効化確認"
    else
        echo -e "ℹ️  基本的なアクセスは可能と思われます"
    fi
    
    echo ""
}

# Cloud Run 権限
check_cloud_run_permissions() {
    local project_id=$1
    local account=$2
    
    echo -e "${CYAN}🏃 Cloud Run 権限調査${NC}"
    echo ""
    
    # Cloud Run API確認
    echo -e "${BLUE}Cloud Run API状況:${NC}"
    if gcloud services list --enabled --filter="config.name:run.googleapis.com" --format="value(config.name)" 2>/dev/null | grep -q "run.googleapis.com"; then
        echo -e "✅ Cloud Run API: 有効"
    else
        echo -e "❌ Cloud Run API: 無効"
        echo -e "${YELLOW}   有効化コマンド: gcloud services enable run.googleapis.com${NC}"
    fi
    
    # Cloud Run権限確認
    echo ""
    echo -e "${BLUE}Cloud Run 権限:${NC}"
    local run_roles=$(gcloud projects get-iam-policy "$project_id" \
        --flatten="bindings" \
        --format="value(bindings.role)" \
        --filter="bindings.members:user:$account" 2>/dev/null | grep -i "run")
    
    if [ -n "$run_roles" ]; then
        echo -e "✅ Cloud Run専用権限:"
        while IFS= read -r role; do
            if [ -n "$role" ]; then
                echo -e "   - $role"
            fi
        done <<< "$run_roles"
    else
        echo -e "⚠️  Cloud Run専用権限なし（基本権限でカバーの可能性）"
    fi
    
    # Cloud Runサービス一覧テスト
    echo ""
    echo -e "${BLUE}Cloud Run アクセステスト:${NC}"
    local run_test=$(gcloud run services list --limit=1 2>&1)
    if echo "$run_test" | grep -q "PERMISSION_DENIED"; then
        echo -e "❌ アクセス拒否"
    elif echo "$run_test" | grep -q "API.*not enabled"; then
        echo -e "❌ API未有効化"
    else
        echo -e "✅ アクセス可能"
    fi
    
    echo ""
}

# 必要権限診断
diagnose_required_permissions() {
    local project_id=$1
    local account=$2
    
    echo -e "${CYAN}🩺 必要権限診断${NC}"
    echo ""
    
    echo -e "${BLUE}GenieUs開発に必要な権限診断:${NC}"
    echo ""
    
    # 基本権限チェック
    local has_owner=$(gcloud projects get-iam-policy "$project_id" \
        --flatten="bindings" \
        --format="value(bindings.role)" \
        --filter="bindings.members:user:$account" 2>/dev/null | grep -q "roles/owner" && echo "true" || echo "false")
    
    local has_editor=$(gcloud projects get-iam-policy "$project_id" \
        --flatten="bindings" \
        --format="value(bindings.role)" \
        --filter="bindings.members:user:$account" 2>/dev/null | grep -q "roles/editor" && echo "true" || echo "false")
    
    # 診断結果
    echo -e "${BLUE}基本権限診断:${NC}"
    if [ "$has_owner" = "true" ]; then
        echo -e "✅ オーナー権限: すべての操作が可能"
        local diagnosis="excellent"
    elif [ "$has_editor" = "true" ]; then
        echo -e "✅ 編集者権限: 開発作業に十分"
        local diagnosis="good"
    else
        echo -e "❌ 基本権限不足: 開発作業に制限あり"
        local diagnosis="poor"
    fi
    
    # API診断
    echo ""
    echo -e "${BLUE}API有効化診断:${NC}"
    local critical_apis=("aiplatform.googleapis.com" "run.googleapis.com" "cloudbuild.googleapis.com")
    local enabled_apis=0
    
    for api in "${critical_apis[@]}"; do
        if gcloud services list --enabled --filter="config.name:$api" --format="value(config.name)" 2>/dev/null | grep -q "$api"; then
            enabled_apis=$((enabled_apis + 1))
        fi
    done
    
    if [ $enabled_apis -eq ${#critical_apis[@]} ]; then
        echo -e "✅ 重要API: すべて有効化済み ($enabled_apis/${#critical_apis[@]})"
    elif [ $enabled_apis -gt 0 ]; then
        echo -e "⚠️  重要API: 一部有効化済み ($enabled_apis/${#critical_apis[@]})"
    else
        echo -e "❌ 重要API: 未有効化 ($enabled_apis/${#critical_apis[@]})"
    fi
    
    # 総合診断
    echo ""
    echo -e "${BLUE}総合診断:${NC}"
    if [ "$diagnosis" = "excellent" ] && [ $enabled_apis -eq ${#critical_apis[@]} ]; then
        echo -e "${GREEN}🎉 状態: 最適${NC}"
        echo -e "${GREEN}   GenieUs開発に最適な環境です${NC}"
    elif [ "$diagnosis" = "good" ] && [ $enabled_apis -gt 1 ]; then
        echo -e "${YELLOW}⚠️  状態: 良好${NC}"
        echo -e "${YELLOW}   開発可能ですが、一部改善の余地があります${NC}"
    else
        echo -e "${RED}❌ 状態: 要改善${NC}"
        echo -e "${RED}   開発前に権限・API設定の見直しが必要です${NC}"
    fi
    
    # 改善提案
    echo ""
    echo -e "${BLUE}改善提案:${NC}"
    
    if [ "$has_owner" != "true" ] && [ "$has_editor" != "true" ]; then
        echo -e "   🔧 プロジェクトオーナーに編集者権限以上の付与を依頼"
    fi
    
    if [ $enabled_apis -lt ${#critical_apis[@]} ]; then
        echo -e "   🔧 未有効化APIの有効化:"
        for api in "${critical_apis[@]}"; do
            if ! gcloud services list --enabled --filter="config.name:$api" --format="value(config.name)" 2>/dev/null | grep -q "$api"; then
                echo -e "      gcloud services enable $api"
            fi
        done
    fi
    
    if [ "$project_id" = "blog-sample-381923" ]; then
        echo -e "   🔧 team-sa-laboプロジェクトへの切り替えを検討"
    fi
    
    echo ""
}

# メイン処理
main() {
    while true; do
        clear
        print_logo
        show_menu
        
        read -p "選択してください (0-33): " choice
        echo ""
        
        case $choice in
            1) start_local_dev ;;
            2) start_test_environment ;;
            3) interactive_startup ;;
            4) stop_local_dev ;;
            5) start_fastapi_only ;;
            6) start_adk_ui ;;
            7) start_integrated_dev ;;
            8) test_api ;;
            9) show_logs ;;
            10) update_docs_navigation ;;
            11) watch_docs_changes ;;
            12) start_docs_server_advanced ;;
            13) stop_docs_server ;;
            14) check_api_consistency ;;
            15) update_api_mapping ;;
            16) start_docker_dev ;;
            17) start_docker_prod ;;
            18) stop_docker ;;
            19) clean_docker ;;
            20) deploy_cloudbuild_staging ;;
            21) deploy_cloudbuild_production ;;
            22) deploy_traditional_staging ;;
            23) deploy_traditional_production ;;
            24) check_cloud_run_status ;;
            25) show_cloud_run_logs ;;
            26) check_cloud_run_config ;;
            27) switch_gcp_project ;;
            28) check_gcp_auth_config ;;
            29) check_gcp_permissions_detailed ;;
            30) setup_gcp_cicd ;;
            31) setup_github_secrets ;;
            32) test_cicd_pipeline ;;
            33) interactive_deployment ;;
            0) 
                echo -e "${GREEN}👋 お疲れ様でした！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 無効な選択です。0-33の数字を入力してください。${NC}"
                ;;
        esac
        
        echo ""
        read -p "Enterキーを押して続行..."
    done
}

# 21. インタラクティブ起動メニュー
interactive_startup() {
    echo -e "${CYAN}"
    echo "  ____            _      _   _     "
    echo " / ___| ___ _ __ (_) ___| | | |___ "
    echo "| |  _ / _ \ '_ \| |/ _ \ | | / __|"
    echo "| |_| |  __/ | | | |  __/ |_| \__ \\"
    echo " \____|\_____|_| |_|_|\___|\___/|___/"
    echo -e "${NC}"
    echo -e "${PURPLE}見えない成長に、光をあてる。不安な毎日を、自信に変える。${NC}"
    echo ""
    
    # 環境選択メニュー
    echo -e "${YELLOW}🚀 起動環境を選択してください:${NC}"
    echo ""
    echo "1) 開発環境 (local)  - フロント:3000, バック:8080"
    echo "2) テスト環境 (test)  - フロント:3001, バック:8001"
    echo "3) 戻る"
    echo ""
    
    read -p "選択 (1-3): " env_choice
    
    case $env_choice in
        1)
            ENV_NAME="開発環境"
            FRONTEND_PORT=3000
            BACKEND_PORT=8080
            API_URL="http://localhost:8080/api/v1"
            CORS_PORT=3000
            ;;
        2)
            ENV_NAME="テスト環境"
            FRONTEND_PORT=3001
            BACKEND_PORT=8001
            API_URL="http://localhost:8001/api/v1"
            CORS_PORT=3001
            ;;
        3)
            return
            ;;
        *)
            echo -e "${RED}❌ 無効な選択です。${NC}"
            return
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}📊 起動設定:${NC}"
    echo "  - 環境: $ENV_NAME"
    echo "  - フロントエンド: http://localhost:$FRONTEND_PORT"
    echo "  - バックエンド: http://localhost:$BACKEND_PORT"
    echo "  - API URL: $API_URL"
    echo ""
    
    # 起動モード選択
    echo -e "${YELLOW}🛠️ 起動モードを選択してください:${NC}"
    echo ""
    echo "1) 両方起動 (フロントエンド + バックエンド)"
    echo "2) フロントエンドのみ"
    echo "3) バックエンドのみ"
    echo "4) キャンセル"
    echo ""
    
    read -p "選択 (1-4): " mode_choice
    
    case $mode_choice in
        1)
            echo -e "${GREEN}🚀 フロントエンド + バックエンドを起動します...${NC}"
            start_both_services
            ;;
        2)
            echo -e "${GREEN}🚀 フロントエンドを起動します...${NC}"
            start_frontend_only
            ;;
        3)
            echo -e "${GREEN}🚀 バックエンドを起動します...${NC}"
            start_backend_only
            ;;
        4)
            echo "キャンセルしました。"
            return
            ;;
        *)
            echo -e "${RED}❌ 無効な選択です。${NC}"
            return
            ;;
    esac
}

# 両方起動
start_both_services() {
    echo -e "${GREEN}⚡ バックエンド起動中... (ポート: $BACKEND_PORT)${NC}"
    cd backend
    PORT="$BACKEND_PORT" FRONTEND_PORT="$CORS_PORT" LOG_LEVEL=info uv run python -m src.main &
    BACKEND_PID=$!
    cd ..
    
    echo "⏳ バックエンドの起動を待機中..."
    sleep 5
    
    echo -e "${GREEN}🎨 フロントエンド起動中... (ポート: $FRONTEND_PORT)${NC}"
    cd frontend
    NEXT_PUBLIC_API_URL="$API_URL" npm run dev -- -p "$FRONTEND_PORT" &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ 起動完了!"
    echo "  - フロントエンド: http://localhost:$FRONTEND_PORT"
    echo "  - バックエンド: http://localhost:$BACKEND_PORT"
    echo "  - API仕様書: http://localhost:$BACKEND_PORT/docs"
    echo ""
    echo "🛑 終了するには Ctrl+C を押してください"
    
    # 終了時のクリーンアップ
    cleanup_services() {
        echo ""
        echo "🛑 サーバーを停止中..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✅ 停止完了"
    }
    
    trap cleanup_services EXIT INT TERM
    wait
}

# フロントエンドのみ起動
start_frontend_only() {
    echo -e "${GREEN}🎨 フロントエンド起動中... (ポート: $FRONTEND_PORT)${NC}"
    cd frontend
    NEXT_PUBLIC_API_URL="$API_URL" npm run dev -- -p "$FRONTEND_PORT"
    cd ..
}

# バックエンドのみ起動
start_backend_only() {
    echo -e "${GREEN}⚡ バックエンド起動中... (ポート: $BACKEND_PORT)${NC}"
    cd backend
    PORT="$BACKEND_PORT" FRONTEND_PORT="$CORS_PORT" LOG_LEVEL=info uv run python -m src.main
    cd ..
}

# 22. API URL整合性チェック
check_api_consistency() {
    echo -e "${CYAN}🔍 API URL整合性チェック${NC}"
    echo -e "${BLUE}フロントエンドとバックエンドのAPI URL整合性を検証します${NC}"
    echo ""
    
    # Node.js確認
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js がインストールされていません${NC}"
        echo -e "${YELLOW}   Node.js 16以上をインストールしてください${NC}"
        return 1
    fi
    
    # スクリプト存在確認
    if [ ! -f "scripts/check-api-consistency.js" ]; then
        echo -e "${RED}❌ API整合性チェックスクリプトが見つかりません${NC}"
        echo -e "${YELLOW}   scripts/check-api-consistency.js を確認してください${NC}"
        return 1
    fi
    
    echo -e "${GREEN}🚀 API整合性チェックを実行中...${NC}"
    echo ""
    
    # API整合性チェック実行
    node scripts/check-api-consistency.js
    
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ API整合性チェックが正常に完了しました${NC}"
    else
        echo -e "${RED}❌ API整合性チェックでエラーが発生しました${NC}"
        echo -e "${YELLOW}   修正が必要な項目があります${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📚 その他のコマンド:${NC}"
    echo -e "   ${YELLOW}選択肢23: APIマッピング自動更新${NC}"
    echo -e "   ${YELLOW}./scripts/check-api.sh: APIスクリプト直接実行${NC}"
    
    return $exit_code
}

# 23. APIマッピング自動更新
update_api_mapping() {
    echo -e "${CYAN}🔄 APIマッピング自動更新${NC}"
    echo -e "${BLUE}バックエンドとフロントエンドを解析してAPIマッピングを更新します${NC}"
    echo ""
    
    # Node.js確認
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js がインストールされていません${NC}"
        echo -e "${YELLOW}   Node.js 16以上をインストールしてください${NC}"
        return 1
    fi
    
    # スクリプト存在確認
    if [ ! -f "scripts/update-api-mapping.js" ]; then
        echo -e "${RED}❌ APIマッピング更新スクリプトが見つかりません${NC}"
        echo -e "${YELLOW}   scripts/update-api-mapping.js を確認してください${NC}"
        return 1
    fi
    
    # 現在のマッピングファイルをバックアップ
    if [ -f "api-endpoints-mapping.json" ]; then
        local backup_file="api-endpoints-mapping.json.backup.$(date +%Y%m%d_%H%M%S)"
        cp "api-endpoints-mapping.json" "$backup_file"
        echo -e "${YELLOW}📋 既存マッピングをバックアップ: ${backup_file}${NC}"
    fi
    
    echo -e "${GREEN}🚀 APIマッピング更新を実行中...${NC}"
    echo ""
    
    # APIマッピング更新実行
    node scripts/update-api-mapping.js
    
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ APIマッピング更新が正常に完了しました${NC}"
        echo -e "${CYAN}📊 更新後の整合性チェックを実行します...${NC}"
        echo ""
        
        # 更新後に整合性チェックを自動実行
        node scripts/check-api-consistency.js
        
    else
        echo -e "${RED}❌ APIマッピング更新でエラーが発生しました${NC}"
        
        # エラー時はバックアップから復元
        if [ -f "$backup_file" ]; then
            echo -e "${YELLOW}🔄 バックアップから復元中...${NC}"
            cp "$backup_file" "api-endpoints-mapping.json"
            echo -e "${GREEN}✅ バックアップから復元しました${NC}"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}📚 その他のコマンド:${NC}"
    echo -e "   ${YELLOW}選択肢22: API整合性チェック${NC}"
    echo -e "   ${YELLOW}./scripts/update-api.sh: APIマッピング更新スクリプト直接実行${NC}"
    
    return $exit_code
}

# 26. ドキュメントサーバー起動（高機能版）
# 26. ドキュメント自動更新 (ワンショット)
update_docs_navigation() {
    echo -e "${GREEN}📝 ドキュメント自動更新を実行します...${NC}"
    echo -e "${BLUE}🔍 docs/配下の.mdファイルをスキャンしてnavigation.jsonとindex.htmlを更新します${NC}"
    echo ""
    
    if [ ! -f "scripts/generate-docs-navigation.js" ]; then
        echo -e "${RED}❌ scripts/generate-docs-navigation.js が見つかりません${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🔄 実行中...${NC}"
    node scripts/generate-docs-navigation.js
    
    echo ""
    echo -e "${GREEN}✅ ドキュメント更新完了${NC}"
    echo -e "${CYAN}📍 確認先:${NC}"
    echo "   - Web版: docs/web/index.html"
    echo "   - 簡易版: docs/index.html"
}

# 27. ドキュメント監視モード (リアルタイム自動更新)
watch_docs_changes() {
    echo -e "${GREEN}👀 ドキュメント監視モードを開始します...${NC}"
    echo -e "${BLUE}📝 .mdファイルの変更を監視して自動更新します${NC}"
    echo -e "${YELLOW}🛑 停止するには Ctrl+C を押してください${NC}"
    echo ""
    
    if [ ! -f "scripts/watch-docs.js" ]; then
        echo -e "${RED}❌ scripts/watch-docs.js が見つかりません${NC}"
        return 1
    fi
    
    echo -e "${CYAN}🚀 監視開始...${NC}"
    node scripts/watch-docs.js
}

# 28. ドキュメントサーバー起動 (Web版)
start_docs_server_advanced() {
    echo -e "${GREEN}📖 ドキュメントサーバー（高機能版）を起動します...${NC}"
    echo -e "${BLUE}🔄 自動更新機能・検索機能付きでマークダウンを表示します${NC}"
    echo -e "${CYAN}📍 アクセス先: http://localhost:15080${NC}"
    echo ""
    
    # docsディレクトリの存在確認
    if [ ! -d "docs" ]; then
        echo -e "${RED}❌ docsディレクトリが見つかりません${NC}"
        return 1
    fi
    
    # start-docs.shスクリプトの存在確認
    if [ ! -f "docs/start-docs.sh" ]; then
        echo -e "${RED}❌ docs/start-docs.sh が見つかりません${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🚀 起動中...${NC}"
    cd docs && ./start-docs.sh
}

# 27. ドキュメントサーバー起動（シンプル版）
start_docs_server_simple() {
    echo -e "${GREEN}📖 ドキュメントサーバー（シンプル版）を起動します...${NC}"
    echo -e "${BLUE}📋 軽量HTMLビューアーでマークダウンを表示します${NC}"
    echo -e "${CYAN}📍 アクセス先: http://localhost:15080${NC}"
    echo ""
    
    # docsディレクトリの存在確認
    if [ ! -d "docs" ]; then
        echo -e "${RED}❌ docsディレクトリが見つかりません${NC}"
        return 1
    fi
    
    # start-docs.shスクリプトの存在確認
    if [ ! -f "docs/start-docs.sh" ]; then
        echo -e "${RED}❌ docs/start-docs.sh が見つかりません${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🚀 起動中...${NC}"
    cd docs && ./start-docs.sh simple
}

# 28. ドキュメントサーバー停止
stop_docs_server() {
    echo -e "${YELLOW}🛑 ドキュメントサーバーを停止します...${NC}"
    echo ""
    
    # docsディレクトリの存在確認
    if [ ! -d "docs" ]; then
        echo -e "${RED}❌ docsディレクトリが見つかりません${NC}"
        return 1
    fi
    
    # start-docs.shスクリプトの存在確認
    if [ ! -f "docs/start-docs.sh" ]; then
        echo -e "${RED}❌ docs/start-docs.sh が見つかりません${NC}"
        return 1
    fi
    
    cd docs && ./start-docs.sh stop
}

# ヘルパー関数: GCPアカウント選択
select_gcp_account() {
    echo -e "${CYAN}👤 GCPアカウント選択${NC}"
    echo "======================="
    echo ""
    
    # 利用可能なアカウント一覧取得
    local accounts=$(gcloud auth list --format="value(account)" 2>/dev/null)
    if [ -z "$accounts" ]; then
        echo -e "${RED}❌ 認証済みアカウントが見つかりません${NC}"
        echo -e "${YELLOW}💡 ログインしますか？ (y/N): ${NC}"
        read -p "" login_choice
        
        if [[ $login_choice =~ ^[Yy]$ ]]; then
            echo -e "${CYAN}🔐 GCPにログイン中...${NC}"
            gcloud auth login
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ ログインに失敗しました${NC}"
                return 1
            fi
            accounts=$(gcloud auth list --format="value(account)" 2>/dev/null)
        else
            echo -e "${YELLOW}⚠️ ログインがキャンセルされました${NC}"
            return 1
        fi
    fi
    
    # アカウント選択メニュー
    echo -e "${BLUE}📋 利用可能なアカウント:${NC}"
    echo ""
    
    local account_array=()
    local count=1
    
    while IFS= read -r account; do
        if [ -n "$account" ]; then
            echo -e "  ${YELLOW}${count}${NC}) $account"
            account_array+=("$account")
            count=$((count + 1))
        fi
    done <<< "$accounts"
    
    echo -e "  ${YELLOW}${count}${NC}) 新しいアカウントでログイン"
    echo -e "  ${YELLOW}0${NC}) キャンセル"
    echo ""
    
    read -p "アカウントを選択してください (0-$count): " account_choice
    
    if [ "$account_choice" = "0" ]; then
        echo -e "${YELLOW}⚠️ キャンセルされました${NC}"
        return 1
    elif [ "$account_choice" = "$count" ]; then
        echo -e "${CYAN}🔐 新しいアカウントでログイン中...${NC}"
        gcloud auth login
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ ログインに失敗しました${NC}"
            return 1
        fi
        # 新しくログインしたアカウントを取得
        SELECTED_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
    elif [ "$account_choice" -ge 1 ] && [ "$account_choice" -lt "$count" ]; then
        local array_index=$((account_choice - 1))
        SELECTED_ACCOUNT="${account_array[$array_index]}"
        
        # アカウント切り替え
        echo -e "${CYAN}🔄 アカウントを切り替え中: $SELECTED_ACCOUNT${NC}"
        gcloud config set account "$SELECTED_ACCOUNT"
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ アカウント切り替えに失敗しました${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ 無効な選択です${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 選択されたアカウント: $SELECTED_ACCOUNT${NC}"
    echo ""
    return 0
}

# ヘルパー関数: GCPプロジェクト選択
select_gcp_project() {
    echo -e "${CYAN}🏗️ GCPプロジェクト選択${NC}"
    echo "======================"
    echo ""
    
    echo -e "${BLUE}📋 プロジェクト選択方法:${NC}"
    echo ""
    echo -e "  ${YELLOW}1${NC}) 全プロジェクトから選択"
    echo -e "  ${YELLOW}2${NC}) blog-で始まるプロジェクトから選択"
    echo -e "  ${YELLOW}3${NC}) プロジェクトIDを直接入力"
    echo -e "  ${YELLOW}0${NC}) キャンセル"
    echo ""
    
    read -p "選択してください (0-3): " project_method
    
    case $project_method in
        1)
            echo -e "${CYAN}📋 全プロジェクトを取得中...${NC}"
            local projects=$(gcloud projects list --format="value(projectId,name)" --sort-by=projectId 2>/dev/null)
            ;;
        2)
            echo -e "${CYAN}📋 blog-プロジェクトを取得中...${NC}"
            local projects=$(gcloud projects list --filter="projectId:blog*" --format="value(projectId,name)" --sort-by=projectId 2>/dev/null)
            ;;
        3)
            echo -e "${YELLOW}💡 プロジェクトIDを直接入力してください:${NC}"
            read -p "Project ID: " direct_project_id
            if [ -z "$direct_project_id" ]; then
                echo -e "${RED}❌ プロジェクトIDが入力されていません${NC}"
                return 1
            fi
            SELECTED_PROJECT="$direct_project_id"
            echo -e "${GREEN}✅ 選択されたプロジェクト: $SELECTED_PROJECT${NC}"
            echo ""
            return 0
            ;;
        0)
            echo -e "${YELLOW}⚠️ キャンセルされました${NC}"
            return 1
            ;;
        *)
            echo -e "${RED}❌ 無効な選択です${NC}"
            return 1
            ;;
    esac
    
    if [ -z "$projects" ]; then
        echo -e "${RED}❌ プロジェクトが見つかりません${NC}"
        echo -e "${YELLOW}💡 権限またはフィルタ条件を確認してください${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}📋 利用可能なプロジェクト:${NC}"
    echo ""
    
    local project_array=()
    local count=1
    
    while IFS= read -r project_line; do
        if [ -n "$project_line" ]; then
            local project_id=$(echo "$project_line" | cut -f1)
            local project_name=$(echo "$project_line" | cut -f2)
            echo -e "  ${YELLOW}${count}${NC}) $project_id"
            if [ -n "$project_name" ] && [ "$project_name" != "$project_id" ]; then
                echo -e "      └─ $project_name"
            fi
            project_array+=("$project_id")
            count=$((count + 1))
        fi
    done <<< "$projects"
    
    echo -e "  ${YELLOW}0${NC}) キャンセル"
    echo ""
    
    read -p "プロジェクトを選択してください (0-$((count-1))): " project_choice
    
    if [ "$project_choice" = "0" ]; then
        echo -e "${YELLOW}⚠️ キャンセルされました${NC}"
        return 1
    elif [ "$project_choice" -ge 1 ] && [ "$project_choice" -lt "$count" ]; then
        local array_index=$((project_choice - 1))
        SELECTED_PROJECT="${project_array[$array_index]}"
        
        # プロジェクト切り替え
        echo -e "${CYAN}🔄 プロジェクトを切り替え中: $SELECTED_PROJECT${NC}"
        gcloud config set project "$SELECTED_PROJECT"
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ プロジェクト切り替えに失敗しました${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ 無効な選択です${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 選択されたプロジェクト: $SELECTED_PROJECT${NC}"
    echo ""
    return 0
}

# 29. GCP CI/CD環境自動構築 (インタラクティブ版)
setup_gcp_cicd() {
    echo -e "${GREEN}🔧 GCP CI/CD環境自動構築 (インタラクティブ)${NC}"
    echo "=================================================="
    echo ""
    
    # gcloud CLIチェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        echo -e "${YELLOW}   https://cloud.google.com/sdk/docs/install からインストールしてください${NC}"
        return 1
    fi
    
    # Step 1: アカウント選択
    if ! select_gcp_account; then
        echo -e "${RED}❌ アカウント選択に失敗しました${NC}"
        return 1
    fi
    
    # Step 2: プロジェクト選択
    if ! select_gcp_project; then
        echo -e "${RED}❌ プロジェクト選択に失敗しました${NC}"
        return 1
    fi
    
    # Step 3: 設定確認
    echo -e "${BLUE}📋 設定確認${NC}"
    echo "==================="
    echo -e "アカウント: ${YELLOW}$SELECTED_ACCOUNT${NC}"
    echo -e "プロジェクト: ${YELLOW}$SELECTED_PROJECT${NC}"
    echo ""
    
    echo -e "${YELLOW}💡 この設定でGCP CI/CD環境を構築しますか？ (y/N): ${NC}"
    read -p "" confirm_setup
    
    if [[ ! $confirm_setup =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⚠️ セットアップがキャンセルされました${NC}"
        return 1
    fi
    
    # Step 4: スクリプト実行
    echo -e "${CYAN}🚀 GCP CI/CD環境構築を開始します...${NC}"
    echo ""
    
    # スクリプト実行権限確認
    if [ ! -f "./scripts/setup-gcp-cicd.sh" ]; then
        echo -e "${RED}❌ setup-gcp-cicd.sh が見つかりません${NC}"
        return 1
    fi
    
    chmod +x ./scripts/setup-gcp-cicd.sh
    ./scripts/setup-gcp-cicd.sh "$SELECTED_PROJECT"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ GCP CI/CD環境構築完了！${NC}"
        echo -e "${YELLOW}📋 次のステップ: entrypoint.sh で選択肢31を実行してGitHub Secretsを設定してください${NC}"
    else
        echo -e "${RED}❌ GCP CI/CD環境構築でエラーが発生しました${NC}"
    fi
    
    return $exit_code
}

# 30. GitHub Secrets自動設定
setup_github_secrets() {
    echo -e "${GREEN}🔐 GitHub Secrets自動設定${NC}"
    echo "=================================="
    echo ""
    
    # GitHub CLIチェック
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
        return 1
    fi
    
    # GitHub認証チェック
    if ! gh auth status &>/dev/null; then
        echo -e "${YELLOW}🔑 GitHub認証が必要です${NC}"
        echo "以下のコマンドを実行してログインしてください:"
        echo "gh auth login"
        return 1
    fi
    
    # 設定ファイル存在確認
    if [ ! -f "./gcp-secrets.env" ]; then
        echo -e "${RED}❌ gcp-secrets.env ファイルが見つかりません${NC}"
        echo -e "${YELLOW}   先に選択肢29でGCP CI/CD環境構築を実行してください${NC}"
        return 1
    fi
    
    echo -e "${CYAN}🚀 GitHub Secrets設定を開始します...${NC}"
    echo ""
    
    # スクリプト実行権限確認
    if [ ! -f "./scripts/setup-github-secrets.sh" ]; then
        echo -e "${RED}❌ setup-github-secrets.sh が見つかりません${NC}"
        return 1
    fi
    
    chmod +x ./scripts/setup-github-secrets.sh
    ./scripts/setup-github-secrets.sh
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ GitHub Secrets設定完了！${NC}"
        echo -e "${YELLOW}📋 次のステップ: entrypoint.sh で選択肢31を実行してCI/CDをテストしてください${NC}"
    else
        echo -e "${RED}❌ GitHub Secrets設定でエラーが発生しました${NC}"
    fi
    
    return $exit_code
}

# 31. CI/CDパイプライン動作テスト
test_cicd_pipeline() {
    echo -e "${GREEN}🧪 CI/CDパイプライン動作テスト${NC}"
    echo "=================================="
    echo ""
    
    # GitHub CLIチェック
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) がインストールされていません${NC}"
        return 1
    fi
    
    # GitHub認証チェック
    if ! gh auth status &>/dev/null; then
        echo -e "${YELLOW}🔑 GitHub認証が必要です${NC}"
        echo "以下のコマンドを実行してログインしてください:"
        echo "gh auth login"
        return 1
    fi
    
    echo -e "${BLUE}🔍 現在のブランチとリポジトリ状態確認:${NC}"
    echo ""
    
    local current_branch=$(git branch --show-current)
    local repo_status=$(git status --porcelain)
    
    echo "現在のブランチ: $current_branch"
    echo "変更ファイル数: $(echo "$repo_status" | wc -l)"
    echo ""
    
    if [ -n "$repo_status" ]; then
        echo -e "${YELLOW}⚠️ 未コミットの変更があります:${NC}"
        git status --short
        echo ""
        echo -e "${YELLOW}先にコミットしますか？ (y/N): ${NC}"
        read -p "" commit_choice
        
        if [[ $commit_choice =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "${CYAN}📝 コミットメッセージを入力してください:${NC}"
            read -p "Commit message: " commit_message
            
            if [ -n "$commit_message" ]; then
                git add .
                git commit -m "$commit_message"
                echo -e "${GREEN}✅ コミット完了${NC}"
            else
                echo -e "${RED}❌ コミットメッセージが入力されていません${NC}"
                return 1
            fi
        fi
    fi
    
    echo -e "${BLUE}🚀 CI/CDテスト方法を選択してください:${NC}"
    echo "  1) テスト用ブランチでPR作成 (推奨)"
    echo "  2) 現在のブランチで直接プッシュ"
    echo "  3) GitHub Actions実行状況確認のみ"
    echo "  0) キャンセル"
    echo ""
    read -p "選択 (0-3): " test_choice
    
    case $test_choice in
        1)
            echo -e "${CYAN}🌿 テスト用ブランチでPRテスト${NC}"
            local test_branch="test-cicd-$(date +%Y%m%d-%H%M%S)"
            
            echo "テストブランチ: $test_branch"
            git checkout -b "$test_branch"
            
            # 空コミット作成
            git commit --allow-empty -m "test: CI/CD pipeline test"
            git push origin "$test_branch"
            
            echo ""
            echo -e "${YELLOW}📝 PR作成中...${NC}"
            gh pr create --title "Test: CI/CD Pipeline" --body "CI/CDパイプライン動作テスト用PR" || true
            
            echo ""
            echo -e "${GREEN}✅ テスト用PR作成完了${NC}"
            echo -e "${YELLOW}📋 GitHub Actionsの実行を確認してください:${NC}"
            echo "   gh run list --repo shu-nagaoka/GenieUs"
            ;;
            
        2)
            echo -e "${CYAN}⚡ 直接プッシュテスト${NC}"
            
            if [ "$current_branch" = "main" ]; then
                echo -e "${RED}⚠️ mainブランチへの直接プッシュは本番デプロイを実行します${NC}"
                echo -e "${YELLOW}実行しますか？ (y/N): ${NC}"
                read -p "" push_choice
                
                if [[ ! $push_choice =~ ^[Yy]$ ]]; then
                    echo -e "${YELLOW}キャンセルされました${NC}"
                    return 0
                fi
            fi
            
            git push origin "$current_branch"
            echo -e "${GREEN}✅ プッシュ完了${NC}"
            ;;
            
        3)
            echo -e "${CYAN}👀 GitHub Actions実行状況確認${NC}"
            ;;
            
        0|*)
            echo -e "${YELLOW}キャンセルされました${NC}"
            return 0
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}📊 GitHub Actions実行状況:${NC}"
    gh run list --repo shu-nagaoka/GenieUs --limit 5
    
    echo ""
    echo -e "${YELLOW}💡 便利なコマンド:${NC}"
    echo "   gh run watch --repo shu-nagaoka/GenieUs  # 実行状況をリアルタイム監視"
    echo "   gh run list --repo shu-nagaoka/GenieUs   # 実行履歴一覧"
    echo "   gh run view --repo shu-nagaoka/GenieUs   # 最新実行の詳細"
}

# 33. インタラクティブデプロイメント
interactive_deployment() {
    echo -e "${GREEN}🚀 インタラクティブデプロイメント${NC}"
    echo "=================================="
    echo ""
    
    # gcloud CLIチェック
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLIがインストールされていません${NC}"
        echo -e "${YELLOW}   https://cloud.google.com/sdk/docs/install からインストールしてください${NC}"
        return 1
    fi
    
    # Step 1: アカウント選択
    if ! select_gcp_account; then
        echo -e "${RED}❌ アカウント選択に失敗しました${NC}"
        return 1
    fi
    
    # Step 2: プロジェクト選択
    if ! select_gcp_project; then
        echo -e "${RED}❌ プロジェクト選択に失敗しました${NC}"
        return 1
    fi
    
    # Step 3: デプロイ方式選択
    echo -e "${BLUE}🏗️ デプロイ方式選択${NC}"
    echo "==================="
    echo ""
    echo -e "  ${YELLOW}1${NC}) Cloud Build デプロイ (ステージング) - 推奨"
    echo -e "  ${YELLOW}2${NC}) Cloud Build デプロイ (本番)"
    echo -e "  ${YELLOW}3${NC}) 従来型デプロイ (ステージング) - ローカルDocker必要"
    echo -e "  ${YELLOW}4${NC}) 従来型デプロイ (本番) - ローカルDocker必要"
    echo -e "  ${YELLOW}5${NC}) GitHub Actions経由デプロイ"
    echo -e "  ${YELLOW}0${NC}) キャンセル"
    echo ""
    
    read -p "デプロイ方式を選択してください (0-5): " deploy_choice
    
    # Step 4: 設定確認
    echo ""
    echo -e "${BLUE}📋 デプロイ設定確認${NC}"
    echo "========================"
    echo -e "アカウント: ${YELLOW}$SELECTED_ACCOUNT${NC}"
    echo -e "プロジェクト: ${YELLOW}$SELECTED_PROJECT${NC}"
    
    case $deploy_choice in
        1)
            echo -e "デプロイ方式: ${CYAN}Cloud Build (ステージング)${NC}"
            echo -e "特徴: ${GREEN}ローカルDocker不要、高速並行ビルド${NC}"
            ;;
        2)
            echo -e "デプロイ方式: ${RED}Cloud Build (本番)${NC}"
            echo -e "特徴: ${RED}本番環境、注意が必要${NC}"
            ;;
        3)
            echo -e "デプロイ方式: ${CYAN}従来型 (ステージング)${NC}"
            echo -e "特徴: ${YELLOW}ローカルDocker必要${NC}"
            ;;
        4)
            echo -e "デプロイ方式: ${RED}従来型 (本番)${NC}"
            echo -e "特徴: ${RED}本番環境、ローカルDocker必要${NC}"
            ;;
        5)
            echo -e "デプロイ方式: ${BLUE}GitHub Actions${NC}"
            echo -e "特徴: ${CYAN}CI/CDパイプライン経由${NC}"
            ;;
        0)
            echo -e "${YELLOW}⚠️ デプロイがキャンセルされました${NC}"
            return 0
            ;;
        *)
            echo -e "${RED}❌ 無効な選択です${NC}"
            return 1
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}💡 この設定でデプロイを実行しますか？ (y/N): ${NC}"
    read -p "" confirm_deploy
    
    if [[ ! $confirm_deploy =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⚠️ デプロイがキャンセルされました${NC}"
        return 1
    fi
    
    # Step 5: デプロイ実行
    echo -e "${CYAN}🚀 デプロイを開始します...${NC}"
    echo ""
    
    case $deploy_choice in
        1)
            # Cloud Build ステージング
            export GCP_PROJECT_ID="$SELECTED_PROJECT"
            deploy_cloudbuild_staging
            ;;
        2)
            # Cloud Build 本番
            export GCP_PROJECT_ID="$SELECTED_PROJECT"
            deploy_cloudbuild_production
            ;;
        3)
            # 従来型ステージング
            export GCP_PROJECT_ID="$SELECTED_PROJECT"
            deploy_traditional_staging
            ;;
        4)
            # 従来型本番
            export GCP_PROJECT_ID="$SELECTED_PROJECT"
            deploy_traditional_production
            ;;
        5)
            # GitHub Actions経由
            echo -e "${BLUE}🔄 GitHub Actions経由デプロイ${NC}"
            echo ""
            echo -e "${YELLOW}💡 GitHub ActionsでデプロイするにはGitにプッシュしてください${NC}"
            echo "1. git add ."
            echo "2. git commit -m \"deploy: [メッセージ]\""
            echo "3. git push origin main  # 本番デプロイ"
            echo "   または"
            echo "   git push origin develop  # ステージングデプロイ"
            echo ""
            echo -e "${CYAN}📊 GitHub Actions実行状況:${NC}"
            if command -v gh &> /dev/null && gh auth status &>/dev/null; then
                gh run list --repo shu-nagaoka/GenieUs --limit 5
            else
                echo -e "${YELLOW}⚠️ GitHub CLI未設定。ブラウザでGitHub Actionsを確認してください${NC}"
            fi
            ;;
    esac
}

# スクリプト実行
main "$@"