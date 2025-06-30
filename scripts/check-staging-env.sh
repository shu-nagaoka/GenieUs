#!/bin/bash
# Staging環境チェック専用スクリプト

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 環境設定
PROJECT_ID="blog-sample-381923"
REGION="asia-northeast1"
ENVIRONMENT="staging"

# サービス名（固定）
BACKEND_SERVICE="genius-backend-staging"
FRONTEND_SERVICE="genius-frontend-staging"

# URL形式（Cloud Runの新しい形式）
BASE_DOMAIN="280304291898.asia-northeast1.run.app"
BACKEND_URL="https://${BACKEND_SERVICE}-${BASE_DOMAIN}"
FRONTEND_URL="https://${FRONTEND_SERVICE}-${BASE_DOMAIN}"

echo -e "${BLUE}🔍 GenieUs Staging Environment Check${NC}"
echo -e "${BLUE}====================================${NC}"
echo -e "Expected Backend URL: ${GREEN}${BACKEND_URL}${NC}"
echo -e "Expected Frontend URL: ${GREEN}${FRONTEND_URL}${NC}"
echo ""

# チェック結果のカウンター
total_checks=0
passed_checks=0
failed_checks=0
warnings=0

# チェック関数
check_item() {
    local check_name="$1"
    local check_result="$2"
    local expected="$3"
    local actual="$4"
    
    total_checks=$((total_checks + 1))
    
    if [[ "$check_result" == "pass" ]]; then
        echo -e "   ✅ ${check_name}: ${GREEN}${actual}${NC}"
        passed_checks=$((passed_checks + 1))
    elif [[ "$check_result" == "fail" ]]; then
        echo -e "   ❌ ${check_name}: ${RED}${actual}${NC}"
        if [[ -n "$expected" ]]; then
            echo -e "      Expected: ${expected}"
        fi
        failed_checks=$((failed_checks + 1))
    elif [[ "$check_result" == "warn" ]]; then
        echo -e "   ⚠️  ${check_name}: ${YELLOW}${actual}${NC}"
        if [[ -n "$expected" ]]; then
            echo -e "      Expected: ${expected}"
        fi
        warnings=$((warnings + 1))
    fi
}

# 1. ローカルファイルチェック
echo -e "${BLUE}1. Local Files Check${NC}"

# Dockerfileチェック
dockerfile_backend_url=$(grep "ENV NEXT_PUBLIC_API_BASE_URL" /Users/tnoce/dev/GenieUs/frontend/Dockerfile | cut -d'=' -f2 2>/dev/null || echo "not found")
if [[ "$dockerfile_backend_url" == "$BACKEND_URL" ]]; then
    check_item "Dockerfile NEXT_PUBLIC_API_BASE_URL" "pass" "" "$dockerfile_backend_url"
else
    check_item "Dockerfile NEXT_PUBLIC_API_BASE_URL" "fail" "$BACKEND_URL" "$dockerfile_backend_url"
fi

# .env.production.localチェック
if [[ -f "/Users/tnoce/dev/GenieUs/frontend/.env.production.local" ]]; then
    env_backend_url=$(grep "NEXT_PUBLIC_API_BASE_URL" /Users/tnoce/dev/GenieUs/frontend/.env.production.local | cut -d'=' -f2 2>/dev/null || echo "not found")
    if [[ "$env_backend_url" == "$BACKEND_URL" ]]; then
        check_item ".env.production.local" "pass" "" "$env_backend_url"
    else
        check_item ".env.production.local" "fail" "$BACKEND_URL" "$env_backend_url"
    fi
else
    check_item ".env.production.local" "warn" "file should exist" "file not found"
fi

echo ""

# 2. Cloud Run サービス状態チェック
echo -e "${BLUE}2. Cloud Run Services Check${NC}"

# サービスの存在チェック
backend_exists=$(gcloud run services describe ${BACKEND_SERVICE} --region=${REGION} --format="value(metadata.name)" 2>/dev/null || echo "")
if [[ -n "$backend_exists" ]]; then
    check_item "Backend service exists" "pass" "" "$BACKEND_SERVICE"
else
    check_item "Backend service exists" "fail" "$BACKEND_SERVICE" "service not found"
fi

frontend_exists=$(gcloud run services describe ${FRONTEND_SERVICE} --region=${REGION} --format="value(metadata.name)" 2>/dev/null || echo "")
if [[ -n "$frontend_exists" ]]; then
    check_item "Frontend service exists" "pass" "" "$FRONTEND_SERVICE"
else
    check_item "Frontend service exists" "fail" "$FRONTEND_SERVICE" "service not found"
fi

echo ""

# 3. 環境変数チェック
echo -e "${BLUE}3. Environment Variables Check${NC}"

