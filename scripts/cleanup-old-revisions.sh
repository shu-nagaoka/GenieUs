#!/bin/bash

# Cloud Run 古いリビジョンクリーンアップスクリプト
# 最新3つのリビジョンを保持し、それ以外を削除

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 環境変数の確認
if [ -z "$GCP_PROJECT_ID" ] || [ -z "$GCP_REGION" ]; then
    echo -e "${RED}❌ 環境変数が設定されていません${NC}"
    echo "以下の環境変数を設定してください:"
    echo "  export GCP_PROJECT_ID=your-project-id"
    echo "  export GCP_REGION=asia-northeast1"
    exit 1
fi

echo -e "${BLUE}🧹 Cloud Run 古いリビジョンクリーンアップ${NC}"
echo -e "プロジェクト: ${YELLOW}$GCP_PROJECT_ID${NC}"
echo -e "リージョン: ${YELLOW}$GCP_REGION${NC}"
echo ""

# サービス一覧を取得
SERVICES=$(gcloud run services list --region="$GCP_REGION" --format="value(metadata.name)" --filter="metadata.name~genius")

if [ -z "$SERVICES" ]; then
    echo -e "${YELLOW}⚠️ geniusサービスが見つかりませんでした${NC}"
    exit 0
fi

echo -e "${GREEN}対象サービス:${NC}"
echo "$SERVICES" | while read service; do
    echo "  - $service"
done
echo ""

# 確認
read -p "古いリビジョンを削除しますか？（最新3つを保持）[y/N]: " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}キャンセルされました${NC}"
    exit 0
fi

echo ""

# 各サービスの古いリビジョンを削除
echo "$SERVICES" | while read service; do
    echo -e "${BLUE}📦 $service の古いリビジョンを削除中...${NC}"
    
    # 現在のリビジョン数を確認
    TOTAL_REVISIONS=$(gcloud run revisions list \
        --service="$service" \
        --region="$GCP_REGION" \
        --format="value(metadata.name)" | wc -l)
    
    echo "  現在のリビジョン数: $TOTAL_REVISIONS"
    
    if [ "$TOTAL_REVISIONS" -le 3 ]; then
        echo -e "  ${GREEN}✅ リビジョン数が3以下のため、削除対象なし${NC}"
        echo ""
        continue
    fi
    
    # 最新3つ以外のリビジョンを取得して削除
    OLD_REVISIONS=$(gcloud run revisions list \
        --service="$service" \
        --region="$GCP_REGION" \
        --format="value(metadata.name)" \
        --sort-by="~metadata.creationTimestamp" \
        --limit=1000 | tail -n +4)
    
    if [ -n "$OLD_REVISIONS" ]; then
        DELETE_COUNT=$(echo "$OLD_REVISIONS" | wc -l)
        echo "  削除対象リビジョン数: $DELETE_COUNT"
        
        echo "$OLD_REVISIONS" | while read revision; do
            echo "    削除中: $revision"
            if gcloud run revisions delete "$revision" \
                --region="$GCP_REGION" \
                --quiet 2>/dev/null; then
                echo -e "      ${GREEN}✅ 削除完了${NC}"
            else
                echo -e "      ${RED}❌ 削除失敗${NC}"
            fi
        done
        
        # 削除後のリビジョン数を確認
        NEW_TOTAL=$(gcloud run revisions list \
            --service="$service" \
            --region="$GCP_REGION" \
            --format="value(metadata.name)" | wc -l)
        
        echo -e "  ${GREEN}✅ 完了: $TOTAL_REVISIONS → $NEW_TOTAL リビジョン${NC}"
    else
        echo -e "  ${YELLOW}⚠️ 削除対象のリビジョンが見つかりませんでした${NC}"
    fi
    
    echo ""
done

echo -e "${GREEN}🎉 全サービスのクリーンアップ完了！${NC}"