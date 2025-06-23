#!/bin/bash

# GenieUs 簡易起動スクリプト
# Docker不要の開発環境起動

echo "🧞‍♂️ GenieUs を起動します..."

# バックエンドを別プロセスで起動
echo "🔧 バックエンドを起動中..."
cd backend && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# フロントエンドを別プロセスで起動
echo "📱 フロントエンドを起動中..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

# プロセスIDを保存
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✅ GenieUs が起動しました！"
echo ""
echo "📱 フロントエンド: http://localhost:3000"
echo "🔧 バックエンドAPI: http://localhost:8000"
echo "📖 API仕様書: http://localhost:8000/docs"
echo ""
echo "停止するには: ./stop.sh"
echo "または Ctrl+C"

# シグナルハンドラー
cleanup() {
    echo ""
    echo "🛑 GenieUs を停止しています..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    rm -f .backend.pid .frontend.pid
    echo "✅ 停止しました"
    exit 0
}

trap cleanup INT TERM

# プロセスの完了を待機
wait