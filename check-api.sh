#!/bin/bash

# API整合性チェックスクリプト（プロジェクトルート用）
# 使用方法: ./check-api.sh

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🔍 GenieUs API整合性チェック${NC}"
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
if [ ! -f "scripts/check-api-consistency.js" ]; then
    echo -e "${RED}❌ API整合性チェックスクリプトが見つかりません${NC}"
    echo -e "${YELLOW}   scripts/check-api-consistency.js を確認してください${NC}"
    exit 1
fi

# API整合性チェック実行
echo -e "${BLUE}🚀 API整合性チェックを実行中...${NC}"
echo ""

node scripts/check-api-consistency.js

# 実行結果の確認
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ API整合性チェックが正常に完了しました${NC}"
else
    echo -e "${RED}❌ API整合性チェックでエラーが発生しました${NC}"
    echo -e "${YELLOW}   修正が必要な項目があります${NC}"
fi

echo -e "${BLUE}================================${NC}"
echo -e "${CYAN}📚 その他のコマンド:${NC}"
echo -e "   ${YELLOW}node scripts/update-api-mapping.js${NC}  # APIマッピング更新"
echo -e "   ${YELLOW}./update-api.sh${NC}                     # APIマッピング更新（シェル版）"

exit $EXIT_CODE