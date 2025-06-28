#!/bin/bash

# GenieUs Documentation Server Launcher
# 
# Usage:
#   ./start-docs.sh          # 高機能ビューアーで起動
#   ./start-docs.sh simple   # シンプル版で起動
#   ./start-docs.sh --help   # ヘルプ表示

set -e

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ヘルプ表示
# ポート停止関数
stop_docs_server() {
    echo -e "${YELLOW}🛑 ドキュメントサーバーを停止中...${NC}"
    
    PORT=15080
    PID=$(lsof -ti:$PORT 2>/dev/null)
    
    if [ -n "$PID" ]; then
        echo -e "${BLUE}📍 ポート $PORT で実行中のプロセス (PID: $PID) を停止します${NC}"
        kill $PID 2>/dev/null
        sleep 1
        
        # 強制終了が必要かチェック
        if lsof -ti:$PORT >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  通常停止に失敗、強制停止中...${NC}"
            kill -9 $PID 2>/dev/null
            sleep 1
        fi
        
        if ! lsof -ti:$PORT >/dev/null 2>&1; then
            echo -e "${GREEN}✅ ドキュメントサーバーを停止しました${NC}"
        else
            echo -e "${RED}❌ サーバー停止に失敗しました${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  ポート $PORT でドキュメントサーバーは実行されていません${NC}"
    fi
}

# ポートチェック・停止関数
check_and_stop_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}⚠️  ポート $port が使用中です (PID: $pid)${NC}"
        echo -e "${BLUE}🔄 既存のサーバーを停止中...${NC}"
        
        kill $pid 2>/dev/null
        sleep 2
        
        # 強制終了が必要かチェック
        if lsof -ti:$port >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  強制停止中...${NC}"
            kill -9 $pid 2>/dev/null
            sleep 1
        fi
        
        if ! lsof -ti:$port >/dev/null 2>&1; then
            echo -e "${GREEN}✅ ポート $port を解放しました${NC}"
        else
            echo -e "${RED}❌ ポート解放に失敗しました${NC}"
            exit 1
        fi
    fi
}

show_help() {
    echo -e "${CYAN}"
    echo "🧞‍♂️ GenieUs Documentation Server"
    echo -e "${NC}"
    echo "📖 Markdownドキュメントをローカルで閲覧するためのツール"
    echo ""
    echo -e "${YELLOW}使用方法:${NC}"
    echo "  ./start-docs.sh          # 高機能ビューアーで起動（推奨）"
    echo "  ./start-docs.sh simple   # シンプル版HTMLで起動"
    echo "  ./start-docs.sh stop     # ドキュメントサーバー停止"
    echo "  ./start-docs.sh --help   # このヘルプを表示"
    echo ""
    echo -e "${YELLOW}機能:${NC}"
    echo "  📋 階層化されたナビゲーション"
    echo "  🎨 シンタックスハイライト"
    echo "  📱 レスポンシブデザイン"
    echo "  🔍 リアルタイムMarkdown表示"
    echo "  📑 ブラウザ履歴対応"
    echo "  🔄 マークダウン自動更新検知 (5秒間隔)"
    echo ""
    echo -e "${YELLOW}対象ドキュメント:${NC}"
    echo "  🏗️  アーキテクチャ設計思想"
    echo "  👨‍💻 開発ガイド・規約"
    echo "  ⚙️  技術詳細・ベストプラクティス"
    echo "  📖 実装チュートリアル"
    echo ""
}

# メイン実行
main() {
    local mode="viewer"
    
    # 引数処理
    case "${1:-}" in
        "--help"|"-h")
            show_help
            exit 0
            ;;
        "stop")
            stop_docs_server
            exit 0
            ;;
        "simple")
            mode="simple"
            ;;
        "")
            mode="viewer"
            ;;
        *)
            echo -e "${RED}❌ 不明なオプション: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    # docsディレクトリに移動
    cd "$(dirname "$0")"
    
    echo -e "${CYAN}"
    echo "🧞‍♂️ GenieUs Documentation Server"
    echo -e "${NC}"
    echo -e "${BLUE}📖 ドキュメントサーバーを起動中...${NC}"
    echo ""
    
    # Pythonが利用可能かチェック
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3が見つかりません${NC}"
        echo "Python3をインストールしてから再実行してください"
        exit 1
    fi
    
    # サーバー起動
    if [ "$mode" = "simple" ]; then
        echo -e "${YELLOW}🎯 シンプル版HTMLビューアーで起動${NC}"
        echo ""
        python3 -c "
import webbrowser
import http.server
import socketserver
import os

PORT = 15080
os.chdir('$(pwd)')

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        super().do_GET()

try:
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f'📋 シンプル版ドキュメント: http://localhost:{PORT}')
        print('⏹️  停止: Ctrl+C')
        print('')
        webbrowser.open(f'http://localhost:{PORT}')
        httpd.serve_forever()
except KeyboardInterrupt:
    print('\\n👋 サーバーを停止しました')
"
    else
        echo -e "${YELLOW}🎯 高機能ビューアー（自動更新対応）で起動${NC}"
        echo ""
        # docsディレクトリから起動（web/とmarkdownファイル両方にアクセス可能）
        python3 serve.py
    fi
}

# エラーハンドリング
trap 'echo -e "\n${YELLOW}👋 ドキュメントサーバーを停止しました${NC}"; exit 0' INT

# 実行
main "$@"