#!/bin/bash

# GenieUs 開発環境起動スクリプト
# Usage: ./start-dev.sh [start|stop|restart]

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# PIDファイルのパス
BACKEND_PID_FILE="./backend/.backend.pid"
FRONTEND_PID_FILE="./frontend/.frontend.pid"
DOCS_PID_FILE="./docs/.docs.pid"

# 環境チェック
check_prerequisites() {
    echo -e "${CYAN}🔍 環境をチェック中...${NC}"
    
    # Node.js チェック
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.jsがインストールされていません${NC}"
        exit 1
    fi
    
    # Python チェック
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3がインストールされていません${NC}"
        exit 1
    fi
    
    # uv チェック
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uvがインストールされていません${NC}"
        echo "pip install uv でインストールしてください"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 必要な環境が揃っています${NC}"
}

# バックエンド起動
start_backend() {
    echo -e "${CYAN}🔧 バックエンドを起動中...${NC}"
    cd backend
    
    # 環境変数をチェック
    if [ ! -f .env.dev ]; then
        echo -e "${RED}❌ .env.dev ファイルがありません${NC}"
        exit 1
    fi
    
    # uvでバックエンド起動（バックグラウンド）
    nohup uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ".backend.pid"
    
    echo -e "${GREEN}✅ バックエンド起動完了 (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}   🔗 API: http://localhost:8000${NC}"
    echo -e "${BLUE}   📖 Docs: http://localhost:8000/docs${NC}"
    
    cd ..
}

# フロントエンド起動
start_frontend() {
    echo -e "${CYAN}📱 フロントエンドを起動中...${NC}"
    cd frontend
    
    # npm install (必要に応じて)
    if [ ! -d node_modules ]; then
        echo -e "${YELLOW}📦 依存関係をインストール中...${NC}"
        npm install
    fi
    
    # Next.js起動（バックグラウンド）
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ".frontend.pid"
    
    echo -e "${GREEN}✅ フロントエンド起動完了 (PID: $FRONTEND_PID)${NC}"
    echo -e "${BLUE}   🔗 アプリ: http://localhost:3000${NC}"
    echo -e "${BLUE}   💬 チャット: http://localhost:3000/chat${NC}"
    
    cd ..
}

# ドキュメントサーバー起動
start_docs_server() {
    echo -e "${CYAN}📚 ドキュメントサーバーを起動中...${NC}"
    cd docs
    
    # ドキュメントサーバーをバックグラウンドで起動
    python3 serve.py > docs.log 2>&1 &
    DOCS_PID=$!
    echo $DOCS_PID > .docs.pid
    
    echo -e "${GREEN}✅ ドキュメントサーバー起動完了 (PID: $DOCS_PID)${NC}"
    echo -e "${BLUE}   🔗 ドキュメント: http://localhost:15080${NC}"
    
    cd ..
}

