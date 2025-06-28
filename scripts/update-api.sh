#!/bin/bash

# APIマッピング更新スクリプト（プロジェクトルート用）
# 使用方法: ./update-api.sh

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🔄 GenieUs APIマッピング更新${NC}"
echo -e "${BLUE}================================${NC}"

# Node.js の確認
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js がインストールされていません${NC}"
    echo -e "${YELLOW}   Node.js 16以上をインストールしてください${NC}"
    exit 1
fi

# Node.jsバージョン確認
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js バージョン: ${NODE_VERSION}${NC}"

# スクリプトファイルの存在確認
if [ ! -f "scripts/update-api-mapping.js" ]; then
    echo -e "${RED}❌ APIマッピング更新スクリプトが見つかりません${NC}"
    echo -e "${YELLOW}   scripts/update-api-mapping.js を確認してください${NC}"
    exit 1
fi

# 現在のマッピングファイルをバックアップ
if [ -f "api-endpoints-mapping.json" ]; then
    BACKUP_FILE="api-endpoints-mapping.json.backup.$(date +%Y%m%d_%H%M%S)"
    cp "api-endpoints-mapping.json" "$BACKUP_FILE"
    echo -e "${YELLOW}📋 既存マッピングをバックアップ: ${BACKUP_FILE}${NC}"
fi

# APIマッピング更新実行
echo -e "${BLUE}🚀 APIマッピング更新を実行中...${NC}"
echo ""

node scripts/update-api-mapping.js

# 実行結果の確認
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ APIマッピング更新が正常に完了しました${NC}"
    echo -e "${CYAN}📊 更新後の整合性チェックを実行します...${NC}"
    echo ""
    
    # 更新後に整合性チェックを自動実行
    node scripts/check-api-consistency.js
    
else
    echo -e "${RED}❌ APIマッピング更新でエラーが発生しました${NC}"
    
    # エラー時はバックアップから復元
    if [ -f "$BACKUP_FILE" ]; then
        echo -e "${YELLOW}🔄 バックアップから復元中...${NC}"
        cp "$BACKUP_FILE" "api-endpoints-mapping.json"
        echo -e "${GREEN}✅ バックアップから復元しました${NC}"
    fi
fi

echo -e "${BLUE}================================${NC}"
echo -e "${CYAN}📚 その他のコマンド:${NC}"
echo -e "   ${YELLOW}./check-api.sh${NC}                      # API整合性チェック"
echo -e "   ${YELLOW}node scripts/check-api-consistency.js${NC}  # 整合性チェック（Node.js版）"

exit $EXIT_CODE