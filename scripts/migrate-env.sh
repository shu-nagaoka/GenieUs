#!/bin/bash
# 既存の環境変数設定をenvironments/に移行するヘルパースクリプト

echo "🔄 環境変数移行ヘルパー"
echo "====================="
echo ""
echo "このスクリプトは既存の.envファイルの値を"
echo "environments/ディレクトリの設定に反映します。"
echo ""

# バックアップ作成
if [ -f "frontend/.env.local" ]; then
    echo "📋 frontend/.env.localの値を確認してください："
    echo "これらの値をenvironments/.env.localに手動で設定してください"
    grep -E "GOOGLE_CLIENT_ID|GOOGLE_CLIENT_SECRET|NEXTAUTH_SECRET" frontend/.env.local || echo "（OAuth設定なし）"
    echo ""
fi

if [ -f "backend/.env.dev" ]; then
    echo "📋 backend/.env.devはそのまま残します（開発用デフォルト）"
    echo ""
fi

echo "📝 推奨される環境構成："
echo ""
echo "environments/"
echo "├── .env.local          # ローカル開発（全体設定）"
echo "├── .env.staging        # ステージング環境"
echo "└── .env.production     # 本番環境"
echo ""
echo "frontend/"
echo "├── .env.local          # 個人のOAuth設定（Git無視）"
echo "└── .env.example        # 設定例"
echo ""
echo "backend/"
echo "├── .env.dev            # 開発用デフォルト"
echo "└── （.env.productionは削除済み）"
echo ""
echo "✅ 移行完了！"
echo ""
echo "次のステップ："
echo "1. environments/.env.localにOAuth設定を追加"
echo "2. ./scripts/start-local-with-env.sh で開発開始"
echo "3. ./scripts/deploy-with-env.sh staging でデプロイ"