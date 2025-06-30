#!/bin/bash
# Cloud SQL最小インスタンス自動セットアップスクリプト

set -e

PROJECT_ID="blog-sample-381923"
REGION="us-central1"
INSTANCE_NAME="genieus-postgres-mini"
DATABASE_NAME="genieus_db"
USERNAME="genieus_user"

echo "🚀 Cloud SQL最小インスタンス自動セットアップ開始"
echo "プロジェクト: $PROJECT_ID"
echo "リージョン: $REGION"
echo "インスタンス: $INSTANCE_NAME"
echo "=================================="

# 1. Google Cloud認証確認
echo "🔐 Google Cloud認証確認中..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Google Cloud認証が必要です"
    echo "実行してください: gcloud auth login"
    exit 1
fi

ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
echo "✅ 認証済み: $ACCOUNT"

# 2. プロジェクト設定
echo "📋 プロジェクト設定中..."
gcloud config set project $PROJECT_ID
echo "✅ プロジェクト設定完了: $PROJECT_ID"

# 3. 必要なAPI有効化
echo "🔧 必要なAPI有効化中..."
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
echo "✅ API有効化完了"

# 4. Cloud SQLインスタンス作成（最小構成）
echo "🗄️ Cloud SQL最小インスタンス作成中..."
if gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "✅ Cloud SQLインスタンス既存: $INSTANCE_NAME"
else
    echo "📦 新規Cloud SQLインスタンス作成中..."
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --maintenance-release-channel=production \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=02 \
        --deletion-protection \
        --no-backup
    
    echo "✅ Cloud SQLインスタンス作成完了"
fi

# 5. データベース作成
echo "📊 データベース作成中..."
if gcloud sql databases describe $DATABASE_NAME --instance=$INSTANCE_NAME --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "✅ データベース既存: $DATABASE_NAME"
else
    gcloud sql databases create $DATABASE_NAME --instance=$INSTANCE_NAME
    echo "✅ データベース作成完了: $DATABASE_NAME"
fi

# 6. ユーザー作成
echo "👤 ユーザー作成中..."
if gcloud sql users describe $USERNAME --instance=$INSTANCE_NAME --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "✅ ユーザー既存: $USERNAME"
else
    # パスワード生成
    PASSWORD=$(openssl rand -base64 32)
    
    gcloud sql users create $USERNAME \
        --instance=$INSTANCE_NAME \
        --password=$PASSWORD
    
    echo "✅ ユーザー作成完了: $USERNAME"
    echo "🔐 生成されたパスワード: $PASSWORD"
    
    # Secret Managerにパスワード保存
    echo "🔐 Secret Managerにパスワード保存中..."
    echo -n "$PASSWORD" | gcloud secrets create postgres-password --data-file=-
    echo "✅ Secret Manager保存完了"
fi

# 7. 接続設定情報表示
echo ""
echo "🎉 Cloud SQL最小インスタンス設定完了！"
echo "=================================="
echo "接続情報:"
echo "  インスタンス名: $INSTANCE_NAME"
echo "  接続名: $PROJECT_ID:$REGION:$INSTANCE_NAME"
echo "  データベース: $DATABASE_NAME"
echo "  ユーザー: $USERNAME"
echo "  パスワード: Secret Managerに保存済み"
echo ""
echo "📋 環境変数設定例:"
echo "export DATABASE_TYPE=postgresql"
echo "export CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$INSTANCE_NAME"
echo "export POSTGRES_USER=$USERNAME"
echo "export POSTGRES_DB=$DATABASE_NAME"
echo ""
echo "🧪 接続テスト実行:"
echo "python test_cloud_sql_connection.py"

# 8. 接続テスト実行確認
echo ""
read -p "接続テストを実行しますか？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 接続テスト実行中..."
    cd "$(dirname "$0")"
    python test_cloud_sql_connection.py
fi

echo "🎯 セットアップ完了！"