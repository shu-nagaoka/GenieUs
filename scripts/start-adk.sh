#!/bin/bash

# GenieUs ADK Web UI 起動スクリプト
# Usage: ./start-adk.sh [start|stop]

set -e

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# PIDファイル
ADK_PID_FILE="./backend/.adk.pid"

print_logo() {
    echo -e "${YELLOW}"
    echo "🧞‍♂️ GenieUs ADK Web Interface"
    echo -e "${NC}"
}

# ADK Web UI起動
start_adk() {
    print_logo
    echo -e "${CYAN}🔧 ADK Web UIを起動中...${NC}"
    
    cd backend
    
    # 環境変数チェック
    if [ ! -f .env.dev ]; then
        echo -e "${RED}❌ .env.dev ファイルがありません${NC}"
        exit 1
    fi
    
    # ADK起動（バックグラウンド）
    nohup uv run adk web > adk.log 2>&1 &
    ADK_PID=$!
    echo $ADK_PID > $ADK_PID_FILE
    
    echo -e "${GREEN}✅ ADK Web UI起動完了 (PID: $ADK_PID)${NC}"
    echo ""
    echo -e "${BLUE}🧞‍♂️ ADK Web UI: http://localhost:8000${NC}"
    echo -e "${YELLOW}📝 ログ: tail -f backend/adk.log${NC}"
    echo -e "${YELLOW}⏹️  停止: ./start-adk.sh stop${NC}"
    echo ""
    
    cd ..
}

# ADK停止
stop_adk() {
    print_logo
    echo -e "${YELLOW}🛑 ADK Web UIを停止中...${NC}"
    
    if [ -f $ADK_PID_FILE ]; then
        ADK_PID=$(cat $ADK_PID_FILE)
        if kill -0 $ADK_PID 2>/dev/null; then
            kill $ADK_PID
            echo -e "${GREEN}✅ ADK Web UI停止 (PID: $ADK_PID)${NC}"
        fi
        rm -f $ADK_PID_FILE
    fi
    
    # adk プロセスも強制終了
    pkill -f "adk web" 2>/dev/null || true
    
    echo -e "${GREEN}✅ ADK Web UIを停止しました${NC}"
}

# メイン処理
case "${1:-start}" in
    "start")
        start_adk
        ;;
    "stop")
        stop_adk
        ;;
    *)
        print_logo
        echo "使用方法: ./start-adk.sh [start|stop]"
        echo ""
        echo "  start  ADK Web UIを起動"
        echo "  stop   ADK Web UIを停止"
        ;;
esac