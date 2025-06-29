#!/bin/bash
# 既存のCloud Runサービスの環境変数を更新

set -e

# 使用方法
usage() {
    echo "Usage: $0 <environment> <service> [key=value ...]"
    echo ""
    echo "Services: frontend, backend"
    echo ""
    echo "Examples:"
    echo "  $0 staging frontend GOOGLE_CLIENT_ID=new-client-id"
    echo "  $0 production backend LOG_LEVEL=DEBUG"
    exit 1
}

if [ $# -lt 3 ]; then
    usage
fi

ENVIRONMENT=$1
SERVICE_TYPE=$2
shift 2

# 環境変数を読み込み
source scripts/load-env.sh "$ENVIRONMENT"

# サービス名を決定
if [ "$SERVICE_TYPE" = "frontend" ]; then
    SERVICE_NAME=$FRONTEND_SERVICE_NAME
elif [ "$SERVICE_TYPE" = "backend" ]; then
    SERVICE_NAME=$BACKEND_SERVICE_NAME
else
    echo "Error: Unknown service type: $SERVICE_TYPE"
    usage
fi

echo "🔧 Updating environment variables for $SERVICE_NAME"

# 環境変数を更新
UPDATE_ARGS=""
for arg in "$@"; do
    UPDATE_ARGS="$UPDATE_ARGS --update-env-vars $arg"
done

gcloud run services update "$SERVICE_NAME" \
    --region "$GCP_REGION" \
    --project "$GCP_PROJECT_ID" \
    $UPDATE_ARGS

echo "✅ Environment variables updated successfully"

# サービスURL表示
URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$GCP_REGION" \
    --project "$GCP_PROJECT_ID" \
    --format "value(status.url)")

echo "Service URL: $URL"