#!/bin/bash
# 環境変数ファイルを読み込んでCloud Build用の置換変数を生成

set -e

# 使用方法チェック
if [ $# -ne 1 ]; then
    echo "Usage: $0 <environment>"
    echo "Available environments: local, staging, production"
    exit 1
fi

ENVIRONMENT=$1
ENV_FILE="environments/.env.${ENVIRONMENT}"

# 環境変数ファイルの存在チェック
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file not found: $ENV_FILE"
    exit 1
fi

echo "🔧 Loading environment: $ENVIRONMENT"

# 環境変数をエクスポート
set -a
source "$ENV_FILE"
set +a

# Cloud Build用の置換変数を生成
generate_substitutions() {
    local substitutions=""
    
    # 基本設定
    substitutions="_GCP_PROJECT_ID=${GCP_PROJECT_ID}"
    substitutions+=",_GCP_REGION=${GCP_REGION}"
    substitutions+=",_ENVIRONMENT=${ENVIRONMENT}"
    substitutions+=",_BACKEND_SERVICE_NAME=${BACKEND_SERVICE_NAME}"
    substitutions+=",_FRONTEND_SERVICE_NAME=${FRONTEND_SERVICE_NAME}"
    
    # Backend設定
    substitutions+=",_GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI}"
    substitutions+=",_GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}"
    substitutions+=",_DATABASE_URL=${DATABASE_URL}"
    substitutions+=",_LOG_LEVEL=${LOG_LEVEL}"
    substitutions+=",_ROUTING_STRATEGY=${ROUTING_STRATEGY:-enhanced}"
    
    # Service設定
    substitutions+=",_BACKEND_MIN_INSTANCES=${BACKEND_MIN_INSTANCES}"
    substitutions+=",_BACKEND_MAX_INSTANCES=${BACKEND_MAX_INSTANCES}"
    substitutions+=",_FRONTEND_MIN_INSTANCES=${FRONTEND_MIN_INSTANCES}"
    substitutions+=",_FRONTEND_MAX_INSTANCES=${FRONTEND_MAX_INSTANCES}"
    substitutions+=",_NODE_ENV=${NODE_ENV}"
    
    # OAuth設定
    substitutions+=",_NEXTAUTH_SECRET=${NEXTAUTH_SECRET}"
    substitutions+=",_GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}"
    substitutions+=",_GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}"
    
    # API Keys
    if [ ! -z "$GOOGLE_API_KEY" ]; then
        substitutions+=",_GOOGLE_API_KEY=${GOOGLE_API_KEY}"
    fi
    if [ ! -z "$GOOGLE_AIPSK" ]; then
        substitutions+=",_GOOGLE_AIPSK=${GOOGLE_AIPSK}"
    fi
    
    echo "$substitutions"
}

# 環境変数の検証
validate_env() {
    local errors=0
    
    # 必須変数のチェック
    required_vars=(
        "GCP_PROJECT_ID"
        "GCP_REGION"
        "ENVIRONMENT"
        "BACKEND_SERVICE_NAME"
        "FRONTEND_SERVICE_NAME"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "❌ Error: Required variable $var is not set"
            ((errors++))
        fi
    done
    
    # OAuth設定の警告
    if [[ "$GOOGLE_CLIENT_ID" == *"your-"* ]]; then
        echo "⚠️  Warning: GOOGLE_CLIENT_ID seems to be a placeholder"
    fi
    if [[ "$GOOGLE_CLIENT_SECRET" == *"your-"* ]]; then
        echo "⚠️  Warning: GOOGLE_CLIENT_SECRET seems to be a placeholder"
    fi
    
    if [ $errors -gt 0 ]; then
        echo "❌ Validation failed with $errors errors"
        exit 1
    fi
    
    echo "✅ Environment validation passed"
}

# メイン処理
validate_env

# 置換変数を出力（他のスクリプトから使用）
if [ "${EXPORT_SUBSTITUTIONS}" = "true" ]; then
    generate_substitutions
fi

echo "✅ Environment loaded: $ENVIRONMENT"