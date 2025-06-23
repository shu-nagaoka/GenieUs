#!/bin/bash

# GieieNest Backend Entrypoint Script
# Usage: ./entrypoint.sh [option]

set -e

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}═══════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}🚀 GieieNest Backend Development Tools${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════${NC}"
}

print_menu() {
    echo ""
    echo -e "${CYAN}📋 起動オプション${NC}"
    echo -e "  1) FastAPI起動 (ポート8000)"
    echo -e "  2) ADK Web UI起動 (ポート8001)"
    echo -e "  3) 両方同時起動 (FastAPI:8000 + ADK:8001)"
    echo -e "  4) テスト実行"
    echo -e "  5) ログ確認"
    echo -e "  6) 開発環境セットアップ"
    echo ""
    echo -e "${YELLOW}🛑 その他${NC}"
    echo -e "  0) 終了"
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════${NC}"
}

stop_port() {
    local port=$1
    echo -e "${YELLOW}📛 既存のポート${port}プロセスを停止中...${NC}"
    
    # ポートを使用しているプロセスを確認
    local pid=$(lsof -ti:${port})
    if [ ! -z "$pid" ]; then
        kill -TERM $pid 2>/dev/null || true
        sleep 2
        # まだ生きていたら強制終了
        kill -KILL $pid 2>/dev/null || true
        echo -e "   ${GREEN}✅ ポート${port}を停止${NC}"
    else
        echo -e "   ${BLUE}ℹ️  ポート${port}は使用されていません${NC}"
    fi
}

start_fastapi() {
    echo -e "${GREEN}🚀 FastAPI (ポート8000) を起動中...${NC}"
    stop_port 8000
    echo "uvでFastAPIを起動します..."
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
}

start_adk_web() {
    echo -e "${GREEN}🚀 ADK Web UI (ポート8001) を起動中...${NC}"
    stop_port 8001
    echo "ADK Web UIを起動します..."
    echo -e "${BLUE}ℹ️  ADKはプロジェクトルートからエージェントを自動発見します${NC}"
    # プロジェクトルート（backendディレクトリ）から起動
    cd "$(dirname "$0")"
    uv run adk web --port 8001
}

start_both() {
    echo -e "${GREEN}🚀 FastAPI + ADK Web UI 同時起動中...${NC}"
    stop_port 8000
    stop_port 8001
    
    echo -e "${BLUE}バックグラウンドでFastAPIを起動...${NC}"
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
    FASTAPI_PID=$!
    
    echo -e "${BLUE}フォアグラウンドでADK Web UIを起動...${NC}"
    echo "FastAPI: http://localhost:8000"
    echo "ADK Web UI: http://localhost:8001"
    echo ""
    echo "Ctrl+C で両方停止します"
    
    # 終了時にFastAPIも停止
    trap "kill $FASTAPI_PID 2>/dev/null || true" EXIT
    
    # プロジェクトルートから起動
    cd "$(dirname "$0")"
    uv run adk web --port 8001
}

run_tests() {
    echo -e "${GREEN}🧪 テスト実行中...${NC}"
    if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
        uv run pytest
    else
        echo -e "${YELLOW}⚠️ テスト設定が見つかりません${NC}"
        echo "簡易テストを実行します..."
        uv run python test_simple_chat.py
    fi
}

show_logs() {
    echo -e "${GREEN}📋 ログ確認${NC}"
    echo "どのログを確認しますか？"
    echo "1) ADKログ (adk.log)"
    echo "2) バックエンドログ (backend.log)"
    echo "3) 両方"
    read -p "選択 (1-3): " log_choice
    
    case $log_choice in
        1)
            if [ -f "adk.log" ]; then
                tail -f adk.log
            else
                echo -e "${YELLOW}adk.logが見つかりません${NC}"
            fi
            ;;
        2)
            if [ -f "backend.log" ]; then
                tail -f backend.log
            else
                echo -e "${YELLOW}backend.logが見つかりません${NC}"
            fi
            ;;
        3)
            if [ -f "adk.log" ] && [ -f "backend.log" ]; then
                echo -e "${BLUE}ADKログとバックエンドログを同時表示${NC}"
                tail -f adk.log backend.log
            else
                echo -e "${YELLOW}ログファイルが見つかりません${NC}"
            fi
            ;;
        *)
            echo -e "${RED}無効な選択です${NC}"
            ;;
    esac
}

setup_dev() {
    echo -e "${GREEN}🔧 開発環境セットアップ中...${NC}"
    
    # UV確認
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}uvが見つかりません。インストールしてください${NC}"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    # 依存関係インストール
    echo "依存関係をインストール中..."
    uv sync
    
    # 環境変数確認
    if [ ! -f ".env.dev" ]; then
        echo -e "${YELLOW}⚠️ .env.devが見つかりません${NC}"
        echo "Google Cloud認証を確認してください:"
        echo "gcloud auth application-default login"
    fi
    
    echo -e "${GREEN}✅ セットアップ完了${NC}"
}

# メイン処理
main() {
    print_header
    
    # コマンドライン引数での直接実行
    case "$1" in
        "fastapi"|"api"|"1")
            start_fastapi
            ;;
        "adk"|"web"|"2")
            start_adk_web
            ;;
        "both"|"all"|"3")
            start_both
            ;;
        "test"|"tests"|"4")
            run_tests
            ;;
        "logs"|"log"|"5")
            show_logs
            ;;
        "setup"|"init"|"6")
            setup_dev
            ;;
        "help"|"-h"|"--help")
            print_menu
            echo ""
            echo "使用例:"
            echo "  ./entrypoint.sh fastapi    # FastAPI起動"
            echo "  ./entrypoint.sh adk        # ADK Web UI起動"
            echo "  ./entrypoint.sh both       # 両方起動"
            echo "  ./entrypoint.sh test       # テスト実行"
            ;;
        "")
            # 対話モード
            while true; do
                print_menu
                read -p "選択してください (0-6): " choice
                
                case $choice in
                    1)
                        start_fastapi
                        break
                        ;;
                    2)
                        start_adk_web
                        break
                        ;;
                    3)
                        start_both
                        break
                        ;;
                    4)
                        run_tests
                        ;;
                    5)
                        show_logs
                        ;;
                    6)
                        setup_dev
                        ;;
                    0)
                        echo -e "${GREEN}👋 終了します${NC}"
                        exit 0
                        ;;
                    *)
                        echo -e "${RED}無効な選択です${NC}"
                        ;;
                esac
            done
            ;;
        *)
            echo -e "${RED}無効なオプション: $1${NC}"
            echo "使用可能なオプション: fastapi, adk, both, test, logs, setup"
            echo "ヘルプ: ./entrypoint.sh help"
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"