if [[ -n "$frontend_exists" ]]; then
    current_frontend_api=$(gcloud run services describe ${FRONTEND_SERVICE} --region=${REGION} --format="json" 2>/dev/null | jq -r '.spec.template.spec.containers[0].env[]? | select(.name=="NEXT_PUBLIC_API_BASE_URL") | .value' || echo "not found")
    if [[ "$current_frontend_api" == "$BACKEND_URL" ]]; then
        check_item "Frontend API URL" "pass" "" "$current_frontend_api"
    else
        check_item "Frontend API URL" "warn" "$BACKEND_URL" "$current_frontend_api"
    fi
    
    current_nextauth_url=$(gcloud run services describe ${FRONTEND_SERVICE} --region=${REGION} --format="json" 2>/dev/null | jq -r '.spec.template.spec.containers[0].env[]? | select(.name=="NEXTAUTH_URL") | .value' || echo "not found")
    if [[ "$current_nextauth_url" == "$FRONTEND_URL" ]]; then
        check_item "Frontend NEXTAUTH_URL" "pass" "" "$current_nextauth_url"
    else
        check_item "Frontend NEXTAUTH_URL" "warn" "$FRONTEND_URL" "$current_nextauth_url"
    fi
fi

if [[ -n "$backend_exists" ]]; then
    current_cors=$(gcloud run services describe ${BACKEND_SERVICE} --region=${REGION} --format="json" 2>/dev/null | jq -r '.spec.template.spec.containers[0].env[]? | select(.name=="CORS_ORIGINS") | .value' || echo "not found")
    if [[ "$current_cors" == "$FRONTEND_URL" ]]; then
        check_item "Backend CORS" "pass" "" "$current_cors"
    else
        check_item "Backend CORS" "warn" "$FRONTEND_URL" "$current_cors"
    fi
fi

echo ""

# 4. 接続テスト
echo -e "${BLUE}4. Connectivity Check${NC}"

if [[ -n "$backend_exists" ]]; then
    # 実際のバックエンドURLを取得
    actual_backend_url=$(gcloud run services describe ${BACKEND_SERVICE} --region=${REGION} --format="value(status.url)" 2>/dev/null || echo "")
    if [[ -n "$actual_backend_url" ]]; then
        if curl -f "${actual_backend_url}/health" -m 10 >/dev/null 2>&1; then
            check_item "Backend health check" "pass" "" "${actual_backend_url}/health"
        else
            check_item "Backend health check" "fail" "HTTP 200" "connection failed"
        fi
    fi
fi

if [[ -n "$frontend_exists" ]]; then
    # 実際のフロントエンドURLを取得
    actual_frontend_url=$(gcloud run services describe ${FRONTEND_SERVICE} --region=${REGION} --format="value(status.url)" 2>/dev/null || echo "")
    if [[ -n "$actual_frontend_url" ]]; then
        if curl -f "${actual_frontend_url}" -m 10 >/dev/null 2>&1; then
            check_item "Frontend accessibility" "pass" "" "${actual_frontend_url}"
        else
            check_item "Frontend accessibility" "fail" "HTTP 200" "connection failed"
        fi
    fi
fi

echo ""

# 5. 認証・権限チェック
echo -e "${BLUE}5. Authentication & Permissions Check${NC}"

# gcloud認証チェック
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    active_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    check_item "gcloud authentication" "pass" "" "$active_account"
else
    check_item "gcloud authentication" "fail" "authenticated account" "not authenticated"
fi

# プロジェクトアクセスチェック
if gcloud projects describe ${PROJECT_ID} >/dev/null 2>&1; then
    check_item "Project access" "pass" "" "$PROJECT_ID"
else
    check_item "Project access" "fail" "$PROJECT_ID" "access denied"
fi

# Cloud Run APIチェック
if gcloud services list --enabled --filter="name:run.googleapis.com" --format="value(name)" | grep -q "run.googleapis.com"; then
    check_item "Cloud Run API" "pass" "" "enabled"
else
    check_item "Cloud Run API" "fail" "enabled" "not enabled"
fi

echo ""

# 結果サマリー
echo -e "${BLUE}📊 Check Summary${NC}"
echo -e "${BLUE}================${NC}"
echo -e "Total checks: ${total_checks}"
echo -e "✅ Passed: ${GREEN}${passed_checks}${NC}"
echo -e "⚠️  Warnings: ${YELLOW}${warnings}${NC}"
echo -e "❌ Failed: ${RED}${failed_checks}${NC}"
echo ""

# URLs表示
if [[ -n "$actual_backend_url" && -n "$actual_frontend_url" ]]; then
    echo -e "${BLUE}🌐 Actual URLs${NC}"
    echo -e "${BLUE}=============${NC}"
    echo -e "Frontend: ${GREEN}${actual_frontend_url}${NC}"
    echo -e "Backend:  ${GREEN}${actual_backend_url}${NC}"
    echo -e "API Docs: ${GREEN}${actual_backend_url}/docs${NC}"
    echo ""
fi

# 最終判定
if [[ $failed_checks -eq 0 ]]; then
    if [[ $warnings -eq 0 ]]; then
        echo -e "${GREEN}🎉 All checks passed! Ready for deployment.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Some warnings found. Deployment should work but may need attention.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Critical issues found. Please fix before deployment.${NC}"
    exit 1
fi