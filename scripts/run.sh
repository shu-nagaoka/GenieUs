#!/bin/bash

# GenieUs アプリケーション起動スクリプト
# Usage: ./run.sh [dev|prod|stop|clean]

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo -e "${BLUE}🧞‍♂️ AI子育て支援アプリケーション${NC}"
    echo -e "${GREEN}✨ あなたの育児をサポートする魔法のジーニー ✨${NC}"
    echo ""
}

# ヘルプ表示
show_help() {
    echo "使用方法: ./run.sh [COMMAND]"
    echo ""
    echo "COMMANDS:"
    echo "  dev     開発環境で起動 (ホットリロード有効)"
    echo "  prod    本番環境で起動"
    echo "  stop    すべてのコンテナを停止"
    echo "  clean   すべてのコンテナとボリュームを削除"
    echo "  logs    ログを表示"
    echo "  status  サービスの状態を表示"
    echo "  help    このヘルプを表示"
    echo ""
    echo "例:"
    echo "  ./run.sh dev    # 開発環境で起動"
    echo "  ./run.sh prod   # 本番環境で起動"
    echo "  ./run.sh stop   # 停止"
    echo ""
}

# 開発環境起動
start_dev() {
    echo -e "${GREEN}🚀 開発環境を起動しています...${NC}"
    
    # Docker Composeで開発環境起動
    docker-compose -f docker-compose.dev.yml up --build -d
    
    echo -e "${GREEN}✅ 開発環境が起動しました！${NC}"
    echo ""
    echo -e "${BLUE}📱 フロントエンド: http://localhost:3000${NC}"
    echo -e "${BLUE}🔧 バックエンドAPI: http://localhost:8000${NC}"
    echo -e "${BLUE}📖 API仕様書: http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}ログを確認: ./run.sh logs${NC}"
    echo -e "${YELLOW}停止: ./run.sh stop${NC}"
}

# 本番環境起動
start_prod() {
    echo -e "${GREEN}🚀 本番環境を起動しています...${NC}"
    
    # Docker Composeで本番環境起動
    docker-compose up --build -d
    
    echo -e "${GREEN}✅ 本番環境が起動しました！${NC}"
    echo ""
    echo -e "${BLUE}📱 アプリケーション: http://localhost:3000${NC}"
    echo -e "${BLUE}🔧 API: http://localhost:8000${NC}"
    echo ""
    echo -e "${YELLOW}ログを確認: ./run.sh logs${NC}"
    echo -e "${YELLOW}停止: ./run.sh stop${NC}"
}

# サービス停止
stop_services() {
    echo -e "${YELLOW}🛑 サービスを停止しています...${NC}"
    
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    echo -e "${GREEN}✅ すべてのサービスを停止しました${NC}"
}

# クリーンアップ
clean_all() {
    echo -e "${RED}🧹 すべてのコンテナとボリュームを削除しています...${NC}"
    
    # 確認プロンプト
    read -p "本当にすべてのデータを削除しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}キャンセルしました${NC}"
        exit 0
    fi
    
    docker-compose -f docker-compose.dev.yml down -v --remove-orphans 2>/dev/null || true
    docker-compose down -v --remove-orphans 2>/dev/null || true
    
    # GenieUs関連のイメージを削除
    docker images | grep GenieUs | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true
    
    echo -e "${GREEN}✅ クリーンアップが完了しました${NC}"
}

# ログ表示
show_logs() {
    echo -e "${BLUE}📝 ログを表示します (Ctrl+C で終了)...${NC}"
    
    if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.dev.yml logs -f
    elif docker-compose ps | grep -q "Up"; then
        docker-compose logs -f
    else
        echo -e "${RED}❌ 起動中のサービスがありません${NC}"
    fi
}

# ステータス表示
show_status() {
    echo -e "${BLUE}📊 サービス状態:${NC}"
    echo ""
    
    if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        echo -e "${GREEN}開発環境:${NC}"
        docker-compose -f docker-compose.dev.yml ps
    elif docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}本番環境:${NC}"
        docker-compose ps
    else
        echo -e "${YELLOW}起動中のサービスはありません${NC}"
    fi
}

# 前提条件チェック
check_prerequisites() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Dockerがインストールされていません${NC}"
        echo "https://docs.docker.com/get-docker/ からインストールしてください"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Composeがインストールされていません${NC}"
        echo "https://docs.docker.com/compose/install/ からインストールしてください"
        exit 1
    fi
}

# メイン処理
main() {
    print_logo
    check_prerequisites
    
    case "${1:-help}" in
        "dev")
            start_dev
            ;;
        "prod")
            start_prod
            ;;
        "stop")
            stop_services
            ;;
        "clean")
            clean_all
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 不明なコマンド: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"