#!/bin/bash

# GenieUs開発環境起動スクリプト
# フロントエンドとバックエンドを一発で起動・リセット

echo "🚀 GenieUs開発環境を起動します..."

# 既存のプロセスを停止
echo "📛 既存のプロセスを停止中..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "   ポート3000: プロセスなし"
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "   ポート8000: プロセスなし"

sleep 2

# バックエンド起動
echo "🔧 バックエンドを起動中..."
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "   バックエンド PID: $BACKEND_PID (ポート8000)"

sleep 3

# フロントエンド起動
echo "🎨 フロントエンドを起動中..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "   フロントエンド PID: $FRONTEND_PID (ポート3000)"

sleep 3

echo "✅ 起動完了!"
echo ""
echo "📱 フロントエンド: http://localhost:3000"
echo "🔌 バックエンド: http://localhost:8000"
echo "📖 API ドキュメント: http://localhost:8000/docs"
echo ""
echo "停止するには Ctrl+C を押してください"

# シグナルハンドラー - Ctrl+Cで両方のプロセスを停止
cleanup() {
    echo ""
    echo "🛑 プロセスを停止中..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "✅ 停止完了"
    exit 0
}

trap cleanup SIGINT SIGTERM

# プロセスが生きている間待機
wait