# プロセス停止
stop_services() {
    echo -e "${YELLOW}🛑 サービスを停止中...${NC}"
    
    # バックエンド停止
    if [ -f "./backend/.backend.pid" ]; then
        BACKEND_PID=$(cat "./backend/.backend.pid")
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo -e "${GREEN}✅ バックエンド停止 (PID: $BACKEND_PID)${NC}"
        fi
        rm -f "./backend/.backend.pid"
    fi
    
    # フロントエンド停止
    if [ -f "./frontend/.frontend.pid" ]; then
        FRONTEND_PID=$(cat "./frontend/.frontend.pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo -e "${GREEN}✅ フロントエンド停止 (PID: $FRONTEND_PID)${NC}"
        fi
        rm -f "./frontend/.frontend.pid"
    fi
    
    # ドキュメントサーバー停止
    if [ -f "./docs/.docs.pid" ]; then
        DOCS_PID=$(cat "./docs/.docs.pid")
        if kill -0 $DOCS_PID 2>/dev/null; then
            kill $DOCS_PID
            echo -e "${GREEN}✅ ドキュメントサーバー停止 (PID: $DOCS_PID)${NC}"
        fi
        rm -f "./docs/.docs.pid"
    fi
    
    # プロセスも強制終了
    pkill -f "uvicorn.*src.main:app" 2>/dev/null || true
    pkill -f "next.*dev" 2>/dev/null || true
    pkill -f "python3.*serve.py" 2>/dev/null || true
    
    echo -e "${GREEN}✅ すべてのサービスを停止しました${NC}"
}

# ロゴ表示
print_logo() {
    echo -e "${CYAN}"
    echo "  ____            _      _   _           _   "
    echo " / ___| ___ _ __ (_) ___| \ | | ___  ___| |_ "
    echo "| |  _ / _ \ '_ \| |/ _ \  \| |/ _ \/ __| __|"
    echo "| |_| |  __/ | | | |  __/ |\  |  __/\__ \ |_ "
    echo " \____|\___|_| |_|_|\___|_| \_|\___||___/\__|"
    echo -e "${NC}"
    echo -e "${BLUE}AI子育て支援アプリケーション ${YELLOW}v0.1.0${NC}"
    echo ""
}

# サービス起動
start_services() {
    print_logo
    check_prerequisites
    
    echo -e "${GREEN}🚀 GenieUs 開発環境を起動中...${NC}"
    echo ""
    
    # まず停止（既存プロセスがあれば）
    stop_services
    
    # バックエンド起動
    start_backend
    
    # バックエンドの起動を待つ
    echo -e "${CYAN}⏳ バックエンドの起動を待機中...${NC}"
    sleep 5
    
    # ヘルスチェック
    for i in {1..10}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ バックエンドが正常に起動しました${NC}"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ バックエンドの起動に失敗しました${NC}"
            echo -e "${YELLOW}💡 ログを確認: tail -f backend/backend.log${NC}"
            exit 1
        fi
        sleep 2
    done
    
    # フロントエンド起動
    start_frontend
    
    # ドキュメントサーバー起動
    start_docs_server
    
    # フロントエンドの起動を待つ
    echo -e "${CYAN}⏳ フロントエンドの起動を待機中...${NC}"
    sleep 8
    
    # 起動完了メッセージ
    echo ""
    echo -e "${GREEN}🎉 GenieUs 開発環境が起動しました！${NC}"
    echo ""
    echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│             アクセス情報              │${NC}"
    echo -e "${BLUE}├─────────────────────────────────────┤${NC}"
    echo -e "${BLUE}│ 📱 フロントエンド: ${GREEN}http://localhost:3000${BLUE} │${NC}"
    echo -e "${BLUE}│ 💬 チャット画面:   ${GREEN}http://localhost:3000/chat${BLUE} │${NC}"
    echo -e "${BLUE}│ 🔧 API:           ${GREEN}http://localhost:8000${BLUE} │${NC}"
    echo -e "${BLUE}│ 📖 API仕様書:     ${GREEN}http://localhost:8000/docs${BLUE} │${NC}"
    echo -e "${BLUE}│ 🧞‍♂️ ADK Web UI:   ${GREEN}http://localhost:8001${BLUE} │${NC}"
    echo -e "${BLUE}│ 📚 ドキュメント:   ${GREEN}http://localhost:15080${BLUE} │${NC}"
    echo -e "${BLUE}└─────────────────────────────────────┘${NC}"
    echo ""
    echo -e "${YELLOW}💡 コマンド:${NC}"
    echo -e "${YELLOW}   ./start-dev.sh stop    # 停止${NC}"
    echo -e "${YELLOW}   ./start-dev.sh restart # 再起動${NC}"
    echo -e "${YELLOW}   tail -f backend/backend.log   # バックエンドログ${NC}"
    echo -e "${YELLOW}   tail -f frontend/frontend.log # フロントエンドログ${NC}"
    echo ""
}

# ステータス表示
show_status() {
    echo -e "${BLUE}📊 サービス状態:${NC}"
    echo ""
    
    # バックエンド
    if [ -f "./backend/.backend.pid" ]; then
        BACKEND_PID=$(cat "./backend/.backend.pid")
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${GREEN}✅ バックエンド: 実行中 (PID: $BACKEND_PID)${NC}"
        else
            echo -e "${RED}❌ バックエンド: 停止中${NC}"
        fi
    else
        echo -e "${RED}❌ バックエンド: 停止中${NC}"
    fi
    
    # フロントエンド
    if [ -f "./frontend/.frontend.pid" ]; then
        FRONTEND_PID=$(cat "./frontend/.frontend.pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${GREEN}✅ フロントエンド: 実行中 (PID: $FRONTEND_PID)${NC}"
        else
            echo -e "${RED}❌ フロントエンド: 停止中${NC}"
        fi
    else
        echo -e "${RED}❌ フロントエンド: 停止中${NC}"
    fi
}

# ヘルプ表示
show_help() {
    echo "使用方法: ./start-dev.sh [COMMAND]"
    echo ""
    echo "COMMANDS:"
    echo "  start    開発環境を起動 (デフォルト)"
    echo "  stop     すべてのサービスを停止"
    echo "  restart  サービスを再起動"
    echo "  docs     ドキュメントサーバーのみ起動"
    echo "  status   サービスの状態を表示"
    echo "  help     このヘルプを表示"
    echo ""
    echo "例:"
    echo "  ./start-dev.sh         # 起動"
    echo "  ./start-dev.sh start   # 起動"
    echo "  ./start-dev.sh stop    # 停止"
    echo "  ./start-dev.sh restart # 再起動"
    echo "  ./start-dev.sh docs    # ドキュメントのみ"
    echo ""
}

# メイン処理
main() {
    case "${1:-start}" in
        "start")
            start_services
            ;;
        "stop")
            print_logo
            stop_services
            ;;
        "restart")
            print_logo
            stop_services
            echo ""
            start_services
            ;;
        "docs")
            print_logo
            echo -e "${GREEN}🚀 ドキュメントサーバーを起動します${NC}"
            echo ""
            start_docs_server
            echo ""
            echo -e "${GREEN}🎉 ドキュメントサーバーが起動しました！${NC}"
            echo ""
            echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
            echo -e "${BLUE}│          ドキュメントアクセス          │${NC}"
            echo -e "${BLUE}├─────────────────────────────────────┤${NC}"
            echo -e "${BLUE}│ 📚 ドキュメント:   ${GREEN}http://localhost:15080${BLUE} │${NC}"
            echo -e "${BLUE}└─────────────────────────────────────┘${NC}"
            echo ""
            echo -e "${YELLOW}💡 停止: ./start-dev.sh stop${NC}"
            echo ""
            ;;
        "status")
            print_logo
            show_status
            ;;
        "help"|"--help"|"-h")
            print_logo
            show_help
            ;;
        *)
            print_logo
            echo -e "${RED}❌ 不明なコマンド: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"